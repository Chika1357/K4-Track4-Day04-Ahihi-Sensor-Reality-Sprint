# Quickstart T4 — phân biệt code hiện tại và thiết kế mục tiêu

## 1. Cài dependencies

~~~powershell
python -m pip install -r requirements.txt
~~~

## 2. Kiểm tra lại phiên bản cũ

Các lệnh này chạy với schema cũ trong config.yaml:

~~~powershell
python src/run_benchmark.py config.yaml
python src/plot.py results/results.csv plots/
~~~

Runner ghi đè results/results.csv và results/benchmark.log; chỉ chạy trong bản sao kiểm tra nếu cần giữ bằng chứng cũ. CSV/plot phiên bản này có lỗi toán và ghép thời điểm, chưa dùng để báo cáo failure sensor. Xem [review](reports/CODE_REVIEW_T4.md).

Runner hiện tại nhận đường dẫn config dạng positional; chưa hỗ trợ --config, --scenarios hoặc chạy dạng module theo thiết kế mục tiêu.

## 3. Giao diện mục tiêu sau khi TV3/TV4/TV5 sửa

~~~powershell
python -m src.run_benchmark --config config_chot.yaml --scenarios A C
python -m src.run_benchmark --config config_chot.yaml
~~~

Hai lệnh trên là yêu cầu cần hiện thực, chưa phải hướng dẫn chạy thành công cho code hiện tại. A/C là phần ưu tiên, B là mở rộng.

## 4. Nghiệm thu trước khi dùng số đo

- Cùng 100 mẫu, ground truth và noise giữa offset/phương án.
- Offset 0: ba phương án trùng nhau, sai số gần mức nhiễu.
- Thẳng 20 m/s, 100 ms: trước bù gần 2 m, sau bù gần noise.
- Rẽ: đúng quỹ đạo tròn, CTRV dùng tịnh tiến và quay.
- Có samples.csv, bảng tổng hợp, config_used.yaml, log phiên bản/commit và plot ba phương án.
- Formula deviation tại offset 0 là N/A; ngưỡng 0,5 m do nhóm đặt.

Checklist đầy đủ: [việc TV1 và nghiệm thu](reports/TV1_HANDOFF.md).
