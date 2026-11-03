from rand_engine import DataGenerator

customer_pk = {"method": "pk", "kwargs": {"start": 1}}
customers = {"customer_id": customer_pk}
orders = {
    "order_id": {"method": "pk", "kwargs": {"start": 1}},
    "customer_id": {"method": "fk", "kwargs": {"parent": customer_pk, "parent_size": 1000}},
}
DataGenerator(customers, seed=1).size(1000).get_df().to_parquet("customers.parquet")
DataGenerator(orders, seed=2).size(5000).get_df().to_parquet("orders.parquet")
