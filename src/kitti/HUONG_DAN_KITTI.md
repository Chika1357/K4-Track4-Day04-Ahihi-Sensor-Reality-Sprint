# Phần mở rộng T4: Lệch thời gian trên chuyển động thật (KITTI raw)

> Phụ trách: TV2. Đây là **phần mở rộng**, chỉ báo cáo khi phần tối thiểu (mô phỏng của TV3–TV5) đã chạy xong.

## 1. Mục tiêu

Mô phỏng của nhóm dùng quỹ đạo giả (thẳng, tăng tốc, rẽ cua). Phần này thay quỹ đạo giả bằng **vận tốc, yaw rate và vị trí thật của xe KITTI** để kiểm tra kết luận có còn đúng với chuyển động thật không. Đồng thời đo **độ lệch timestamp thật** giữa camera và LiDAR trong KITTI.

## 2. Cần tải gì

- Trang KITTI raw data: https://www.cvlibs.net/datasets/kitti/raw_data.php (có thể phải đăng ký tài khoản để tải).
- Tải **1 sequence bản `synced+rectified`**, ví dụ `2011_09_26_drive_0005`. Không cần file calibration hay tracklets.
- Giải nén, đường dẫn cần có dạng:

```
2011_09_26/2011_09_26_drive_0005_sync/
├── image_02/timestamps.txt
├── oxts/data/*.txt, oxts/timestamps.txt, oxts/dataformat.txt
└── velodyne_points/timestamps.txt, timestamps_start.txt, timestamps_end.txt
```

Script chỉ đọc **file text** (OXTS và timestamp), không đọc ảnh hay point cloud, nên chạy rất nhanh.

**Chọn sequence có rẽ cua.** Sau khi chạy, xem `frames_turn` trong `kitti_timestamps.json`. Nếu dưới khoảng 20 frame thì sequence gần như chỉ chạy thẳng, nên đổi sang sequence khác có rẽ.

## 3. Chạy

```bash
pip install numpy pandas matplotlib

# (tuỳ chọn) test trước bằng dữ liệu giả đúng định dạng KITTI
python make_fake_kitti.py --out fake_kitti/2011_09_26_drive_9999_sync
python kitti_real_motion.py --seq fake_kitti/2011_09_26_drive_9999_sync --out results_fake

# chạy thật
python kitti_real_motion.py --seq 2011_09_26/2011_09_26_drive_0005_sync --out results/kitti
```

⚠️ Kết quả của `fake_kitti` chỉ để kiểm tra code chạy đúng, **không đưa vào báo cáo**.

## 4. Thông số (giống mô phỏng nhóm)

| Hạng mục | Giá trị |
|---|---|
| Offset nhân tạo áp lên LiDAR | 0, 50, 100, 150, 200 ms |
| Vật thể tĩnh ảo | cách xe 10, 20, 40 m phía trước |
| Nhiễu đo | σ = 0,02 m, seed = 42 |
| Frame "đang rẽ" | \|yaw rate\| > 0,10 rad/s |
| Frame "chạy thẳng" | \|yaw rate\| < 0,02 rad/s |
| Ngưỡng đáng lo | 0,5 m (nhóm tự đặt) |

## 5. File kết quả

| File | Nội dung |
|---|---|
| `kitti_timestamps.json` | Độ lệch timestamp thật camera–LiDAR, chu kỳ camera, thời gian một vòng quét LiDAR, số frame thẳng/rẽ, vận tốc và yaw rate lớn nhất |
| `kitti_summary.csv` | Sai số trung bình/lớn nhất theo (thẳng/rẽ, khoảng cách, offset): không bù, bù tuyến tính, bù CTRV, và v×Δt |
| `kitti_frames.csv` | Chi tiết từng frame |
| `kitti_error_vs_offset.png` | Sai số theo offset, d = 40 m, tách chạy thẳng và rẽ |
| `kitti_timeline.png` | Vận tốc, yaw rate và sai số sau bù theo từng frame (offset 100 ms, d = 40 m) |

## 6. Đọc kết quả thế nào

- **`velo_minus_cam_ms_mean`**: độ lệch timestamp thật trong KITTI. KITTI kích hoạt camera theo LiDAR nên số này được kỳ vọng nhỏ; nếu đúng vậy, đây là bằng chứng cho **lợi ích của đồng bộ phần cứng** (dùng cho phần trade-off của TV1).
- **`velo_scan_duration_ms_mean`**: thời gian một vòng quét LiDAR (kỳ vọng khoảng 100 ms). Nghĩa là **ngay trong một frame LiDAR, các điểm đã lệch thời gian nhau tới cỡ đó** — nối với phần mở rộng rolling shutter của nguồn N2.
- **So sánh thẳng vs rẽ**: nếu E_lin của frame rẽ lớn hơn rõ so với frame thẳng còn E_ctrv vẫn nhỏ, thì kết luận failure case rẽ cua của mô phỏng **được xác nhận trên chuyển động thật**.

## 7. Câu mẫu cho báo cáo

- *Nhóm quan sát được:* trên sequence `____` của KITTI raw, độ lệch timestamp thật giữa LiDAR và camera trung bình `____` ms; một vòng quét LiDAR mất trung bình `____` ms.
- *Nhóm quan sát được:* với offset nhân tạo 100 ms và vật thể ảo cách 40 m, sai số sau bù tuyến tính trung bình `____` m ở frame chạy thẳng và `____` m ở frame rẽ; bù CTRV giảm xuống `____` m.

## 8. Limitation (bắt buộc ghi)

1. Vật thể là **điểm ảo**, không phải point cloud thật chiếu lên ảnh.
2. Offset 50–200 ms là **nhân tạo**, không phải offset thật của KITTI.
3. Pose lấy từ OXTS (GPS/INS), có sai số riêng; yaw rate dùng để bù cũng lấy từ OXTS nên CTRV ở đây được lợi hơn thực tế.
4. Chỉ 1 sequence, ở 1 thành phố, tốc độ đô thị.
5. Phép thử chỉ đo **sai số căn chỉnh hình học**, chưa chứng minh detector hay tracker giảm bao nhiêu.
