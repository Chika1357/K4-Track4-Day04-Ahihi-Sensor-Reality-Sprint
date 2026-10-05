# Quick Start Guide - CHỐT LAB T4

## ⚡ Chạy nhanh (5 phút)

### 1. Cài dependencies
```bash
pip install -r requirements.txt
```

### 2. Chạy benchmark đầu tiên
```bash
python src/run_benchmark.py config.yaml
```

### 3. Vẽ biểu đồ
```bash
python src/plot.py results/results.csv plots/
```

### 4. Xem kết quả
```bash
cat results/results.csv          # Bảng dữ liệu
cat results/benchmark.log        # Log chi tiết
ls plots/                        # Biểu đồ
```

---

## 📚 Cấu trúc code

| File | Chuyên môn | Nhiệm vụ |
|------|-----------|---------|
| `simulate.py` | TV3 | Mô phỏng quỹ đạo xe, vị trí vật thể, timestamp camera/LiDAR, tính E_pre |
| `compensate.py` | TV4 | Bù chuyển động (tuyến tính + yaw), tính E_post, phân tích failure |
| `run_benchmark.py` | TV5 | Loop qua tất cả thí nghiệm, ghi CSV + log |
| `plot.py` | TV5 | Vẽ 3 plot: error vs offset, comparison, heatmap |

---

## 🔧 Tuỳ chỉnh thông số

Mở `config.yaml` và sửa:

```yaml
offsets_ms: [0, 50, 100, 150, 200]  # Offset LiDAR (ms)
scenarios:
  scenario_a_straight:
    velocity_ms: 20                 # Tốc độ (m/s)
object_distances_m: [10, 20, 40]    # Khoảng cách vật thể (m)
```

---

## 📊 Đọc kết quả

**results.csv** có các cột:
- `e_pre_mean`: Sai số trước bù
- `e_post_mean`: Sai số sau bù (tuyến tính)
- `e_post_yaw_mean`: Sai số sau bù (có xét yaw)
- `is_failure`: True nếu E_post > 0.5m

**Failure cases** được ghi rõ trong `benchmark.log`

---

## ✅ Checklist

- [ ] Cài dependencies
- [ ] Chạy benchmark lần đầu
- [ ] Xem kết quả CSV
- [ ] Vẽ biểu đồ
- [ ] Xác nhận failure case (scenario C, distance 40m)
- [ ] Điều chỉnh config nếu cần
- [ ] Ghi log để báo cáo

---

## ❓ Thắc mắc?

- **E_pre > v×Δt?** Có thể do quỹ đạo cong hoặc tăng tốc
- **E_post vẫn lớn ở scenario C?** Bù tuyến tính không xét yaw, cần dùng E_post_yaw
- **Sai số lớn ở vật thể 40m?** Bù góc quay rất quan trọng khi object xa

---

**Good luck! 🚀**
