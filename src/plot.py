"""Create the three figures required by the Lab T4 checklist."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml


def plot_timeline(cfg: dict, outdir: Path) -> None:
    b = cfg["benchmark"]
    camera = np.arange(0, 1.0 + 1e-9, 1 / b["camera_rate_hz"])
    lidar_ref = np.arange(0, 1.0 + 1e-9, 1 / b["lidar_rate_hz"])
    capture = lidar_ref - 0.1
    fig, ax = plt.subplots(figsize=(11, 3.8), dpi=150)
    ax.eventplot([camera, lidar_ref, capture[capture >= 0]], lineoffsets=[2, 1, 0], linelengths=.5,
                 colors=["#1f77b4", "#d62728", "#2ca02c"], linewidths=2)
    ax.set(yticks=[0, 1, 2], yticklabels=["LiDAR capture t_ref − 100 ms", "LiDAR timestamp t_ref", "Camera (30 Hz)"],
           xlabel="Time (s)", xlim=(-.04, 1.04), title="Camera–LiDAR timestamps, offset = 100 ms\n[Dữ liệu tổng hợp]")
    ax.grid(axis="x", linestyle=":", alpha=.6)
    fig.tight_layout(); fig.savefig(outdir / "timeline.png"); plt.close(fig)


def plot_error(results: pd.DataFrame, outdir: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=150, sharey=True)
    colors = {"A": "#1f77b4", "B": "#2ca02c", "C": "#d62728"}
    for ax, distance in zip(axes, [20, 40]):
        sub_d = results[results.distance_m == distance]
        for scenario in ["A", "B", "C"]:
            sub = sub_d[sub_d.scenario == scenario].sort_values("offset_ms")
            ax.plot(sub.offset_ms, sub.e_pre_mean, "o--", color=colors[scenario], alpha=.65, label=f"{scenario}: E_pre")
            ax.plot(sub.offset_ms, sub.e_post_mean, "s-", color=colors[scenario], label=f"{scenario}: E_post linear")
            if scenario == "C":
                ax.plot(sub.offset_ms, sub.e_post_ctrv_mean, "^:", color="#9467bd", lw=2, label="C: E_post CTRV")
        ax.axhline(.5, color="black", ls="-.", label="Ngưỡng 0.5 m")
        ax.set(title=f"Object distance = {distance} m", xlabel="Timestamp offset (ms)", xticks=[0, 50, 100, 150, 200])
        ax.grid(linestyle=":", alpha=.6); ax.legend(fontsize=7)
    axes[0].set_ylabel("Mean position error (m)")
    fig.suptitle("Position error versus timestamp offset [Dữ liệu tổng hợp]")
    fig.tight_layout(); fig.savefig(outdir / "error_vs_offset.png"); plt.close(fig)


def plot_alignment(samples: pd.DataFrame, outdir: Path) -> None:
    sub = samples[(samples.scenario == "C") & (samples.distance_m == 40) & (samples.offset_ms == 100)].iloc[::10]
    fig, ax = plt.subplots(figsize=(8, 7), dpi=150)
    ax.scatter(sub.x_true, sub.y_true, label="Ground truth", c="#2ca02c", s=45)
    ax.scatter(sub.x_pre, sub.y_pre, label="Before compensation", c="#d62728", marker="x", s=45)
    ax.scatter(sub.x_linear, sub.y_linear, label="Linear compensation", c="#ff7f0e", marker="s", s=30)
    ax.scatter(sub.x_ctrv, sub.y_ctrv, label="CTRV compensation", c="#1f77b4", marker="^", s=35)
    for _, r in sub.iloc[::3].iterrows():
        ax.plot([r.x_true, r.x_linear], [r.y_true, r.y_linear], color="#ff7f0e", alpha=.3)
    ax.set(aspect="equal", xlabel="World X (m)", ylabel="World Y (m)",
           title="Turning scenario C: d = 40 m, offset = 100 ms\n[Dữ liệu tổng hợp]")
    ax.grid(linestyle=":", alpha=.6); ax.legend(); fig.tight_layout()
    fig.savefig(outdir / "alignment_turn.png"); fig.savefig(outdir / "trajectory_turn.png"); plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config_chot.yaml")
    parser.add_argument("--csv", default="results/results.csv")
    parser.add_argument("--samples", default="results/samples.csv")
    parser.add_argument("--outdir", default="plots")
    args = parser.parse_args()
    output = Path(args.outdir); output.mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    plot_timeline(cfg, output)
    plot_error(pd.read_csv(args.csv), output)
    plot_alignment(pd.read_csv(args.samples), output)
    print(f"Wrote timeline.png, error_vs_offset.png, and alignment_turn.png to {output}")
