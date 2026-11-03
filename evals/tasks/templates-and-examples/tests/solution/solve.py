from rand_engine import DataGenerator, RandSpecs

customers = DataGenerator(RandSpecs.customers(), seed=42).size(200).get_df()
customers.to_parquet("customers.parquet")

orders = DataGenerator(RandSpecs.orders(), seed=42).size(1000).get_df()
orders.to_parquet("orders.parquet")
