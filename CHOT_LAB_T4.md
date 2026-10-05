# CHỐT LAB T4 — Sai số căn chỉnh vị trí do lệch timestamp

Thiết kế này dùng để triển khai. Chưa có kết quả benchmark; dự đoán lý thuyết không phải số đã đo. TV1 quản lý thay đổi và cập nhật đồng thời tài liệu/cấu hình trước khi chạy lại.

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

Giữ cùng mốc, quỹ đạo, vật thể và mẫu nhiễu khi so các offset/phương án. scenario_id: A=0, B=1, C=2; distance_id: 10=0, 20=1, 40=2. Seed tổ hợp = 42 + 100*scenario_id + distance_id; không cộng offset vào seed. Dùng numpy.random.default_rng(seed) sinh mảng nhiễu (100, 2) theo cùng thứ tự.

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

A và C khớp giả định của CTRV; B có gia tốc nên có thể còn sai số. Đây là kết quả dự kiến cần đối chiếu bằng phép chạy.

## 6. Metric và ngưỡng

Với từng mẫu/phương án k: e_k[i] = ||P_k[i] - P_gt[i]||₂, mét. Báo cáo mean và max trên cùng 100 mẫu; nhỏ hơn là tốt hơn.

- E_pre: trước bù.
- E_post_linear: sau bù tịnh tiến.
- E_post_ctrv: sau bù tịnh tiến + quay.
- Baseline offset 0 có nhiễu nền; ba phương án phải trùng nhau trong sai số số học. Không yêu cầu baseline bằng 0 khi bật noise.
- Tham chiếu theo mẫu: vdt[i] = v_ref[i]*Δt; lưu vdt_mean_m.
- formula_dev_pct = 100 * mean(abs(e_pre[i] - vdt[i])) / mean(vdt[i]). Offset 0 ghi N/A (ô trống CSV). Đây là độ lệch khỏi mô hình đơn giản, không phải chất lượng detector; noise cũng ảnh hưởng đại lượng này.

Ngưỡng minh họa 0,5 m do nhóm đặt, chưa phải tiêu chuẩn an toàn. Mỗi phương án có exceed_rate = mean(e_k > 0.5), trong [0,1]. Khi nói vượt ngưỡng theo mean phải chỉ rõ E_mean > 0.5; không dùng lẫn mean, max và exceed_rate.

## 7. Failure case và engineering decision

- Dự kiến C, d=40 m, offset 50–200 ms: linear còn lỗi do bỏ qua quay. Chỉ chốt offset/con số sau chạy.
- Chọn một hàng kết quả cùng baseline tương ứng; ghi mean/max/exceed_rate, plot và log.
- Cải tiến kiểm chứng trong lab: CTRV; so linear/CTRV trên cùng tổ hợp.
- Quyết định dự kiến: kiểm tra timestamp và xét quay khi bù, đặc biệt với vật thể xa. Kết luận cuối bám số đo.
- Fallback cho vòng thử tiếp: đánh dấu dữ liệu chưa căn chỉnh khi đồng bộ hoặc ước lượng chuyển động không đủ tin cậy, tránh association cứng cho tới khi kiểm tra lại. Chưa triển khai tracker/fallback hoặc đo hiệu quả của chúng.
- Bỏ quy tắc cố định 30 ms/0,2 rad/s vì chưa có cơ sở xác nhận.
- Trade-off: giả định biết offset, chất lượng vận tốc/yaw rate, giới hạn khi có gia tốc, chi phí tính toán chưa đo. TV2 tìm nguồn cho PTP/trigger và giới hạn tích hợp trước khi dùng làm khuyến nghị.

## 8. Giao diện bàn giao

TV3: run_simulation(scenario, offset_ms, distance_m, cfg) -> pandas.DataFrame.

~~~text
scenario, frame, object_id, offset_ms, distance_m, noise_seed,
t_ref_s, t_true_s, gt_x_world_m, gt_y_world_m,
lidar_x_ego_m, lidar_y_ego_m,
ego_x_ref_m, ego_y_ref_m, yaw_ref_rad, v_ref_mps, yaw_rate_ref_radps
~~~

object_id phân biệt phép thử độc lập; phải giữ cùng ID giữa offset của cùng scenario/distance/frame. GT chỉ dùng đánh giá, không đưa vào hàm bù.

TV4 cung cấp hai hàm:

~~~text
compensate_linear(q_ego, ego_xy_ref, yaw_ref, v_ref, yaw_rate_ref, dt_s)
compensate_ctrv(q_ego, ego_xy_ref, yaw_ref, v_ref, yaw_rate_ref, dt_s)
~~~

q_ego và ego_xy_ref: NumPy arrays (N, 2); yaw_ref/v_ref/yaw_rate_ref: (N,); dt_s: scalar. Đầu ra (N, 2), vị trí world theo mét. Không mutate input. TV4 sở hữu logic bù; TV5 sở hữu metric chung.

TV5 ghi samples.csv gồm cột mô phỏng và vị trí dự đoán/sai số từng phương án. results.csv có 45 hàng nếu đầy đủ:

~~~text
scenario, offset_ms, distance_m, n_samples, noise_seed, v_ref_mean_mps,
e_pre_mean_m, e_pre_max_m, e_post_linear_mean_m, e_post_linear_max_m,
e_post_ctrv_mean_m, e_post_ctrv_max_m, vdt_mean_m, formula_dev_pct,
pre_exceed_rate, linear_exceed_rate, ctrv_exceed_rate
~~~

## 9. Đường chạy và bằng chứng

Giao diện sẽ triển khai:

~~~powershell
python -m src.run_benchmark --config config.yaml
python -m src.run_benchmark --config config.yaml --scenarios A C
~~~

Lệnh chưa chạy được cho tới khi TV3/TV4/TV5 hoàn thành code.

- results/samples.csv; results/results.csv; results/config_used.yaml; results/run_log.txt.
- Log: thời điểm, lệnh thật, commit hash, working tree sạch/bẩn, seed, phiên bản Python/thư viện, số tổ hợp và runtime.
- plots/timeline.png: phân biệt timestamp báo và thời điểm đo thật.
- plots/error_vs_offset.png: ba phương án, baseline, mức lỗi, đơn vị, ngưỡng minh họa; tách scenario/distance rõ.
- plots/alignment_turn.png: một phép thử C, d=40 m, offset=100 ms, vị trí đúng và ba dự đoán. Không gọi là quỹ đạo một vật thể xuyên suốt mẫu.
- Mỗi plot ghi “Dữ liệu tổng hợp”.

## 10. Phân công và mốc

| Người | Sở hữu | Bàn giao |
|---|---|---|
| TV1 | Tài liệu chốt, README, TEAMMATES, requirements, tích hợp, Problem/Decision | Quy ước chung, slide, báo cáo riêng |
| TV2 | reports/sources.md, Method, nguồn/limitation | Link đúng, thông tin tái hiện, slide Method |
| TV3 | src/simulate.py, triển khai theo config.yaml | DataFrame, quỹ đạo/timestamp/nhiễu |
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
