"""Synthetic 2-D camera--LiDAR timing benchmark.

Each row is an independent reference-time experiment. The object is static
within that experiment and is placed ``distance_m`` ahead of the ego vehicle
at the camera/reference time. LiDAR observes it at ``t_ref - offset``.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd


def _scenario(cfg: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    return cfg["scenarios"][scenario]


def vehicle_state(t: float, scenario_cfg: Dict[str, Any]) -> Tuple[float, float, float, float, float]:
    """Return x, y, yaw, speed, yaw-rate for the configured ego motion."""
    kind = scenario_cfg["type"]
    if kind == "constant_velocity":
        speed = float(scenario_cfg["speed_mps"])
        return speed * t, 0.0, 0.0, speed, 0.0
    if kind == "constant_acceleration":
        v0 = float(scenario_cfg["initial_speed_mps"])
        accel = float(scenario_cfg["acceleration_mps2"])
        return v0 * t + 0.5 * accel * t * t, 0.0, 0.0, v0 + accel * t, 0.0
    if kind == "constant_turn_rate":
        speed = float(scenario_cfg["speed_mps"])
        radius = float(scenario_cfg["radius_m"])
        yaw_rate = speed / radius
        yaw = yaw_rate * t
        return radius * np.sin(yaw), radius * (1.0 - np.cos(yaw)), yaw, speed, yaw_rate
    raise ValueError(f"Unsupported scenario type: {kind}")


def rotate(vector: np.ndarray, angle: float) -> np.ndarray:
    c, s = np.cos(angle), np.sin(angle)
    return np.array([c * vector[0] - s * vector[1], s * vector[0] + c * vector[1]])


def to_world(local: np.ndarray, pose: Tuple[float, float, float, float, float]) -> np.ndarray:
    return np.asarray(pose[:2], dtype=float) + rotate(local, pose[2])


def to_local(world: np.ndarray, pose: Tuple[float, float, float, float, float]) -> np.ndarray:
    return rotate(np.asarray(world, dtype=float) - np.asarray(pose[:2], dtype=float), -pose[2])


def run_simulation(scenario: str, offset_ms: int, distance_m: int, cfg: Dict[str, Any]) -> pd.DataFrame:
    """Generate samples, ground truth, and naive pre-compensation error."""
    bench = cfg["benchmark"]
    scenario_cfg = _scenario(cfg, scenario)
    dt = float(offset_ms) / 1000.0
    count = int(bench["samples_per_condition"])
    t_ref = float(bench["reference_start_s"]) + np.arange(count) / float(bench["reference_rate_hz"])
    seed = int(bench["seed"]) + {"A": 0, "B": 10_000, "C": 20_000}[scenario] + int(offset_ms) * 10 + int(distance_m)
    rng = np.random.default_rng(seed)
    noise_std = float(bench["noise_std_per_axis_m"])
    records = []
    for frame, t in enumerate(t_ref):
        t_capture = t - dt
        pose_ref = vehicle_state(float(t), scenario_cfg)
        pose_capture = vehicle_state(float(t_capture), scenario_cfg)
        object_world = to_world(np.array([float(distance_m), 0.0]), pose_ref)
        lidar_local = to_local(object_world, pose_capture) + rng.normal(0.0, noise_std, size=2)
        pre_world = to_world(lidar_local, pose_ref)
        records.append({
            "frame": frame, "t_ref": t, "t_capture": t_capture,
            "x_true": object_world[0], "y_true": object_world[1],
            "x_lidar": lidar_local[0], "y_lidar": lidar_local[1],
            "x_ref": pose_ref[0], "y_ref": pose_ref[1], "yaw_ref": pose_ref[2],
            "v_ref": pose_ref[3], "yaw_rate_ref": pose_ref[4],
            "x_pre": pre_world[0], "y_pre": pre_world[1],
            "e_pre": float(np.linalg.norm(pre_world - object_world)),
        })
    return pd.DataFrame.from_records(records)
