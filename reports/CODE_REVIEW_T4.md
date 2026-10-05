# Review code T4 — bàn giao TV3/TV4/TV5

## Phạm vi và trạng thái

- Review/chạy lại core benchmark tại ce139094fa25826d339a86308cf078e14e68124d, trong bản sao riêng.
- Main cập nhật tới 4f38036 khi chuẩn bị nhánh TV1: thay đổi plot và thêm ảnh; simulate/compensate/runner vẫn giữ các lỗi dưới đây.
- Đây là bằng chứng lỗi triển khai, chưa phải kết quả đo failure sensor. Không chọn failure từ CSV cũ để pitch.
- TV1 phụ trách đặc tả, bàn giao và nghiệm thu; các owner sửa code trong file được phân công.

## Bằng chứng đã kiểm tra

Chạy python src/run_benchmark.py config.yaml thành công: 45 tổ hợp, 45 failure. Chạy thẳng, distance=10 m:

| Offset | E_pre mean (m) | E_post linear mean (m) |
|---|---:|---:|
| 0 ms | 0,45090795 | 66,00248179 |
| 100 ms | 1,99799738 | 64,05556267 |

Kiểm tra đơn giản: phép đo cũ [12,0], v=20 m/s, Δt=0,1 s, vị trí hiện tại [10,0]. Linear hiện trả [14,0], sai 4 m.

Lệnh module theo thiết kế bị ModuleNotFoundError: No module named 'simulate'. Runner hiện tại cũng không parse --config/--scenarios.

## Findings và trách nhiệm

| ID | Mức | Vị trí | Vấn đề | Owner / yêu cầu sửa |
|---|---|---|---|---|
| R1 | Chặn kết quả | src/run_benchmark.py, camera_pos_aligned | Cắt camera/LiDAR theo cùng index: mẫu 99 là 3,3 s và 9,9 s; E_pre/E_post không cùng mẫu | TV5: dùng cùng batch t_ref và q cho ba phương án |
| R2 | Chặn kết quả | src/compensate.py, compensate_linear_motion | Cộng vΔt làm phép đo cũ xa hơn, sai chiều bù | TV4: công thức/hệ tọa độ mục 5 bản chốt |
| R3 | Chặn kết quả rẽ | src/simulate.py, get_vehicle_state | x=vt, y=R(1-cos yaw) không phải chuyển động tròn tốc độ đã đặt | TV3: x=R sin(ωt), yaw=ωt, ω=v/R |
| R4 | Khác thiết kế | src/simulate.py, simulate/compute_error_pre | Một vật thể world cố định, nearest-frame, mẫu thay đổi theo offset; baseline chứa lỗi ghép mẫu | TV3/TV5: mẫu độc lập với d tại t_ref, 100 mẫu cố định, noise chung |
| R5 | Chưa đúng CTRV | src/compensate.py, compensate_with_yaw | Tịnh tiến x=vΔt bỏ qua thành phần cung tròn; nhánh ω=0 gọi hàm linear sai dấu | TV4: triển khai pose cũ ước lượng theo công thức CTRV |
| R6 | Metric chưa thống nhất | compute_formula_deviation, runner t_mid | Baseline ghi 0% thay vì N/A; dùng vận tốc giữa bài cho tất cả mẫu tăng tốc | TV5: v_ref từng mẫu, formula deviation theo đặc tả, mean/max/exceed_rate |
| R7 | Giao diện/config | imports, sys.argv, config.yaml | Module import/CLI chưa hỗ trợ đặc tả; schema cũ khác cấu hình mục tiêu | TV3/TV5: config_chot.yaml, import package, --config, --scenarios |
| R8 | Bằng chứng thiếu | runner/log/plot | Thiếu samples/config snapshot/commit/version; plot sai số chưa có CTRV; trajectory_2d chỉ scatter d tại y=0 | TV5: dữ liệu từng mẫu, log, timeline và alignment thật |

## Điều kiện đóng findings

Dùng [checklist TV1](TV1_HANDOFF.md). Chạy lại sau sửa; giữ commit/config/lệnh và số liệu tái lập. Lỗi R1–R5 phải được xử lý trước khi diễn giải failure. Tình trạng nguồn tham khảo và thông tin thành viên còn phải hoàn thiện riêng.
