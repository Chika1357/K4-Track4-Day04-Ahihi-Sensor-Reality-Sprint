# Pitch chung T4 — nội dung 6 slide

Bản nội dung nhóm Ahihi để ghép slide/trình bày, chưa phải file PowerPoint hay bằng chứng đã tập. Main đã kiểm tra: 823da21. Số lấy từ results/results.csv hiện tại, cần cập nhật đồng thời sau sửa seed. Thời lượng nói dự kiến 255 s (4 phút 15 giây), còn khoảng 30 s chuyển phần.

## Slide 1 — Problem · TV1 · 35 s

**Trên slide:**

- ADAS, camera–LiDAR: dữ liệu đúng nhưng dùng sai thời điểm.
- t_capture=t_ref−Δt; offset thử 0–200 ms.
- Claim: thẳng đều e≈vΔt; rẽ cần bù cả quay.
- Đo sai số vị trí 2D theo mét, chưa chạy detector.

**Lời nói TV1:** “Nhóm chọn T4: lệch thời gian giữa camera và LiDAR. Camera là mốc tham chiếu; LiDAR đo sớm hơn nhưng dữ liệu được biến đổi bằng pose hiện tại. Khi xe di chuyển, sai thời điểm có thể tạo sai vị trí. Nhóm kiểm tra bằng mô phỏng 2D: chạy thẳng thì lỗi dự kiến gần vận tốc nhân offset; khi rẽ, bù tịnh tiến có thể chưa đủ. Mục tiêu là đo lỗi vị trí và chọn cách bù phù hợp.”

## Slide 2 — Method · TV2 · 45 s

**Trên slide:**

