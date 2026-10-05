"""Run the reproducible 45-condition timing benchmark."""

from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from shutil import copyfile

import numpy as np
import pandas as pd
import yaml

try:
    from .compensate import compensate_ctrv, compensate_linear
    from .simulate import run_simulation, to_world
except ImportError:  # supports: python src/run_benchmark.py
    from compensate import compensate_ctrv, compensate_linear
    from simulate import run_simulation, to_world


SCENARIO_LABELS = {"A": "A - Straight", "B": "B - Acceleration", "C": "C - Turning"}


def git_revision() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unavailable"


def run_benchmark(config_path: str, selected_scenarios: list[str] | None = None) -> pd.DataFrame:
    config_file = Path(config_path)
    cfg = yaml.safe_load(config_file.read_text(encoding="utf-8"))
    bench, output = cfg["benchmark"], cfg["output"]
    results_dir = Path(output["results_dir"])
    results_dir.mkdir(parents=True, exist_ok=True)
    copyfile(config_file, results_dir / "config_used.yaml")
    scenarios = selected_scenarios or list(bench["scenarios"])
    unknown = set(scenarios) - set(cfg["scenarios"])
    if unknown:
        raise ValueError(f"Unknown scenarios: {sorted(unknown)}")

    summaries, samples = [], []
    threshold = float(bench["threshold_m"])
    for scenario in scenarios:
        for offset_ms in bench["offsets_ms"]:
            offset_s = float(offset_ms) / 1000.0
            for distance_m in bench["distances_m"]:
                df = run_simulation(scenario, int(offset_ms), int(distance_m), cfg)
                linear_errors, ctrv_errors = [], []
                for _, row in df.iterrows():
                    point = np.array([row.x_lidar, row.y_lidar])
                    p_linear = compensate_linear(point, row.v_ref, offset_s)
                    p_ctrv = compensate_ctrv(point, row.v_ref, row.yaw_rate_ref, offset_s)
                    pose_ref = (row.x_ref, row.y_ref, row.yaw_ref, row.v_ref, row.yaw_rate_ref)
                    linear_world, ctrv_world = to_world(p_linear, pose_ref), to_world(p_ctrv, pose_ref)
                    linear_error = float(np.linalg.norm(linear_world - np.array([row.x_true, row.y_true])))
                    ctrv_error = float(np.linalg.norm(ctrv_world - np.array([row.x_true, row.y_true])))
                    linear_errors.append(linear_error)
                    ctrv_errors.append(ctrv_error)
                    samples.append({**row.to_dict(), "scenario": scenario, "offset_ms": offset_ms,
                                    "distance_m": distance_m, "x_linear": linear_world[0], "y_linear": linear_world[1],
                                    "x_ctrv": ctrv_world[0], "y_ctrv": ctrv_world[1],
                                    "e_linear": linear_error, "e_ctrv": ctrv_error})
                vdt = df["v_ref"] * offset_s
                deviation = np.where(vdt > 0, np.abs(df["e_pre"] - vdt) / vdt * 100.0, np.nan)
                summaries.append({
                    "scenario": scenario, "scenario_label": SCENARIO_LABELS[scenario], "offset_ms": offset_ms,
                    "distance_m": distance_m, "samples": len(df), "v_mps_mean": df["v_ref"].mean(),
                    "e_pre_mean": df["e_pre"].mean(), "e_pre_max": df["e_pre"].max(),
                    "e_post_mean": float(np.mean(linear_errors)), "e_post_max": float(np.max(linear_errors)),
                    "e_post_ctrv_mean": float(np.mean(ctrv_errors)), "e_post_ctrv_max": float(np.max(ctrv_errors)),
                    "vdt_m_mean": float(np.mean(vdt)), "formula_dev_pct": float(np.nanmean(deviation)) if offset_s else np.nan,
                    "over_threshold": bool(np.mean(linear_errors) > threshold),
                })
    result_df = pd.DataFrame(summaries)
    result_df.to_csv(results_dir / "results.csv", index=False, float_format="%.6f")
    pd.DataFrame(samples).to_csv(results_dir / "samples.csv", index=False, float_format="%.6f")
    log = ["Camera-LiDAR timing benchmark", f"run_at={datetime.now().isoformat(timespec='seconds')}",
           f"command={' '.join(sys.argv)}", f"config={config_file.resolve()}", f"git_revision={git_revision()}",
           f"python={platform.python_version()}", f"numpy={np.__version__}", f"pandas={pd.__version__}",
           f"seed={bench['seed']}", f"conditions={len(result_df)}", f"samples={len(samples)}", "",
           result_df.to_string(index=False)]
    (results_dir / "run_log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
    return result_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config_chot.yaml")
    parser.add_argument("--scenarios", nargs="+", choices=["A", "B", "C"])
    args = parser.parse_args()
    df = run_benchmark(args.config, args.scenarios)
    print(f"Completed {len(df)} conditions; results/results.csv and results/samples.csv were written.")
