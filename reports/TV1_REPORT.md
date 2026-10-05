# Báo cáo TV1 — T4: Lệch thời gian và sai số căn chỉnh vị trí

- Họ tên/MSSV: chờ TV1 cung cấp.
- Tên nhóm: chờ tên chính thức; nhóm có đúng 5 thành viên.
- Vai trò: chốt thiết kế, điều phối tích hợp, kiểm tra bằng chứng, Problem và Engineering decision.
- Repository: https://github.com/Chika1357/K4-Track4-Day04-Ahihi-Sensor-Reality-Sprint
- Code benchmark đã đối chiếu: `107510809f3d8bb988eb53b76310a72603593226`.
- Phạm vi số dưới đây: bản hiện tại đã chạy lại, chưa phải bộ số cuối sau sửa đối chứng seed. Trạng thái bàn giao: [TV1_HANDOFF](TV1_HANDOFF.md).

## 1. Problem

Trong ADAS, LiDAR đo tại t_capture=t_ref−Δt nhưng dữ liệu được căn chỉnh bằng pose ego tại mốc camera t_ref. Khi ego chuyển động, sử dụng sai thời điểm tạo sai số vị trí ngay cả khi phép đo sensor vẫn hợp lệ. Nhóm kiểm tra riêng ảnh hưởng timestamp bằng mô phỏng 2D, không chạy ảnh, detector hay fusion bbox thực tế.

Claim ban đầu: khi chạy thẳng đều, tăng Δt làm sai số trước bù tăng gần vΔt. Bù tịnh tiến giảm lỗi này; khi rẽ, cần xét cả quay để tránh sai số còn lại. Metric chính là mean/max khoảng cách Euclidean tới vị trí chuẩn, đơn vị mét, nhỏ hơn tốt hơn.

## 2. Method

