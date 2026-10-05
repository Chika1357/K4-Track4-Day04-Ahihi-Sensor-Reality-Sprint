"""
compensate.py - TV4: Bù chuyển động và phân tích Failure Case (Lab T4)

Nhiệm vụ của TV4:
  1. compensate_linear(...): Bù chuyển động tuyến tính v * dt dọc hướng xe (không xét yaw).
  2. compensate_ctrv(...): Bù chuyển động có xét góc quay theo mô hình CTRV (Constant Turn Rate and Velocity).
  3. compute_formula_deviation(...): Tính % sai lệch so với công thức v * dt.
  4. analyze_failure_case(...): Phân tích điều kiện failure (kịch bản C, d=40m, E_post > 0.5m).
"""

import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import numpy as np
from typing import Tuple, Dict, Union


def compensate_linear(
    lidar_points: np.ndarray,
    velocity_mps: float,
    offset_s: float
) -> np.ndarray:
    """
    Bù chuyển động tuyến tính (Linear Motion Compensation)
    
    Giả định: Xe chuyển động thẳng đều với vận tốc velocity_mps dọc theo trục x của xe,
              bỏ qua hoàn toàn góc quay yaw_rate.
    
    Tại thời điểm t_report, xe đã đi thêm một quãng đường v * offset_s so với thời điểm t_true.
    Để đưa điểm đo LiDAR (đo ở t_true) về hệ quy chiếu thân xe tại t_report:
        x_comp = x_lidar - v * offset_s
        y_comp = y_lidar
        
    Args:
        lidar_points: Tọa độ điểm đo LiDAR trong hệ xe (dạng [N, 2] hoặc [2,])
        velocity_mps: Vận tốc tức thời của xe (m/s)
        offset_s: Lệch thời gian offset (giây, dt = offset_ms / 1000.0)
        
    Returns:
        np.ndarray: Tọa độ sau bù tuyến tính (cùng shape với lidar_points)
    """
    pts = np.array(lidar_points, dtype=float, copy=True)
    is_1d = (pts.ndim == 1)
    if is_1d:
        pts = pts.reshape(1, -1)
        
    # Dịch lùi dọc trục x thân xe quãng đường v * dt
    pts[:, 0] -= velocity_mps * offset_s
    
    return pts[0] if is_1d else pts


def compensate_ctrv(
    lidar_points: np.ndarray,
    velocity_mps: float,
    yaw_rate_rads: float,
    offset_s: float
) -> np.ndarray:
    """
    Bù chuyển động CTRV (Constant Turn Rate and Velocity Motion Compensation)
    
    Cải tiến cốt lõi của Lab T4:
    Có xét thêm vận tốc góc yaw_rate (rad/s) thu được từ cảm biến IMU.
    
    Trong khoảng thời gian offset_s:
      - Xe quay một góc: delta_yaw = yaw_rate * offset_s
      - Độ dịch chuyển của xe trong hệ quy chiếu t_true:
          dx = (v / yaw_rate) * sin(delta_yaw)       (nếu yaw_rate != 0)
          dy = (v / yaw_rate) * (1 - cos(delta_yaw))
      - Biến đổi điểm đo về hệ quy chiếu thân xe tại t_report (quay ngược -delta_yaw):
          p_rep = R(-delta_yaw) * (p_true - delta_p)
          
    Args:
        lidar_points: Tọa độ điểm đo LiDAR trong hệ xe (dạng [N, 2] hoặc [2,])
        velocity_mps: Vận tốc tức thời của xe (m/s)
        yaw_rate_rads: Tốc độ quay góc yaw từ IMU (rad/s)
        offset_s: Lệch thời gian offset (giây)
        
    Returns:
        np.ndarray: Tọa độ sau bù CTRV (cùng shape với lidar_points)
    """
    pts = np.array(lidar_points, dtype=float, copy=True)
    is_1d = (pts.ndim == 1)
    if is_1d:
        pts = pts.reshape(1, -1)
        
    # Nếu xe không quay hoặc góc quay cực nhỏ, thoái lui về bù tuyến tính
    if abs(yaw_rate_rads) < 1e-6:
        pts[:, 0] -= velocity_mps * offset_s
        return pts[0] if is_1d else pts
        
    delta_yaw = yaw_rate_rads * offset_s
    
    # Dịch chuyển vị trí xe trong hệ quy chiếu local ở t_true
    dx = (velocity_mps / yaw_rate_rads) * np.sin(delta_yaw)
    dy = (velocity_mps / yaw_rate_rads) * (1.0 - np.cos(delta_yaw))
    
    # Tọa độ tương đối so với vị trí mới của xe trước khi quay
    x_rel = pts[:, 0] - dx
    y_rel = pts[:, 1] - dy
    
    # Quay ngược góc delta_yaw để về hệ quy chiếu thân xe tại t_report
    cos_dy = np.cos(delta_yaw)
    sin_dy = np.sin(delta_yaw)
    
    x_ctrv = cos_dy * x_rel + sin_dy * y_rel
    y_ctrv = -sin_dy * x_rel + cos_dy * y_rel
    
    pts[:, 0] = x_ctrv
    pts[:, 1] = y_ctrv
    
    return pts[0] if is_1d else pts


