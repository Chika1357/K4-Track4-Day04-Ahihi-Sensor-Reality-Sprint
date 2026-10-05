# CHỐT LAB T4 — Sai số căn chỉnh vị trí do lệch timestamp

Trạng thái ngày 05/10/2026: benchmark chính tại commit 1075108 đã chạy lại đủ 45 điều kiện/4.500 mẫu; ghép thời điểm, chiều bù và quỹ đạo tròn đã được sửa. Số đo hiện tại dùng được trong phạm vi mô phỏng, nhưng chưa đóng đối chứng nhiễu giữa offset và toàn bộ bàn giao. Xem reports/TV1_HANDOFF.md cho trạng thái mới; reports/CODE_REVIEW_T4.md là review lịch sử. Phần dưới chốt thiết kế và nêu riêng các khác biệt code còn cần sửa.

## 1. Problem và phạm vi

- Nền tảng ADAS; ứng dụng liên quan là căn chỉnh vị trí camera–LiDAR.
- Mô phỏng vị trí vật thể đứng yên trong world khi ego chuyển động, bằng Python và dữ liệu tổng hợp 2D.
- Camera là mốc thời gian tham chiếu; LiDAR cung cấp phép đo cũ nhưng gắn timestamp mới.
- Chưa chạy ảnh, point cloud, bbox, detector/tracker hay phép chiếu pixel. Sai số vị trí theo mét chưa chứng minh chất lượng toàn pipeline fusion.
- Camera 30 Hz và LiDAR 10 Hz dùng minh họa timeline. Phép thử chính đánh giá tại mốc LiDAR báo, cũng thuộc lưới camera đồng pha; không thêm lỗi nearest-frame, queue latency hay rolling shutter.

## 2. Claim trước khi chạy

> Khi chạy thẳng đều, sai số trước bù tăng xấp xỉ v × Δt. Bù tịnh tiến dự kiến giảm sai số về gần mức nhiễu. Khi rẽ, bù tịnh tiến còn sai số do bỏ qua quay; bù tịnh tiến + quay dự kiến giảm sai số đó. Với gia tốc, giả định vận tốc không đổi có thể để lại sai số.

v × Δt là mô hình kiểm tra cho chuyển động thẳng đều. d × |ω| × Δt là xấp xỉ thành phần quay ở góc nhỏ; không cộng vô hướng hai đại lượng này để gọi là sai số tổng chính xác.

## 3. Dữ liệu và đối chứng

| Tham số | Giá trị |
|---|---|
| Offset dương Δt | 0, 50, 100, 150, 200 ms |
| A — chạy thẳng đều | v = 20 m/s, yaw = 0 |
| B — tăng tốc thẳng | v0 = 10 m/s, a = 3 m/s², yaw = 0 |
| C — rẽ đều | v = 10 m/s, bán kính 30 m, ω = v/R = 1/3 rad/s |
| Khoảng cách tại mốc tham chiếu | d = 10, 20, 40 m, phía trước ego |
| Số mẫu mỗi tổ hợp | 100 mẫu, cách nhau 0,1 s |
| Mốc tham chiếu | t_ref[i] = 0,2 + i/10 s, i = 0..99 |
| Nhiễu vị trí LiDAR | Gauss độc lập hai trục, σ = 0,02 m mỗi trục |
| Seed gốc | 42 |

Mỗi mẫu là một phép thử độc lập: đặt một vật thể đứng yên trong world ở phía trước ego tại t_ref, rồi tính phép đo của chính vật thể đó tại t_true. Các mẫu liên tiếp có thể dùng vật thể khác nhau. Không mô tả chúng là một vật thể cố định xuyên suốt 10 giây.

Giữ cùng mốc, quỹ đạo, vật thể và mẫu nhiễu khi so các offset/phương án. scenario_id: A=0, B=1, C=2; distance_id: 10=0, 20=1, 40=2. Seed tổ hợp = 42 + 100*scenario_id + distance_id; không cộng offset vào seed. Dùng numpy.random.default_rng(seed) sinh mảng nhiễu (100, 2) theo cùng thứ tự. Code 1075108 hiện dùng seed phụ thuộc offset; TV3 cần sửa, TV5 chạy lại. Ba phương án trong từng tổ hợp hiện đã dùng cùng mẫu.

Mốc đầu 0,2 s bảo đảm t_true >= 0 với offset tối đa. 100 mẫu thuộc cửa sổ dài 10 s, mẫu cuối ở 10,1 s. Quỹ đạo hỗ trợ toàn bộ thời điểm này.

