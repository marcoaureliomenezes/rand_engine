from rand_engine import DataGenerator

spec = {
    "product_id": {"method": "pk", "kwargs": {"style": "sequence", "start": 1}},
    "views": {"method": "zipf", "kwargs": {"a": 1.5}},
}
DataGenerator(spec, seed=42).size(5000).get_df().to_csv("product_views.csv", index=False)
