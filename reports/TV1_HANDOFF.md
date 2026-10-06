# TV1 — Chốt bàn giao và nghiệm thu T4

Cập nhật 05/10/2026, code benchmark đã kiểm tra: `107510809f3d8bb988eb53b76310a72603593226`. Nhánh TV1: `thanh_dev`, tích hợp qua PR vào `main`. Đây là bảng điều phối hiện tại; review code cũ được giữ tại CODE_REVIEW_T4.md để truy vết.

## 1. Phần đã xác nhận

- [x] Đường chạy module với `--config config_chot.yaml`; đủ A/B/C, 45 điều kiện/4.500 mẫu.
- [x] Tọa độ, dấu offset, quỹ đạo C và phép bù đã được kiểm tra; GT chỉ sinh dữ liệu/chấm điểm.
- [x] Ba phương án dùng cùng mẫu trong từng tổ hợp; baseline 0 ms cho cùng kết quả.
- [x] CSV tổng hợp chạy lại khớp số bản lưu, có samples/config/log/plot.
- [x] Chọn failure C/d40/100 ms cùng baseline C/d40/0 ms.
- [x] TV1 cập nhật README/Quickstart/đặc tả/giao diện thực tế, bảng nhánh và requirements theo môi trường đã đối chiếu.
- [x] TV1 viết báo cáo đủ năm mục và nội dung pitch chung 6 slide, tách quan sát/nguồn/suy luận.

## 2. Các việc cần giao trước bản kết quả cuối

| Owner | Việc và lý do | Điều kiện nghiệm thu |
|---|---|---|
| TV3 | Seed hiện có offset nên noise thay đổi giữa điều kiện. Chuyển sang `42 + 100*scenario_id + distance_id` theo CHOT; giữ thứ tự noise | Cùng scenario/d/frame có cùng vector noise ở cả 5 offset; lưu seed thực tế |
| TV5 | Chạy lại sau sửa seed; thêm exceed_rate từng phương án và thống nhất formula_dev_pct theo CHOT | Có 45 hàng/4.500 mẫu; mean/max/exceed_rate từ cùng samples; baseline formula_dev_pct trống |
| TV5 | Ghi command đầy đủ, commit, working-tree sạch/bẩn, runtime, thư viện và seed thực tế | Run log gắn với chính source/config đã dùng; phân biệt seed gốc và seed tổ hợp |
| TV5 | Đồng bộ TV5_SLIDE4.md/TV5_REPORT.md/PDF với CSV cuối; một số giá trị B/C đang cũ | Đối chiếu tất cả số theo khóa scenario/d/offset, ghi đơn vị và baseline |
| TV4 + TV5 | Config epsilon là 1e-8, code dùng 1e-6. Chốt một nguồn cấu hình nếu duy trì tham số này | Đặc tả/config/code nhất quán; không thay đổi tùy ý giữa điều kiện |
| TV2 | Sửa run_estimate_on_sim.py: API mới cần cfg, trả DataFrame và không có sim.pose/ObjectTrajectorySimulator | Wrapper chạy lại được với đúng API và ghi simulator/version; hoặc loại wrapper khỏi phạm vi pitch |
| TV2 | Rà nguồn/slide: giới hạn Bảng IV của Park, bỏ suy luận target ⇒ offline; diễn giải KITTI là OXTS thật + điểm ảo/offset nhân tạo | Không dùng số paper làm số tự đo; không gọi chênh timestamp là lỗi clock đã chứng minh; mọi claim có nguồn/phạm vi |
| TV4 + TV5 | Báo cáo hiện có quy tắc fallback 30 ms/0,2 rad/s chưa được thử | Xóa hoặc ghi là giả thuyết cần validation; thống nhất với Decision của TV1 |
| TV1 + TV2 | TV1 đã điền Nguyễn Tuấn Thành — 2A202602640; còn thông tin TV2 và tên nhóm chính thức | TEAMMATES và báo cáo không còn ô thông tin cần xác nhận |
| Cả nhóm | Mỗi người viết đủ năm mục và tập pitch | Đủ 5 bản; mỗi người tự nộp VLearn; trình bày 3–5 phút, mở được CSV/log/plot |

Đây là đầu việc để TV1 trao đổi với nhóm; chưa gửi bình luận GitHub hoặc tin nhắn cho thành viên.

## 3. Bảng failure hiện tại để ghép báo cáo

Nguồn: results/results.csv tại code 1075108. Các số cần thay đồng thời sau chạy lại seed.

| C, d=40 m | Trước bù mean/max (m) | Linear mean/max (m) | CTRV mean/max (m) |
|---|---:|---:|---:|
| Baseline 0 ms | 0.025566 / 0.063677 | 0.025566 / 0.063677 | 0.025566 / 0.063677 |
| Offset 100 ms | 1.667546 / 1.716666 | 1.350500 / 1.385999 | 0.024821 / 0.056044 |

Quan sát: CTRV gần nhiễu trong chuyển động rẽ đều và offset/trạng thái biết đúng. Suy luận: linear có thể gây association sai, nhưng nhóm chưa chạy bbox/tracker. Ngưỡng 0,5 m chỉ minh họa, không kết luận an toàn.

## 4. Thứ tự đóng việc

1. TV3 sửa seed; TV4/TV5 thống nhất epsilon, TV5 đóng metric/log.
2. Chạy baseline rồi toàn bộ; lưu config/source/versions và CSV/log/plot cùng lần chạy.
3. TV1 kiểm tra mean/max từ samples, baseline và failure; cập nhật README, TV1_REPORT và GROUP_PITCH cùng số mới. TV5 cập nhật báo cáo/slide/PDF của mình.
4. TV2 quyết định phần mở rộng nào tái hiện được. Benchmark chính giả định offset biết đúng; không phụ thuộc kết quả wrapper.
5. TV1 ghép bản trình bày, kiểm tra đủ 5 báo cáo; cả nhóm tập và tự nộp.

## 5. Chia pitch

Nội dung và lời nói: [GROUP_PITCH](GROUP_PITCH.md). TV1 mở 35 s và kết 35 s; TV2 Method 45 s; TV3 Setup 40 s; TV5 Benchmark 55 s; TV4 Failure 45 s. Tổng 255 s, khoảng 4 phút 15 giây, còn thời gian chuyển phần. Không coi nội dung Markdown này là bằng chứng đã tập hoặc đã nộp slide.
