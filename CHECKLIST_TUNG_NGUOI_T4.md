# CHECKLIST TỪNG NGƯỜI — LAB T4

Đọc [bản chốt](CHOT_LAB_T4.md) trước khi triển khai. Tham số lấy từ config_chot.yaml; công thức/giao diện lấy theo bản chốt. TV1 cập nhật thay đổi rồi nhóm chạy lại các điều kiện liên quan.

## Mọi người

- [ ] Điền họ tên, MSSV và nhánh trong TEAMMATES.
- [ ] Cài dependencies; ghi phiên bản môi trường thật.
- [ ] Dùng mét, giây, radian; offset config/CLI là ms, đổi một lần sang giây trước tính toán.
- [ ] Giữ quyền sở hữu file; thông báo thay đổi giao diện trước bàn giao.
- [ ] Họp phút 95; tách dự đoán, số đo, kết luận nguồn và suy luận.
- [ ] Viết báo cáo riêng đủ năm mục, số truy được về CSV/log.
- [ ] Tập pitch; tự nộp VLearn và kiểm tra bài nộp.

## TV1 — Đội trưởng, tài liệu và quyết định kỹ thuật

### Trước phút 15

- [ ] Điền tên nhóm/thành viên/link repo; đủ 5 người có quyền truy cập.
- [ ] Dùng main làm nhánh tích hợp; thành viên dùng nhánh trong TEAMMATES hoặc cập nhật nhánh sẵn có.
- [ ] Xác nhận mọi người hiểu mẫu độc lập và d tại t_ref.
- [ ] Xác nhận chiều offset, tọa độ, nguồn trạng thái cho bù, ba phương án.
- [ ] Chốt giao diện TV3/TV4/TV5 theo mục 8 bản chốt.

### Phút 15–95

- [ ] Giữ README/config/checklist nhất quán; cập nhật dependency khi cần thật.
- [ ] Thu nguồn/thông tin tái hiện từ TV2.
- [ ] Giao lỗi theo reports/CODE_REVIEW_T4.md; dùng checklist nghiệm thu reports/TV1_HANDOFF.md.
- [ ] Dùng config.yaml chỉ để kiểm tra bản cũ; cấu hình mục tiêu là config_chot.yaml.
- [ ] Tích hợp baseline và A/C trước; thêm B sau.
- [ ] Kiểm tra metric chung, log và config thực tế.
- [ ] Chuẩn bị slide Problem / Method / Setup / Benchmark / Failure / Decision.

### Phút 95–120

- [ ] Chọn hàng failure thật cùng baseline; ghi scenario/d/offset và ba sai số.
- [ ] Decision bám linear/CTRV; fallback là đề xuất chưa đo.
- [ ] Ghi limitation: biết đúng offset/trạng thái, mô phỏng 2D, chưa có detector/latency/association thật.
- [ ] README có lệnh thật, commit/config/version, nguồn, bảng/plot.
- [ ] Ghép slide, kiểm tra từng số; đủ 5 báo cáo, gồm bản riêng TV1.
- [ ] Tập pitch 3–5 phút; TV1 mở 40 s, kết 30 s.

## TV2 — Nguồn, Method và limitation

### Phút 15–45
- [ ] Viết `config.yaml` đúng thông số chốt:
  - [ ] camera 30 Hz, LiDAR 10 Hz, thời lượng 10 s
  - [ ] offset: 0, 50, 100, 150, 200 ms
  - [ ] kịch bản A: 20 m/s thẳng; B: từ 10 m/s, a = 3 m/s²; C: 10 m/s, R = 30 m
  - [ ] khoảng cách vật thể: 10, 20, 40 m
  - [ ] nhiễu σ = 0,02 m, seed = 42
