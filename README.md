# Lab T4 - Camera-LiDAR timestamp offset

This repository contains a reproducible 2-D synthetic benchmark for an ADAS camera-LiDAR fusion timing failure. It measures how a LiDAR timestamp offset changes estimated object position and compares translation-only compensation with constant-turn-rate-and-velocity (CTRV) compensation.

## Reproduce

```powershell
python -m pip install -r requirements.txt
python -m src.run_benchmark --config config_chot.yaml
python -m src.plot --config config_chot.yaml
```

The benchmark runs 45 conditions: A (20 m/s straight), B (10 m/s with 3 m/s2 acceleration), C (10 m/s with a 30 m turn radius); offsets 0/50/100/150/200 ms; and distances 10/20/40 m. Each condition has 100 independent samples, seed 42, and 0.02 m Gaussian LiDAR noise per axis.

## Evidence

| Artifact | Purpose |
|---|---|
| `results/config_used.yaml` | Configuration used for the run |
| `results/samples.csv` | Per-sample ground truth, predictions, and errors |
| `results/results.csv` | Mean/max metrics for all 45 conditions |
| `results/run_log.txt` | Command, revision, versions, seed, and metrics |
| `plots/timeline.png` | Timestamp convention at 100 ms offset |
| `plots/error_vs_offset.png` | Error trend at d = 20 m and 40 m |
| `plots/alignment_turn.png` | C, d = 40 m, offset = 100 ms |

## Measured highlights

- Offset 0 ms baseline mean error: 0.023-0.027 m.
- A, d = 20 m, offset = 100 ms: `E_pre = 2.001 m`, `v x dt = 2.000 m`, linear `E_post = 0.026 m`.
- Failure: C, d = 40 m, offset = 100 ms: `E_pre = 1.668 m`, linear `E_post = 1.351 m`, CTRV `E_post = 0.025 m`.

## Decision and limitations

Use CTRV compensation when the offset estimate and yaw rate are reliable. When estimated offset exceeds 30 ms and yaw rate exceeds 0.2 rad/s, avoid LiDAR-to-camera-bbox association, track each sensor separately, and log a synchronization warning. Prefer PTP/shared-trigger synchronization for high-speed ADAS.

This is synthetic 2-D input-alignment evidence, not detector mAP, tracking, image projection, LiDAR scan distortion, or end-to-end latency. The 0.5 m concern threshold is set by the group, not an external safety standard.
