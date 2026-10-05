# Báo cáo cá nhân TV1 — T4

**Trạng thái: khung báo cáo, chưa phải bài nộp hoàn chỉnh. Số liệu cũ có lỗi không được điền làm kết quả cuối.**

- Họ tên/MSSV: [điền]
- Nhóm: [điền]
- Repository: https://github.com/Chika1357/K4-Track4-Day4-Ahihi
- Commit benchmark đã nghiệm thu: [chờ]
- Config/lệnh thực tế: [chờ]
- Vai trò: chốt thiết kế, điều phối tích hợp, README và engineering decision.

## 1. Problem

Nền tảng ADAS, ứng dụng căn chỉnh camera–LiDAR. LiDAR đo tại t_ref−Δt nhưng báo timestamp t_ref; sử dụng sai pose gây lệch vị trí vật thể. Nhóm mô phỏng 2D, camera làm mốc thời gian, chưa chạy detector/fusion ảnh thật.

Claim: sai số thẳng đều gần vΔt; bù linear bỏ qua quay có thể còn lỗi khi rẽ, CTRV dự kiến giảm lỗi đó.

## 2. Method

Nguồn đã đọc và link/version: [TV2 cung cấp, chờ xác nhận].

Input: phép đo vị trí LiDAR, pose/vận tốc/yaw rate hiện tại và offset biết trước. Output: vị trí world trước bù, sau linear, sau CTRV. GT chỉ dùng sinh dữ liệu/chấm điểm.

Mô hình giản lược của nhóm và khác biệt với nguồn: [điền sau khi đọc nguồn]. Không nhận là tái hiện đầy đủ thuật toán paper.

## 3. Benchmark

Dữ liệu tổng hợp: 100 phép thử độc lập/tổ hợp, offset 0–200 ms, d=10/20/40 m, noise 0,02 m mỗi trục. Liệt kê đúng scenario đã chạy.

Metric: mean/max sai số Euclidean theo mét; exceed_rate với ngưỡng minh họa 0,5 m.

| Scenario / d / offset | Trước bù mean (m) | Linear mean (m) | CTRV mean (m) | Bằng chứng |
|---|---|---|---|---|
| Baseline tương ứng | [chờ] | [chờ] | [chờ] | [CSV/plot/log] |
| Điều kiện lỗi | [chờ] | [chờ] | [chờ] | [CSV/plot/log] |

Nhóm quan sát được: [chỉ điền sau nghiệm thu].
Nguồn báo cáo: [ghi riêng, không so trực tiếp khác dataset/metric].

## 4. Failure case

Điều kiện đầu vào → thay đổi metric → hệ quả kỹ thuật: [điền bằng số thật].
Association sai là suy luận nếu chưa đo trực tiếp.

Limitation: 2D, vật thể tĩnh trong từng phép thử, giả định biết offset/trạng thái, chưa có scan distortion, detector/latency end-to-end.

## 5. Engineering decision

- Quyết định theo so sánh linear/CTRV: [chờ số].
- Trade-off và khi áp dụng: [giả định chuyển động, chất lượng trạng thái/offset].
- Nguồn hỗ trợ nhận định: [điền].
- Fallback hoặc vòng thử tiếp: [đề xuất, không ghi đã kiểm chứng].
- Metric/log để kiểm tra vòng tiếp theo: [điền].

Bản nộp phải có link nguồn, commit/config/lệnh và bằng chứng truy được. Mỗi thành viên tự nộp VLearn.
