"""
simulate.py - TV3: Mô phỏng quỹ đạo, timestamp, offset, tính E_pre

Nhiệm vụ:
  - Mô phỏng quỹ đạo xe và vị trí vật thể
  - Tạo timestamp camera (30Hz) và LiDAR (10Hz)
  - Áp dụng offset vào LiDAR
  - Tính E_pre = khoảng cách giữa vị trí LiDAR (lệch time) vs vị trí thực ở thời điểm camera
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class SimulationConfig:
    """Cấu hình mô phỏng"""
    duration_sec: float
    velocity_ms: float
    acceleration_ms2: float
    turn_radius_m: float = None
    yaw_rate_rads: float = 0.0
    camera_freq_hz: int = 30
    lidar_freq_hz: int = 10
    object_distance_m: float = 10.0
    lidar_noise_sigma_m: float = 0.02
    random_seed: int = 42


class ObjectTrajectorySimulator:
    """Mô phỏng quỹ đạo xe và vị trí vật thể"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        np.random.seed(config.random_seed)
        self.rng = np.random.RandomState(config.random_seed)
    
    def get_vehicle_state(self, t: float) -> Tuple[float, float, float, float]:
        """
        Lấy vị trí và hướng xe tại thời gian t
        
        Returns:
            (x, y, yaw, v) - vị trí xe (m), hướng (rad), vận tốc (m/s)
        """
        # Vị trí xe dọc trục x (chuyển động thuận)
        if self.config.acceleration_ms2 != 0:
            # Tăng tốc: x = v0*t + 0.5*a*t²
            x = self.config.velocity_ms * t + 0.5 * self.config.acceleration_ms2 * t**2
            v = self.config.velocity_ms + self.config.acceleration_ms2 * t
        else:
            # Chuyển động đều
            x = self.config.velocity_ms * t
            v = self.config.velocity_ms
        
        # Góc quay (yaw)
        yaw = self.config.yaw_rate_rads * t
        
        # Vị trí y (0 nếu chạy thẳng)
        if self.config.turn_radius_m is not None and self.config.turn_radius_m > 0:
            # Quỹ đạo tròn: y = R * (1 - cos(yaw))
            y = self.config.turn_radius_m * (1 - np.cos(yaw))
        else:
            y = 0.0
        
        return x, y, yaw, v
    
    def get_object_position_camera_frame(self, t: float) -> Tuple[float, float]:
        """
        Vị trí vật thể trong hệ tọa độ camera (xe)
        Vật thể tĩnh trong hệ tọa độ tuyệt đối ở vị trí (object_distance_m, 0)
        
        Returns:
            (obj_x, obj_y) - tọa độ vật thể so với xe ở thời gian t
        """
        # Vị trí vật thể tĩnh trong hệ tọa độ tuyệt đối
        obj_abs_x = self.config.object_distance_m
        obj_abs_y = 0.0
        
        # Vị trí xe
        xe_x, xe_y, yaw, _ = self.get_vehicle_state(t)
        
        # Chuyển vị trí vật thể từ hệ tọa độ tuyệt đối sang hệ tọa độ xe
        # Bước 1: Dịch xe về gốc
        dx = obj_abs_x - xe_x
        dy = obj_abs_y - xe_y
        
        # Bước 2: Quay ngược góc xe để đưa vào hệ xe (rotate by -yaw)
        cos_yaw = np.cos(-yaw)
        sin_yaw = np.sin(-yaw)
        obj_x = dx * cos_yaw - dy * sin_yaw
        obj_y = -dx * sin_yaw + dy * cos_yaw
        
        return obj_x, obj_y
    
    def simulate(self) -> Dict:
        """
        Chạy mô phỏng và trả về timestamp + vị trí
        
        Returns:
            dict với keys: camera_times, lidar_times, camera_obj_pos, lidar_obj_pos_noisy
        """
        # Tạo timestamp
        camera_dt = 1.0 / self.config.camera_freq_hz
        lidar_dt = 1.0 / self.config.lidar_freq_hz
        
        camera_times = np.arange(0, self.config.duration_sec, camera_dt)
        lidar_times = np.arange(0, self.config.duration_sec, lidar_dt)
        
        # Vị trí vật thể tại camera time (thực tế, không có lệch)
        camera_obj_pos = np.array([
            self.get_object_position_camera_frame(t) for t in camera_times
        ])
        
        # Vị trí vật thể tại LiDAR time (nếu không có lệch)
        lidar_obj_pos = np.array([
            self.get_object_position_camera_frame(t) for t in lidar_times
        ])
        
        # Thêm nhiễu đo LiDAR
        noise_x = self.rng.normal(0, self.config.lidar_noise_sigma_m, len(lidar_times))
        noise_y = self.rng.normal(0, self.config.lidar_noise_sigma_m, len(lidar_times))
        lidar_obj_pos_noisy = lidar_obj_pos + np.column_stack([noise_x, noise_y])
        
        return {
            'camera_times': camera_times,
            'lidar_times': lidar_times,
            'camera_obj_pos': camera_obj_pos,
            'lidar_obj_pos': lidar_obj_pos,
            'lidar_obj_pos_noisy': lidar_obj_pos_noisy,
        }


