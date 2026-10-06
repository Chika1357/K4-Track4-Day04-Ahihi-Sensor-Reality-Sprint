"""TV2: ước lượng time offset camera-LiDAR trên mô phỏng chung của nhóm.

Dùng đúng src/simulate.py (run_simulation, vehicle_state) và config_chot.yaml.
Camera đo vị trí vật thể trong hệ world với nhiễu sigma_cam (mặc định 0,10 m).
Kịch bản D = xe đứng yên (speed 0) để kiểm tra limitation của Park et al. (RA-L 2020):
time lag không quan sát được khi hệ không chuyển động.

Chạy từ thư mục gốc repo:
    python -m src.run_estimate_on_sim --config config_chot.yaml
Kết quả: results/offset/offset_on_sim.csv
"""

from __future__ import annotations

import argparse
import copy
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from src.estimate_offset import estimate_offset
from src.simulate import run_simulation, vehicle_state

OFFSETS_MS = [0, 50, 73, 100, 128, 150, 200]   # 73 và 128 nằm lệch lưới 5 ms
DISTANCE_M = 20
SIGMA_CAM_M = 0.10


def make_pose_fn(scenario_cfg):
    def pose_fn(t):
        states = [vehicle_state(float(ti), scenario_cfg) for ti in np.atleast_1d(t)]
        arr = np.array([s[:3] for s in states])
        return arr[:, 0], arr[:, 1], arr[:, 2]
    return pose_fn


def run(config_path: str) -> pd.DataFrame:
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    rng = np.random.default_rng(int(cfg["benchmark"]["seed"]) + 7)

    # D: xe đứng yên, chạy qua khe "A" của run_simulation để giữ nguyên quy ước seed
    cfg_static = copy.deepcopy(cfg)
    cfg_static["scenarios"]["A"] = {"type": "constant_velocity", "speed_mps": 0.0}
    cases = [("A", "A", cfg), ("B", "B", cfg), ("C", "C", cfg), ("D", "A", cfg_static)]

    rows = []
    for label, slot, c in cases:
        pose_fn = make_pose_fn(c["scenarios"][slot])
        for off in OFFSETS_MS:
            df = run_simulation(slot, off, DISTANCE_M, c)
            cam = df[["x_true", "y_true"]].to_numpy() + rng.normal(0, SIGMA_CAM_M, (len(df), 2))
            r = estimate_offset(pose_fn, df["t_ref"].to_numpy(),
                                df[["x_lidar", "y_lidar"]].to_numpy(), cam)
            rows.append(dict(scenario=label, true_offset_ms=off, est_offset_ms=r["offset_ms"],
                             abs_error_ms=abs(r["offset_ms"] - off),
                             observable=r["observable"], sharpness=round(r["sharpness"], 2)))
    out = pd.DataFrame(rows)
    out_dir = Path(cfg["output"]["results_dir"]) / "offset"
    out_dir.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_dir / "offset_on_sim.csv", index=False)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config_chot.yaml")
    res = run(ap.parse_args().config)
    print(res.to_string(index=False))
    print("\nSai số ước lượng (ms) theo kịch bản:")
    print(res.groupby("scenario").abs_error_ms.agg(["mean", "max"]).round(2).to_string())