def compute_formula_deviation(
    e_pre: float,
    velocity_mps: float,
    offset_s: float
) -> float:
    """
    Tính sai lệch (%) so với công thức xấp xỉ tuyến tính v * dt:
        deviation (%) = |E_pre - v*dt| / (v*dt) * 100
        
    Ý nghĩa:
      - Khi xe chạy thẳng (Kịch bản A), deviation xấp xỉ 0%.
      - Khi xe rẽ cua (Kịch bản C), deviation > 10% do xuất hiện thành phần lệch
        bổ sung d * omega * dt từ góc quay.
    """
    vdt = velocity_mps * offset_s
    if vdt < 1e-6:
        return 0.0
    return abs(e_pre - vdt) / vdt * 100.0


def analyze_failure_case(
    scenario: str,
    distance_m: float,
    offset_ms: float,
    e_pre: float,
    e_post: float,
    e_post_ctrv: float,
    threshold_m: float = 0.5
) -> Dict[str, Union[bool, str, float]]:
    """
    Phân tích Failure Case 3 phần theo chuẩn Checklist:
      1. Điều kiện đầu vào (Kịch bản, offset, khoảng cách d)
      2. Tác động tới metric (E_post vượt ngưỡng 0.5m)
      3. Hệ quả đối với Sensor Fusion
    """
    is_failure = (e_post > threshold_m)
    
    # Dự đoán lý thuyết độ lệch góc quay: d * omega * dt
    dt = offset_ms / 1000.0
    omega = 0.33 if "Turn" in scenario or "C" in scenario else 0.0
    theory_rot_error = distance_m * omega * dt
    
    reason = "OK (An toàn dưới ngưỡng)"
    impact = "Dữ liệu hợp nhất chính xác, nằm trong ngưỡng cho phép."
    
    if is_failure:
        if omega > 0 and distance_m >= 40:
            reason = (
                f"FAILURE CASE ĐIỂN HÌNH: Xe rẽ cua (omega={omega:.2f} rad/s) + vật thể xa (d={distance_m}m). "
                f"Bù tuyến tính bỏ qua góc quay, sinh sai số tiếp tuyến d*omega*dt ≈ {theory_rot_error:.2f}m."
            )
            impact = (
                f"E_post = {e_post:.2f}m > ngưỡng {threshold_m}m. "
                "Hệ quả: Điểm LiDAR bị lệch ngang quá lớn, có nguy cơ gán nhầm điểm vào vật thể/làn bên cạnh."
            )
        elif omega > 0:
            reason = (
                f"Xe rẽ cua: Bù tuyến tính không xét góc quay, tạo sai số góc {theory_rot_error:.2f}m."
            )
            impact = f"E_post = {e_post:.2f}m > {threshold_m}m."
        else:
            reason = f"Lệch thời gian lớn ({offset_ms}ms) làm sai số tích lũy vượt ngưỡng."
            impact = f"E_post = {e_post:.2f}m > {threshold_m}m."
            
    return {
        "scenario": scenario,
        "offset_ms": offset_ms,
        "distance_m": distance_m,
        "e_pre": e_pre,
        "e_post": e_post,
        "e_post_ctrv": e_post_ctrv,
        "threshold_m": threshold_m,
        "is_failure": is_failure,
        "theory_rot_error": theory_rot_error,
        "reason": reason,
        "impact": impact,
        "ctrv_resolved": (e_post_ctrv <= threshold_m)
    }


