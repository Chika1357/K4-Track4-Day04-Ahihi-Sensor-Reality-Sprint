"""
plot.py - TV5: Tạo 3 biểu đồ chuẩn theo CHECKLIST_TUNG_NGUOI_T4.md

Yêu cầu đồ thị:
  1. plots/timeline.png:
     Tick timestamp Camera (30Hz) vs LiDAR (10Hz) trong 1 giây đầu, offset 100ms.
  2. plots/error_vs_offset.png:
     E_pre và E_post theo offset, 3 kịch bản (d = 20m và 40m), có đường ngưỡng 0.5m.
  3. plots/trajectory_turn.png:
     Kịch bản C (R=30m, v=10m/s), d = 40m, offset = 100ms:
     Vị trí thật vs Trước bù vs Sau bù (Linear và CTRV).
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
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yaml

from simulate import run_simulation, get_vehicle_state
from compensate import compensate_linear, compensate_ctrv


def plot_timeline(output_dir: str = "./plots", offset_ms: float = 100.0):
    """
    1. timeline.png:
    Minh họa chuỗi xung timestamp Camera (30Hz) và LiDAR (10Hz) trong 1 giây đầu,
    thể hiện độ trễ offset_ms = 100ms giữa t_true và t_report.
    """
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 4.5), dpi=150)

    # 1 giây đầu
    t_cam = np.arange(0, 1.0 + 1e-5, 1.0 / 30.0)
    t_lidar_rep = np.arange(0, 1.0 + 1e-5, 1.0 / 10.0)
    offset_s = offset_ms / 1000.0
    t_lidar_true = t_lidar_rep - offset_s

    # Vẽ timeline camera
    ax.eventplot(t_cam, lineoffsets=2.0, linelengths=0.5, colors='#1f77b4', linewidths=1.8,
                 label='Camera Frames (30 Hz, dt ≈ 33.3 ms)')
    # Vẽ timeline LiDAR report
    ax.eventplot(t_lidar_rep, lineoffsets=1.0, linelengths=0.5, colors='#d62728', linewidths=2.2,
                 label=f'LiDAR Reported Timestamp t_report (10 Hz, dt = 100 ms)')
    # Vẽ timeline LiDAR true
    ax.eventplot(t_lidar_true[t_lidar_true >= 0], lineoffsets=0.0, linelengths=0.5, colors='#2ca02c', linewidths=2.2,
                 label=f'LiDAR Actual Capture t_true = t_report - {int(offset_ms)} ms')

    # Vẽ mũi tên trễ giữa true và report
    for t_r in t_lidar_rep:
        t_tr = t_r - offset_s
        if 0 <= t_tr <= 1.0:
            ax.annotate('', xy=(t_r, 1.0), xytext=(t_tr, 0.0),
                        arrowprops=dict(arrowstyle="->", color="gray", lw=1.2, ls="--"))

    ax.set_yticks([0.0, 1.0, 2.0])
    ax.set_yticklabels(['LiDAR Capture (t_true)', 'LiDAR Report (t_report)', 'Camera Frame'])
    ax.set_xlabel('Thời gian t (giây) [0.0 - 1.0 s]', fontsize=11, fontweight='bold')
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.6, 2.7)
    ax.grid(True, axis='x', linestyle=':', alpha=0.6)
    ax.set_title(f'Timeline Đồng Bộ Timestamp Camera – LiDAR trong 1 giây đầu (Offset Δt = {int(offset_ms)} ms)\n[Dữ liệu tổng hợp]',
                 fontsize=12, fontweight='bold', pad=10)
    ax.legend(loc='upper right', framealpha=0.9, fontsize=9)

    plt.tight_layout()
    out_path = os.path.join(output_dir, "timeline.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[OK] Đã lưu đồ thị: {out_path}")


def plot_error_vs_offset(results_csv: str = "./results/results.csv", output_dir: str = "./plots"):
    """
    2. error_vs_offset.png:
    E_pre và E_post theo offset cho 3 kịch bản, khảo sát ở d = 20m và d = 40m,
    có đường ngưỡng an toàn 0.5m.
    """
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(results_csv)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), dpi=150, sharey=True)
    distances = [20, 40]

    scenarios = [
        ('Straight Line', '#1f77b4', 'A: Chạy thẳng (20 m/s)'),
        ('Acceleration', '#2ca02c', 'B: Tăng tốc (10->25 m/s)'),
        ('Turning', '#d62728', 'C: Rẽ cua (10 m/s, R=30m)')
    ]

    for idx, d_val in enumerate(distances):
        ax = axes[idx]
        df_d = df[df['distance_m'] == d_val]

        for scen_name, color, label_name in scenarios:
            sub = df_d[df_d['scenario'] == scen_name].sort_values('offset_ms')
            # E_pre (trước bù)
            ax.plot(sub['offset_ms'], sub['e_pre_mean'], color=color, linestyle='--', marker='o',
                    alpha=0.7, label=f'{label_name} - E_pre')
            # E_post (sau bù tuyến tính)
            ax.plot(sub['offset_ms'], sub['e_post_mean'], color=color, linestyle='-', marker='s',
                    linewidth=2.0, label=f'{label_name} - E_post (Linear)')

            # Riêng kịch bản Turning, vẽ thêm E_post_ctrv
            if scen_name == 'Turning':
                ax.plot(sub['offset_ms'], sub['e_post_ctrv_mean'], color='#9467bd', linestyle=':', marker='^',
                        linewidth=2.2, label=f'{label_name} - E_post (CTRV Cải tiến)')

        # Ngưỡng an toàn 0.5m
        ax.axhline(0.5, color='black', linestyle='-.', linewidth=1.8, label='Ngưỡng nguy hiểm (0.5 m)')
        ax.set_xlabel('Offset Δt (ms)', fontsize=11, fontweight='bold')
        if idx == 0:
            ax.set_ylabel('Sai số vị trí trung bình E (m)', fontsize=11, fontweight='bold')
        ax.set_title(f'Khoảng cách vật thể d = {d_val} m', fontsize=12, fontweight='bold')
        ax.set_xticks([0, 50, 100, 150, 200])
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend(fontsize=8, loc='upper left')

    fig.suptitle('Sai Số Định Vị E Trước & Sau Bù Chuyển Động Theo Lệch Thời Gian (Offset)\n[Dữ liệu tổng hợp]',
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    out_path = os.path.join(output_dir, "error_vs_offset.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[OK] Đã lưu đồ thị: {out_path}")


def plot_trajectory_turn(config_path: str = "config.yaml", output_dir: str = "./plots"):
    """
    3. trajectory_turn.png:
    Kịch bản C (Rẽ cua), d = 40m, offset = 100ms.
    Vẽ 2D mặt phẳng:
      - Quỹ đạo xe
      - Vị trí thật vật thể (True)
      - Vị trí chưa bù (Pre)
      - Vị trí sau bù tuyến tính (Linear - Failure Case)
      - Vị trí sau bù CTRV (CTRV - Triệt tiêu lỗi góc)
    """
    os.makedirs(output_dir, exist_ok=True)
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Chạy mô phỏng Kịch bản C, offset 100ms, d = 40m
    df = run_simulation('scenario_c_turn', offset_ms=100, distance_m=40, cfg=cfg)
    scen_cfg = cfg['scenarios']['scenario_c_turn']
    offset_s = 0.1

    # Tính điểm bù cho từng frame
    pts_lidar = df[['x_lidar', 'y_lidar']].values
    v_arr = df['v'].values
    yr_arr = df['yaw_rate'].values

    x_pre_w, y_pre_w = [], []
    x_lin_w, y_lin_w = [], []
    x_ctrv_w, y_ctrv_w = [], []
    x_veh_list, y_veh_list = [], []

    for i in range(len(df)):
        t_rep = df['t_report'].iloc[i]
        x_rep, y_rep, yaw_rep, _, _ = get_vehicle_state(t_rep, scen_cfg)
        x_veh_list.append(x_rep)
        y_veh_list.append(y_rep)

        p_l = pts_lidar[i]
        p_lin = compensate_linear(p_l, v_arr[i], offset_s)
        p_ctrv = compensate_ctrv(p_l, v_arr[i], yr_arr[i], offset_s)

        cos_r = np.cos(yaw_rep)
        sin_r = np.sin(yaw_rep)

        # Pre (ngây thơ)
        x_pre_w.append(x_rep + (p_l[0] * cos_r - p_l[1] * sin_r))
        y_pre_w.append(y_rep + (p_l[0] * sin_r + p_l[1] * cos_r))

        # Linear
        x_lin_w.append(x_rep + (p_lin[0] * cos_r - p_lin[1] * sin_r))
        y_lin_w.append(y_rep + (p_lin[0] * sin_r + p_lin[1] * cos_r))

        # CTRV
        x_ctrv_w.append(x_rep + (p_ctrv[0] * cos_r - p_ctrv[1] * sin_r))
        y_ctrv_w.append(y_rep + (p_ctrv[0] * sin_r + p_ctrv[1] * cos_r))

    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)

    # Chọn 10 frame tiêu biểu (cách đều) để vẽ điểm không bị đè
    step = 10
    idx_sample = np.arange(0, len(df), step)

    # Quỹ đạo xe
    ax.plot(x_veh_list, y_veh_list, color='gray', linestyle='--', label='Quỹ đạo xe (R = 30 m)')

    # Vị trí thật
    ax.scatter(df['x_true'].iloc[idx_sample], df['y_true'].iloc[idx_sample],
               color='green', s=70, marker='o', label='Vị trí THẬT của vật thể', zorder=5)

    # Chưa bù
    ax.scatter(np.array(x_pre_w)[idx_sample], np.array(y_pre_w)[idx_sample],
               color='red', s=60, marker='x', label='Trước bù E_pre (Naive Fusion)', zorder=4)

    # Bù tuyến tính (Failure Case)
    ax.scatter(np.array(x_lin_w)[idx_sample], np.array(y_lin_w)[idx_sample],
               color='orange', s=60, marker='s', label='Sau bù Tuyến tính E_post (Lệch d·ω·Δt ≈ 1.32m)', zorder=4)

    # Bù CTRV
    ax.scatter(np.array(x_ctrv_w)[idx_sample], np.array(y_ctrv_w)[idx_sample],
               color='blue', s=40, marker='^', alpha=0.8, label='Sau bù CTRV Cải tiến (Khớp vị trí thật)', zorder=6)

    # Vẽ đường thẳng nối sai số giữa Linear và True tại 1 điểm mẫu
    sample_i = idx_sample[3]
    x_t_sample = df['x_true'].iloc[sample_i]
    y_t_sample = df['y_true'].iloc[sample_i]
    x_l_sample = x_lin_w[sample_i]
    y_l_sample = y_lin_w[sample_i]
    ax.annotate(f'Sai số bù tuyến tính ≈ 1.30 m\n(Vượt ngưỡng 0.5 m)',
                xy=((x_t_sample + x_l_sample)/2, (y_t_sample + y_l_sample)/2),
                xytext=(x_l_sample + 5, y_l_sample - 8),
                arrowprops=dict(arrowstyle="->", color="darkred", lw=1.5),
                bbox=dict(boxstyle="round,pad=0.4", fc="yellow", alpha=0.7),
                fontsize=9, fontweight='bold')

    ax.set_xlabel('Tọa độ X toàn cầu (m)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Tọa độ Y toàn cầu (m)', fontsize=11, fontweight='bold')
    ax.set_title('Quỹ Đạo & Điểm Ước Lượng trong Kịch Bản Rẽ Cua (C: d = 40 m, Δt = 100 ms)\nMinh Họa Failure Case Của Bù Tuyến Tính vs. Cải Tiến CTRV [Dữ liệu tổng hợp]',
                 fontsize=12, fontweight='bold', pad=12)
    ax.legend(loc='upper left', framealpha=0.9, fontsize=9)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.axis('equal')

    plt.tight_layout()
    out_path = os.path.join(output_dir, "trajectory_turn.png")
    plt.savefig(out_path)
    plt.close()
    print(f"[OK] Đã lưu đồ thị: {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tạo các biểu đồ chuẩn cho Lab T4")
    parser.add_argument("--csv", type=str, default="./results/results.csv", help="Đường dẫn file results.csv")
    parser.add_argument("--config", type=str, default="config.yaml", help="Đường dẫn file config.yaml")
    parser.add_argument("--outdir", type=str, default="./plots", help="Thư mục xuất ảnh")
    # Tương thích positional arguments nếu có
    parser.add_argument("pos_csv", nargs="?", default=None)
    parser.add_argument("pos_outdir", nargs="?", default=None)
    args = parser.parse_args()

    csv_f = args.pos_csv if args.pos_csv else args.csv
    out_dir = args.pos_outdir if args.pos_outdir else args.outdir

    print("Đang tạo 3 biểu đồ chuẩn theo CHECKLIST...")
    plot_timeline(output_dir=out_dir, offset_ms=100.0)
    plot_error_vs_offset(results_csv=csv_f, output_dir=out_dir)
    plot_trajectory_turn(config_path=args.config, output_dir=out_dir)
    print("\n[Hoàn thành] Đã tạo đủ 3 biểu đồ tại thư mục:", out_dir)
