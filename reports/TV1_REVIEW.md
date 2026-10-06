# TV1 — Bằng chứng đối chiếu benchmark hiện tại

Đây là bản kiểm tra ngày 05/10/2026. Kiểm tra main mới ngày 06/10/2026 tại [MAIN_REVIEW_2026-10-06](MAIN_REVIEW_2026-10-06.md); wrapper TV2 và log revision đã được cập nhật sau bản này.

Code được đối chiếu: `107510809f3d8bb988eb53b76310a72603593226`. TV1 chạy trong bản sao tạm từ source archive của commit này, dùng cùng giá trị config; không ghi đè CSV/log/plot đã lưu trong repository. Đây là lần kiểm tra của TV1, tách biệt với run log TV5.

## Phạm vi kiểm tra

- Toàn bộ A/B/C: 45 điều kiện, 4.500 mẫu; số trong results.csv khớp bản lưu ở độ chính xác 6 chữ số thập phân.
- Tính lại mean/max từ samples.csv; chênh do làm tròn dưới 1,1e-6 m.
- Baseline 0 ms: ba phương án cho cùng kết quả; formula_dev_pct trống.
- Lệnh tối thiểu `--scenarios A C`: 30 điều kiện, 3.000 mẫu.
- Plot timeline, error_vs_offset và alignment_turn sinh được ở cả đường chạy đầy đủ/tối thiểu.
- Bảng số mới của README/TV1_REPORT/TV1_HANDOFF/GROUP_PITCH được đối chiếu với CSV; liên kết file Markdown được kiểm tra.

Kết quả chi tiết, command/runtime của lần kiểm tra và SHA-256 bằng chứng workspace: [TV1_REVIEW.json](TV1_REVIEW.json).

## Môi trường và provenance

Python 3.11.9; NumPy 1.26.4; pandas 2.2.3; matplotlib 3.10.1; PyYAML 6.0.2. Requirements mới chốt các phiên bản thư viện này. Kiểm tra sử dụng môi trường đã có, chưa xác nhận cài dependencies từ đầu trong venv trống.

Source archive không có `.git`; run log sinh trong bản sao không tự đọc được revision. Commit archive được ghi riêng trong manifest TV1. Không dùng log bản sao để giả định nó là working tree Git sạch. Thay đổi tài liệu/config comment trên nhánh TV1 không đổi giá trị tham số benchmark.

Log TV5 đã commit ghi revision `0fb1450cf5db15bbd55f802458487689bfd76d5f`, Python 3.13.9/NumPy 2.4.6/pandas 3.0.3. Metadata đó khác source hiện tại và requirements đã chốt; chưa có trạng thái working tree nên không đủ xác nhận source nào thực sự chạy khi tạo log. TV1 đối chiếu được số bằng source 1075108, nhưng không viết lại lịch sử log TV5. Vòng chạy cuối cần TV5 tạo log đầy đủ từ đúng source/config/environment.

## Giới hạn chưa đóng

Noise giữa offset còn khác; thiếu exceed_rate theo phương án; formula_dev_pct của B khác công thức chốt; wrapper TV2 lỗi API; một số slide/báo cáo TV5 còn cũ. Chi tiết, owner và tiêu chí nghiệm thu: [TV1_HANDOFF](TV1_HANDOFF.md). Không coi việc tái hiện được CSV là đã hoàn tất các mục đối chứng hoặc nộp bài.
