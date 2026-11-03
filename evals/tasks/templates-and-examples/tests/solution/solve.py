from rand_engine import DataGenerator, RandSpecs

customers = DataGenerator(RandSpecs.customers(), seed=42).size(200).get_df()
customers.to_parquet("customers.parquet")

orders = DataGenerator(RandSpecs.orders(), seed=42).size(1000).get_df()
orders.to_parquet("orders.parquet")

cities_spec = {"city": RandSpecs.faker_pool("city", locale="en_US", pool_size=50, seed=7)}
cities = DataGenerator(cities_spec, seed=42).size(500).get_df()
cities.to_parquet("cities.parquet")