if __name__ == "__main__":
    print("=" * 70)
    print("TV4 SELF-TEST: Motion Compensation (Linear vs CTRV)")
    print("=" * 70)
    
    # 1. Test Kịch bản A: Chạy thẳng 20 m/s, offset 100 ms, vật thể 20m
    v_a = 20.0
    dt_a = 0.1  # 100 ms
    d_a = 20.0
    pt_lidar_a = np.array([d_a, 0.0])  # LiDAR đo được ở t_true
    
    # Bù tuyến tính
    pt_comp_a = compensate_linear(pt_lidar_a, v_a, dt_a)
    # Pose xe ở t_report tiến thêm v * dt = 2m
    # Điểm thực tế trong hệ xe t_report phải là: d_a - v*dt = 18m
    err_a_linear = abs(pt_comp_a[0] - (d_a - v_a * dt_a))
    print(f"\n[Test Kịch bản A] Thẳng đều v=20m/s, dt=100ms:")
    print(f"  Điểm gốc: {pt_lidar_a}")
    print(f"  Sau bù tuyến tính: {pt_comp_a}")
    print(f"  Sai số sau bù tuyến tính: {err_a_linear:.6f} m (PASS: ≈ 0)")

    # 2. Test Kịch bản C: Rẽ cua v=10 m/s, omega=0.33 rad/s, offset 100 ms, vật thể d=40m
    v_c = 10.0
    omega_c = 0.33
    dt_c = 0.1  # 100 ms
    d_c = 40.0
    pt_lidar_c = np.array([d_c, 0.0])
    
    pt_lin_c = compensate_linear(pt_lidar_c, v_c, dt_c)
    pt_ctrv_c = compensate_ctrv(pt_lidar_c, v_c, omega_c, dt_c)
    
    # Tính tọa độ thật chính xác trong hệ xe tại t_report
    # Trong thời gian dt_c, xe quay delta_yaw = omega * dt
    delta_yaw = omega_c * dt_c
    dx = (v_c / omega_c) * np.sin(delta_yaw)
    dy = (v_c / omega_c) * (1.0 - np.cos(delta_yaw))
    cos_dy, sin_dy = np.cos(delta_yaw), np.sin(delta_yaw)
    # Tọa độ lý thuyết thật trong hệ xe t_report:
    x_true_rep = cos_dy * (d_c - dx) + sin_dy * (0.0 - dy)
    y_true_rep = -sin_dy * (d_c - dx) + cos_dy * (0.0 - dy)
    pt_true_rep = np.array([x_true_rep, y_true_rep])
    
    err_lin_c = np.linalg.norm(pt_lin_c - pt_true_rep)
    err_ctrv_c = np.linalg.norm(pt_ctrv_c - pt_true_rep)
    theory_err = d_c * omega_c * dt_c
    
    print(f"\n[Test Kịch bản C] Rẽ cua v=10m/s, omega=0.33rad/s, dt=100ms, d=40m:")
    print(f"  Vị trí chuẩn trong hệ xe t_report: ({x_true_rep:.3f}, {y_true_rep:.3f})")
    print(f"  Sau bù tuyến tính:                  ({pt_lin_c[0]:.3f}, {pt_lin_c[1]:.3f})")
    print(f"  Sau bù CTRV:                        ({pt_ctrv_c[0]:.3f}, {pt_ctrv_c[1]:.3f})")
    print(f"  --> Sai số bù tuyến tính (E_post):     {err_lin_c:.3f} m  (> 0.5m -> FAILURE CASE!)")
    print(f"  --> Ước lượng lý thuyết d*omega*dt:    {theory_err:.3f} m (Khớp rất sát)")
    print(f"  --> Sai số sau cải tiến CTRV:          {err_ctrv_c:.6f} m (Triệt tiêu hoàn toàn)")
    
    # 3. Phân tích Failure Case
    fc_info = analyze_failure_case("Turning", d_c, 100, 1.66, err_lin_c, err_ctrv_c, threshold_m=0.5)
    print(f"\n[Phân tích Failure Case TV4]:")
    print(f"  Trạng thái: {'FAIL' if fc_info['is_failure'] else 'PASS'}")
    print(f"  Nguyên nhân: {fc_info['reason']}")
    print(f"  Hệ quả: {fc_info['impact']}")
    print(f"  CTRV giải quyết được không: {'CÓ' if fc_info['ctrv_resolved'] else 'KHÔNG'}")
    print("=" * 70)
