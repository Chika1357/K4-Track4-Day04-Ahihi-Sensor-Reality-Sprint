# 📌 CHỐT LAB T4: Lệch thời gian camera–LiDAR tạo sai số vị trí bao nhiêu?

## 1. Bài toán (đã chốt, không đổi)

- **Nền tảng:** xe ADAS.
- **Tính năng:** fusion camera–LiDAR để định vị vật thể phía trước.
- **Sensor:** camera 30 Hz, LiDAR 10 Hz.
- **Failure case:** timestamp LiDAR lệch so với camera trong khi xe đang chạy, nên điểm LiDAR chiếu lên ảnh bị lệch khỏi vị trí thật của vật thể.
- **Dữ liệu:** mô phỏng 2D bằng Python (numpy, matplotlib). Ghi rõ trong báo cáo là **dữ liệu tổng hợp**.

## 2. Claim (giả thuyết để thử, chưa phải kết luận)

> Khi offset tăng từ 0 lên 200 ms, sai số vị trí tăng gần tuyến tính theo `v × Δt` (20 m/s, 100 ms thì khoảng 2 m). Bù chuyển động tuyến tính giảm sai số rõ khi xe chạy thẳng, nhưng **còn sai số đáng kể khi xe rẽ cua**, vì góc quay làm vật thể ở xa bị lệch thêm khoảng `d × ω × Δt`.

## 3. Thông số benchmark

| Hạng mục | Giá trị chốt |
|---|---|
| Offset (áp lên timestamp LiDAR) | 0 (baseline), 50, 100, 150, 200 ms |
| Kịch bản A: chạy thẳng đều | 20 m/s |
| Kịch bản B: tăng tốc | từ 10 m/s, gia tốc 3 m/s² |
| Kịch bản C: rẽ cua | 10 m/s, bán kính 30 m (yaw rate ≈ 0,33 rad/s) |
| Vật thể tĩnh phía trước | cách xe 10, 20, 40 m |
| Nhiễu đo LiDAR | σ = 0,02 m, seed = 42 |
| Thời lượng mỗi lần chạy | 10 giây |

Tổng cộng: 3 kịch bản × 5 offset × 3 khoảng cách, mỗi tổ hợp đo trước bù và sau bù.

## 4. Metric (định nghĩa trước khi chạy, không đổi giữa các điều kiện)

- **E_pre (m):** khoảng cách giữa vị trí vật thể theo LiDAR (bị lệch thời gian) và vị trí thật ở thời điểm camera. Báo cáo cả **mean** và **max**.
- **E_post (m):** giống E_pre nhưng sau khi bù chuyển động tuyến tính (giả định vận tốc không đổi, không xét yaw).
- **Sai lệch so với công thức (%)** = |E_pre − v×Δt| / (v×Δt) × 100. Cho biết khi nào công thức `v × Δt` không còn đúng.
- **Chiều tốt/xấu:** cả ba càng nhỏ càng tốt.
- **Metric này đo gì:** chất lượng căn chỉnh dữ liệu đầu vào của fusion. Nó **chưa** chứng minh detector hay tracker giảm bao nhiêu phần trăm độ chính xác.

## 5. Ngưỡng đáng lo (nhóm tự đặt)

**E > 0,5 m** được coi là nguy hiểm, vì sai lệch cỡ này đủ để gán nhầm điểm LiDAR sang vật thể bên cạnh (ví dụ người đi bộ đứng sát xe đỗ). Trong báo cáo ghi rõ: *"ngưỡng do nhóm tự đặt, chưa có nguồn chuẩn"*.

## 6. Failure case (dự kiến, xác nhận lại bằng số sau khi chạy)

Kịch bản **C (rẽ cua), vật thể cách 40 m**: bù tuyến tính không xét góc quay nên E_post vẫn vượt ngưỡng 0,5 m ở offset ≥ 50 ms. Nếu số thực tế khác dự kiến, nhóm chọn hàng có E_post lớn nhất và họp lại lúc phút 95.

## 7. Cải tiến và fallback (đã chốt)

