# Lab T4 — Lệch timestamp và sai số căn chỉnh vị trí

Nhóm kiểm tra tác động lệch thời gian tới căn chỉnh vị trí camera–LiDAR trong bối cảnh ADAS bằng dữ liệu tổng hợp 2D.

**Trạng thái:** main đã có code và CSV/plot phiên bản cũ. Review xác nhận lỗi ghép thời điểm, dấu bù và quỹ đạo rẽ; số đo hiện tại chưa dùng để kết luận về failure sensor. Thiết kế dưới đây là mục tiêu cho vòng sửa tiếp theo, chưa phải benchmark đã nghiệm thu.

## Tài liệu và việc của từng người

- [Thiết kế, công thức và giao diện](CHOT_LAB_T4.md)
- [Checklist từng người](CHECKLIST_TUNG_NGUOI_T4.md)
- [Việc TV1 cần làm và điều kiện nghiệm thu](reports/TV1_HANDOFF.md)
- [Review code và bằng chứng lỗi](reports/CODE_REVIEW_T4.md)
- [Khung báo cáo riêng của TV1](reports/TV1_REPORT_TEMPLATE.md)
- [Thành viên/nhánh](TEAMMATES.md)
- [Nguồn và phiếu đọc của TV2](reports/sources.md)

## Problem và claim

LiDAR đo tại t_true = t_ref - Δt nhưng báo timestamp t_ref. Dùng pose tại timestamp báo để đổi phép đo ra world sẽ gây sai số vị trí.

So không bù, bù tịnh tiến và bù tịnh tiến + quay (CTRV). Claim: chạy thẳng đều có sai số gần v × Δt; khi rẽ, linear còn lỗi do bỏ qua quay, CTRV dự kiến giảm lỗi đó.

Mỗi mẫu của thiết kế mục tiêu là một phép thử độc lập với vật thể đứng yên cách ego 10/20/40 m tại mốc tham chiếu. Camera là mốc thời gian; chưa chạy ảnh, point cloud, bbox, detector/tracker hay pixel error.

## Benchmark mục tiêu

- A: thẳng 20 m/s; B: tăng tốc từ 10 m/s, 3 m/s²; C: rẽ 10 m/s, bán kính 30 m.
- Offset 0/50/100/150/200 ms; cùng mốc/dữ liệu/nhiễu giữa phương án.
- 100 mẫu/tổ hợp, seed gốc 42, noise 0,02 m mỗi trục.
- 45 tổ hợp đầy đủ; ưu tiên A/C (30 tổ hợp), B là mở rộng.
- Mean/max sai số Euclidean theo mét trước bù, sau linear, sau CTRV.
- Ngưỡng minh họa 0,5 m do nhóm đặt, chưa phải tiêu chuẩn an toàn.
- Giả định biết đúng offset/trạng thái hiện tại; GT chỉ dùng sinh dữ liệu/chấm điểm.

## Cài đặt và hai phiên bản cấu hình

~~~powershell
python -m pip install -r requirements.txt
~~~

Giữ requirements của code hiện tại; TV5 ghi Python và phiên bản thư viện thật vào log. Nếu cần đổi dependency, ghi lý do và kiểm tra lại môi trường.

| File | Dùng cho |
|---|---|
| [config.yaml](config.yaml) | Schema code phiên bản cũ, dùng kiểm tra lại lỗi |
| [config_chot.yaml](config_chot.yaml) | Thiết kế mục tiêu, cần TV3/TV5 cập nhật code trước khi chạy |

[Quickstart](QUICKSTART.md) ghi riêng lệnh bản cũ và giao diện mục tiêu.

Lệnh mục tiêu, **chưa được runner hiện tại hỗ trợ**:

~~~powershell
python -m src.run_benchmark --config config_chot.yaml
python -m src.run_benchmark --config config_chot.yaml --scenarios A C
~~~

## Bằng chứng phải có sau khi sửa

| File | Nội dung |
|---|---|
| results/samples.csv | Phép đo, GT, dự đoán và sai số từng mẫu |
| results/results.csv | Metric từng scenario/offset/distance |
| results/config_used.yaml | Cấu hình thực sự dùng |
| results/run_log.txt | Lệnh, commit/working tree, seed, phiên bản và runtime |
| plots/timeline.png | Timestamp báo và thời điểm đo thật |
| plots/error_vs_offset.png | Ba phương án theo offset |
| plots/alignment_turn.png | Một mẫu rẽ: vị trí đúng và các dự đoán |

CSV/log/plot đang có thuộc phiên bản cũ có lỗi, không dùng cho kết luận cuối. Sau khi sửa, TV5 tạo lại bằng chứng; TV1 thêm bảng thật, plot chính và commit/lệnh tương ứng vào README.

## Failure, decision và limitation

Chọn failure từ CSV đã kiểm tra cùng baseline; kiểm chứng CTRV so với linear trên cùng dữ liệu. Fallback association/tracking là đề xuất thử tiếp, chưa triển khai.

Limitation: mô phỏng 2D, mẫu độc lập, biết đúng offset/trạng thái, chưa có scan distortion, detector/association/latency end-to-end. Kết quả nguồn và kết quả nhóm ghi riêng.

TV1 tài liệu/tích hợp; TV2 nguồn; TV3 mô phỏng; TV4 bù/failure; TV5 runner/metric/plot. Mỗi báo cáo theo Problem → Method → Benchmark → Failure case → Engineering decision; mỗi người tự nộp VLearn. Pitch nhóm 3–5 phút.
