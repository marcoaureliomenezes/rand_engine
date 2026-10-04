# Speed benchmark

commit `9d5a0963f5c066d7a3391da1b407146388a3ff45` · Python 3.12.14 · NumPy 2.1.1 · GitHub Actions 1000032270

| method / sink | rows | rows/µs | median s | baseline s | ratio | peak MiB |
|---|---|---|---|---|---|---|
| integers | 1,000,000 | 155.144 | 0.006 | — | absent → recorded | 15.3 |
| int_zfilled | 1,000,000 | 3.402 | 0.294 | — | absent → recorded | 125.9 |
| floats | 1,000,000 | 67.585 | 0.015 | — | absent → recorded | 30.6 |
| floats_normal | 1,000,000 | 42.195 | 0.024 | — | absent → recorded | 15.3 |
| distincts | 1,000,000 | 39.588 | 0.025 | — | absent → recorded | 19.1 |
| distincts_prop | 1,000,000 | 13.499 | 0.074 | — | absent → recorded | 82.8 |
| unix_timestamps | 1,000,000 | 104.049 | 0.010 | — | absent → recorded | 15.3 |
| uuid4 | 1,000,000 | 0.306 | 3.286 | — | absent → recorded | 226.0 |
| booleans | 1,000,000 | 62.155 | 0.016 | — | absent → recorded | 22.9 |
| dates | 1,000,000 | 0.351 | 2.850 | — | absent → recorded | 102.5 |
| distincts_map | 1,000,000 | 5.414 | 0.184 | — | absent → recorded | 87.1 |
| distincts_multi_map | 1,000,000 | 3.859 | 0.260 | — | absent → recorded | 102.8 |
| distincts_map_prop | 1,000,000 | 5.305 | 0.188 | — | absent → recorded | 87.1 |
| complex_distincts | 1,000,000 | 0.839 | 1.191 | — | absent → recorded | 438.7 |
| pk | 1,000,000 | 450.323 | 0.002 | — | absent → recorded | 22.9 |
| fk | 1,000,000 | 33.422 | 0.030 | — | absent → recorded | 45.8 |
| integers | 10,000,000 | 121.051 | 0.083 | — | absent → recorded | 152.6 |
| int_zfilled | 10,000,000 | 3.419 | 2.926 | — | absent → recorded | 1258.9 |
| floats | 10,000,000 | 66.928 | 0.149 | — | absent → recorded | 305.2 |
| floats_normal | 10,000,000 | 36.769 | 0.272 | — | absent → recorded | 152.6 |
| distincts | 10,000,000 | 35.558 | 0.282 | — | absent → recorded | 190.7 |
| distincts_prop | 10,000,000 | 13.035 | 0.768 | — | absent → recorded | 827.8 |
| unix_timestamps | 10,000,000 | 105.198 | 0.095 | — | absent → recorded | 152.6 |
| uuid4 | 10,000,000 | 0.304 | 32.823 | — | absent → recorded | 2260.2 |
| booleans | 10,000,000 | 62.183 | 0.161 | — | absent → recorded | 228.9 |
| dates | 10,000,000 | 0.349 | 28.626 | — | absent → recorded | 1029.1 |
| distincts_map | 10,000,000 | 5.440 | 1.836 | — | absent → recorded | 884.3 |
| distincts_multi_map | 10,000,000 | 3.791 | 2.612 | — | absent → recorded | 1045.6 |
| distincts_map_prop | 10,000,000 | 5.319 | 1.882 | — | absent → recorded | 884.3 |
| complex_distincts | 10,000,000 | 0.834 | 12.002 | — | absent → recorded | 4386.9 |
| pk | 10,000,000 | 264.401 | 0.038 | — | absent → recorded | 228.9 |
| fk | 10,000,000 | 19.565 | 0.512 | — | absent → recorded | 457.8 |
| csv | 1,000,000 | 0.114 | 8.790 | — | absent → recorded | — |
| parquet | 1,000,000 | 0.146 | 6.840 | — | absent → recorded | — |
| json | 1,000,000 | 0.127 | 7.884 | — | absent → recorded | — |
| stream_dict | 1,000,000 | 0.106 | 9.438 | — | absent → recorded | — |
