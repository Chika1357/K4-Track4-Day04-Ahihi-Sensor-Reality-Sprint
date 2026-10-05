# Slide 4 - Results (TV5, 60 seconds)

Use `plots/error_vs_offset.png`. All values are from `results/results.csv`; data are synthetic.

| Scenario | Offset | Distance | E_pre mean | E_post linear | E_post CTRV |
|---|---:|---:|---:|---:|---:|
| A | 0 ms | 20 m | 0.024 m | 0.024 m | 0.024 m |
| A | 100 ms | 20 m | 2.001 m | 0.026 m | 0.026 m |
| B | 100 ms | 20 m | 2.505 m | 0.041 m | 0.041 m |
| C | 50 ms | 40 m | 0.828 m | 0.678 m | 0.025 m |
| C | 100 ms | 40 m | 1.668 m | 1.351 m | 0.025 m |
| C | 200 ms | 40 m | 3.348 m | 2.693 m | 0.025 m |

“Nhóm quan sát được baseline 0 ms chỉ khoảng 2-3 cm. Khi xe chạy thẳng 20 m/s và lệch 100 ms, E_pre là 2.001 m, gần bằng v x Delta t = 2 m; bù tuyến tính đưa sai số về mức nhiễu. Khi rẽ, d = 40 m và offset = 100 ms, bù tuyến tính vẫn còn 1.351 m, vượt ngưỡng 0.5 m; CTRV giảm còn 0.025 m trên cùng mẫu.”

Limitation: benchmark synthetic 2-D, không đo detector, tracker hoặc latency đầu-cuối.
