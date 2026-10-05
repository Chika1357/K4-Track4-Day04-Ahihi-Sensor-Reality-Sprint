"""
simulate.py - TV3: Mô phỏng quỹ đạo xe, timestamp camera-LiDAR, tính E_pre

Quy ước:
  - Camera: 30 Hz, LiDAR: 10 Hz, thời lượng: 10 s
  - LiDAR báo timestamp t_report, nhưng thực sự chụp lúc t_true = t_report - offset
  - Mỗi frame LiDAR: Vật thể tĩnh cách xe d mét phía trước tại thời điểm t_true
  - LiDAR đo trong hệ thân xe lúc t_true kèm nhiễu Gaussian sigma = 0.02 m
  - Fusion ngây thơ (chưa bù): Dùng pose xe lúc t_report để chiếu điểm LiDAR ra hệ world
  - E_pre: Sai số khoảng cách giữa vị trí fusion và vị trí thật của vật thể
"""

import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import numpy as np
import pandas as pd
import yaml
from typing import Dict, Tuple, Optional


def get_vehicle_state(
    t: float,
    scenario_cfg: dict
) -> Tuple[float, float, float, float, float]:
    """
    Tính trạng thái xe tại thời gian t (x, y, yaw, v, yaw_rate)
    
    Kịch bản:
      - A (Straight): Chạy thẳng đều v = 20 m/s
      - B (Acceleration): v0 = 10 m/s, a = 3 m/s²
      - C (Turning): v = 10 m/s, R = 30 m, yaw_rate = 10/30 = 0.3333 rad/s
    """
    v0 = float(scenario_cfg.get('velocity_ms', 20.0))
    a = float(scenario_cfg.get('acceleration_ms2', 0.0))
    turn_r = scenario_cfg.get('turn_radius_m')
    yaw_rate = float(scenario_cfg.get('yaw_rate_rads', 0.0))
    
    if a != 0:
        # Kịch bản B: Chạy thẳng tăng tốc
        v = v0 + a * t
        x = v0 * t + 0.5 * a * (t ** 2)
        y = 0.0
        yaw = 0.0
        actual_yaw_rate = 0.0
    elif turn_r is not None and float(turn_r) > 0:
        # Kịch bản C: Rẽ cua tròn đều
        r = float(turn_r)
        actual_yaw_rate = v0 / r if yaw_rate == 0.0 else yaw_rate
        yaw = actual_yaw_rate * t
        # Quỹ đạo tròn tiếp tuyến với trục x tại (0,0):
        # x(t) = R * sin(yaw), y(t) = R * (1 - cos(yaw))
        x = r * np.sin(yaw)
        y = r * (1.0 - np.cos(yaw))
        v = v0
    else:
        # Kịch bản A: Thẳng đều
        v = v0
        x = v0 * t
        y = 0.0
        yaw = 0.0
        actual_yaw_rate = 0.0
        
    return x, y, yaw, v, actual_yaw_rate


