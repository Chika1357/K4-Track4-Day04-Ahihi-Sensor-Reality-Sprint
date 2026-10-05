"""
Lab T4 - TV2: Ước lượng time offset camera-LiDAR bằng tìm kiếm lưới (grid search).

Ý tưởng (đơn giản hoá từ Park et al., RA-L 2020 - nguồn N1):
  Paper tối ưu time lag để giảm sai số chiếu (reprojection error) bằng Gauss-Newton.
  Ở đây: thử từng Δt trên lưới 0..250 ms, với mỗi Δt đưa điểm LiDAR ra hệ world bằng
  pose của xe lúc (t_report - Δt), so với vị trí vật thể camera thấy, chọn Δt cho sai lệch nhỏ nhất.

Giả định: biết pose xe theo thời gian (odometry/IMU), camera đo được vị trí vật thể (có nhiễu).
Kiểm tra thêm limitation của N1: khi xe đứng yên, Δt KHÔNG quan sát được.

Chạy test độc lập (không cần simulate.py của TV3):
  python estimate_offset.py --out results_offset
"""
import argparse
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

GRID_MS = np.arange(0, 255, 5)     # 0..250 ms, bước 5 ms
FLAT_RATIO = 0.05                  # đường cost "phẳng" nếu chênh < 5% -> không quan sát được


# ------------------------------------------------------------------ hàm chính
def ego_to_world(x, y, yaw, mx, my):
    c, s = np.cos(yaw), np.sin(yaw)
    return x + c * mx - s * my, y + s * mx + c * my


def estimate_offset(pose_fn, t_report, lidar_ego, cam_world, grid_ms=GRID_MS):
    """
    pose_fn(t)  -> (x, y, yaw) của xe tại các thời điểm t (mảng)
    t_report    : (N,) timestamp LiDAR ghi trong dữ liệu (s)
    lidar_ego   : (N,2) vị trí vật thể LiDAR đo được, trong hệ xe
    cam_world   : (N,2) vị trí vật thể camera đo được, trong hệ world
    Trả về: dict(offset_ms, cost_curve, observable, sharpness)
    """
    costs = []
    for g in grid_ms:
        x, y, yaw = pose_fn(t_report - g / 1000.0)
        wx, wy = ego_to_world(x, y, yaw, lidar_ego[:, 0], lidar_ego[:, 1])
        costs.append(np.mean(np.hypot(wx - cam_world[:, 0], wy - cam_world[:, 1])))
    costs = np.array(costs)
    i = int(np.argmin(costs))
    sharp = (costs.max() - costs.min()) / max(costs.min(), 1e-9)
    return dict(offset_ms=float(grid_ms[i]), cost_curve=costs,
                observable=bool(sharp > FLAT_RATIO), sharpness=float(sharp))


# ------------------------------------------------------------------ dữ liệu giả để test
def make_trajectory(kind, T=10.0, hz=100):
    t = np.arange(0, T, 1 / hz)
    if kind == "A_thang_20mps":
        v, w = np.full_like(t, 20.0), np.zeros_like(t)
    elif kind == "B_tang_toc":
        v, w = 10.0 + 3.0 * t, np.zeros_like(t)
    elif kind == "C_re_cua":
        v, w = np.full_like(t, 10.0), np.full_like(t, 10.0 / 30.0)
    elif kind == "D_dung_yen":
        v, w = np.zeros_like(t), np.zeros_like(t)
    else:
        raise ValueError(kind)
    yaw = np.cumsum(w) / hz
    x = np.cumsum(v * np.cos(yaw)) / hz
    y = np.cumsum(v * np.sin(yaw)) / hz

    def pose_fn(tq):
        return np.interp(tq, t, x), np.interp(tq, t, y), np.interp(tq, t, yaw)
    return pose_fn


def make_measurements(pose_fn, true_offset_ms, d=20.0, lidar_hz=10, T=10.0,
                      sigma_lidar=0.02, sigma_cam=0.10, rng=None):
    """Vật thể tĩnh ảo cách xe d m phía trước; LiDAR thật sự chụp lúc t_report - offset."""
    t_report = np.arange(0.5, T - 0.5, 1 / lidar_hz)
    t_true = t_report - true_offset_ms / 1000.0
    x, y, yaw = pose_fn(t_true)
    ox, oy = ego_to_world(x, y, yaw, d, 0.0)                     # vị trí thật của vật thể
    lidar_ego = np.column_stack([np.full_like(t_report, d), np.zeros_like(t_report)])
    lidar_ego += rng.normal(0, sigma_lidar, lidar_ego.shape)
    cam_world = np.column_stack([ox, oy]) + rng.normal(0, sigma_cam, (len(t_report), 2))
    return t_report, lidar_ego, cam_world


def run_tests(out):
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(42)
    rows, curves = [], {}
    for kind in ["A_thang_20mps", "B_tang_toc", "C_re_cua", "D_dung_yen"]:
        pose_fn = make_trajectory(kind)
        for true_ms in [0, 50, 100, 150, 200]:
            t_rep, l_ego, c_w = make_measurements(pose_fn, true_ms, rng=rng)
            r = estimate_offset(pose_fn, t_rep, l_ego, c_w)
            rows.append(dict(scenario=kind, true_offset_ms=true_ms, est_offset_ms=r["offset_ms"],
                             abs_error_ms=abs(r["offset_ms"] - true_ms),
                             observable=r["observable"], sharpness=round(r["sharpness"], 3)))
            if true_ms == 100:
                curves[kind] = r["cost_curve"]
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(out, "offset_estimation.csv"), index=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    for k, c in curves.items():
        ax.plot(GRID_MS, c, label=k)
    ax.axvline(100, color="k", ls=":", lw=1, label="Offset thật = 100 ms")
    ax.set_xlabel("Δt thử (ms)")
    ax.set_ylabel("Sai lệch LiDAR–camera trung bình (m)")
    ax.set_title("Đường cost khi ước lượng offset (dữ liệu tổng hợp)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(out, "offset_cost_curves.png"), dpi=150)
    plt.close(fig)
    return df


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results_offset")
    df = run_tests(ap.parse_args().out)
    print(df.to_string(index=False))
