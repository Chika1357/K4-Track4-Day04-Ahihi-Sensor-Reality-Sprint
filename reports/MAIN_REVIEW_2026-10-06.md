# Kiểm tra main 06/10/2026 - nhóm Ahihi

Main: `823da210463fb82ba1ef190c75bdbe2fbfd91892`. Đã tích hợp vào thanh_dev và giải quyết conflict TEAMMATES bằng cách giữ tên nhóm Ahihi, thông tin TV1 và thông tin mới của TV2. Kiểm tra code trong source archive riêng; không ghi đè CSV/log/plot nhóm đã lưu.

**Kết luận: phần demo cốt lõi đã đạt yêu cầu chạy được; bộ bàn giao đã đủ file nhưng chưa nên coi là bản nộp cuối.**

## Đã xác nhận

| Mục | Kết quả kiểm tra |
|---|---|
| Benchmark chính | 45 điều kiện, 4.500 mẫu; mean/max khớp samples; số khớp CSV đã commit |
| Baseline | Offset 0: ba phương án trùng nhau; formula_dev_pct trống |
| Plot | Sinh được timeline, error_vs_offset và alignment_turn |
| TV2 ước lượng offset | Wrapper API mới chạy được 28 trường hợp; CSV tái hiện khớp bản lưu |
| Ước lượng khi chuyển động | A/B mean 0,571429 ms, max 2 ms; C mean 0,714286 ms, max 3 ms |
| Khi đứng yên D | Đánh dấu observable=False; giá trị 0 ms trả về không phải ước lượng đáng tin cậy |
| Thông tin/báo cáo | Đủ thông tin 5 thành viên và 5 PDF cá nhân trong reports/ |
| Log revision | Core ở revision 979355a trong log mới khớp main hiện tại |

Môi trường kiểm tra: Python 3.11.9; NumPy 1.26.4; pandas 2.2.3; matplotlib 3.10.1; PyYAML 6.0.2. Command, thời gian chạy và hash bằng chứng: [MAIN_REVIEW_2026-10-06.json](MAIN_REVIEW_2026-10-06.json). Không kiểm chứng lại KITTI trên dữ liệu thật vì input sequence chưa có trong repo.

## Các mục còn mở

| Mức ưu tiên / owner | Phát hiện | Việc cần làm |
|---|---|---|
| Trước số cuối / TV3 | Seed trong simulate.py vẫn chứa offset; vector noise giữa offset khác nhau | Sửa theo CHOT, giữ cùng vector noise ở cùng frame; TV5 chạy lại |
| Trước số cuối / TV5 | Chưa có exceed_rate cho ba phương án; formula_dev_pct của B khác định nghĩa chốt, chênh tối đa khoảng 0,223 điểm phần trăm | Thống nhất công thức và thêm cột từ samples; không nhầm over_threshold với tỷ lệ lỗi |
| Trước nộp / TV5 | TV5_SLIDE4 có một số số liệu cũ so với CSV | Cập nhật bảng theo khóa scenario/d/offset và làm tròn thống nhất |
| Trước nộp / TV3, TV4, TV5 | PDF đã có đủ năm mục nhưng còn Decision dùng ngưỡng 30 ms/0,2 rad/s như quy tắc được xác nhận; thiếu chi tiết nguồn và limitation | Gắn nhãn đề xuất chưa kiểm chứng hoặc bỏ; thêm paper/link, commit/config và giới hạn phép thử |
| Hoàn thiện / TV4, TV5 | Epsilon config 1e-8 nhưng code 1e-6; log chưa có dirty flag/runtime/seed tổ hợp | Thống nhất nguồn cấu hình và bổ sung metadata lần chạy cuối |
| Trước trình bày / cả nhóm | Chưa có bằng chứng tập pitch hoặc nộp VLearn | Ghép slide cuối, tập 3–5 phút; mỗi người kiểm tra bài nộp riêng |

Ví dụ các số cũ trên TV5_SLIDE4:

| Điều kiện | Slide hiện tại: pre / linear / CTRV (m) | CSV đúng: pre / linear / CTRV (m) |
|---|---|---|
| B/d20/100 ms | 2.505 / 0.041 / 0.041 | 2.530 / 0.028 / 0.028 |
| C/d40/50 ms | 0.828 / 0.678 / 0.025 | 0.832 / 0.670 / 0.024 |
| C/d40/200 ms | 3.348 / 2.693 / 0.025 | 3.336 / 2.735 / 0.025 |

## Báo cáo TV1

PDF TV1 mới nhận từ main còn thiếu tên nhóm và chứa quy tắc fallback chưa kiểm chứng. TV1 cập nhật lại PDF theo nội dung TV1_REPORT: tên/MSSV/nhóm đúng, có nguồn và thông tin tái hiện, baseline cùng failure, hạn chế và Decision theo số đo. PDF được render để kiểm tra chữ/bảng trước bàn giao. Nội dung đầy đủ: [TV1_REPORT.md](TV1_REPORT.md).

Nội dung/code của TV2–TV5 không được sửa thay trong lượt review này. Các đầu việc và tiêu chí nghiệm thu nằm tại [TV1_HANDOFF.md](TV1_HANDOFF.md).
