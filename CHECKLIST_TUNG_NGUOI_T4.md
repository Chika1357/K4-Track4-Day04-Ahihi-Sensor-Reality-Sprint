# Checklist bàn giao cuối — Lab T4

Code kiểm tra: 1075108, ngày 05/10/2026. `[x]` chỉ việc đã kiểm tra/đã có artifact; quyền truy cập, trình bày và nộp bài cần từng người xác nhận. Chi tiết lỗi: [TV1_HANDOFF](reports/TV1_HANDOFF.md).

## TV1 — Thiết kế, tích hợp, báo cáo và Decision

- [x] Chốt ADAS, camera–LiDAR, offset dương, hệ tọa độ, dữ liệu tổng hợp và metric vị trí.
- [x] Cập nhật đặc tả theo API thực tế; giữ yêu cầu cùng nhiễu giữa offset.
- [x] Kiểm tra benchmark chính 45 điều kiện/4.500 mẫu và chọn failure cùng baseline.
- [x] Cập nhật README/Quickstart/requirements/bảng nhánh hiện có.
- [x] Viết [TV1_REPORT](reports/TV1_REPORT.md) đủ năm mục; quyết định có giới hạn và vòng thử tiếp.
- [x] Ghép [GROUP_PITCH](reports/GROUP_PITCH.md), gồm phần mở/kết TV1 và lời nói chung.
- [x] Ghi đầu việc TV2–TV5, không đánh dấu lỗi còn mở thành hoàn thành.
- [ ] Điền họ tên/MSSV TV1 và tên nhóm; nhận thông tin TV2.
- [ ] Nghiệm thu chạy lại sau sửa seed/metric/log; thay số cùng lúc ở tài liệu TV1.
- [ ] Nhận đủ 5 báo cáo, ghép slide theo định dạng trình bày của lớp, tập pitch và tự nộp VLearn.

## TV2 — Nguồn, Method và mở rộng ước lượng offset

- [x] Có reports/sources.md và code demo độc lập estimate_offset.py.
- [ ] Sửa wrapper run_estimate_on_sim.py cho API hiện tại, hoặc bỏ wrapper khỏi bằng chứng tái hiện.
- [ ] Rà phạm vi số paper, nguồn chính xác, input/output/metric/limitation; không suy từ target sang bắt buộc offline.
- [ ] Nếu trình bày KITTI: ghi rõ chuyển động OXTS thật, điểm ảo, offset nhân tạo và khác biệt điều kiện so sánh.
- [ ] Ghi phiên bản/dữ liệu/lệnh thực sự dùng cho phần mở rộng.
- [ ] Điền thông tin cá nhân, hoàn thiện Method và báo cáo riêng; tập pitch và tự nộp.

## TV3 — Mô phỏng

- [x] A/B/C, mốc t_ref, dấu offset, đặt vật thể tại t_ref và quỹ đạo C đã đúng.
- [x] Hàm run_simulation(scenario, offset_ms, distance_m, cfg) trả DataFrame đúng API hiện tại.
- [ ] Sửa seed độc lập offset, giữ cùng vector noise giữa các offset; lưu seed thực tế.
- [ ] Đối chiếu noise bằng cách trừ phép đo không nhiễu theo từng frame, không chỉ so e_pre.
- [ ] Slide Setup ghi mẫu độc lập, điểm 2D, state/offset biết đúng; báo cáo riêng, tập pitch và tự nộp.

## TV4 — Bù, Failure và cải tiến

- [x] Linear/CTRV đúng chiều; chỉ dùng phép đo và trạng thái hiện tại/offset, không dùng GT để bù.
- [x] Baseline không đổi; CTRV đạt gần mức nhiễu cho C trong giả định đã đặt.
- [ ] Thống nhất epsilon giữa config/code với TV5.
- [ ] Chốt Failure bằng CSV cuối; ghi association sai là suy luận chưa đo.
- [ ] Không tuyên bố fallback/ngưỡng kích hoạt đã kiểm chứng; viết báo cáo riêng, tập pitch và tự nộp.

## TV5 — Runner, metric, log, plot và số liệu

- [x] Có CLI module --config/--scenarios, CSV 45 hàng/4.500 mẫu và các plot yêu cầu.
- [x] Mean/max hiện tại khớp samples; baseline formula_dev_pct trống.
- [ ] Chạy lại sau sửa seed; thêm noise_seed và exceed_rate cho cả ba phương án.
- [ ] Thống nhất formula_dev_pct theo CHOT, đặc biệt B có vận tốc thay đổi.
- [ ] Log đầy đủ source/working tree/runtime/versions/seed thực tế; dùng môi trường đã chốt hoặc ghi và kiểm chứng môi trường khác.
- [ ] Cập nhật toàn bộ số trên TV5_SLIDE4/TV5_REPORT/PDF và bỏ fallback chưa kiểm chứng.
- [ ] Bàn giao CSV/log/plot cùng lần chạy, báo cáo riêng, tập pitch và tự nộp.

## Cổng hoàn thành lab

- [x] Demo chạy được với baseline và điều kiện lỗi, có số và bằng chứng.
- [x] Có failure thật trong phạm vi mô phỏng và một cải tiến đã so sánh (CTRV).
- [ ] Đóng các điểm đối chứng/metric/log trong handoff; số các tài liệu thống nhất.
- [ ] Đủ thông tin 5 người và báo cáo riêng; cả nhóm pitch 3–5 phút.
- [ ] Mỗi người tự kiểm tra bài nộp VLearn. Không có bằng chứng nộp trong repository thì không đánh dấu đã nộp.