- **Cải tiến:** bù chuyển động có xét yaw rate từ IMU (mô hình constant turn rate). Kiểm chứng bằng E_post ở kịch bản C trước và sau cải tiến.
- **Fallback:** khi offset ước lượng > 30 ms **và** yaw rate > 0,2 rad/s, không ghép điểm LiDAR vào bbox camera mà để mỗi sensor tracking riêng, đồng thời ghi log cảnh báo đồng bộ.
- **Trade-off:** bù bằng phần mềm thì rẻ nhưng phụ thuộc vào việc biết đúng offset. Đồng bộ phần cứng (PTP, trigger chung) chính xác hơn nhưng tốn chi phí và công tích hợp. Với ADAS chạy tốc độ cao, nên có đồng bộ phần cứng; bù phần mềm chỉ là lớp bảo vệ thứ hai.

## 8. Cấu trúc repo (bắt buộc đúng tên)

```
K4-Track4-Day04-TenNhom-Sensor-Reality-Sprint/
├── TEAMMATES.md          (họ tên đầy đủ + MSSV của 5 người)
├── README.md             (bài toán, cài đặt, lệnh chạy, nguồn)
├── requirements.txt
├── config.yaml           (toàn bộ thông số ở mục 3)
├── src/
│   ├── simulate.py       (TV3)
│   ├── compensate.py     (TV4)
│   ├── run_benchmark.py  (TV5)
│   └── plot.py           (TV5)
├── results/              (results.csv + log)
├── plots/
└── reports/
    ├── TV1_HoTen_MSSV.pdf
    └── ... (đủ 5 bản riêng)
```

Lệnh chạy chung: `python src/run_benchmark.py --config config.yaml`

## 9. Phân công

| Người | Phụ trách | Nộp lên repo |
|---|---|---|
| TV1 [Tên] (đội trưởng) | Repo, README, TEAMMATES.md, trade-off, ghép slide | README.md, TEAMMATES.md, slide chung |
| TV2 [Tên] | Đọc nguồn (S9 Huai 2021 + 1 nguồn motion compensation), viết phần Method | `reports/sources.md` |
| TV3 [Phạm Hoàng Anh Khôi-2A202602404] | Code mô phỏng quỹ đạo, timestamp, offset, tính E_pre | `simulate.py`, `config.yaml` |
| TV4 [Tên] | Code bù chuyển động, tính E_post, so với `v × Δt`, phân tích failure case | `compensate.py`, đoạn phân tích failure |
| TV5 [Tên] | Chạy toàn bộ benchmark, bảng kết quả, 3 plot (timeline, sai số theo offset, quỹ đạo trước/sau bù) | `run_benchmark.py`, `plot.py`, `results/`, `plots/` |

## 10. Mốc thời gian

| Phút | Phải xong |
|---|---|
| 15 | Repo đã tạo, mọi người clone được. TEAMMATES.md đủ 5 người. |
| 45 | TV2 có tóm tắt nguồn. TV3 chạy được baseline (E ≈ 0 ở offset 0). TV4 có hàm bù. TV5 có khung bảng và code plot. |
| 80 | Code ghép xong, chạy đủ ma trận thí nghiệm. |
| 95 | Có bảng kết quả + 3 plot. **Họp 5 phút xác nhận failure case.** |
| 115 | Mỗi người xong bản báo cáo riêng, đẩy vào `reports/`. |
| 120 | Tập pitch xong. |

## 11. Pitch 5 phút

| Thứ tự | Người | Nội dung | Thời lượng |
|---|---|---|---|
| 1 | TV1 | Problem: ADAS, camera–LiDAR, lệch timestamp | 40 giây |
| 2 | TV2 | Method: nguồn nói gì, input/output, limitation | 50 giây |
| 3 | TV3 | Setup mô phỏng + chạy demo trực tiếp | 50 giây |
| 4 | TV5 | Kết quả: bảng + plot sai số theo offset | 60 giây |
| 5 | TV4 | Failure case rẽ cua, vì sao bù tuyến tính chưa đủ | 50 giây |
| 6 | TV1 | Cải tiến, fallback, trade-off | 30 giây |

## 12. Luật chung

- Báo cáo riêng của mỗi người đủ 5 mục: **Problem, Method, Benchmark, Failure case, Engineering decision**. Dùng chung số liệu nhóm nhưng tự viết bằng lời của mình.
- Câu kết quả nhóm đo viết dạng *"Nhóm quan sát được…"*. Câu từ paper viết dạng *"Paper/repo cho biết…"*. Không trộn hai loại.
- Mọi con số trong báo cáo phải truy được về `results.csv` hoặc log.
- **Mỗi người tự nộp trên VLearn**: file báo cáo riêng + URL repo chung. Nộp xong mở lại link kiểm tra.
