# Lệch Thời Gian Camera–LiDAR Tạo Sai Số Vị Trí Bao Nhiêu?

## 📋 Bài Toán

**Nền tảng:** Xe ADAS (Advanced Driver Assistance Systems)  
**Tính năng:** Fusion camera–LiDAR để định vị vật thể phía trước  
**Failure case:** Timestamp LiDAR lệch so với camera khi xe đang chạy, gây lệch vị trí vật thể trong quá trình fusion

### Thông số chính
- **Camera:** 30 Hz
- **LiDAR:** 10 Hz  
- **Offset (ms):** 0, 50, 100, 150, 200
- **Kịch bản:** A (chạy thẳng), B (tăng tốc), C (rẽ cua)
- **Vật thể tĩnh:** 10m, 20m, 40m phía trước
- **Nhiễu LiDAR:** σ = 0.02m

## 📊 Metric & Ngưỡng

| Metric | Ý nghĩa | Ngưỡng |
|--------|---------|--------|
| **E_pre** | Sai số **trước** bù | < 0.5m (tốt) |
| **E_post** | Sai số **sau** bù tuyến tính | < 0.5m (tốt) |
| **E_yaw** | Sai số **sau** bù có xét yaw | < 0.5m (tốt) |

**Ngưỡng đáng lo:** E > 0.5m (đủ để gán nhầm điểm sang vật thể bên cạnh)

## 🚀 Cài Đặt & Chạy

### 1. Clone repo & cài dependencies
```bash
pip install -r requirements.txt
```

### 2. Xem & chỉnh thông số
```bash
cat config.yaml
```

### 3. Chạy toàn bộ benchmark
```bash
python src/run_benchmark.py --config config.yaml
```

### 4. Xem kết quả
```bash
cat results/results.csv
ls -la plots/
```

## 📁 Cấu Trúc Thư Mục

```
.
├── TEAMMATES.md              # Danh sách 5 thành viên + MSSV
├── README.md                 # File này
├── requirements.txt          # Dependencies
├── config.yaml               # Thông số chốt (offset, speed, scenario, etc.)
├── src/
│   ├── simulate.py          # (TV3) Mô phỏng quỹ đạo, timestamp, E_pre
│   ├── compensate.py        # (TV4) Bù chuyển động tuyến tính & yaw
│   ├── run_benchmark.py     # (TV5) Loop qua tất cả thí nghiệm
│   └── plot.py              # (TV5) Vẽ 3 plot (timeline, offset, trajectory)
├── results/
│   ├── results.csv          # Bảng kết quả tổng hợp
│   └── benchmark.log        # Log chi tiết
├── plots/
│   ├── timeline.png         # Vị trí theo thời gian (trước/sau bù)
│   ├── error_vs_offset.png  # Sai số vs offset
│   └── trajectory.png       # Quỹ đạo 2D phía trước xe
└── reports/
    ├── TV1_HoTen_MSSV.pdf   # Báo cáo riêng từng người
    ├── TV2_HoTen_MSSV.pdf
    ├── ...
    └── sources.md           # (TV2) Tóm tắt nguồn
```

## 📖 Claim & Dự Kiến

**Hypothesis:**  
Khi offset tăng từ 0 → 200ms, sai số vị trí tăng gần tuyến tính theo `v × Δt`.  
- Bù chuyển động tuyến tính giảm sai số rõ khi **xe chạy thẳng**
- Nhưng vẫn còn sai số đáng kể khi **xe rẽ cua** vì góc quay làm vật thể xa bị lệch thêm `d × ω × Δt`

**Failure case dự kiến:**  
Kịch bản C (rẽ cua) + vật thể 40m: E_post vẫn **> 0.5m** ở offset ≥ 50ms  
→ Bù tuyến tính không đủ, cần xét yaw rate từ IMU

## 🔧 Cải Tiến & Fallback

### Cải tiến  
Bù chuyển động có xét **yaw rate** từ IMU (constant turn rate model)

### Fallback (an toàn)
Khi `offset_est > 30ms` **AND** `yaw_rate > 0.2 rad/s`:
- Không ghép điểm LiDAR vào bbox camera
- Tracking riêng mỗi sensor
- Ghi log cảnh báo đồng bộ

## 📚 Nguồn Tham Khảo

- Huai et al. 2021 (S9) - Motion Compensation for Camera-LiDAR Fusion
- [Thêm nguồn khác từ TV2]

---

**Dữ liệu:** Tổng hợp (simulation) bằng NumPy + Matplotlib  
**Mục tiêu:** Chứng minh ảnh hưởng của lệch timestamp đến sai số fusion sensor
