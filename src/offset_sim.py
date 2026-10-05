"""
offset_sim.py - TV2: bản mô phỏng dùng RIÊNG cho run_estimate_on_sim.py.
Cùng quy ước với file chốt nhóm (giống bản sửa simulate.py đã gửi TV3).
Khi simulate.py của TV3 có run_simulation, run_estimate_on_sim.py sẽ tự dùng simulate.py.
Sửa so với bản gốc:
  1. Không ghép "frame LiDAR gần nhất" nữa -> baseline offset 0 ms cho E_pre ≈ mức nhiễu.
     Quy ước: LiDAR BÁO timestamp t_report nhưng THỰC SỰ chụp lúc t_true = t_report - offset.
  2. Vật thể tĩnh ảo đặt cách xe đúng d mét phía trước tại mỗi frame -> d có ý nghĩa.
  3. Quỹ đạo rẽ cua là đường tròn đúng: x = R sin(wt), y = R(1 - cos(wt)), w = v/R.
Thêm:
  - run_simulation(scenario, offset_ms, distance_m, cfg) -> DataFrame theo giao diện nhóm đã chốt.
  - Cột lidar_ex, lidar_ey (LiDAR đo trong hệ xe) và cam_x, cam_y (camera đo trong hệ world)
    để TV2 dùng cho estimate_offset; hàm pose(t) dùng được với mảng t.
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass, replace
from typing import Optional


@dataclass
class SimulationConfig:
    duration_sec: float = 10.0
    velocity_ms: float = 20.0
    acceleration_ms2: float = 0.0
    turn_radius_m: Optional[float] = None   # None = chạy thẳng
    camera_freq_hz: int = 30
    lidar_freq_hz: int = 10
    object_distance_m: float = 20.0
    lidar_noise_sigma_m: float = 0.02
    camera_noise_sigma_m: float = 0.10
    random_seed: int = 42


# Ba kịch bản đã chốt trong file CHOT_LAB_T4.md
SCENARIOS = {
    "A": dict(velocity_ms=20.0, acceleration_ms2=0.0, turn_radius_m=None),
    "B": dict(velocity_ms=10.0, acceleration_ms2=3.0, turn_radius_m=None),
    "C": dict(velocity_ms=10.0, acceleration_ms2=0.0, turn_radius_m=30.0),
}


def ego_to_world(x, y, yaw, mx, my):
    c, s = np.cos(yaw), np.sin(yaw)
    return x + c * mx - s * my, y + s * mx + c * my


def world_to_ego(x, y, yaw, px, py):
    dx, dy = px - x, py - y
    c, s = np.cos(yaw), np.sin(yaw)
    return c * dx + s * dy, -s * dx + c * dy


class ObjectTrajectorySimulator:
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.rng = np.random.RandomState(config.random_seed)

    def get_vehicle_state(self, t):
        """(x, y, yaw, v, yaw_rate) tại thời điểm t (số hoặc mảng)."""
        c = self.config
        t = np.asarray(t, dtype=float)
        if c.turn_radius_m:                                  # rẽ cua: tròn đều, w = v/R
            w = c.velocity_ms / c.turn_radius_m
            yaw = w * t
            x = c.turn_radius_m * np.sin(yaw)
            y = c.turn_radius_m * (1 - np.cos(yaw))
            v = np.full_like(t, c.velocity_ms)
            yaw_rate = np.full_like(t, w)
        else:                                                # thẳng đều / tăng tốc
            x = c.velocity_ms * t + 0.5 * c.acceleration_ms2 * t ** 2
            y = np.zeros_like(t)
            yaw = np.zeros_like(t)
            v = c.velocity_ms + c.acceleration_ms2 * t
            yaw_rate = np.zeros_like(t)
        return x, y, yaw, v, yaw_rate

    def pose(self, t):
        """(x, y, yaw) - dùng cho estimate_offset và compensate."""
        x, y, yaw, _, _ = self.get_vehicle_state(t)
        return x, y, yaw

    def simulate(self, offset_ms: float) -> pd.DataFrame:
        c = self.config
        dt = offset_ms / 1000.0
        # LiDAR 10 Hz; camera 30 Hz nên mỗi timestamp LiDAR trùng đúng một frame camera
        t_report = np.arange(0.5, c.duration_sec, 1.0 / c.lidar_freq_hz)
        t_true = t_report - dt

        xr, yr, yawr, v, w = self.get_vehicle_state(t_report)   # pose lúc camera chụp
        xt, yt, yawt, _, _ = self.get_vehicle_state(t_true)     # pose lúc LiDAR thật sự chụp

        # vật thể tĩnh ảo cách xe d mét phía trước (tại thời điểm camera)
        ox, oy = ego_to_world(xr, yr, yawr, c.object_distance_m, 0.0)

        # LiDAR đo vật thể trong hệ xe lúc t_true (+ nhiễu)
        lex, ley = world_to_ego(xt, yt, yawt, ox, oy)
        lex = lex + self.rng.normal(0, c.lidar_noise_sigma_m, len(t_report))
        ley = ley + self.rng.normal(0, c.lidar_noise_sigma_m, len(t_report))

        # Fusion (cố ý sai): dùng pose lúc t_report để đổi điểm LiDAR ra world
        fx, fy = ego_to_world(xr, yr, yawr, lex, ley)
        e_pre = np.hypot(fx - ox, fy - oy)

        # Camera đo vật thể trong world (+ nhiễu) - dùng cho estimate_offset
        cam_x = ox + self.rng.normal(0, c.camera_noise_sigma_m, len(t_report))
        cam_y = oy + self.rng.normal(0, c.camera_noise_sigma_m, len(t_report))

        return pd.DataFrame(dict(
            frame=np.arange(len(t_report)), t_report=t_report, t_true=t_true,
            x_true=ox, y_true=oy, x_lidar=fx, y_lidar=fy,
            v=v, yaw_rate=w, e_pre=e_pre,
            lidar_ex=lex, lidar_ey=ley, cam_x=cam_x, cam_y=cam_y))


def run_simulation(scenario: str, offset_ms: float, distance_m: float,
                   cfg: Optional[SimulationConfig] = None):
    """Giao diện nhóm đã chốt. Trả về (DataFrame, simulator) - simulator.pose(t) cho TV2/TV4."""
    cfg = cfg or SimulationConfig()
    cfg = replace(cfg, object_distance_m=distance_m, **SCENARIOS[scenario])
    sim = ObjectTrajectorySimulator(cfg)
    return sim.simulate(offset_ms), sim


if __name__ == "__main__":
    print("Kiểm tra nhanh E_pre trung bình (m), d = 20 m:")
    print(f"{'kịch bản':>9} " + " ".join(f"{o:>7}ms" for o in [0, 50, 100, 150, 200]))
    for sc in "ABC":
        vals = [run_simulation(sc, o, 20)[0].e_pre.mean() for o in [0, 50, 100, 150, 200]]
        print(f"{sc:>9} " + " ".join(f"{v:9.3f}" for v in vals))
    df, sim = run_simulation("C", 0, 20)
    x, y, _ = sim.pose(np.array([0, 2, 4.71, 9.42]))
    print("Kịch bản C - khoảng cách tới tâm cua (phải luôn = 30):", np.round(np.hypot(x, y - 30), 2))
