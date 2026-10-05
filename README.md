# Lab T4 — Lệch timestamp và sai số căn chỉnh vị trí

Nhóm kiểm tra tác động lệch thời gian tới căn chỉnh vị trí camera–LiDAR trong bối cảnh ADAS bằng dữ liệu tổng hợp 2D.

**Trạng thái:** đã chốt thiết kế/cấu hình/phân công. Code benchmark chưa triển khai; chưa có số đo/plot kết quả. Lệnh dưới đây là giao diện cần hiện thực.

## Đọc trước khi làm

- [Thiết kế, công thức và giao diện](CHOT_LAB_T4.md)
- [Checklist từng thành viên](CHECKLIST_TUNG_NGUOI_T4.md)
- [Thành viên/nhánh](TEAMMATES.md)
- [Cấu hình](config.yaml)
- [Nguồn và phiếu đọc](reports/sources.md)

## Problem và claim

LiDAR đo tại t_true = t_ref - Δt nhưng báo timestamp t_ref. Dùng pose tại timestamp báo để đổi phép đo ra world sẽ gây sai số vị trí.

So không bù, bù tịnh tiến và bù tịnh tiến + quay (CTRV). Claim: chạy thẳng đều có sai số gần v × Δt; khi rẽ, linear có thể còn lỗi, CTRV dự kiến giảm lỗi đó.

Mỗi mẫu là phép thử độc lập với vật thể đứng yên cách ego 10/20/40 m tại mốc tham chiếu. Camera là mốc thời gian; chưa chạy ảnh, point cloud, bbox, detector/tracker hay pixel error.

## Benchmark

- A: thẳng 20 m/s; B: tăng tốc từ 10 m/s, 3 m/s²; C: rẽ 10 m/s, bán kính 30 m.
- Offset 0/50/100/150/200 ms; cùng mốc/dữ liệu/nhiễu giữa phương án.
- 100 mẫu/tổ hợp, seed gốc 42, noise 0,02 m mỗi trục.
- 45 tổ hợp đầy đủ; ưu tiên A/C (30 tổ hợp), B là mở rộng.
- Mean/max sai số Euclidean theo mét trước bù, sau linear, sau CTRV.
- Ngưỡng minh họa 0,5 m do nhóm đặt, chưa phải tiêu chuẩn an toàn.
- Giả định biết đúng offset/trạng thái hiện tại; GT chỉ dùng sinh dữ liệu/chấm điểm.

## Setup và giao diện chạy

Dùng môi trường Python của nhóm, sau đó:

~~~powershell
python -m pip install -r requirements.txt
~~~

Dependencies chưa pin; TV5 ghi phiên bản thật vào log sau lần chạy thành công. Lệnh benchmark **chưa chạy được cho tới khi TV3/TV4/TV5 hoàn thành code**:

~~~powershell
python -m src.run_benchmark --config config.yaml
~~~

Phần ưu tiên A/C, khi runner hỗ trợ chọn scenario:

~~~powershell
python -m src.run_benchmark --config config.yaml --scenarios A C
~~~

## Bằng chứng cần có

| File | Nội dung |
|---|---|
| results/samples.csv | Phép đo, GT, dự đoán và sai số từng mẫu |
| results/results.csv | Metric từng scenario/offset/distance |
| results/config_used.yaml | Config thực sự dùng |
| results/run_log.txt | Lệnh, commit/working tree, seed, phiên bản và runtime |
| plots/timeline.png | Timestamp báo và thời điểm đo thật |
| plots/error_vs_offset.png | Ba phương án theo offset |
| plots/alignment_turn.png | Một mẫu rẽ: vị trí đúng và các dự đoán |

Sau chạy, TV1 cập nhật trạng thái bằng bảng thật, plot chính, lệnh và thông tin tái hiện. Không dùng dự đoán lý thuyết như số tự đo.

## Failure và decision

Chọn failure từ CSV cùng baseline; kiểm chứng CTRV so với linear trên cùng dữ liệu. Fallback association/tracking là đề xuất thử tiếp, chưa triển khai.

Limitation: mô phỏng 2D, mẫu độc lập, biết đúng offset/trạng thái, chưa scan distortion, detector/association/latency end-to-end. Kết quả nguồn và kết quả nhóm ghi riêng.

## Phân công và báo cáo

TV1 tài liệu/tích hợp; TV2 nguồn; TV3 mô phỏng; TV4 bù/failure; TV5 runner/metric/plot. Điền danh tính/nhánh thật trong TEAMMATES.

Mỗi báo cáo theo Problem → Method → Benchmark → Failure case → Engineering decision. Tự nộp VLearn; pitch nhóm 3–5 phút.
