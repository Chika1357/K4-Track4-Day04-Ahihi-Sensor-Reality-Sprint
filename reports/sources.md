# Nguồn khởi đầu — TV2 cần hoàn thiện

Trạng thái: link để bắt đầu đọc, chưa phải bằng chứng nhóm tái hiện thuật toán. Định hướng dưới đây dựa trên abstract; TV2 kiểm tra toàn văn trước khi ghi phương pháp/metric/limitation chi tiết.

## Ego-motion correction và projection LiDAR/camera

- Mao Shan và cộng sự, 2020: Probabilistic Egocentric Motion Correction of Lidar Point Cloud and Projection to Camera Images for Moving Platforms.
- [Paper gốc](https://arxiv.org/abs/2003.03954).
- Liên hệ: bù ego-motion LiDAR, projection lên camera, bất định chuyển động và time jitter.
- Nhóm dùng mô hình hình học 2D giản lược, chưa tái hiện đầy đủ phương pháp xác suất/projection.

## Calibration thời gian và rolling shutter

- Jianzhu Huai và cộng sự, 2021: Continuous-Time Spatiotemporal Calibration of a Rolling Shutter Camera-IMU System.
- [Paper gốc](https://arxiv.org/abs/2108.07200).
- Liên hệ: calibration camera–IMU và line delay.
- Nhóm dùng camera–LiDAR, giả định biết offset; chưa tái hiện calibration camera–IMU/rolling shutter.

## Phiếu đọc cần điền cho từng nguồn

| Nội dung | Ghi chép |
|---|---|
| Phiên bản paper/ngày đọc | Chưa điền |
| Input → output | Chưa điền |
| Phương pháp/giả định | Chưa điền |
| Dataset, metric, điều kiện đo | Chưa điền |
| Limitation do tác giả nêu, vị trí trong nguồn | Chưa điền |
| Repo chính thức, commit/version nếu có | Chưa điền |
| Yêu cầu/lệnh chạy gốc nếu xét tái hiện | Chưa điền |
| Vì sao chọn benchmark giản lược | Chưa điền |
| Phần nhóm đo/phần chưa chứng minh | Chưa điền |

Nếu lớp yêu cầu nguồn mới theo mốc năm, TV2 kiểm tra và bổ sung; không tự coi hai nguồn khởi đầu là đã đáp ứng. Bổ sung nguồn PTP/trigger nếu dùng trong engineering decision.
