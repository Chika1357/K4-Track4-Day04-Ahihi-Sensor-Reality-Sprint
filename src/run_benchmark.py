"""
run_benchmark.py - TV5: Chạy toàn bộ benchmark, tạo bảng kết quả, log

Nhiệm vụ:
  - Loop qua tất cả thí nghiệm (scenario × offset × distance)
  - Gọi simulate.py, compensate.py
  - Ghi kết quả vào results.csv
  - Ghi log chi tiết
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import yaml
import numpy as np
import pandas as pd
import os
from datetime import datetime
from simulate import SimulationConfig, ObjectTrajectorySimulator, compute_error_pre
from compensate import (
    compensate_linear_motion,
    compensate_with_yaw,
    compute_error_post,
    compute_formula_deviation,
    analyze_failure_case
)


def run_benchmark(config_path: str):
    """Chạy toàn bộ benchmark"""
    
    # Load config
    with open(config_path, 'r', encoding='utf-8') as f:
        config_dict = yaml.safe_load(f)
    
    # Tạo thư mục output
    results_dir = config_dict.get('results_dir', './results')
    plots_dir = config_dict.get('plots_dir', './plots')
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)
    
    # Khởi tạo log
    log_file = os.path.join(results_dir, 'benchmark.log')
    csv_file = os.path.join(results_dir, 'results.csv')
    
    all_results = []
    failure_cases = []
    
    with open(log_file, 'w', encoding='utf-8') as log:
        log.write(f"=== CHỐT LAB T4 Benchmark ===\n")
        log.write(f"Start: {datetime.now()}\n")
        log.write(f"Config: {config_path}\n\n")
        
        # Lấy thông số
        offsets_ms = config_dict['offsets_ms']
        object_distances_m = config_dict['object_distances_m']
        scenarios = config_dict['scenarios']
        threshold_m = config_dict.get('threshold_m', 0.5)
        
        # Duyệt qua tất cả kịch bản
        for scenario_key, scenario_cfg in scenarios.items():
            scenario_name = scenario_cfg['name']
            
            # Duyệt qua offset
            for offset_ms in offsets_ms:
                # Duyệt qua khoảng cách
                for distance_m in object_distances_m:
                    log.write(f"\n{'='*60}\n")
                    log.write(f"Scenario: {scenario_name} | Offset: {offset_ms}ms | Distance: {distance_m}m\n")
                    log.write(f"{'='*60}\n")
                    
                    # Tạo config mô phỏng
                    sim_config = SimulationConfig(
                        duration_sec=scenario_cfg['duration_sec'],
                        velocity_ms=scenario_cfg['velocity_ms'],
                        acceleration_ms2=scenario_cfg['acceleration_ms2'],
                        turn_radius_m=scenario_cfg.get('turn_radius_m'),
                        yaw_rate_rads=scenario_cfg['yaw_rate_rads'],
                        camera_freq_hz=config_dict['camera_freq_hz'],
                        lidar_freq_hz=config_dict['lidar_freq_hz'],
                        object_distance_m=distance_m,
                        lidar_noise_sigma_m=config_dict['lidar_noise_sigma_m'],
                        random_seed=config_dict['random_seed'],
                    )
                    
                    # Chạy mô phỏng
                    simulator = ObjectTrajectorySimulator(sim_config)
                    sim_result = simulator.simulate()
                    
                    # Tính E_pre
                    errors_pre, mean_e_pre, max_e_pre = compute_error_pre(
                        sim_result['camera_times'],
                        sim_result['camera_obj_pos'],
                        sim_result['lidar_times'],
                        sim_result['lidar_obj_pos_noisy'],
                        offset_ms
                    )
                    
                    # Lấy vận tốc hiện tại (có thể thay đổi do tăng tốc)
                    # Lấy vận tốc ở giữa test
                    t_mid = sim_config.duration_sec / 2
                    if sim_config.acceleration_ms2 != 0:
                        velocity_avg = sim_config.velocity_ms + sim_config.acceleration_ms2 * t_mid
                    else:
                        velocity_avg = sim_config.velocity_ms
                    
                    # Tính công thức deviation
                    formula_dev = compute_formula_deviation(mean_e_pre, velocity_avg, offset_ms)
                    
                    # Bù tuyến tính
                    offset_s = offset_ms / 1000.0
                    lidar_pos_linear = compensate_linear_motion(
                        sim_result['lidar_obj_pos_noisy'],
                        velocity_avg,
                        offset_s
                    )
                    
                    # Align về cùng chiều dài với camera
                    n_camera = len(sim_result['camera_times'])
                    n_lidar = len(sim_result['lidar_times'])
                    min_len = min(n_camera, n_lidar)
                    
                    camera_pos_aligned = sim_result['camera_obj_pos'][:min_len]
                    lidar_pos_aligned = lidar_pos_linear[:min_len]
                    
                    # Tính E_post (tuyến tính)
                    errors_post, mean_e_post, max_e_post = compute_error_post(
                        camera_pos_aligned,
                        lidar_pos_aligned
                    )
                    
                    # Bù có yaw
                    lidar_pos_yaw = compensate_with_yaw(
                        sim_result['lidar_obj_pos_noisy'],
                        velocity_avg,
                        scenario_cfg['yaw_rate_rads'],
                        offset_s
                    )
                    lidar_pos_yaw_aligned = lidar_pos_yaw[:min_len]
                    errors_post_yaw, mean_e_post_yaw, max_e_post_yaw = compute_error_post(
                        camera_pos_aligned,
                        lidar_pos_yaw_aligned
                    )
                    
                    # Phân tích failure
                    failure_info = analyze_failure_case(
                        scenario_name, distance_m, mean_e_post, threshold_m
                    )
                    
                    # Ghi log
                    log_msg = (
                        f"E_pre:      mean={mean_e_pre:.4f}m  max={max_e_pre:.4f}m\n"
                        f"E_post:     mean={mean_e_post:.4f}m  max={max_e_post:.4f}m  (linear)\n"
                        f"E_post_yaw: mean={mean_e_post_yaw:.4f}m  max={max_e_post_yaw:.4f}m  (with yaw)\n"
                        f"Formula deviation: {formula_dev:.2f}%\n"
                        f"Velocity: {velocity_avg:.2f}m/s, Yaw rate: {scenario_cfg['yaw_rate_rads']:.3f}rad/s\n"
                        f"Status: {'FAIL (E > {:.2f}m)'.format(threshold_m) if failure_info['is_failure'] else 'PASS'}\n"
                    )
                    log.write(log_msg)
                    
                    # Thêm vào danh sách kết quả
                    result_row = {
                        'scenario': scenario_name,
                        'offset_ms': offset_ms,
                        'distance_m': distance_m,
                        'velocity_ms': velocity_avg,
                        'yaw_rate_rads': scenario_cfg['yaw_rate_rads'],
                        'e_pre_mean': mean_e_pre,
                        'e_pre_max': max_e_pre,
                        'e_post_mean': mean_e_post,
                        'e_post_max': max_e_post,
                        'e_post_yaw_mean': mean_e_post_yaw,
                        'e_post_yaw_max': max_e_post_yaw,
                        'formula_deviation_pct': formula_dev,
                        'is_failure': failure_info['is_failure'],
                        'failure_reason': failure_info['reason'],
                    }
                    all_results.append(result_row)
                    
                    if failure_info['is_failure']:
                        failure_cases.append(result_row)
        
        # Ghi log tóm tắt
        log.write(f"\n\n=== SUMMARY ===\n")
        log.write(f"Total experiments: {len(all_results)}\n")
        log.write(f"Failures: {len(failure_cases)}\n")
        
        if failure_cases:
            log.write(f"\nFailure cases:\n")
            for fc in failure_cases:
                log.write(
                    f"  - {fc['scenario']}, offset={fc['offset_ms']}ms, "
                    f"distance={fc['distance_m']}m: {fc['failure_reason']}\n"
                )
        
        log.write(f"\nEnd: {datetime.now()}\n")
    
    # Lưu CSV
    df = pd.DataFrame(all_results)
    df.to_csv(csv_file, index=False)
    
    print(f"✓ Benchmark complete!")
    print(f"  Results: {csv_file}")
    print(f"  Log: {log_file}")
    print(f"  Total: {len(all_results)} experiments, {len(failure_cases)} failures")
    
    return df, failure_cases


if __name__ == "__main__":
    import sys
    
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    df, failures = run_benchmark(config_path)
    
    print("\nFirst 10 rows:")
    print(df.head(10))
