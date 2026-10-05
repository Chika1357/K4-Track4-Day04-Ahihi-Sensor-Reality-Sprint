# Nguồn tham khảo: Lab T4 (lệch thời gian camera–LiDAR)

> Người phụ trách: TV2. File này đặt tại `reports/sources.md` trong repo nhóm.
> Mọi câu trong file này là **kết luận của nguồn**, không phải kết quả nhóm tự đo.

---

## Nguồn chính (N1): Spatiotemporal Camera-LiDAR Calibration: A Targetless and Structureless Approach

- **Tác giả:** Chanoh Park, Peyman Moghadam, Soohwan Kim, Sridha Sridharan, Clinton Fookes (CSIRO Data61 và QUT, Úc)
- **Nơi đăng:** IEEE Robotics and Automation Letters (RA-L), chấp nhận tháng 1/2020
- **Link:** https://arxiv.org/abs/2001.06175 (bản HTML: https://ar5iv.labs.arxiv.org/html/2001.06175)
- **Code:** paper không công bố repo. Nhóm **không chạy code gốc**, chỉ dùng ý tưởng phương pháp.

### Vì sao chọn
Đúng cặp sensor của nhóm (camera–LiDAR) và ước lượng trực tiếp **time lag** giữa hai sensor không chung đồng hồ — đúng failure case nhóm đang thử.

### Bảng 5 câu hỏi

| Câu hỏi | Ghi chép |
|---|---|
| Phương pháp nhận gì và tạo gì? | **Input:** quỹ đạo LiDAR (từ LiDAR odometry), quỹ đạo camera (từ visual odometry, ORB-SLAM), và các điểm đặc trưng 2D được tracking trên ảnh. Camera là hệ độc lập, không chung đồng hồ với LiDAR. **Output:** extrinsic 6 bậc tự do camera–LiDAR và **time lag** giữa hai sensor. |
| Cách làm (2 giai đoạn) | **(1) Coarse:** đồng bộ thô bằng cách phát hiện thời điểm hệ bắt đầu chuyển động; giải extrinsic dạng closed-form (bài toán hand-eye AX = XB). **(2) Refine:** biểu diễn quỹ đạo LiDAR liên tục theo thời gian, rồi tối ưu đồng thời extrinsic và time lag để giảm sai số chiếu điểm 3D (tam giác hóa từ ảnh) lên ảnh. Dùng Gauss-Newton, M-estimator loại outlier, marginalize các điểm 3D (structureless). |
| Nguồn đo chất lượng bằng gì? | Sai số quay (đơn vị 10⁻³ rad), sai số tịnh tiến (m), sai số time lag (ms). Ground truth extrinsic lấy bằng chọn cặp điểm 3D–2D thủ công; ground truth time lag lấy từ một phương pháp khác và kiểm tra thủ công. |
| Dữ liệu và phần cứng | Dữ liệu tự thu: 8 bộ trên thiết bị cầm tay, xe và robot chân, môi trường trong nhà/ngoài trời, có bộ camera và LiDAR quay ngược hướng nhau. LiDAR UTM-30LX và VLP-16. Thêm mô phỏng camera 1280×720, 20 Hz. |
| Chạy được ở lớp không? | **Không.** Không có repo, cần ROS-style pipeline, LiDAR odometry, visual odometry và dữ liệu thật. Nhóm chuyển sang benchmark mô phỏng 2D. |
| Nhóm tái hiện phần nào? | Ý tưởng cốt lõi ở mức đơn giản hóa: **tìm Δt làm sai số căn chỉnh nhỏ nhất** (hàm `estimate_offset`, thử Δt theo lưới thay vì Gauss-Newton). Metric là **proxy**: sai số vị trí 2D (m) và sai số ước lượng Δt (ms) trên dữ liệu tổng hợp. |

### Kết quả nguồn báo cáo (để trích dạng "Paper cho biết…")
- Với các đoạn quỹ đạo cầm tay dài 3 giây (khoảng 0,7 rad/s và 0,9 m/s), time lag được đặt từ 33 đến 133 ms, phương pháp vẫn ước lượng được time lag với sai số **dưới khoảng 0,15 ms** và extrinsic gần như không bị ảnh hưởng (Bảng IV).
- Trong mô phỏng, sai số time lag giảm khi dùng nhiều frame hơn: khoảng 3,5 ms với 10 frame, còn khoảng 0,4 ms với 50 frame (Bảng III).
- Giai đoạn coarse vẫn cho extrinsic đủ tốt làm điểm khởi đầu khi time lag lên tới ±0,5 s (Bảng II).
- Paper nhấn mạnh: chỉ cần lệch thời gian nhỏ cũng gây lệch căn chỉnh đáng kể, nhất là khi **vận tốc góc lớn** → khớp với giả thuyết failure case rẽ cua của nhóm.

### Limitation do chính nguồn nêu (mục VI-A và V-C2)
1. **Time lag không quan sát được khi hệ đứng yên**; độ bất định tăng dần trong lúc đứng yên.
2. Cần **chuyển động đủ mạnh** (roll/pitch/yaw) để hiệu chuẩn; với **xe ô tô khó tạo đủ chuyển động trong thời gian ngắn**.
3. Cần đủ đặc trưng hình học 3D và đặc trưng ảnh tracking được; thiếu thì LiDAR odometry bị trượt, kéo theo sai kết quả.
4. Time lag thay đổi theo thời gian nên **phải theo dõi liên tục**, kết quả chỉ đúng trong đoạn frame đã dùng.
5. Độ chính xác time lag sau refine **không đánh giá được** trên dữ liệu thật vì phương pháp lấy ground truth có độ chính xác cùng cỡ.

