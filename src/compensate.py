"""
compensate.py - TV4: Bù chuyển động, tính E_post, so với v×Δt, phân tích failure case

Nhiệm vụ:
  - Bù chuyển động tuyến tính (giả định vận tốc không đổi, không xét yaw)
  - Bù chuyển động có xét yaw rate từ IMU (cải tiến)
  - Tính E_post
  - So sánh E_pre với công thức v×Δt
  - Phân tích failure case (rẽ cua, vật thể xa)
"""

import numpy as np
from typing import Tuple, Dict


def compensate_linear_motion(
    lidar_pos: np.ndarray,
    vehicle_velocity_ms: float,
    offset_s: float
) -> np.ndarray:
    """
    Bù chuyển động tuyến tính (giả định vận tốc không đổi)
    
    Logic: Nếu LiDAR lệch trễ offset_s, thì xe đã di chuyển thêm v*offset_s.
    Ta bù bằng cách tịnh tiến điểm LiDAR từ hệ xe cũ sang hệ xe mới.
    
    Trong hệ tọa độ xe (camera-frame):
    - LiDAR measure at t - offset (old frame)
    - Camera capture at t (current frame)
    - Sai số = LiDAR didn't account for motion
    - Correction: shift lidar_x by v * offset (xe di chuyển về phía trước)
    
    Args:
        lidar_pos: tọa độ vật thể trong hệ xe (x, y) từ LiDAR
        vehicle_velocity_ms: vận tốc xe (m/s)
        offset_s: lệch thời gian (s), giá trị dương = LiDAR trễ
    
    Returns:
        lidar_pos_compensated: vị trí sau bù tuyến tính
    """
    # Bù: điểm LiDAR được đo ở t-offset, nên object ở gần hơn
    # Trong hệ tọa độ xe, bù = -v*offset (object ở phía sau)
    # Hoặc từ góc độ: LiDAR lệch, nên vị trí object từng được gần hơn.
    # Bù = object thực tế xa hơn = tịnh tiến x thêm +v*offset
    
    correction_x = vehicle_velocity_ms * offset_s
    lidar_pos_compensated = lidar_pos.copy()
    lidar_pos_compensated[:, 0] += correction_x
    
    return lidar_pos_compensated


def compensate_with_yaw(
    lidar_pos: np.ndarray,
    vehicle_velocity_ms: float,
    yaw_rate_rads: float,
    offset_s: float
) -> np.ndarray:
    """
    Bù chuyển động có xét yaw rate (constant turn rate model)
    
    Khi xe rẽ cua với yaw_rate, vật thể xa sẽ bị lệch thêm do sự quay.
    Bù: dịch + quay ngược lại
    
    Args:
        lidar_pos: tọa độ vật thể trong hệ xe (x, y)
        vehicle_velocity_ms: vận tốc (m/s)
        yaw_rate_rads: tốc độ quay (rad/s), dương = quay trái
        offset_s: lệch thời gian (s)
    
    Returns:
        lidar_pos_compensated: vị trí sau bù (có xét yaw)
    """
    if np.abs(yaw_rate_rads) < 1e-6:
        # Nếu yaw_rate ≈ 0, dùng bù tuyến tính
        return compensate_linear_motion(lidar_pos, vehicle_velocity_ms, offset_s)
    
    # Constant turn rate model
    # Trong thời gian offset_s, xe:
    # - Di chuyển arc dài s = v * offset_s
    # - Quay góc Δyaw = yaw_rate * offset_s
    
    delta_yaw = yaw_rate_rads * offset_s
    
    # Lấy lại vị trí cũ (ở frame khi LiDAR được đo)
    # trong frame cũ: vật thể ở (x, y)
    # Để về frame cũ, quay ngược (-delta_yaw), dịch ngược
    
    lidar_pos_compensated = lidar_pos.copy()
    
    # Quay ngược
    cos_yaw = np.cos(-delta_yaw)
    sin_yaw = np.sin(-delta_yaw)
    
    x_rotated = (lidar_pos[:, 0] * cos_yaw - lidar_pos[:, 1] * sin_yaw)
    y_rotated = (lidar_pos[:, 0] * sin_yaw + lidar_pos[:, 1] * cos_yaw)
    
    # Dịch ngược theo hướng mũi xe
    # Trong frame cũ, xe ở gốc, mũi xe trỏ +x
    x_translated = x_rotated - vehicle_velocity_ms * offset_s
    
    lidar_pos_compensated[:, 0] = x_translated
    lidar_pos_compensated[:, 1] = y_rotated
    
    return lidar_pos_compensated