- [ ] Hàm sinh quỹ đạo ego cho A, B, C, trả về theo thời gian: `x, y, yaw, v, yaw_rate`.
- [ ] Hàm sinh timestamp: camera và LiDAR. Quy ước: LiDAR **báo** timestamp `t_report`, nhưng **thực sự chụp** lúc `t_true = t_report − Δt`.
- [ ] Mỗi frame LiDAR: đặt vật thể tĩnh cách xe `d` mét phía trước; đo vật thể trong hệ tọa độ xe lúc `t_true`, cộng nhiễu.
- [ ] Fusion (cố ý sai): dùng pose xe lúc `t_report` để đổi điểm LiDAR ra hệ world.
- [ ] Tính **E_pre** = khoảng cách giữa vị trí fusion và vị trí thật của vật thể.
- [ ] Hàm chính, trả về DataFrame:
  `run_simulation(scenario, offset_ms, distance_m, cfg)`
  → cột: `frame, t_report, t_true, x_true, y_true, x_lidar, y_lidar, v, yaw_rate, e_pre`

## TV3 — Mô phỏng, src/simulate.py

- [ ] Đọc config_chot.yaml, tạo A/B/C và t_ref = 0.2 + arange(100)/10.
- [ ] Mỗi mẫu đặt P_gt trước ego tại t_ref; giữ P_gt khi tính phép đo tại t_true.
- [ ] Sinh q trong ego tại t_true; noise hai trục cùng seed giữa offset.
- [ ] Trả DataFrame đúng mục 8; GT chỉ cho chấm điểm.
- [ ] Không thêm nearest-frame hoặc camera measurement noise.
- [ ] Kiểm tra offset 0 gần mức nhiễu; A/100 ms trước bù gần 2 m.
- [ ] Phút 45 giao DataFrame/tên hàm/đơn vị cho TV4/TV5.
- [ ] Slide Setup ghi mô phỏng điểm 2D, mẫu độc lập, chưa có scan distortion.

## TV4 — src/compensate.py, failure/cải tiến

- [ ] Triển khai linear/CTRV theo mục 5/8; nhánh ω gần 0.
- [ ] Chỉ dùng q, pose hiện tại, v_ref, yaw_rate_ref, Δt; không GT/pose thật quá khứ/gia tốc thật.
- [ ] Kiểm tra Δt=0 giữ nguyên kết quả không bù; A linear/CTRV trùng nhau; C CTRV dự kiến gần nhiễu.
- [ ] Phút 45 giao hàm, không mutate input.
- [ ] Chọn failure từ số TV5 đo; không ép khớp dự đoán.
- [ ] d|ω|Δt là thành phần quay xấp xỉ, không phải tổng lỗi vô hướng.
- [ ] Slide Failure/cải tiến ghi association sai là suy luận chưa đo.

## TV5 — Runner, metric, plot và bằng chứng

- [ ] Triển khai python -m src.run_benchmark --config config_chot.yaml; hỗ trợ --scenarios A C.
- [ ] Gọi TV3/TV4; chấm ba phương án bằng cùng metric.
- [ ] Ghi samples/results theo schema; 45 hàng đầy đủ hoặc 30 hàng A/C.
- [ ] Formula deviation baseline N/A, tính theo mẫu trước tổng hợp.
- [ ] Exceed_rate từng phương án; không lẫn mean/max/fraction.
- [ ] Lưu config, command, commit/working tree, seed, phiên bản và runtime.
- [ ] Kiểm tra baseline ba phương án trùng nhau; noise giống giữa offset; A/100 ms gần 2 m.
- [ ] Timeline có true/reported time; error_vs_offset có CTRV; alignment_turn là một mẫu độc lập.
- [ ] Plot có đơn vị/baseline/mức lỗi/dữ liệu tổng hợp/ngưỡng nhóm đặt.
- [ ] Phút 95 giao CSV/log/plot; phút 115 slide Benchmark và báo cáo riêng.

### Phút 45–95
- [ ] Ghép với `simulate.py`, tính **E_post** (linear) và **E_post_ctrv** cho mọi tổ hợp.
- [ ] Tính **sai lệch công thức (%)** = |E_pre − v×Δt| / (v×Δt) × 100.
- [ ] Liệt kê các tổ hợp có sai lệch > 10% → đây là nơi công thức `v × Δt` không còn đúng.
- [ ] Dự đoán lý thuyết để đối chiếu: kịch bản C có thêm thành phần lệch khoảng `d × ω × Δt` (vd. d = 40 m, ω = 0,33 rad/s, Δt = 0,1 s → ~1,3 m). Đánh dấu đây là **ước lượng**, so với số đo thật.

