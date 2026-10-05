"""
TV2: chạy estimate_offset trên mô phỏng của nhóm.
Ưu tiên simulate.py của TV3 nếu đã có run_simulation (giao diện đã chốt);
nếu chưa có thì dùng offset_sim.py (bản cùng quy ước, do TV2 viết).
Chạy (từ thư mục gốc repo): python src/run_estimate_on_sim.py
Kết quả: results/offset/offset_on_sim.csv
"""
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import simulate as sim_mod
    if not hasattr(sim_mod, "run_simulation"):
        raise ImportError
    SOURCE = "simulate.py (TV3)"
except ImportError:
    import offset_sim as sim_mod
    SOURCE = "offset_sim.py (TV2)"

from estimate_offset import estimate_offset

OFFSETS = [0, 50, 73, 100, 128, 150, 200]   # 73, 128 lệch lưới 5 ms để đo sai số thật
D = 20.0
OUT = "results/offset"


def estimate(df, sim):
    return estimate_offset(sim.pose, df.t_report.values,
                           df[["lidar_ex", "lidar_ey"]].values, df[["cam_x", "cam_y"]].values)


def main():
    os.makedirs(OUT, exist_ok=True)
    print(f"Dùng mô phỏng: {SOURCE}")
    rows = []
    for sc in ["A", "B", "C", "D"]:
        for off in OFFSETS:
            if sc == "D":   # xe đứng yên - kiểm tra limitation của nguồn N1
                sim = sim_mod.ObjectTrajectorySimulator(
                    sim_mod.SimulationConfig(velocity_ms=0.0, object_distance_m=D))
                df = sim.simulate(off)
            else:
                df, sim = sim_mod.run_simulation(sc, off, D)
            r = estimate(df, sim)
            rows.append(dict(scenario=sc, true_offset_ms=off, est_offset_ms=r["offset_ms"],
                             abs_error_ms=abs(r["offset_ms"] - off), observable=r["observable"],
                             sharpness=round(r["sharpness"], 2), sim_source=SOURCE))
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(OUT, "offset_on_sim.csv"), index=False)
    print(out.drop(columns="sim_source").to_string(index=False))
    print("\nSai số (ms) theo kịch bản:")
    print(out.groupby("scenario").abs_error_ms.agg(["mean", "max"]).to_string())


if __name__ == "__main__":
    main()
