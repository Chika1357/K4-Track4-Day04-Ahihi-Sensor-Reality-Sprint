# T4 — Lệch timestamp và bù chuyển động trong ADAS

Nhóm đo sai số căn chỉnh vị trí khi LiDAR đo tại `t_capture = t_ref − Δt` nhưng phép biến đổi dùng pose tại `t_ref`. Dữ liệu tổng hợp 2D mô phỏng một rủi ro của camera–LiDAR; camera là mốc thời gian, không có ảnh/bbox hay detector trong phép thử.

Nhóm **Ahihi**. Main mới nhất đã kiểm tra: `823da210463fb82ba1ef190c75bdbe2fbfd91892`. Benchmark chính chạy lại **45 điều kiện, 4.500 mẫu**, CSV tổng hợp khớp bản lưu. Wrapper ước lượng offset TV2 chạy được 28 trường hợp; đủ 5 PDF cá nhân đã có trong reports/. Vẫn còn các mục đối chứng và bàn giao cần đóng trước bản nộp cuối; xem [TV1_HANDOFF](reports/TV1_HANDOFF.md).

## Chạy

Môi trường TV1 kiểm tra: Python 3.11.9 và các phiên bản trong `requirements.txt`. Hướng dẫn tạo môi trường: [QUICKSTART](QUICKSTART.md).

~~~powershell
python -m pip install -r requirements.txt
python -m src.run_benchmark --config config_chot.yaml
python -m src.plot --config config_chot.yaml
~~~

Chạy A/C tối thiểu: thêm `--scenarios A C` vào lệnh benchmark. Lệnh ghi đè CSV/log/plot tương ứng. `config.yaml` là cấu hình lịch sử, không dùng với runner mới.

## Đối chứng và metric

- A: chạy thẳng 20 m/s; B: v0=10 m/s, gia tốc 3 m/s²; C: 10 m/s, bán kính rẽ 30 m.
- Offset 0/50/100/150/200 ms; d=10/20/40 m; 100 mẫu độc lập mỗi tổ hợp; nhiễu Gauss σ=0,02 m mỗi trục, seed gốc 42.
- Mỗi mẫu đặt vật thể đứng yên phía trước ego tại `t_ref`, rồi tính phép đo của chính vật thể đó tại `t_capture`. Không phải một vật thể cố định xuyên suốt 100 mẫu.
- Cùng dữ liệu đầu vào cho ba phương án: không bù, tịnh tiến (linear), tịnh tiến + quay với vận tốc/yaw rate không đổi (CTRV). Ground truth chỉ sinh dữ liệu/chấm điểm.
- Sai số Euclidean trong world, mean/max theo mét; nhỏ hơn là tốt hơn. Ngưỡng 0,5 m do nhóm đặt để minh họa.
- Code hiện tại đổi seed theo offset; đối chứng giữa offset chưa giữ cùng mẫu nhiễu như thiết kế. TV3 cần sửa seed, TV5 chạy lại; số dưới đây mô tả bản hiện tại.

## Số đo hiện tại

Nguồn: `results/results.csv`, commit benchmark nêu trên; làm tròn 3 chữ số thập phân.

| Kịch bản | d (m) | Offset (ms) | Trước bù mean (m) | Linear mean (m) | CTRV mean (m) |
|---|---:|---:|---:|---:|---:|
| A | 20 | 0 | 0.024 | 0.024 | 0.024 |
| A | 20 | 100 | 2.001 | 0.026 | 0.026 |
| C | 40 | 0 | 0.026 | 0.026 | 0.026 |
| C | 40 | 100 | 1.668 | 1.351 | 0.025 |

Failure chính: khi rẽ, linear bỏ qua quay nên còn lỗi vị trí. Với C/d40/100 ms, CTRV giảm lỗi trên cùng mẫu. Rủi ro gán nhầm điểm vào bbox là suy luận kỹ thuật; benchmark chưa đo association.

## Quyết định và giới hạn

Trong phạm vi mô phỏng đã đo, chọn CTRV cho trường hợp rẽ khi biết đúng offset, vận tốc và yaw rate. Linear phù hợp với chuyển động thẳng đều; CTRV cũng giả định vận tốc/yaw rate không đổi trong khoảng bù. Chưa đo chi phí tính toán hoặc độ tin cậy của trạng thái/offset thực tế.

Vòng thử tiếp: thêm sai số ước lượng offset/vận tốc/yaw rate và gia tốc; đo lại mean/max, tỷ lệ mẫu vượt 0,5 m và runtime. Đánh dấu dữ liệu chưa căn chỉnh khi thông tin đồng bộ/chuyển động không đủ tin cậy là đề xuất fallback, chưa triển khai hoặc đo hiệu quả. Chưa chốt ngưỡng kích hoạt fallback hay lựa chọn PTP/shared trigger từ phép thử này.

Đây là sai số căn chỉnh đầu vào tổng hợp 2D, chưa đo mAP, tracking, phép chiếu pixel, LiDAR scan distortion hay latency đầu-cuối. Camera 30 Hz/LiDAR 10 Hz minh họa timeline; benchmark đánh giá ở mốc tham chiếu đồng pha và không đo lỗi nearest-frame.

## Bằng chứng và bàn giao

| File | Nội dung |
|---|---|
| `results/results.csv` / `results/samples.csv` | Tổng hợp / từng mẫu, ba phương án |
| `results/config_used.yaml` / `results/run_log.txt` | Cấu hình / log lần chạy TV5 |
| `plots/timeline.png` | Mốc tham chiếu và thời điểm đo cũ |
| `plots/error_vs_offset.png` | Mean theo offset, d=20/40 m |
| `plots/alignment_turn.png` | Nhiều phép thử độc lập C/d40/100 ms |
| [MAIN_REVIEW_2026-10-06](reports/MAIN_REVIEW_2026-10-06.md) | Kiểm tra main mới, số đo, báo cáo và các điểm còn mở |
| [TV1_REPORT](reports/TV1_REPORT.md) | Báo cáo TV1 đủ năm mục |
| [GROUP_PITCH](reports/GROUP_PITCH.md) | Nội dung 6 slide, lời nói và phân chia 3–5 phút |

Nguồn chính: [Park và cộng sự, RA-L 2020, arXiv v1](https://arxiv.org/abs/2001.06175v1). Benchmark nhóm là mô hình giản lược, không chạy thuật toán paper. Chi tiết nguồn do TV2 quản lý tại [sources](reports/sources.md). Ước lượng offset là phần mở rộng độc lập: `python -m src.run_estimate_on_sim --config config_chot.yaml`; benchmark bù chính vẫn dùng offset biết đúng.

Nhóm có đúng 5 thành viên; mỗi người tự viết và nộp báo cáo riêng trên VLearn. [TEAMMATES](TEAMMATES.md) ghi thông tin và nhánh, [CHECKLIST](CHECKLIST_TUNG_NGUOI_T4.md) ghi phần việc còn lại.