Ma trận đầy đủ: 3 kịch bản × 5 offset × 3 khoảng cách = 45 tổ hợp, mỗi tổ hợp so ba phương án. Ưu tiên hoàn tất A và C (30 tổ hợp). B là mở rộng nếu còn thời gian; báo cáo ghi đúng phần đã chạy.

## 4. Tọa độ, timestamp và quỹ đạo

- World: trục x/y, mét. Ego: x hướng trước, y hướng trái; yaw dương ngược chiều kim đồng hồ, radian.
- R(θ) = [[cosθ, -sinθ], [sinθ, cosθ]]; c(t) là vị trí ego trong world.
- t_report = t_ref; t_true = t_ref - Δt. Công thức dùng Δt bằng giây.
- Vị trí vật thể đúng: P_gt = c_ref + R(yaw_ref) @ [d, 0].
- Phép đo: q = R(yaw_true).T @ (P_gt - c_true) + noise, trong ego tại t_true.
- Không bù: P_pre = c_ref + R(yaw_ref) @ q. Đây là phép biến đổi cố ý dùng pose ở timestamp báo sai.

Ego bắt đầu tại (0, 0), yaw 0, thời điểm 0:

- A: c(t) = [20*t, 0], v(t) = 20.
- B: c(t) = [10*t + 0.5*3*t², 0], v(t) = 10 + 3*t.
- C: c(t) = [30*sin(ω*t), 30*(1-cos(ω*t))], yaw(t) = ω*t, v(t) = 10.

## 5. Phương án bù và thông tin được phép dùng

Hàm bù nhận q, pose tại t_ref, v_ref, yaw_rate_ref và Δt. Nhóm giả định biết đúng offset và trạng thái hiện tại, chưa ước lượng chúng từ sensor.

**P_gt và pose thật tại t_true chỉ dùng sinh dữ liệu/chấm điểm. Hàm bù không được dùng chúng hoặc gia tốc thật.**

### Không bù

P_pre = c_ref + R(yaw_ref) @ q.

### Bù tịnh tiến, bỏ qua quay

c_old_hat = c_ref - R(yaw_ref) @ [v_ref*Δt, 0].

yaw_old_hat = yaw_ref.

P_linear = c_old_hat + R(yaw_old_hat) @ q.

### Bù vận tốc và yaw rate không đổi (CTRV)

Với ω = yaw_rate_ref: nếu |ω| < 1e-8, dùng nhánh tịnh tiến để tránh chia cho 0. Ngược lại:

~~~text
b = [v_ref/ω * sin(ω*Δt), v_ref/ω * (cos(ω*Δt) - 1)]
c_old_hat = c_ref - R(yaw_ref) @ b
yaw_old_hat = yaw_ref - ω*Δt
P_ctrv = c_old_hat + R(yaw_old_hat) @ q
~~~

A và C khớp giả định của CTRV; B có gia tốc nên có thể còn sai số. Phép chạy hiện tại xác nhận A/C sau CTRV gần nhiễu. Không dùng kết quả này để khẳng định CTRV xử lý được mọi chuyển động có gia tốc.

## 6. Metric và ngưỡng

Với từng mẫu/phương án k: e_k[i] = ||P_k[i] - P_gt[i]||₂, mét. Báo cáo mean và max trên cùng 100 mẫu; nhỏ hơn là tốt hơn.

- E_pre: trước bù.
- E_post_linear: sau bù tịnh tiến.
- E_post_ctrv: sau bù tịnh tiến + quay.
- Baseline offset 0 có nhiễu nền; ba phương án phải trùng nhau trong sai số số học. Không yêu cầu baseline bằng 0 khi bật noise.
- Tham chiếu theo mẫu: vdt[i] = v_ref[i]*Δt; lưu vdt_mean_m.
- Định nghĩa đã chốt: formula_dev_pct = 100 * mean(abs(e_pre[i] - vdt[i])) / mean(vdt[i]). Offset 0 ghi N/A (ô trống CSV). Đây là độ lệch khỏi mô hình đơn giản, không phải chất lượng detector; noise cũng ảnh hưởng đại lượng này.
- Runner hiện lấy mean(100 * abs(e_pre[i] - vdt[i]) / vdt[i]); khác định nghĩa chốt khi v thay đổi (B). TV5 cần thống nhất về công thức trên và chạy lại. Báo cáo TV1 lấy mean/max sai số làm metric chính, chưa dùng formula_dev_pct của B để kết luận.