def compute_error_post(
    camera_obj_pos: np.ndarray,
    lidar_obj_pos_compensated: np.ndarray
) -> Tuple[np.ndarray, float, float]:
    """
    Tính E_post: Sai số sau bù chuyển động
    
    Args:
        camera_obj_pos: vị trí thực từ camera
        lidar_obj_pos_compensated: vị trí LiDAR sau bù
    
    Returns:
        (errors, mean_error, max_error)
    """
    # Giả sử camera_obj_pos và lidar_obj_pos_compensated cùng chiều dài
    # (đã được align trong run_benchmark.py)
    errors = np.linalg.norm(camera_obj_pos - lidar_obj_pos_compensated, axis=1)
    mean_error = np.mean(errors)
    max_error = np.max(errors)
    
    return errors, mean_error, max_error


def compute_formula_deviation(
    mean_error_pre: float,
    vehicle_velocity_ms: float,
    offset_ms: float
) -> float:
    """
    Tính sai lệch so với công thức v×Δt (%)
    
    Công thức: deviation = |E_pre - v*Δt| / (v*Δt) * 100
    
    Args:
        mean_error_pre: trung bình sai số trước bù (m)
        vehicle_velocity_ms: vận tốc (m/s)
        offset_ms: offset (ms)
    
    Returns:
        deviation (%): nếu < 100% thì công thức còn tốt, > 100% thì công thức sai
    """
    offset_s = offset_ms / 1000.0
    formula_val = vehicle_velocity_ms * offset_s
    
    if formula_val < 1e-6:
        return 0.0
    
    deviation = abs(mean_error_pre - formula_val) / formula_val * 100
    return deviation


def analyze_failure_case(
    scenario_name: str,
    object_distance_m: float,
    mean_error_post: float,
    threshold_m: float = 0.5
) -> Dict:
    """
    Phân tích failure case
    
    Returns:
        dict: {'is_failure': bool, 'reason': str, 'severity': str}
    """
    result = {
        'scenario': scenario_name,
        'distance': object_distance_m,
        'error': mean_error_post,
        'is_failure': mean_error_post > threshold_m,
        'threshold': threshold_m,
    }
    
    if result['is_failure']:
        if scenario_name == "Turning" and object_distance_m >= 40:
            result['reason'] = "Rẽ cua + vật thể xa: bù tuyến tính không xét góc quay"
            result['severity'] = "High"
        elif scenario_name == "Turning":
            result['reason'] = "Rẽ cua: bù tuyến tính không đủ"
            result['severity'] = "Medium"
        elif object_distance_m >= 40:
            result['reason'] = f"Vật thể ở {object_distance_m}m: sai số tích lũy lớn"
            result['severity'] = "Medium"
        else:
            result['reason'] = "Lệch offset lớn"
            result['severity'] = "Low"
    else:
        result['reason'] = "OK"
        result['severity'] = "None"
    
    return result


if __name__ == "__main__":
    # Test
    import numpy as np
    
    # Vị trí LiDAR (100 frame, 2D)
    lidar_pos = np.random.randn(100, 2) * 5 + np.array([15, 0])
    
    # Bù tuyến tính
    lidar_compensated = compensate_linear_motion(lidar_pos, 20, 0.1)
    print(f"Linear: dịch thêm {20 * 0.1:.2f}m")
    
    # Bù có yaw
    lidar_compensated_yaw = compensate_with_yaw(lidar_pos, 10, 0.33, 0.1)
    print(f"With yaw: quay {0.33 * 0.1:.4f} rad")
    
    # Tính sai số
    camera_pos = lidar_pos + np.random.randn(100, 2) * 0.05
    errors, mean_err, max_err = compute_error_post(camera_pos, lidar_compensated)
    print(f"E_post: mean={mean_err:.4f}m, max={max_err:.4f}m")
