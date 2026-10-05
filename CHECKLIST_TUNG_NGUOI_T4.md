# ✅ CHECKLIST TỪNG NGƯỜI: LAB T4 (lệch thời gian camera–LiDAR)

> Đọc kèm file **CHOT_LAB_T4.md**. Mọi thông số (offset, kịch bản, metric, ngưỡng 0,5 m) lấy theo file chốt, không tự đổi.

---

## 🔁 Việc MỌI NGƯỜI đều phải làm

- [ ] Đọc hết file chốt trước phút 10.
- [ ] Clone repo trước phút 15, chạy được `pip install -r requirements.txt`.
- [ ] Push code/tài liệu của mình đúng thư mục, commit message ghi rõ tên (vd. `TV3: add simulate.py`).
- [ ] Tham gia họp 5 phút lúc phút 95 để xác nhận failure case.
- [ ] Viết **báo cáo riêng** `reports/TVx_HoTen_MSSV.pdf` đủ 5 mục: Problem, Method, Benchmark, Failure case, Engineering decision.
  - [ ] Dùng chung bảng/plot của nhóm, ghi rõ tên file plot và lệnh chạy.
  - [ ] Tự viết bằng lời của mình, phần mình phụ trách viết sâu hơn.
  - [ ] Tách rõ "Nhóm quan sát được…" và "Paper/repo cho biết…".
- [ ] Tập phần pitch của mình, đúng thời lượng.
- [ ] Nộp VLearn: file báo cáo riêng + URL repo chung. Mở lại link kiểm tra sau khi nộp.

---

## 👤 TV1: Đội trưởng (repo, README, trade-off, slide) · Pitch slide 1 và 6

### Phút 0–15
- [ ] Tạo repo tên `K4-Track4-Day04-TenNhom-Sensor-Reality-Sprint`.
- [ ] Thêm 4 thành viên làm collaborator, gửi link vào nhóm.
- [ ] Tạo `TEAMMATES.md`: họ tên đầy đủ + MSSV của **đúng 5 người**.
- [ ] Tạo cấu trúc thư mục: `src/`, `results/`, `plots/`, `reports/` và file rỗng `simulate.py`, `compensate.py`, `run_benchmark.py`, `plot.py`.
- [ ] Tạo `requirements.txt`: `numpy`, `pandas`, `matplotlib`, `pyyaml`.

### Phút 15–45
- [ ] Viết khung `README.md`: bài toán, claim, cách cài, lệnh chạy, cấu trúc repo, mục Nguồn (để trống chờ TV2).
- [ ] Phút 45: hỏi tiến độ từng người theo mốc trong file chốt, ai trễ thì hỗ trợ ngay.

### Phút 45–95
- [ ] Theo dõi việc ghép code TV3 + TV4 + TV5, đảm bảo không ai đổi định nghĩa metric.
- [ ] Làm khung slide 6 trang: Problem / Method / Setup / Kết quả / Failure / Decision.
- [ ] Viết slide 1 (Problem): xe ADAS, fusion camera–LiDAR, lệch timestamp, claim.

### Phút 95–115
- [ ] Chủ trì họp failure case: chốt hàng kết quả, cấu hình, plot sẽ dùng.
- [ ] Viết slide 6 (Decision): cải tiến CTRV, fallback (offset > 30 ms và yaw rate > 0,2 rad/s), trade-off phần mềm vs đồng bộ phần cứng (PTP/trigger).
- [ ] Cập nhật README: lệnh chạy chính xác, commit hash, link nguồn từ TV2, ảnh plot chính.

### Phút 115–120 và sau buổi
- [ ] Ghép slide từ 5 người, tập pitch bấm giờ (≤ 5 phút).
- [ ] Kiểm tra `reports/` có đủ 5 bản riêng, đúng tên file.
- [ ] Xác nhận cả 5 người đã nộp VLearn.
- [ ] Đối chiếu rubric: demo chạy được 40%, failure 25%, thuật toán 20%, trade-off 15%.

---

## 👤 TV2: Nghiên cứu nguồn (Method) · Pitch slide 2

### Phút 15–45
- [ ] Đọc **S9: Huai và cộng sự, 2021** (rolling-shutter camera–IMU spatiotemporal calibration). Ghi:
  - [ ] Input (dữ liệu gì vào)
  - [ ] Output (ước lượng time offset, extrinsic, line delay…)
  - [ ] Metric và dataset nguồn dùng
  - [ ] Yêu cầu phần cứng/phần mềm
  - [ ] Limitation **do chính nguồn nêu** (không tự bịa thêm)
- [ ] Tìm thêm **1 nguồn** về motion compensation hoặc đồng bộ camera–LiDAR, từ khóa: `motion compensation LiDAR autonomous driving`, `camera LiDAR time synchronization`. Ghi đủ 5 mục như trên.
- [ ] Lưu link chính xác + version/commit (nếu là repo) vào `reports/sources.md`.

### Phút 45–95
- [ ] Viết slide 2 (Method): nguồn làm gì, input → output, khác gì so với phép thử nhóm (nhóm **giả định đã biết offset**, nguồn **ước lượng offset**).
- [ ] Nếu nguồn có nêu độ lớn offset hoặc sai số điển hình, ghi lại dạng "Paper cho biết…", kèm điều kiện đo.
- [ ] Giải thích ngắn cho TV4 mô hình constant turn rate (nếu TV4 cần).
- [ ] (Mở rộng) Viết 3–4 câu về rolling-shutter line delay: mỗi hàng ảnh chụp ở thời điểm khác nhau nên một frame cũng có lệch thời gian bên trong.

### Phút 95–115
- [ ] Viết đoạn limitation so sánh: nguồn dùng dữ liệu/phần cứng thật, nhóm dùng mô phỏng 2D, nên **không đặt hai con số cạnh nhau như so sánh trực tiếp**.
- [ ] Gửi link nguồn cho TV1 cập nhật README.

---

## 👤 TV3: Code mô phỏng (`simulate.py`, `config.yaml`) · Pitch slide 3 (demo)

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

### Kiểm tra trước khi bàn giao (phút 45)
- [ ] Offset 0: E_pre ≈ mức nhiễu (khoảng 0,02–0,03 m).
- [ ] Kịch bản A, offset 100 ms: E_pre ≈ 2 m (= 20 × 0,1).
- [ ] Gửi tên hàm + cột output cho TV4 và TV5.

### Phút 45–95
- [ ] Sửa lỗi khi TV4/TV5 ghép code.
- [ ] Chuẩn bị demo chạy trực tiếp: lệnh `python src/run_benchmark.py --config config.yaml`, chạy dưới 30 giây.

### Phút 95–115
- [ ] Viết slide 3 (Setup): sơ đồ mô phỏng, thông số, giải thích vì sao lệch timestamp sinh sai số vị trí.
- [ ] Ghi limitation mô phỏng: 2D, vật thể tĩnh, nhiễu Gauss, không có méo do quét LiDAR.

---

## 👤 TV4: Bù chuyển động và failure case (`compensate.py`) · Pitch slide 5

### Phút 15–45
- [ ] Viết `compensate_linear(...)`: dịch điểm theo `v × Δt` dọc hướng xe, **không xét yaw** (đây là phương pháp chính để thử).
- [ ] Viết `compensate_ctrv(...)`: bù có xét `yaw_rate` (constant turn rate) — đây là **cải tiến** dùng ở Bước 5.
- [ ] Tự test với kịch bản A: E_post ≈ mức nhiễu.

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