Ngưỡng minh họa 0,5 m do nhóm đặt, chưa phải tiêu chuẩn an toàn. Yêu cầu bổ sung mỗi phương án có exceed_rate = mean(e_k > 0.5), trong [0,1]; runner chưa xuất các cột này. Cột over_threshold hiện chỉ là mean(linear) > 0,5 m. Khi nói vượt ngưỡng theo mean phải chỉ rõ E_mean > 0.5; không dùng lẫn mean, max và exceed_rate.

## 7. Failure case và engineering decision

- Failure đã chọn: C, d=40 m, offset=100 ms; E_pre mean=1,667546 m, linear mean=1,350500 m, CTRV mean=0,024821 m. Baseline cùng C/d40 có mean=0,025566 m cho cả ba phương án.
- Ghi mean/max, plot và log; exceed_rate bổ sung sau TV5 cập nhật. Số trên thuộc bản 1075108, cần cập nhật sau khi sửa seed.
- Cải tiến kiểm chứng trong lab: CTRV; so linear/CTRV trên cùng tổ hợp.
- Quyết định trong phạm vi đã đo: xét quay khi bù bằng CTRV cho trường hợp rẽ nếu biết đúng offset/vận tốc/yaw rate. Kiểm tra timestamp và chất lượng trạng thái trước khi áp dụng ngoài mô phỏng.
- Fallback cho vòng thử tiếp: đánh dấu dữ liệu chưa căn chỉnh khi đồng bộ hoặc ước lượng chuyển động không đủ tin cậy, tránh association cứng cho tới khi kiểm tra lại. Chưa triển khai tracker/fallback hoặc đo hiệu quả của chúng.
- Bỏ quy tắc cố định 30 ms/0,2 rad/s vì chưa có cơ sở xác nhận.
- Trade-off: giả định biết offset, chất lượng vận tốc/yaw rate, giới hạn khi có gia tốc, chi phí tính toán chưa đo. TV2 tìm nguồn cho PTP/trigger và giới hạn tích hợp trước khi dùng làm khuyến nghị.

## 8. Giao diện bàn giao hiện tại

TV3: run_simulation(scenario, offset_ms, distance_m, cfg) -> pandas.DataFrame.

~~~text
frame, t_ref, t_capture, x_true, y_true, x_lidar, y_lidar,
x_ref, y_ref, yaw_ref, v_ref, yaw_rate_ref, x_pre, y_pre, e_pre
~~~

Cột vị trí dùng mét, thời gian dùng giây, yaw dùng radian, yaw_rate_ref dùng rad/s. Trong samples.csv, TV5 thêm scenario/offset_ms/distance_m và dự đoán/sai số. Khóa (scenario, distance_m, frame) phân biệt phép thử độc lập và giữ nguyên giữa offset. noise_seed cần được bổ sung để truy vết; không bắt buộc đổi tên toàn bộ cột. GT chỉ dùng đánh giá, không đưa vào hàm bù.

TV4 cung cấp hai hàm:

~~~text
compensate_linear(q_ego, v_ref, dt_s)
compensate_ctrv(q_ego, v_ref, yaw_rate_ref, dt_s)
~~~

q_ego là NumPy array (2,) hoặc (N,2); v_ref/yaw_rate_ref/dt_s là scalar cho cùng phép biến đổi. Đầu ra giữ shape input, trong ego tại t_ref; runner gọi to_world với pose hiện tại rồi chấm điểm world. Không mutate input. Nhánh yaw rate gần 0 hiện dùng 1e-6 rad/s; config có 1e-8 nhưng chưa được đọc, cần TV4/TV5 thống nhất nếu dùng ngưỡng này ngoài ba kịch bản hiện tại.

TV5 ghi samples.csv gồm cột mô phỏng và x_linear/y_linear/x_ctrv/y_ctrv/e_linear/e_ctrv. results.csv hiện có 45 hàng với schema:

~~~text
scenario, scenario_label, offset_ms, distance_m, samples, v_mps_mean,
e_pre_mean, e_pre_max, e_post_mean, e_post_max,
e_post_ctrv_mean, e_post_ctrv_max, vdt_m_mean, formula_dev_pct, over_threshold
~~~

Yêu cầu bổ sung noise_seed và pre_exceed_rate/linear_exceed_rate/ctrv_exceed_rate; giữ các tên hiện tại để tránh làm hỏng plot/script đã tích hợp.

## 9. Đường chạy và bằng chứng

Lệnh hiện tại đã chạy được:

~~~powershell
python -m src.run_benchmark --config config_chot.yaml
python -m src.run_benchmark --config config_chot.yaml --scenarios A C
python -m src.plot --config config_chot.yaml
~~~

Lệnh toàn bộ tạo 45 điều kiện/4.500 mẫu; A/C tạo 30 điều kiện/3.000 mẫu. Runner ghi đè results/, plot ghi đè ảnh cùng tên. Hướng dẫn môi trường: QUICKSTART.md.

- results/samples.csv; results/results.csv; results/config_used.yaml; results/run_log.txt.
- Log: thời điểm, lệnh thật, commit hash, working tree sạch/bẩn, seed, phiên bản Python/thư viện, số tổ hợp và runtime.
- plots/timeline.png: phân biệt timestamp báo và thời điểm đo thật.
- plots/error_vs_offset.png: ba phương án, baseline, mức lỗi, đơn vị, ngưỡng minh họa; tách scenario/distance rõ.
- plots/alignment_turn.png: nhiều phép thử độc lập C, d=40 m, offset=100 ms, vị trí đúng và ba dự đoán. Không gọi là quỹ đạo một vật thể xuyên suốt mẫu.
- Mỗi plot ghi “Dữ liệu tổng hợp”.

## 10. Phân công và mốc

| Người | Sở hữu | Bàn giao |
|---|---|---|
| TV1 | Tài liệu chốt, README, TEAMMATES, requirements, tích hợp, Problem/Decision | Quy ước chung, slide, báo cáo riêng |
| TV2 | reports/sources.md, Method, nguồn/limitation | Link đúng, thông tin tái hiện, slide Method |
| TV3 — Phạm Hoàng Anh Khôi (2A202602404) | src/simulate.py, triển khai theo config_chot.yaml | DataFrame, quỹ đạo/timestamp/nhiễu |
| TV4 | src/compensate.py | Hai hàm bù, failure/cải tiến |
| TV5 | src/run_benchmark.py, src/plot.py, kết quả/bằng chứng | Metric, CSV/log/plot, slide Benchmark |

TV1 quản lý thay đổi config; TV3 đề xuất chỉnh khi cần. Mỗi người làm nhánh riêng, sở hữu file phân công; chốt nhánh tích hợp trong TEAMMATES và ghép theo mốc. Không ghi đè việc người khác. Ghi commit và trạng thái code thật dùng để chạy.

| Phút | Đầu ra |
|---|---|
| 15 | Chốt quy ước/giao diện, đủ 5 người có repo/nhánh |
| 45 | Nguồn sơ bộ, baseline, hàm bù, runner/plot |
| 80 | A/C chạy được; thêm B khi phép chạy chính ổn |
| 95 | CSV/log/plot; họp 5 phút chốt failure từ số đo |
| 115 | README chính xác, slide và 5 báo cáo riêng |
| 120 | Pitch đã tập 3–5 phút |

## 11. Báo cáo và pitch

Mỗi báo cáo có Problem → Method → Benchmark → Failure case → Engineering decision. Dùng bằng chứng chung nhưng viết bằng lời của từng người. Tách kết quả nguồn, số tự đo và suy luận.

Pitch: TV1 Problem 40 s; TV2 Method 50 s; TV3 Setup 50 s; TV5 Benchmark 60 s; TV4 Failure/cải tiến 50 s; TV1 Decision 30 s. Tổng 280 s, còn 20 s chuyển phần. Ưu tiên plot/log đã lưu; demo trực tiếp khi đã xác nhận ổn định.

Mỗi người tự nộp VLearn theo hướng dẫn lớp. Tên repo, định dạng PDF và tên file là quy ước nhóm; đối chiếu yêu cầu giảng viên nếu có hướng dẫn bổ sung.

## 12. Trạng thái bàn giao cuối

config_chot.yaml đang được runner hiện tại đọc. config.yaml chỉ giữ schema lịch sử; muốn kiểm tra bản cũ cần checkout riêng commit cũ, không dùng nó với runner hiện tại.

Báo cáo TV1 và nội dung pitch nằm tại reports/TV1_REPORT.md và reports/GROUP_PITCH.md. Chưa đóng lab cho tới khi sửa đối chứng seed, thống nhất metric/log, cập nhật báo cáo từng người và tập pitch. Benchmark chính không phụ thuộc wrapper ước lượng offset TV2; chỉ đưa phần mở rộng vào pitch khi wrapper chạy lại được hoặc ghi rõ dùng demo độc lập.
