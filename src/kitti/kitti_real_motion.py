"""
Lab T4 - Phần mở rộng: lệch thời gian camera-LiDAR trên CHUYỂN ĐỘNG THẬT (KITTI raw).

Dùng gì từ KITTI:
  - oxts/            : vị trí (lat/lon), yaw, vận tốc tiến vf, yaw rate wz thật của xe (10 Hz)
  - image_02/timestamps.txt            : timestamp camera màu trái
  - velodyne_points/timestamps*.txt    : timestamp LiDAR (lúc hướng trước, bắt đầu, kết thúc quét)

Làm gì:
  1. Đo độ lệch timestamp THẬT giữa camera và LiDAR trong KITTI, và thời gian 1 vòng quét LiDAR.
  2. Bơm offset nhân tạo 0-200 ms lên LiDAR, dùng quỹ đạo thật của xe để tính sai số vị trí
     của một vật thể tĩnh ảo cách xe d mét phía trước (giống mô phỏng nhóm, chỉ thay quỹ đạo giả bằng quỹ đạo thật).
  3. So sánh: không bù (E_pre), bù tuyến tính (E_lin), bù CTRV có yaw rate (E_ctrv), và công thức v*dt.

Giới hạn (ghi vào báo cáo): vật thể là điểm ẢO, không dùng point cloud thật;
offset là NHÂN TẠO; pose lấy từ OXTS (sai số GPS/INS cỡ vài cm).

Chạy:
  python kitti_real_motion.py --seq <đường dẫn tới 2011_09_26_drive_XXXX_sync> --out results_kitti
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OFFSETS_MS = [0, 50, 100, 150, 200]
DISTANCES_M = [10, 20, 40]
NOISE_SIGMA_M = 0.02
SEED = 42
TURN_THRESH = 0.10      # |yaw rate| > 0.10 rad/s  -> frame "đang rẽ"
STRAIGHT_THRESH = 0.02  # |yaw rate| < 0.02 rad/s  -> frame "chạy thẳng"
DANGER_M = 0.5          # ngưỡng đáng lo nhóm tự đặt

# Thứ tự 30 trường OXTS chuẩn của KITTI (dùng khi không có dataformat.txt)
OXTS_FIELDS = ["lat", "lon", "alt", "roll", "pitch", "yaw", "vn", "ve", "vf", "vl", "vu",
               "ax", "ay", "az", "af", "al", "au", "wx", "wy", "wz", "wf", "wl", "wu",
               "pos_accuracy", "vel_accuracy", "navstat", "numsats", "posmode", "velmode", "orimode"]


# ---------------------------------------------------------------- đọc dữ liệu
def read_timestamps(path):
    """KITTI timestamp dạng '2011-09-26 13:02:25.964389445' -> giây (float, tương đối)."""
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip()]
    ts = pd.to_datetime(lines, format="ISO8601")
    return ts.values.astype("datetime64[ns]").astype(np.int64) / 1e9


def read_oxts(seq):
    d = os.path.join(seq, "oxts")
    fmt = os.path.join(d, "dataformat.txt")
    fields = OXTS_FIELDS
    if os.path.exists(fmt):
        with open(fmt) as f:
            names = [l.split(":")[0].strip() for l in f if ":" in l]
        if len(names) == 30:
            fields = names
    files = sorted(os.listdir(os.path.join(d, "data")))
    rows = [np.loadtxt(os.path.join(d, "data", fn)) for fn in files]
    df = pd.DataFrame(np.vstack(rows), columns=fields)
    df["t"] = read_timestamps(os.path.join(d, "timestamps.txt"))
    return df


def latlon_to_xy(lat, lon):
    """Phép chiếu Mercator giống devkit KITTI, gốc tại điểm đầu tiên (m)."""
    er = 6378137.0
    scale = np.cos(np.deg2rad(lat[0]))
    x = scale * np.deg2rad(lon) * er
    y = scale * er * np.log(np.tan(np.deg2rad(90.0 + lat) / 2.0))
    return x - x[0], y - y[0]


# ---------------------------------------------------------------- pose theo thời gian
class Trajectory:
    def __init__(self, oxts):
        self.t = oxts["t"].values
        self.x, self.y = latlon_to_xy(oxts["lat"].values, oxts["lon"].values)
        self.yaw = np.unwrap(oxts["yaw"].values)
        self.v = oxts["vf"].values
        self.w = oxts["wz"].values

    def pose(self, t):
        return (np.interp(t, self.t, self.x), np.interp(t, self.t, self.y),
                np.interp(t, self.t, self.yaw))

    def vel(self, t):
        return np.interp(t, self.t, self.v), np.interp(t, self.t, self.w)


def ego_to_world(x, y, yaw, m):
    """Đổi điểm m=(mx,my) từ hệ xe sang hệ world."""
    c, s = np.cos(yaw), np.sin(yaw)
    return np.array([x + c * m[0] - s * m[1], y + s * m[0] + c * m[1]])


def comp_linear(x, y, yaw, v, dt):
    """Lùi pose theo vận tốc không đổi, KHÔNG xét quay."""
    return x - v * dt * np.cos(yaw), y - v * dt * np.sin(yaw), yaw


def comp_ctrv(x, y, yaw, v, w, dt):
    """Lùi pose theo cung tròn (constant turn rate & velocity)."""
    if abs(w) < 1e-4:
        return comp_linear(x, y, yaw, v, dt)
    yaw0 = yaw - w * dt
    x0 = x - (v / w) * (np.sin(yaw) - np.sin(yaw0))
    y0 = y + (v / w) * (np.cos(yaw) - np.cos(yaw0))
    return x0, y0, yaw0


# ---------------------------------------------------------------- phân tích timestamp thật
def timestamp_report(seq):
    cam = read_timestamps(os.path.join(seq, "image_02", "timestamps.txt"))
    vd = os.path.join(seq, "velodyne_points")
    velo = read_timestamps(os.path.join(vd, "timestamps.txt"))
    n = min(len(cam), len(velo))
    rep = {
        "n_frames": int(n),
        "cam_period_ms_mean": float(np.mean(np.diff(cam)) * 1e3),
        "cam_period_ms_std": float(np.std(np.diff(cam)) * 1e3),
        "velo_minus_cam_ms_mean": float(np.mean(velo[:n] - cam[:n]) * 1e3),
        "velo_minus_cam_ms_absmax": float(np.max(np.abs(velo[:n] - cam[:n])) * 1e3),
    }
    s_path, e_path = os.path.join(vd, "timestamps_start.txt"), os.path.join(vd, "timestamps_end.txt")
    if os.path.exists(s_path) and os.path.exists(e_path):
        s, e = read_timestamps(s_path), read_timestamps(e_path)
        k = min(len(s), len(e))
        rep["velo_scan_duration_ms_mean"] = float(np.mean(e[:k] - s[:k]) * 1e3)
    return rep, cam


# ---------------------------------------------------------------- benchmark
def run(seq, out):
    os.makedirs(out, exist_ok=True)
    rng = np.random.default_rng(SEED)
    oxts = read_oxts(seq)
    traj = Trajectory(oxts)
    ts_rep, cam_t = timestamp_report(seq)

    rows = []
    for off in OFFSETS_MS:
        dt = off / 1000.0
        for d in DISTANCES_M:
            for k, tc in enumerate(cam_t):
                t_true = tc - dt
                if t_true < traj.t[0] or tc > traj.t[-1]:
                    continue
                xt, yt, yawt = traj.pose(t_true)                  # pose thật lúc LiDAR chụp
                p_obj = ego_to_world(xt, yt, yawt, (d, 0.0))      # vật thể tĩnh ảo
                m = np.array([d, 0.0]) + rng.normal(0, NOISE_SIGMA_M, 2)  # đo trong hệ xe

                xr, yr, yawr = traj.pose(tc)                      # fusion dùng nhầm pose lúc t_report
                v, w = traj.vel(tc)
                e_pre = np.linalg.norm(ego_to_world(xr, yr, yawr, m) - p_obj)
                e_lin = np.linalg.norm(ego_to_world(*comp_linear(xr, yr, yawr, v, dt), m) - p_obj)
                e_ctrv = np.linalg.norm(ego_to_world(*comp_ctrv(xr, yr, yawr, v, w, dt), m) - p_obj)
                rows.append(dict(frame=k, offset_ms=off, distance_m=d, v_mps=v, yaw_rate=w,
                                 e_pre=e_pre, e_lin=e_lin, e_ctrv=e_ctrv, vdt_m=abs(v) * dt))
    df = pd.DataFrame(rows)
    df["motion"] = np.where(df.yaw_rate.abs() > TURN_THRESH, "turn",
                            np.where(df.yaw_rate.abs() < STRAIGHT_THRESH, "straight", "mild"))
    df.to_csv(os.path.join(out, "kitti_frames.csv"), index=False)

    summary = (df.groupby(["motion", "distance_m", "offset_ms"])
                 .agg(n=("e_pre", "size"), v_mean=("v_mps", "mean"),
                      yaw_rate_absmean=("yaw_rate", lambda s: s.abs().mean()),
                      e_pre_mean=("e_pre", "mean"), e_pre_max=("e_pre", "max"),
                      e_lin_mean=("e_lin", "mean"), e_lin_max=("e_lin", "max"),
                      e_ctrv_mean=("e_ctrv", "mean"), e_ctrv_max=("e_ctrv", "max"),
                      vdt_mean=("vdt_m", "mean"))
                 .reset_index())
    summary["over_threshold_lin"] = summary.e_lin_max > DANGER_M
    summary.to_csv(os.path.join(out, "kitti_summary.csv"), index=False, float_format="%.4f")

    with open(os.path.join(out, "kitti_timestamps.json"), "w") as f:
        json.dump(dict(sequence=os.path.basename(os.path.normpath(seq)), **ts_rep,
                       frames_turn=int((df.motion == "turn").sum() / len(OFFSETS_MS) / len(DISTANCES_M)),
                       frames_straight=int((df.motion == "straight").sum() / len(OFFSETS_MS) / len(DISTANCES_M)),
                       v_max=float(traj.v.max()), yaw_rate_absmax=float(np.abs(traj.w).max()),
                       seed=SEED, noise_sigma_m=NOISE_SIGMA_M), f, indent=2)

    plot(df, traj, out)
    return df, summary, ts_rep


def plot(df, traj, out):
    # 1) sai số theo offset, d=40 m, tách chạy thẳng / rẽ
    fig, ax = plt.subplots(figsize=(8, 5))
    for motion, ls in [("straight", "-"), ("turn", "--")]:
        g = df[(df.distance_m == 40) & (df.motion == motion)].groupby("offset_ms").mean(numeric_only=True)
        if g.empty:
            continue
        ax.plot(g.index, g.e_pre, "o" + ls, label=f"Không bù ({motion})")
        ax.plot(g.index, g.e_lin, "s" + ls, label=f"Bù tuyến tính ({motion})")
        ax.plot(g.index, g.e_ctrv, "^" + ls, label=f"Bù CTRV ({motion})")
    ax.axhline(DANGER_M, color="red", lw=1, ls=":", label="Ngưỡng 0,5 m (nhóm tự đặt)")
    ax.set_xlabel("Offset LiDAR (ms)")
    ax.set_ylabel("Sai số vị trí trung bình (m)")
    ax.set_title("KITTI raw - chuyển động thật, vật thể ảo d = 40 m, offset nhân tạo")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "kitti_error_vs_offset.png"), dpi=150)
    plt.close(fig)

    # 2) theo thời gian: vận tốc, yaw rate và sai số sau bù tuyến tính (offset 100 ms, d=40 m)
    g = df[(df.offset_ms == 100) & (df.distance_m == 40)].sort_values("frame")
    fig, axs = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
    axs[0].plot(g.frame, g.v_mps); axs[0].set_ylabel("v (m/s)")
    axs[1].plot(g.frame, g.yaw_rate); axs[1].set_ylabel("yaw rate (rad/s)")
    axs[2].plot(g.frame, g.e_lin, label="Bù tuyến tính")
    axs[2].plot(g.frame, g.e_ctrv, label="Bù CTRV")
    axs[2].axhline(DANGER_M, color="red", ls=":", lw=1)
    axs[2].set_ylabel("Sai số (m)"); axs[2].set_xlabel("Frame camera"); axs[2].legend(fontsize=8)
    axs[0].set_title("KITTI raw - offset 100 ms, d = 40 m")
    for a in axs:
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "kitti_timeline.png"), dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seq", required=True, help="thư mục 2011_09_26_drive_XXXX_sync")
    ap.add_argument("--out", default="results_kitti")
    a = ap.parse_args()
    df, summary, ts = run(a.seq, a.out)
    print("== Timestamp thật trong KITTI ==")
    for k, v in ts.items():
        print(f"  {k}: {v:.3f}" if isinstance(v, float) else f"  {k}: {v}")
    print("\n== Tóm tắt (d = 40 m) ==")
    cols = ["motion", "offset_ms", "n", "v_mean", "e_pre_mean", "e_lin_mean", "e_ctrv_mean", "vdt_mean"]
    print(summary[summary.distance_m == 40][cols].to_string(index=False, float_format="%.3f"))
    print(f"\nĐã lưu vào: {a.out}/")
