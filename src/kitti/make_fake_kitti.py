"""
Tạo một sequence GIẢ đúng cấu trúc thư mục KITTI raw để test kitti_real_motion.py
trước khi tải dữ liệu thật. KHÔNG dùng kết quả của dữ liệu này trong báo cáo.

Chạy: python make_fake_kitti.py --out fake_kitti/2011_09_26_drive_9999_sync
"""
import argparse
import os
import numpy as np
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="fake_kitti/2011_09_26_drive_9999_sync")
out = ap.parse_args().out

hz, n = 10, 200
t = np.arange(n) / hz
v = np.full(n, 12.0)                                   # 12 m/s
w = np.where((t >= 8) & (t < 13), 0.3, 0.0)            # rẽ 5 giây, 0,3 rad/s
yaw = np.cumsum(w) / hz
x = np.cumsum(v * np.cos(yaw)) / hz
y = np.cumsum(v * np.sin(yaw)) / hz

# xy -> lat/lon (nghịch đảo Mercator của devkit)
er, lat0 = 6378137.0, 49.0
scale = np.cos(np.deg2rad(lat0))
lon0_m = scale * np.deg2rad(8.4) * er
lat0_m = scale * er * np.log(np.tan(np.deg2rad(90 + lat0) / 2))
lon = np.rad2deg((x + lon0_m) / (scale * er))
lat = np.rad2deg(2 * np.arctan(np.exp((y + lat0_m) / (scale * er)))) - 90

base = pd.Timestamp("2011-09-26 13:02:25.000000000")
for sub in ["oxts/data", "image_02/data", "velodyne_points/data"]:
    os.makedirs(os.path.join(out, sub), exist_ok=True)

for i in range(n):
    row = np.zeros(30)
    row[0], row[1], row[5], row[8], row[19] = lat[i], lon[i], yaw[i], v[i], w[i]
    np.savetxt(os.path.join(out, "oxts/data", f"{i:010d}.txt"), row[None], fmt="%.12f")

rng = np.random.default_rng(0)
cam = t + rng.normal(0, 0.0005, n)                     # jitter 0,5 ms
velo = cam + 0.002                                     # LiDAR lệch 2 ms
for path, ts in [("oxts/timestamps.txt", t), ("image_02/timestamps.txt", cam),
                 ("velodyne_points/timestamps.txt", velo),
                 ("velodyne_points/timestamps_start.txt", velo - 0.05),
                 ("velodyne_points/timestamps_end.txt", velo + 0.05)]:
    with open(os.path.join(out, path), "w") as f:
        f.write("\n".join((base + pd.to_timedelta(s, unit="s")).strftime("%Y-%m-%d %H:%M:%S.%f") + "000" for s in ts) + "\n")
print("Đã tạo:", out)
