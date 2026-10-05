# Việc TV1 cần làm — bàn giao và nghiệm thu

## Phần đã chuẩn bị

- Thiết kế đối chứng, công thức, giả định và giao diện TV3/TV4/TV5.
- Checklist trách nhiệm, config mục tiêu, README/Quickstart phân biệt hai phiên bản.
- Review lỗi code, nguồn khởi đầu và khung báo cáo riêng.
- Nhánh TV1: thanh_dev; nhánh tích hợp: main. Code của đồng đội được giữ trong nhánh tích hợp; owner sửa theo review.

## Việc làm ngay

1. Điền tên nhóm và họ tên/MSSV bốn người còn thiếu trong TEAMMATES; thông tin TV3 được giữ từ main.
2. Xác nhận mỗi owner biết file mình sửa và nhánh thực tế đang làm; cập nhật TEAMMATES.
3. Bàn giao R1–R8 trong CODE_REVIEW_T4.md, thống nhất config_chot.yaml và mục 8 bản chốt.
4. TV3/TV4 giao một batch mẫu và output hai hàm bù cho TV5 trước khi ghép toàn bộ.
5. Thu phiếu đọc nguồn từ TV2: input/output, dataset/metric, limitation và link/version đúng. Kiểm tra yêu cầu “nguồn mới” nếu lớp có mốc năm.
6. Merge tài liệu TV1 để nhóm dùng cùng đặc tả. Ghi trạng thái code đang cần sửa; kết quả CSV/plot cũ chưa nghiệm thu.

## Nghiệm thu sau khi sửa code

- [ ] Runner hỗ trợ lệnh module --config config_chot.yaml và --scenarios A C.
- [ ] Dữ liệu 100 mẫu/tổ hợp, cùng frame/object/noise giữa các offset.
- [ ] Phương án bù không dùng P_gt hoặc pose thật tại t_true.
- [ ] Offset 0: ba phương án cho cùng kết quả, gần mức nhiễu.
- [ ] Kiểm tra không noise: A/100 ms trước bù 2 m, sau bù gần 0.
- [ ] Quỹ đạo C và trạng thái v/yaw_rate nhất quán; bù CTRV gần mức nhiễu trong giả định đã đặt.
- [ ] B nếu chạy: dùng v_ref từng mẫu và ghi giới hạn vận tốc không đổi.
- [ ] CSV có mean/max/exceed_rate, baseline formula deviation N/A.
- [ ] Có samples.csv, config_used.yaml, log command/commit/working tree/seed/version/runtime.
- [ ] Plot có ba phương án, đơn vị, baseline/mức lỗi, chú thích dữ liệu tổng hợp.
- [ ] Tự chạy lại từ cùng commit/config và đối chiếu số.
- [ ] README ghi số thật và trạng thái đã chạy, không giữ kết quả lỗi như benchmark cuối.

## Chốt failure và engineering decision

- Chọn một hàng C có sai số linear rõ, cùng baseline và kết quả CTRV.
- Ghi scenario/d/offset, mean/max/exceed_rate, đường dẫn bằng chứng.
- “Nhóm quan sát được…” chỉ cho số đã đo; “Nguồn cho biết…” có link; tác động tới association là suy luận nếu chưa chạy pipeline thật.
- Ngưỡng 0,5 m là minh họa do nhóm đặt, chưa phải chuẩn an toàn.
- Quyết định nối với metric; fallback tracking và đồng bộ phần cứng cần nguồn hoặc phép thử tiếp, chưa tuyên bố hiệu quả.
- Biết đúng offset/trạng thái là giả định quan trọng; chưa chứng minh mức cải thiện trên ADAS thật.

## Slide và báo cáo của bạn

| Slide | Owner | Nội dung | Thời lượng |
|---|---|---|---:|
| 1 Problem | TV1 | ADAS, lỗi timestamp, phạm vi, claim | 40 s |
| 2 Method | TV2 | Nguồn, input/output, khác biệt mô phỏng | 50 s |
| 3 Setup | TV3 | Dữ liệu, offset, noise, giả định | 50 s |
| 4 Benchmark | TV5 | Bảng thật/plot, baseline và lỗi | 60 s |
| 5 Failure | TV4 | Linear/CTRV, giải thích và limitation | 50 s |
| 6 Decision | TV1 | Quyết định theo số đo, trade-off, thử tiếp | 30 s |

Tổng 280 s, còn 20 s chuyển phần. TV1 chuẩn bị slide 1/6 và ghép phần của cả nhóm. Điền TV1_REPORT_TEMPLATE.md rồi xuất theo định dạng lớp yêu cầu; chưa có kết quả thì giữ ô chờ điền. Kiểm tra đủ 5 bản và mỗi người tự nộp VLearn.