- Nguồn liên quan: [Park et al., RA-L 2020, arXiv v1](https://arxiv.org/abs/2001.06175v1).
- Đường chạy nhóm: mô phỏng tối thiểu; offset/trạng thái biết đúng.
- Input: điểm cũ + pose/v/yaw rate hiện tại + Δt → output: vị trí world.
- Ba phương án: không bù / linear / CTRV; GT chỉ chấm điểm.

**Lời nói gợi ý:** “Nguồn chính của nhóm là paper Park 2020 về hiệu chuẩn không gian và thời gian camera–LiDAR. Nhóm không chạy toàn bộ phương pháp của paper mà dùng benchmark nhỏ để kiểm tra tác động timestamp. Phép bù nhận điểm LiDAR, trạng thái ego hiện tại và offset biết trước. Linear chỉ xét tịnh tiến; CTRV xét thêm quay với vận tốc và yaw rate không đổi. Vị trí chuẩn chỉ dùng sinh dữ liệu và chấm sai số.”

## Slide 3 — Setup · TV3 · 40 s

**Trên slide:**

- A: 20 m/s; B: v0=10 m/s, a=3 m/s²; C: 10 m/s, R=30 m.
- 5 offset × 3 khoảng cách × 3 kịch bản × 100 mẫu = 4.500 mẫu.
- Baseline 0 ms; σ=0,02 m/trục; mẫu độc lập, vật thể đặt tại t_ref.
- Camera 30 Hz/LiDAR 10 Hz minh họa timeline: [timeline.png](../plots/timeline.png).

**Lời nói gợi ý:** “Nhóm thử ba kiểu chuyển động, năm offset từ 0 đến 200 mili giây và ba khoảng cách. Mỗi tổ hợp có 100 phép thử độc lập, tổng 45 điều kiện. Trong mỗi phép thử, vật thể đứng yên trong world và được đặt phía trước ego tại mốc tham chiếu. Ba phương án nhận cùng điểm có nhiễu. Camera 30 Hz và LiDAR 10 Hz chỉ minh họa timeline; nhóm không đo ảnh hoặc việc chọn frame gần nhất.”

**Lưu ý khi ghép bản cuối:** Code hiện thay noise giữa offset; TV3 sửa theo CHOT rồi TV5 chạy lại. Nếu chưa sửa, phải nói rõ hạn chế này, không tuyên bố mọi offset dùng cùng noise.

## Slide 4 — Benchmark · TV5 · 55 s

**Trên slide:** [error_vs_offset.png](../plots/error_vs_offset.png); bảng mean dưới đây, đơn vị mét, dữ liệu tổng hợp.

| Scenario / d / offset | Không bù | Linear | CTRV |
|---|---:|---:|---:|
| A / 20 m / 0 ms | 0.024 | 0.024 | 0.024 |
| A / 20 m / 100 ms | 2.001 | 0.026 | 0.026 |
| C / 40 m / 0 ms | 0.026 | 0.026 | 0.026 |
| C / 40 m / 100 ms | 1.668 | 1.351 | 0.025 |

**Lời nói gợi ý:** “Nhóm đã chạy đủ 45 điều kiện. Với A, khoảng cách 20 mét, baseline có lỗi nền khoảng 2,4 centimet. Offset 100 mili giây tạo lỗi trung bình 2,001 mét, gần 20 nhân 0,1 bằng 2 mét. Bù đưa lỗi về khoảng 2,6 centimet. Khi rẽ, khoảng cách 40 mét và cùng offset, linear còn 1,351 mét; CTRV còn khoảng 2,5 centimet. Đây là số vị trí nhóm tự đo, không phải mAP hay số của paper.”

## Slide 5 — Failure và limitation · TV4 · 45 s

**Trên slide:** [alignment_turn.png](../plots/alignment_turn.png).

- C/d40/100 ms: linear mean/max = 1,350500 / 1,385999 m.
- Bỏ qua quay: d|ω|Δt≈1,333 m là xấp xỉ thành phần quay.
- CTRV mean/max = 0,024821 / 0,056044 m.
- 0,5 m là ngưỡng nhóm đặt; association sai là suy luận chưa đo.
- Offset/state biết đúng; không đo detector/latency/scan distortion.

**Lời nói gợi ý:** “Failure cụ thể là xe rẽ với vật thể cách 40 mét. Linear bỏ qua thay đổi hướng nên còn lỗi lớn dù đã bù tịnh tiến. Thành phần quay xấp xỉ 1,33 mét giải thích độ lớn này. CTRV giảm lỗi về gần nhiễu vì chuyển động C khớp giả định mô hình. Nhóm chỉ đo vị trí: nguy cơ gán nhầm bbox là suy luận, còn ngưỡng nửa mét là minh họa. Dữ liệu và trạng thái lý tưởng giới hạn việc suy ra hiệu quả trên xe thật.”

## Slide 6 — Engineering decision · TV1 · 35 s

**Trên slide:**

- Chọn CTRV cho rẽ khi offset/v/yaw rate đủ tin cậy; linear đủ cho thẳng đều trong phép thử.
- Trade-off: giả định chuyển động không đổi, chất lượng state/offset; chưa đo runtime.
- Thử tiếp: sai offset/state/gia tốc → mean/max/exceed_rate/runtime.
- Fallback chưa kiểm chứng: đánh dấu dữ liệu chưa căn chỉnh; chưa chốt ngưỡng kích hoạt.

**Lời nói TV1:** “Từ số đo, nhóm chọn bù có xét quay cho trường hợp rẽ, với điều kiện offset và trạng thái ego đáng tin cậy. Linear đã đủ trong chuyển động thẳng đều của phép thử; CTRV cũng có giả định và chưa được đo chi phí tính toán. Bước tiếp theo là thêm lỗi offset, vận tốc và yaw rate rồi đo lại sai số và runtime. Khi dữ liệu chưa căn chỉnh đáng tin cậy, nhóm đề xuất đánh dấu và hạn chế association cứng; fallback và ngưỡng kích hoạt cần kiểm chứng tiếp.”

## Chuẩn bị trả lời câu hỏi

| Câu hỏi | Câu trả lời ngắn / bằng chứng |
|---|---|
| Nhóm đã chạy gì? | Lệnh module trong README; results.csv có 45 hàng, samples.csv có 4.500 mẫu, config/log/plot lưu trong repo |
| Tại sao baseline không bằng 0? | Nhiễu Gauss 0,02 m mỗi trục; ba phương án trùng nhau ở 0 ms |
| Có biết trước đáp án để bù không? | Biết offset/state theo giả định; GT/pose quá khứ thật không vào hàm bù |
| Đây có phải fusion camera–LiDAR thật? | Mô phỏng căn chỉnh điểm 2D, chưa có ảnh/bbox/scan thực tế |
| Có chứng minh an toàn hoặc cải thiện detector không? | Chưa; metric vị trí và ngưỡng nhóm đặt không chứng minh mAP/an toàn |
| Code còn hạn chế nào cần sửa? | Nhiễu giữa offset, metric/log và nội dung một số báo cáo; wrapper TV2 đã chạy được; xem TV1_HANDOFF |
| Tại sao không kết luận ngưỡng 30 ms? | Nhóm chưa đo miền ngưỡng/fallback hay tỷ lệ association sai |

Trước nộp: đóng các mục trong TV1_HANDOFF, cập nhật số chung, điền thông tin cá nhân, xuất định dạng lớp yêu cầu, kiểm tra ảnh/đơn vị/nguồn và tập một lượt có bấm giờ. Mỗi người tự nộp báo cáo riêng.
