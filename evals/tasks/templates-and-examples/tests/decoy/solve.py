import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

customers = pd.DataFrame({
    "customer_id": [f"c{i}" for i in range(200)],
    "age": rng.integers(18, 81, 200),
    "city": rng.choice(["São Paulo", "Rio de Janeiro", "Curitiba"], 200),
    "total_spent": rng.normal(1500, 500, 200).round(2),
    "is_premium": rng.random(200) < 0.15,
    "registration_date": rng.choice(["2021-01-01", "2023-06-15"], 200),
})
customers.to_parquet("customers.parquet")

orders = pd.DataFrame({
    "order_id": [f"o{i}" for i in range(1000)],
    "customer_id": rng.choice(customers["customer_id"], 1000),
    "amount": rng.normal(200, 100, 1000).round(2),
    "order_timestamp": rng.choice(["2025-01-02", "2025-05-20"], 1000),
    "status": rng.choice(["completed", "pending", "cancelled"], 1000),
    "payment_method": rng.choice(["credit_card", "pix", "boleto"], 1000),
})
orders.to_parquet("orders.parquet")

pool = [f"City {i:02d}" for i in range(50)]
pd.DataFrame({"city": rng.choice(pool, 500)}).to_parquet("cities.parquet")
