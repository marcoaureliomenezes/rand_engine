from rand_engine import DataGenerator

spec = {
    "age": {"method": "integers", "kwargs": {"min": 18, "max": 80}},
    "country": {"method": "distincts", "kwargs": {"distincts": ["BR", "US", "DE"]}},
    "amount": {"method": "floats", "kwargs": {"min": 1, "max": 500, "decimals": 2}},
}

DataGenerator(spec, seed=42).size(1000).write.format("csv").option("compression", "gzip").save("customers.csv.gz")
(DataGenerator(spec, seed=42).size(10).writeStream
    .format("csv").trigger(frequency=0.2).option("timeout", 1).start("stream_out"))
