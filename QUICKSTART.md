# Quickstart T4 — benchmark hiện tại

Chạy từ thư mục gốc repository. Cấu hình đang dùng là `config_chot.yaml`; `config.yaml` giữ schema lịch sử và không dùng với runner hiện tại.

## 1. Môi trường

TV1 đã đối chiếu lại kết quả với Python 3.11.9, NumPy 1.26.4, pandas 2.2.3, matplotlib 3.10.1 và PyYAML 6.0.2. `requirements.txt` chốt các phiên bản thư viện này. Log TV5 cũ dùng môi trường khác; không coi log đó là bằng chứng cài đặt theo requirements mới.

~~~powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
~~~

Nếu không có Python launcher `py`, dùng Python 3.11 đang cài để tạo venv. Venv dùng riêng cho phép thử, không cần kích hoạt PowerShell.

## 2. Chạy toàn bộ và tạo plot

~~~powershell
.\.venv\Scripts\python.exe -m src.run_benchmark --config config_chot.yaml
.\.venv\Scripts\python.exe -m src.plot --config config_chot.yaml
~~~

Kỳ vọng: 45 điều kiện, 4.500 mẫu; `results/results.csv`, `results/samples.csv`, `results/config_used.yaml`, `results/run_log.txt`; các plot `timeline.png`, `error_vs_offset.png`, `alignment_turn.png`. Runner ghi đè bằng chứng ở `results/`; plot ghi đè ảnh ở `plots/`. Lưu bản kết quả cần giữ trước khi chạy lại.

Nếu chỉ chạy phần tối thiểu A/C:

~~~powershell
.\.venv\Scripts\python.exe -m src.run_benchmark --config config_chot.yaml --scenarios A C
.\.venv\Scripts\python.exe -m src.plot --config config_chot.yaml
~~~

Kỳ vọng: 30 điều kiện, 3.000 mẫu. Sau lệnh này CSV chỉ có A/C; không dùng nó để báo cáo B. Plot C cần có C trong tập vừa chạy.

## 3. Kiểm tra nhanh

- Offset 0: ba phương án có cùng sai số nền khoảng 2–3 cm.
- A, d=20 m, offset=100 ms: trước bù gần 2 m, sau bù gần nhiễu.
- C, d=40 m, offset=100 ms: linear còn lỗi rõ; CTRV gần nhiễu trong giả định biết đúng offset/trạng thái.
- Metric chính: mean/max sai số vị trí theo mét. `over_threshold` chỉ là mean của linear > 0,5 m, không phải tỷ lệ mẫu lỗi hay chứng nhận an toàn.
- Bảng báo cáo phải lấy từ CSV của chính lần chạy; đối chiếu cấu hình và commit.

## 4. Phần mở rộng TV2

`src/estimate_offset.py` có demo độc lập; nó không phải benchmark bù chính. `src/run_estimate_on_sim.py` đang cần TV2 cập nhật API với `src/simulate.py`; chưa dùng kết quả cũ của wrapper làm bằng chứng tái hiện trên phiên bản hiện tại. KITTI là nhánh mở rộng dùng chuyển động thật với điểm ảo/offset nhân tạo, không thay thế benchmark chính.

Trạng thái nghiệm thu và các lỗi còn mở: [TV1_HANDOFF](reports/TV1_HANDOFF.md). Báo cáo hiện tại: [TV1_REPORT](reports/TV1_REPORT.md).
