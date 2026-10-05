"""
run_benchmark.py - TV5: Chạy ma trận benchmark thực nghiệm Lab T4

Thực hiện:
  - 3 kịch bản x 5 mức offset x 3 khoảng cách = 45 tổ hợp
  - Gọi simulate.py (TV3) và compensate.py (TV4)
  - Ghi bảng kết quả chuẩn vào results/results.csv
  - Ghi log chi tiết vào results/benchmark.log
"""

import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import os
import argparse
from datetime import datetime
import numpy as np
import pandas as pd
import yaml

from simulate import run_simulation, get_vehicle_state
from compensate import (
    compensate_linear,
    compensate_ctrv,
    compute_formula_deviation,
    analyze_failure_case
)


def run_benchmark(config_path: str = "config.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    results_dir = cfg.get("results_dir", "./results")
    plots_dir = cfg.get("plots_dir", "./plots")
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)

    csv_path = os.path.join(results_dir, "results.csv")
    log_path = os.path.join(results_dir, "benchmark.log")

    scenarios = cfg["scenarios"]
    offsets_ms = cfg["offsets_ms"]
    distances_m = cfg["object_distances_m"]
    threshold_m = float(cfg.get("threshold_m", 0.5))

    results = []
    failure_cases = []

    with open(log_path, "w", encoding="utf-8") as log:
        log.write("=" * 70 + "\n")
        log.write(f"CHỐT LAB T4 BENCHMARK RUN LOG\n")
        log.write(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log.write(f"Config: {config_path}\n")
        log.write(f"Ngưỡng nguy hiểm: {threshold_m} m\n")
        log.write("=" * 70 + "\n\n")

        for scen_key, scen_cfg in scenarios.items():
            scen_name = scen_cfg.get("name", scen_key)
            log.write(f"\n{'#'*60}\n")
            log.write(f"Kịch bản: {scen_name} ({scen_key})\n")
            log.write(f"{'#'*60}\n")

            for offset_ms in offsets_ms:
                offset_s = offset_ms / 1000.0

                for dist_m in distances_m:
                    # 1. Chạy mô phỏng TV3
                    df_sim = run_simulation(scen_key, offset_ms, dist_m, cfg)

                    pts_lidar = df_sim[['x_lidar', 'y_lidar']].values
                    v_arr = df_sim['v'].values
                    yaw_rate_arr = df_sim['yaw_rate'].values
                    v_mean = float(np.mean(v_arr))
                    yaw_rate_mean = float(np.mean(yaw_rate_arr))

                    # 2. Bù chuyển động TV4
                    # Bù tuyến tính từng frame
                    pts_lin_comp = []
                    pts_ctrv_comp = []
                    for i in range(len(df_sim)):
                        p_l = pts_lidar[i]
                        v_i = v_arr[i]
                        yr_i = yaw_rate_arr[i]
                        p_lin = compensate_linear(p_l, v_i, offset_s)
                        p_ctrv = compensate_ctrv(p_l, v_i, yr_i, offset_s)
                        pts_lin_comp.append(p_lin)
                        pts_ctrv_comp.append(p_ctrv)

                    pts_lin_comp = np.array(pts_lin_comp)
                    pts_ctrv_comp = np.array(pts_ctrv_comp)

                    # 3. Chiếu ra hệ world dùng pose tại t_report
                    e_post_list = []
                    e_post_ctrv_list = []

                    for i in range(len(df_sim)):
                        t_rep = df_sim['t_report'].iloc[i]
                        x_rep, y_rep, yaw_rep, _, _ = get_vehicle_state(t_rep, scen_cfg)
                        cos_rep = np.cos(yaw_rep)
                        sin_rep = np.sin(yaw_rep)

                        # Vị trí thật
                        x_true = df_sim['x_true'].iloc[i]
                        y_true = df_sim['y_true'].iloc[i]

                        # Vị trí sau bù tuyến tính
                        x_lin_w = x_rep + (pts_lin_comp[i, 0] * cos_rep - pts_lin_comp[i, 1] * sin_rep)
                        y_lin_w = y_rep + (pts_lin_comp[i, 0] * sin_rep + pts_lin_comp[i, 1] * cos_rep)
                        e_lin = np.sqrt((x_lin_w - x_true)**2 + (y_lin_w - y_true)**2)
                        e_post_list.append(e_lin)

                        # Vị trí sau bù CTRV
                        x_ctrv_w = x_rep + (pts_ctrv_comp[i, 0] * cos_rep - pts_ctrv_comp[i, 1] * sin_rep)
                        y_ctrv_w = y_rep + (pts_ctrv_comp[i, 0] * sin_rep + pts_ctrv_comp[i, 1] * cos_rep)
                        e_ctrv = np.sqrt((x_ctrv_w - x_true)**2 + (y_ctrv_w - y_true)**2)
                        e_post_ctrv_list.append(e_ctrv)

                    e_pre_mean = float(df_sim['e_pre'].mean())
                    e_pre_max = float(df_sim['e_pre'].max())
                    e_post_mean = float(np.mean(e_post_list))
                    e_post_max = float(np.max(e_post_list))
                    e_post_ctrv_mean = float(np.mean(e_post_ctrv_list))

                    vdt_m = v_mean * offset_s
                    formula_dev_pct = float(compute_formula_deviation(e_pre_mean, v_mean, offset_s))
                    over_thresh = bool(e_post_mean > threshold_m)

                    # Phân tích Failure case TV4
                    fc = analyze_failure_case(
                        scen_name, dist_m, offset_ms,
                        e_pre_mean, e_post_mean, e_post_ctrv_mean,
                        threshold_m
                    )
                    if fc['is_failure']:
                        failure_cases.append(fc)

                    log_entry = (
                        f"Offset={offset_ms:3d}ms | d={dist_m:2d}m | v={v_mean:.1f}m/s: "
                        f"E_pre={e_pre_mean:.3f}m, E_post={e_post_mean:.3f}m, "
                        f"E_ctrv={e_post_ctrv_mean:.3f}m, v*dt={vdt_m:.3f}m, "
                        f"Dev={formula_dev_pct:5.1f}% | "
                        f"{'FAIL (>0.5m)' if over_thresh else 'PASS'}\n"
                    )
                    log.write(log_entry)

                    # Lưu theo đúng cấu trúc cột Checklist
                    results.append({
                        'scenario': scen_name,
                        'offset_ms': int(offset_ms),
                        'distance_m': int(dist_m),
                        'v_mps': round(v_mean, 2),
                        'e_pre_mean': round(e_pre_mean, 4),
                        'e_pre_max': round(e_pre_max, 4),
                        'e_post_mean': round(e_post_mean, 4),
                        'e_post_max': round(e_post_max, 4),
                        'e_post_ctrv_mean': round(e_post_ctrv_mean, 4),
                        'vdt_m': round(vdt_m, 4),
                        'formula_dev_pct': round(formula_dev_pct, 2),
                        'over_threshold': over_thresh
                    })

        # Ghi tóm tắt Failure cases vào log
        log.write("\n" + "=" * 70 + "\n")
        log.write("TỔNG KẾT FAILURE CASES (E_post > 0.5m)\n")
        log.write("=" * 70 + "\n")
        for f in failure_cases:
            log.write(
                f"- [{f['scenario']}] offset={f['offset_ms']}ms, d={f['distance_m']}m: "
                f"E_post={f['e_post']:.3f}m, E_ctrv={f['e_post_ctrv']:.3f}m\n"
                f"  Lý do: {f['reason']}\n"
            )

    df_results = pd.DataFrame(results)
    df_results.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[OK] Đã hoàn thành benchmark: 45/45 tổ hợp.")
    print(f"[OK] File kết quả: {csv_path}")
    print(f"[OK] File log: {log_path}")
    print(f"[OK] Số trường hợp vượt ngưỡng 0.5m: {len(failure_cases)} / 45")

    return df_results, failure_cases


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chạy benchmark mô phỏng Lab T4")
    parser.add_argument("--config", "-c", type=str, default="config.yaml", help="Đường dẫn file config.yaml")
    # Cho phép truyền positional argument nếu có
    parser.add_argument("pos_config", nargs="?", default=None, help="Đường dẫn file config (positional)")
    args = parser.parse_args()

    cfg_file = args.pos_config if args.pos_config else args.config
    run_benchmark(cfg_file)