---

## Nguồn phụ (N2, = S9 của đề lab): Continuous-Time Spatiotemporal Calibration of a Rolling Shutter Camera-IMU System

- **Tác giả:** Jianzhu Huai, Yuan Zhuang, Qicheng Yuan, Yukai Lin
- **Năm:** 2021 (arXiv 16/08/2021)
- **Link:** https://arxiv.org/abs/2108.07200
- **Code:** abstract cho biết code mô phỏng và hiệu chuẩn được công khai; link nằm trên trang arXiv. Nhóm **không chạy code này**.

### Bảng 5 câu hỏi

| Câu hỏi | Ghi chép |
|---|---|
| Phương pháp nhận gì và tạo gì? | **Input:** ảnh từ camera rolling shutter quay bảng hiệu chuẩn (calibration target) + dữ liệu IMU. **Output:** tham số không gian–thời gian camera–IMU (extrinsic và time offset), có xét hiệu ứng rolling shutter. |
| Cách làm | Biểu diễn quỹ đạo bằng B-spline liên tục theo thời gian; mỗi quan sát điểm trên bảng có pose camera riêng (vì mỗi hàng ảnh chụp ở thời điểm khác nhau). |
| Nguồn đo chất lượng bằng gì? | Sai số extrinsic (góc, tịnh tiến) và độ nhất quán của kết quả hiệu chuẩn. |
| Dữ liệu | Mô phỏng từ 4 bộ dữ liệu hiệu chuẩn công khai; dữ liệu thật từ 2 hệ camera–IMU công nghiệp. |
| Chạy được ở lớp không? | Không trong 120 phút: cần bảng hiệu chuẩn, IMU, camera rolling shutter thật. |
| Nhóm dùng phần nào? | Chỉ dùng để giải thích **phần mở rộng rolling-shutter line delay**: trong một frame, các hàng ảnh cũng lệch thời gian nhau. |

### Kết quả nguồn báo cáo
- Trong mô phỏng với thiết lập rolling shutter giống camera điện thoại phổ biến, bỏ qua hiệu ứng rolling shutter làm extrinsic sai khoảng **1° về góc và 2 cm về tịnh tiến**.
- Trên dữ liệu thật, xét hiệu ứng rolling shutter cho kết quả hiệu chuẩn chính xác và nhất quán hơn.

### Phạm vi áp dụng (nhóm ghi nhận từ abstract, **không phải** limitation tác giả tự nêu)
- Cần bảng hiệu chuẩn → hiệu chuẩn offline, không phải trong lúc xe chạy.
- Cặp sensor là camera–IMU, không phải camera–LiDAR → chỉ liên quan gián tiếp đến bài toán của nhóm.
- ⚠️ Nếu muốn ghi limitation do tác giả tự nêu, cần đọc mục kết luận của bản PDF.

---

## Liên hệ giữa nguồn và phép thử của nhóm

| | Nguồn N1 | Nhóm |
|---|---|---|
| Dữ liệu | Thật + mô phỏng 3D | Mô phỏng 2D tổng hợp |
| Δt | **Ước lượng** bằng tối ưu reprojection error | (a) **Giả định đã biết** để bù chuyển động; (b) **ước lượng** bằng thử lưới Δt |
| Metric | Sai số time lag (ms), extrinsic (rad, m) | Sai số vị trí (m), sai số ước lượng Δt (ms) |
| Chuyển động | Cầm tay, robot, xe | Xe chạy thẳng, tăng tốc, rẽ cua |

**Không được so sánh trực tiếp** số của nguồn với số của nhóm: khác dữ liệu, khác metric, khác mức độ phức tạp.

Hai limitation của N1 có thể **kiểm tra được trong mô phỏng của nhóm**:
1. "Không quan sát được time lag khi đứng yên" → cho xe đứng yên (v = 0) và xem `estimate_offset` có tìm ra Δt không.
2. "Vận tốc góc lớn làm lệch nhiều" → kịch bản C (rẽ cua) của nhóm.

---

## Câu mẫu dùng cho báo cáo và slide

- *Paper/repo cho biết:* Park và cộng sự (RA-L 2020) ước lượng đồng thời extrinsic và time lag camera–LiDAR mà không cần bảng hiệu chuẩn, đạt sai số time lag dưới khoảng 0,15 ms trên dữ liệu cầm tay với time lag 33–133 ms.
- *Paper/repo cho biết:* phương pháp này không ước lượng được time lag khi hệ đứng yên, và với xe ô tô khó tạo đủ chuyển động trong thời gian ngắn.
- *Paper/repo cho biết:* Huai và cộng sự (2021) chỉ ra bỏ qua rolling shutter có thể làm extrinsic camera–IMU sai khoảng 1° và 2 cm.
- *Nhóm quan sát được:* (điền sau khi có `results.csv`).

---

## Thông tin tái hiện

| Nguồn | Link | Phiên bản | Nhóm chạy code? |
|---|---|---|---|
| N1 | https://arxiv.org/abs/2001.06175 | arXiv v1, RA-L 2020 | Không (không có repo) |
| N2 (S9) | https://arxiv.org/abs/2108.07200 | arXiv v1, 16/08/2021 | Không |