def compute_error_pre(
    camera_times: np.ndarray,
    camera_obj_pos: np.ndarray,
    lidar_times: np.ndarray,
    lidar_obj_pos_noisy: np.ndarray,
    offset_ms: float
) -> Tuple[np.ndarray, float, float]:
    """
    Tính E_pre: Khi LiDAR lệch offset_ms, điểm LiDAR (bị lệch) được ghép với camera.
    Sai số = khoảng cách giữa vị trí LiDAR (tại thời gian t - offset) và vị trí thực (tại t)
    
    Args:
        camera_times: thời gian capture của camera
        camera_obj_pos: vị trí thực của vật thể ở thời gian camera
        lidar_times: thời gian capture của LiDAR
        lidar_obj_pos_noisy: vị trí LiDAR đo được (có nhiễu)
        offset_ms: lệch thời gian (ms)
    
    Returns:
        (errors, mean_error, max_error)
    """
    offset_s = offset_ms / 1000.0  # Chuyển ms → s
    
    errors = []
    
    # Duyệt qua từng frame camera
    for i, t_camera in enumerate(camera_times):
        # Tìm frame LiDAR gần nhất ở thời gian t_lidar = t_camera - offset
        t_lidar_target = t_camera - offset_s
        
        # Tìm index LiDAR gần nhất
        if t_lidar_target < lidar_times[0] or t_lidar_target > lidar_times[-1]:
            continue  # Bỏ qua nếu ngoài range
        
        idx_lidar = np.argmin(np.abs(lidar_times - t_lidar_target))
        
        # Vị trí LiDAR tại thời gian t_lidar_target (lệch thời gian)
        lidar_pos = lidar_obj_pos_noisy[idx_lidar]
        
        # Vị trí thực tại thời gian camera
        camera_pos = camera_obj_pos[i]
        
        # Sai số = khoảng cách Euclidean
        error = np.linalg.norm(camera_pos - lidar_pos)
        errors.append(error)
    
    errors = np.array(errors)
    mean_error = np.mean(errors)
    max_error = np.max(errors)
    
    return errors, mean_error, max_error


if __name__ == "__main__":
    # Test
    config = SimulationConfig(
        duration_sec=10,
        velocity_ms=20,
        acceleration_ms2=0,
        yaw_rate_rads=0.0,
        object_distance_m=10.0,
    )
    
    simulator = ObjectTrajectorySimulator(config)
    result = simulator.simulate()
    
    # Tính E_pre ở offset 100ms
    errors, mean_err, max_err = compute_error_pre(
        result['camera_times'],
        result['camera_obj_pos'],
        result['lidar_times'],
        result['lidar_obj_pos_noisy'],
        offset_ms=100
    )
    
    print(f"E_pre (offset=100ms): mean={mean_err:.4f}m, max={max_err:.4f}m")