### Phút 95–115
- [ ] Chọn hàng failure case (dự kiến: C, d = 40 m), ghi chính xác: kịch bản, offset, d, E_pre, E_post, E_post_ctrv, so với ngưỡng 0,5 m.
- [ ] Viết đoạn failure case 3 phần: **điều kiện đầu vào → tác động tới metric → hệ quả với fusion** (gán nhầm điểm LiDAR sang vật thể bên cạnh — ghi là **suy luận**, nhóm chưa chạy detector).
- [ ] Viết slide 5: failure + kết quả cải tiến CTRV (metric kiểm chứng = E_post ở kịch bản C trước/sau cải tiến).
- [ ] Ghi giả thuyết nếu có (vd. "cải tiến CTRV vẫn sai khi offset ước lượng sai") và đánh dấu là giả thuyết.

---

## 👤 TV5: Benchmark, bảng và plot (`run_benchmark.py`, `plot.py`) · Pitch slide 4

### Phút 15–45
- [ ] Viết khung `run_benchmark.py`: lặp 3 kịch bản × 5 offset × 3 khoảng cách, gọi hàm TV3 và TV4.
- [ ] Định nghĩa cột `results/results.csv`:
  `scenario, offset_ms, distance_m, v_mps, e_pre_mean, e_pre_max, e_post_mean, e_post_max, e_post_ctrv_mean, vdt_m, formula_dev_pct, over_threshold`
- [ ] Ghi log `results/run_log.txt`: thời điểm chạy, commit hash, seed, đường dẫn config.
- [ ] Viết `plot.py`, thử trước với dữ liệu giả.

### Phút 45–95
- [ ] Chạy toàn bộ ma trận thí nghiệm, lưu `results.csv`.
- [ ] Kiểm tra hợp lý: offset 0 ≈ 0; E_pre tăng theo offset; kịch bản A khớp `v × Δt`.
- [ ] Vẽ 3 plot, lưu vào `plots/`:
  - [ ] `timeline.png`: tick timestamp camera vs LiDAR trong 1 giây đầu, offset 100 ms.
  - [ ] `error_vs_offset.png`: E_pre và E_post theo offset, 3 kịch bản (d = 20 và 40 m), có đường ngưỡng 0,5 m.
  - [ ] `trajectory_turn.png`: kịch bản C, d = 40 m, offset 100 ms — vị trí thật vs trước bù vs sau bù (linear và CTRV).
- [ ] Mỗi plot có tiêu đề, trục có đơn vị, chú thích "Dữ liệu tổng hợp".

### Phút 95–115
- [ ] Trích 5–6 hàng tiêu biểu từ `results.csv` làm bảng cho slide 4 (gồm baseline và hàng failure case).
- [ ] Viết slide 4 (Kết quả): bảng + `error_vs_offset.png`, 2–3 câu "Nhóm quan sát được…".
- [ ] Ghi limitation benchmark: dữ liệu tổng hợp, 2D, ít kịch bản, không đo latency end-to-end, không có ground truth từ detector thật.
- [ ] Đảm bảo mọi số trên slide truy được về `results.csv`.

---

## ⏱️ Bàn giao giữa các người

| Phút | Ai giao | Giao cho | Nội dung |
|---|---|---|---|
| 15 | TV1 | Cả nhóm | Link repo, cấu trúc thư mục |
| 45 | TV3 | TV4, TV5 | Hàm `run_simulation` + danh sách cột |
| 45 | TV4 | TV5 | Hàm `compensate_linear`, `compensate_ctrv` |
| 45 | TV2 | TV1 | Link nguồn + tóm tắt |
| 95 | TV5 | Cả nhóm | `results.csv` + 3 plot |
| 115 | Mỗi người | TV1 | Slide phần mình + báo cáo riêng trong `reports/` |
