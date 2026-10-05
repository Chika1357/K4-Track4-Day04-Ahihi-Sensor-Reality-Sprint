# Kết quả phần mở rộng KITTI (TV2)

> Sequence: `2011_09_26_drive_0005_sync` (KITTI raw, synced+rectified).
> Lệnh chạy: `python kitti_real_motion.py --seq data\2011_09_26\2011_09_26_drive_0005_sync --out results\kitti`
> Seed 42, nhiễu σ = 0,02 m, vật thể tĩnh **ảo**, offset **nhân tạo**.

## 1. Timestamp thật trong KITTI

| Đại lượng | Giá trị |
|---|---|
| Timestamp LiDAR − timestamp camera (trung bình) | −10,50 ms |
| Độ lệch lớn nhất (trị tuyệt đối) | 10,61 ms |
| Thời gian một vòng quét LiDAR (trung bình) | 103,3 ms |

**Nhóm quan sát được:** timestamp LiDAR trong file sớm hơn timestamp camera khoảng 10,5 ms và gần như **không đổi** giữa các frame (trung bình 10,50 ms, lớn nhất 10,61 ms). Một vòng quét LiDAR mất khoảng 103 ms.

**Diễn giải (suy luận, chưa kiểm chứng):**
- Độ lệch ổn định cỡ 10 ms cho thấy KITTI có đồng bộ phần cứng (camera kích hoạt theo LiDAR); phần lệch còn lại có thể đến từ độ trễ ghi timestamp chứ chưa chắc là lệch thời điểm chụp thật. Vì vậy chỉ nên nói đây là **độ lệch giữa timestamp ghi trong file**.
- Nếu coi 10,5 ms là lệch thật: ở tốc độ của sequence này (~4,5 m/s) sai số chỉ khoảng 5 cm; nhưng với xe chạy 30 m/s (108 km/h) thì `v × Δt` ≈ 0,32 m — tính bằng công thức, chưa đo.
- Một vòng quét 103 ms nghĩa là **ngay trong một frame LiDAR, điểm đầu và điểm cuối đã lệch nhau cỡ 100 ms**, lớn hơn cả offset 50 ms nhóm đang thử. Đây là hiệu ứng kiểu "rolling shutter" của LiDAR quay, nối với nguồn N2.

## 2. Sai số vị trí theo offset nhân tạo (vật thể ảo cách 40 m)

Phân loại frame theo yaw rate thật: **rẽ** (|ω| > 0,10 rad/s): 129–130 frame; **hơi rẽ** (0,02–0,10 rad/s): 20 frame; **thẳng** (|ω| < 0,02 rad/s): 3 frame. Vận tốc trung bình khoảng 4,5–5 m/s (16–18 km/h, đường đô thị).

| Loại frame | Offset (ms) | n | Không bù (m) | Bù tuyến tính (m) | Bù CTRV (m) | v×Δt (m) |
|---|---|---|---|---|---|---|
| Rẽ | 0 | 130 | 0,026 | 0,026 | 0,026 | 0,000 |
| Rẽ | 50 | 130 | 0,397 | 0,332 | 0,030 | 0,222 |
| Rẽ | 100 | 129 | **0,804** | **0,664** | **0,035** | 0,446 |
| Rẽ | 150 | 129 | 1,202 | 0,990 | 0,045 | 0,669 |
| Rẽ | 200 | 129 | 1,606 | 1,322 | 0,059 | 0,891 |
| Hơi rẽ | 100 | 20 | 0,564 | 0,251 | 0,031 | 0,500 |
| Thẳng | 100 | 3 | 0,445 | 0,041 | 0,035 | 0,454 |

## 3. Nhận xét

**Nhóm quan sát được:**
1. **Baseline đúng:** ở offset 0 ms, sai số chỉ 0,02–0,05 m, đúng mức nhiễu đã cài.
2. **Ở frame thẳng, công thức `v × Δt` khớp:** offset 100 ms cho sai số 0,445 m so với dự đoán 0,454 m, và bù tuyến tính đưa về 0,04 m. ⚠️ Chỉ có **3 frame thẳng** nên kết luận này yếu.
3. **Ở frame rẽ, công thức `v × Δt` đánh giá thấp sai số:** offset 100 ms cho sai số 0,80 m, gần **gấp đôi** dự đoán 0,45 m.
4. **Bù tuyến tính không đủ khi rẽ:** ở offset 100 ms vẫn còn 0,66 m, **vượt ngưỡng 0,5 m** nhóm đặt; ở 50 ms còn 0,33 m (dưới ngưỡng). Như vậy với vật thể cách 40 m, offset khoảng **từ 100 ms trở lên** là nguy hiểm dù đã bù tuyến tính.
5. **Bù CTRV giảm khoảng 95% sai số khi rẽ:** từ 0,66 m xuống 0,035 m ở offset 100 ms, và vẫn dưới 0,06 m ở 200 ms.
6. Phần sai số còn lại sau bù tuyến tính (0,66 m ở 100 ms) khớp với ước lượng `d × ω × Δt` khi ω ≈ 0,17 rad/s — tức là gần như toàn bộ phần dư đến từ **góc quay của xe**.

**Kết luận chính:** failure case "rẽ cua" của mô phỏng **được xác nhận trên chuyển động thật của xe KITTI**: dù xe chỉ chạy khoảng 16 km/h, khi rẽ thì góc quay khuếch đại sai số với vật thể ở xa, và bù tuyến tính không xử lý được.

## 4. Limitation (ghi vào báo cáo)

1. Vật thể là **điểm ảo**, không phải point cloud thật chiếu lên ảnh.
2. Offset 50–200 ms là **nhân tạo**.
3. **CTRV được lợi hơn thực tế:** yaw rate dùng để bù lấy từ chính OXTS dùng để tạo quỹ đạo; ngoài đời yaw rate từ IMU có nhiễu và bias.
4. Chỉ 1 sequence, đô thị, tốc độ thấp (~4,5 m/s); chỉ 3 frame chạy thẳng.
5. Chỉ đo sai số căn chỉnh hình học, chưa đo ảnh hưởng tới detector/tracker.

## 5. Câu dùng cho slide (1 dòng)

> Trên chuyển động thật của KITTI (drive_0005, ~16 km/h), offset 100 ms làm sai số vị trí vật thể cách 40 m lên 0,80 m khi xe rẽ; bù tuyến tính còn 0,66 m (vượt ngưỡng 0,5 m), bù CTRV còn 0,035 m.
