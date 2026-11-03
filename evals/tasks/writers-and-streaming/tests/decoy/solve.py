import os, time, uuid

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)


def frame(n):
    return pd.DataFrame({"age": rng.integers(18, 81, n), "country": rng.choice(["BR", "US", "DE"], n),
                         "amount": rng.uniform(1, 500, n).round(2)})


frame(1000).to_csv("customers.csv.gz", index=False, compression="gzip")
os.makedirs("stream_out", exist_ok=True)
end = time.time() + 1
while time.time() < end:
    frame(10).to_csv(f"stream_out/part-{uuid.uuid4()}.csv", index=False)
    time.sleep(0.2)
