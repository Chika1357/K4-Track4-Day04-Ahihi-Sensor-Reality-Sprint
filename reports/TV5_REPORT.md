# TV5 Report - Benchmark, Results, and Plots

**Student:** Hoàng Trung Anh - 2A202602521  
**Repository:** K4-Track4-Day4-Ahihi  
**Evidence:** `results/results.csv`, `results/samples.csv`, `results/run_log.txt`, and `plots/`.

## 1. Problem

This project evaluates a camera-LiDAR fusion risk in an ADAS vehicle. LiDAR captures a static object at `t_capture = t_ref - offset`, but its data is fused using the ego pose at camera/reference time `t_ref`. The mismatch can place a LiDAR point at an incorrect world/image location. The test uses synthetic 2-D data; it does not measure detector mAP, tracking accuracy, or end-to-end latency.

## 2. Method

The benchmark evaluates 45 conditions: scenarios A (20 m/s straight), B (10 m/s with 3 m/s2 acceleration), and C (10 m/s, 30 m turn radius), five offsets (0, 50, 100, 150, 200 ms), and object distances 10, 20, and 40 m. Each condition has 100 independent reference-time samples, Gaussian LiDAR noise of 0.02 m per axis, and seed 42.

For every identical sample, the runner computes three estimates: no compensation (`E_pre`), translation-only compensation (`E_post`), and constant-turn-rate-and-velocity compensation (`E_post_ctrv`). The metric is Euclidean position error in metres against synthetic ground truth. The illustrative concern threshold is 0.5 m, chosen by the group and not claimed as an external safety standard.

## 3. Benchmark

The group observed that every 0 ms baseline mean error is 0.023-0.027 m, which is consistent with the configured measurement noise. In scenario A at 100 ms and 20 m, the group observed `E_pre = 2.001 m`, close to `v x dt = 2.000 m`; translation compensation reduced the mean error to `0.026 m`.

Run command: `python -m src.run_benchmark --config config_chot.yaml`  
Plot command: `python -m src.plot --config config_chot.yaml`

Use `plots/timeline.png` for the timestamp convention, `plots/error_vs_offset.png` for the 45-condition trend, and `plots/alignment_turn.png` for the turn example.

## 4. Failure Case

The selected failure is scenario C, object distance 40 m, offset 100 ms. The group observed `E_pre = 1.668 m` and translation-only `E_post = 1.351 m`, both above 0.5 m. The remaining error is primarily lateral because translation-only compensation omits the 0.333 rad/s yaw rate. CTRV reduced the mean error to `0.025 m` on the same samples. Assigning a point to a neighbouring object or camera box is an engineering inference, not a detector result measured in this benchmark.

## 5. Engineering Decision

Use motion compensation with yaw rate (CTRV) when a reliable offset estimate and ego state are available. As a conservative fallback, when estimated offset exceeds 30 ms and yaw rate exceeds 0.2 rad/s, avoid point-to-camera-bbox association, track sensors separately, and record a synchronization warning. Hardware synchronization (PTP or shared trigger) is preferred for high-speed ADAS; software compensation is a second defence. Limitations are synthetic 2-D geometry, known offset/state, independent samples, no LiDAR scan distortion, and no detector, association, or end-to-end latency measurement.
