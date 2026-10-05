"""
TV2: chạy estimate_offset trên mô phỏng chính của nhóm (simulate.py của TV3).
Chạy: python run_estimate_on_sim.py   -> results/offset/offset_on_sim.csv
"""
import os
import pandas as pd
from simulate import run_simulation, ObjectTrajectorySimulator, SimulationConfig
from estimate_offset import estimate_offset

OFFSETS = [0, 50, 73, 100, 128, 150, 200]   # 73, 128 nằm lệch lưới 5 ms để đo sai số thật
D = 20.0
os.makedirs("results/offset", exist_ok=True)

def estimate(df, sim):
    return estimate_offset(sim.pose, df.t_report.values,
                           df[["lidar_ex", "lidar_ey"]].values, df[["cam_x", "cam_y"]].values)

rows = []
for sc in ["A", "B", "C", "D"]:
    for off in OFFSETS:
        if sc == "D":   # xe đứng yên - kiểm tra limitation của nguồn N1
            sim = ObjectTrajectorySimulator(SimulationConfig(velocity_ms=0.0, object_distance_m=D))
            df = sim.simulate(off)
        else:
            df, sim = run_simulation(sc, off, D)
        r = estimate(df, sim)
        rows.append(dict(scenario=sc, true_offset_ms=off, est_offset_ms=r["offset_ms"],
                         abs_error_ms=abs(r["offset_ms"] - off), observable=r["observable"],
                         sharpness=round(r["sharpness"], 2)))
out = pd.DataFrame(rows)
out.to_csv("results/offset/offset_on_sim.csv", index=False)
print(out.to_string(index=False))
print("\nSai số trung bình (ms) theo kịch bản:")
print(out.groupby("scenario").abs_error_ms.agg(["mean", "max"]).to_string())