def run_simulation(
    scenario_key: str,
    offset_ms: float,
    distance_m: float,
    cfg: dict
) -> pd.DataFrame:
    """
    Hàm mô phỏng chính theo chuẩn Checklist TV3:
      run_simulation(scenario, offset_ms, distance_m, cfg)
      
    Returns:
        pd.DataFrame với các cột:
        frame, t_report, t_true, x_true, y_true, x_lidar, y_lidar, v, yaw_rate, e_pre
    """
    scenarios = cfg['scenarios']
    scen_cfg = scenarios[scenario_key]
    
    duration = float(scen_cfg.get('duration_sec', 10.0))
    lidar_freq = int(cfg.get('lidar_freq_hz', 10))
    sigma = float(cfg.get('lidar_noise_sigma_m', 0.02))
    seed = int(cfg.get('random_seed', 42))
    
    # Thiết lập seed để kết quả tái lập tuyệt đối
    rng = np.random.RandomState(seed + int(offset_ms) + int(distance_m))
    
    dt_lidar = 1.0 / lidar_freq
    t_reports = np.arange(0.0, duration, dt_lidar)
    offset_s = offset_ms / 1000.0
    
    records = []
    
    for frame_idx, t_rep in enumerate(t_reports):
        t_true = t_rep - offset_s
        
        # 1. Trạng thái xe tại thời điểm thực tế t_true (khi sensor LiDAR quét điểm)
        x_veh_true, y_veh_true, yaw_true, v_true, yaw_rate_true = get_vehicle_state(t_true, scen_cfg)
        
        # 2. Vật thể tĩnh nằm cách xe distance_m mét thẳng phía trước theo hướng xe lúc t_true
        x_obj_true = x_veh_true + distance_m * np.cos(yaw_true)
        y_obj_true = y_veh_true + distance_m * np.sin(yaw_true)
        
        # 3. Tọa độ điểm vật thể trong hệ quy chiếu thân xe tại t_true (kèm nhiễu đo)
        # Trong hệ thân xe, trục x trỏ thẳng phía trước, trục y trỏ sang trái:
        noise_x = rng.normal(0, sigma)
        noise_y = rng.normal(0, sigma)
        x_lidar = distance_m + noise_x
        y_lidar = 0.0 + noise_y
        
        # 4. Trạng thái xe tại thời điểm báo cáo t_report (khi fusion nhận được dữ liệu)
        x_veh_rep, y_veh_rep, yaw_rep, _, _ = get_vehicle_state(t_rep, scen_cfg)
        
        # 5. Fusion ngây thơ (chưa bù): Chiếu điểm LiDAR ra hệ world bằng pose t_report
        cos_rep = np.cos(yaw_rep)
        sin_rep = np.sin(yaw_rep)
        x_fusion_pre = x_veh_rep + (x_lidar * cos_rep - y_lidar * sin_rep)
        y_fusion_pre = y_veh_rep + (x_lidar * sin_rep + y_lidar * cos_rep)
        
        # 6. Sai số E_pre = khoảng cách Euclidean giữa vị trí fusion và vị trí thật
        e_pre = np.sqrt((x_fusion_pre - x_obj_true) ** 2 + (y_fusion_pre - y_obj_true) ** 2)
        
        records.append({
            'frame': frame_idx,
            't_report': t_rep,
            't_true': t_true,
            'x_true': x_obj_true,
            'y_true': y_obj_true,
            'x_lidar': x_lidar,
            'y_lidar': y_lidar,
            'v': v_true,
            'yaw_rate': yaw_rate_true,
            'e_pre': e_pre
        })
        
    df = pd.DataFrame(records)
    return df


if __name__ == "__main__":
    with open("config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
        
    print("=" * 70)
    print("TV3 SELF-TEST: Kiểm tra hàm run_simulation theo Checklist")
    print("=" * 70)
    
    # Test 1: Offset = 0 ms -> E_pre phải xấp xỉ mức nhiễu (0.02 - 0.03 m)
    df_0 = run_simulation('scenario_a_straight', offset_ms=0, distance_m=10, cfg=cfg)
    e_pre_0_mean = df_0['e_pre'].mean()
    print(f"\n[Test Offset 0 ms] Kịch bản A, d=10m:")
    print(f"  E_pre mean: {e_pre_0_mean:.4f} m (Kỳ vọng ≈ 0.02 - 0.03 m) -> {'PASS' if e_pre_0_mean < 0.05 else 'FAIL'}")
    
    # Test 2: Kịch bản A, Offset = 100 ms -> E_pre phải xấp xỉ 2.0 m (20 m/s * 0.1 s)
    df_100 = run_simulation('scenario_a_straight', offset_ms=100, distance_m=20, cfg=cfg)
    e_pre_100_mean = df_100['e_pre'].mean()
    print(f"\n[Test Offset 100 ms] Kịch bản A, v=20m/s, dt=0.1s:")
    print(f"  E_pre mean: {e_pre_100_mean:.4f} m (Kỳ vọng ≈ 2.0 m) -> {'PASS' if abs(e_pre_100_mean - 2.0) < 0.05 else 'FAIL'}")
    
    print("\nDataFrame Output Columns:")
    print(df_100.columns.tolist())
    print("\nHead 3 rows:")
    print(df_100.head(3))
    print("=" * 70)