Nguồn chính: [Park và cộng sự, Spatiotemporal Camera-LiDAR Calibration, RA-L 2020, arXiv v1](https://arxiv.org/abs/2001.06175v1). Paper nhận quỹ đạo LiDAR/camera và đặc trưng ảnh, ước lượng extrinsic cùng time lag qua khởi tạo thô rồi tối ưu sai số chiếu. Paper nêu time lag không quan sát được khi đứng yên; chất lượng chuyển động/odometry giới hạn hiệu chuẩn. Đây là kết luận của nguồn, không phải số nhóm tự đo.

Nhóm chọn đường chạy tối thiểu: mô phỏng chuyển động và bù với **offset biết đúng**, không tái hiện tối ưu 3D của paper. Input gồm điểm LiDAR trong ego tại lúc đo, pose/vận tốc/yaw rate hiện tại và Δt. Output là vị trí world trước bù, sau linear và sau CTRV. Linear trừ v_refΔt dọc trục trước; CTRV bù cung chuyển động rồi quay về ego tại t_ref. Ground truth và pose thật quá khứ chỉ sinh dữ liệu/chấm điểm, không đưa vào hàm bù.

Phần TV2 ước lượng offset/KITTI là mở rộng, không dùng làm bằng chứng cho số chính trong báo cáo này. Wrapper ước lượng offset tích hợp đang cần sửa API. [sources.md](sources.md) do TV2 quản lý; không so trực tiếp số time lag của paper với sai số vị trí của nhóm.

## 3. Benchmark

Dữ liệu tổng hợp: A chạy thẳng 20 m/s; B từ 10 m/s với a=3 m/s²; C chạy 10 m/s, R=30 m, ω=1/3 rad/s. Offset 0/50/100/150/200 ms, d=10/20/40 m; 100 mẫu độc lập/tổ hợp, tổng 45 điều kiện/4.500 mẫu. t_ref=0,2+i/10 s. Mỗi mẫu đặt vật thể đứng yên d mét phía trước ego tại t_ref rồi tính phép đo ở t_capture. Nhiễu Gauss σ=0,02 m/trục, seed gốc 42.

Ba phương án dùng cùng mẫu trong mỗi tổ hợp. Code hiện đổi seed theo offset, nên đối chứng giữa offset chưa giữ nguyên mẫu nhiễu như thiết kế; cần sửa rồi chạy lại. Bảng dưới ghi đúng số hiện tại, không khẳng định đã đóng điểm này.

| Điều kiện | Trước bù mean/max (m) | Linear mean/max (m) | CTRV mean/max (m) |
|---|---:|---:|---:|
| A, d20, 0 ms | 0.023686 / 0.062031 | 0.023686 / 0.062031 | 0.023686 / 0.062031 |
| A, d20, 100 ms | 2.001101 / 2.071137 | 0.025580 / 0.072192 | 0.025580 / 0.072192 |
| C, d40, 0 ms | 0.025566 / 0.063677 | 0.025566 / 0.063677 | 0.025566 / 0.063677 |
| C, d40, 100 ms | 1.667546 / 1.716666 | 1.350500 / 1.385999 | 0.024821 / 0.056044 |

**Nhóm quan sát được:** A/100 ms trước bù gần 20×0,1=2 m, linear đưa sai số về gần nhiễu. C/100 ms còn lỗi rõ sau linear; CTRV gần nhiễu trên cùng mẫu. Baseline ba phương án trùng nhau. Không trích số định lượng của paper làm kết quả nhóm.

Lệnh từ thư mục gốc:

~~~powershell
python -m src.run_benchmark --config config_chot.yaml
python -m src.plot --config config_chot.yaml
~~~

Cấu hình: [config_chot.yaml](../config_chot.yaml), bản lưu lần chạy: [config_used.yaml](../results/config_used.yaml). Bằng chứng: [results.csv](../results/results.csv), [samples.csv](../results/samples.csv), [run_log.txt](../results/run_log.txt), [error_vs_offset.png](../plots/error_vs_offset.png), [alignment_turn.png](../plots/alignment_turn.png). Môi trường TV1 đối chiếu: Python 3.11.9, NumPy 1.26.4, pandas 2.2.3, matplotlib 3.10.1, PyYAML 6.0.2; hash và giới hạn provenance tại [TV1_REVIEW](TV1_REVIEW.md).

## 4. Failure case

Failure chọn: C, d=40 m, Δt=100 ms. Linear có mean 1,350500 m và max 1,385999 m, so với baseline mean 0,025566 m. Linear bỏ qua thay đổi hướng ego nên dịch chuyển dọc trục trước chưa đủ. Xấp xỉ thành phần quay ở góc nhỏ d|ω|Δt≈1,333 m giúp giải thích độ lớn; đây không phải công thức tổng sai số chính xác.

Mean linear vượt ngưỡng **minh họa** 0,5 m do nhóm đặt. CTRV có mean 0,024821 m, max 0,056044 m. Chưa xuất exceed_rate từng phương án; không gọi over_threshold là tỷ lệ lỗi. Điểm lệch có thể gây association sai với bbox là suy luận kỹ thuật, chưa được đo bằng detector/tracker.

Giới hạn: dữ liệu 2D tổng hợp; vật thể chỉ tĩnh trong từng phép thử; biết đúng offset/trạng thái; A/C khớp giả định mô hình bù. Chưa đo offset/vận tốc/yaw rate không chính xác, vật thể chuyển động, scan distortion, calibration drift, mAP hay latency đầu-cuối. Nhiễu giữa offset cần đồng nhất; log TV5 cũ ghi commit/môi trường khác nên không đủ chứng minh working tree đã sạch khi chạy.

## 5. Engineering decision

Từ số đo hiện tại, chọn **CTRV cho trường hợp rẽ trong mô hình này**, với điều kiện có offset và trạng thái đủ tin cậy. Khi chuyển động thẳng đều, linear đã gần nhiễu; CTRV cũng có giả định vận tốc/yaw rate không đổi nên chưa được coi là lời giải cho mọi chuyển động. Chi phí tính toán và lợi ích trên hệ ADAS thật chưa được đo.

Vòng thử tiếp ưu tiên sửa đối chứng seed và chạy lại, sau đó thêm lỗi ước lượng offset/vận tốc/yaw rate và gia tốc. Giữ cùng dữ liệu/nhiễu, đo mean/max, exceed_rate=mean(e>0,5 m) theo từng phương án và runtime. Log phải gắn source/config/versions/seed thực tế. Đây là phép thử để xác định miền áp dụng CTRV và ngưỡng cảnh báo, không suy ngưỡng từ một hàng failure.

Khi không đủ tin cậy về thời gian/trạng thái, đề xuất đánh dấu dữ liệu chưa căn chỉnh và hạn chế association cứng tới khi kiểm tra lại. Fallback này chưa triển khai/đo; chưa chốt quy tắc 30 ms/0,2 rad/s hoặc chọn PTP/shared trigger từ benchmark. Trước áp dụng thật cần kiểm tra giao diện sensor và đo đồng bộ/latency trên phần cứng thực tế.

Phần nội dung TV1 đã hoàn thiện; thông tin cá nhân và số sau nghiệm thu cuối cần cập nhật trước nộp. Mỗi người tự nộp bản riêng trên VLearn.
