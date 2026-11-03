from rand_engine import DataGenerator  # noqa: F401

spec = {
    "id": {"method": "pk", "kwargs": {"start": 1}},
    "name": {"method": "distincts", "kwargs": {"distincts": ["ana", "bia", "caio"]}},
    "amount": {"method": "integer", "kwargs": {"min": 1, "max": 500}},
    "status": {"method": "distincts", "kwargs": {"distincts": ["new", "paid"]}},
}
