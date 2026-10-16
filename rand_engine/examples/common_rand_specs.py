"""Ready-made RandSpec factories for DataGenerator and SparkGenerator."""
import copy
from typing import Dict, Any

import pyarrow as pa

from rand_engine.validators.advanced_validator import AdvancedValidator
from rand_engine.validators.exceptions import RandEngineError, SpecValidationError
from rand_engine.validators.method_specs import is_declared_scalar


class CommonRandSpecs:
    """
    Cross-compatible specification examples for DataGenerator and SparkGenerator.
    
    All specs use the unified API with date_format parameter.

    Examples
    --------
    >>> from rand_engine import DataGenerator, RandSpecs
    >>> df = DataGenerator(RandSpecs.customers(), seed=42).size(100).get_df()
    >>> list(df.columns)
    ['customer_id', 'age', 'city', 'total_spent', 'is_premium', 'registration_date']
    >>> len(df)
    100
    """

    @classmethod
    def faker_pool(
        cls,
        provider: str,
        locale: str = "en_US",
        pool_size: int = 100,
        seed: int | None = None,
    ) -> Dict[str, Any]:
        """
        Build one materialized distincts spec with a local Faker instance.

        Parameters
        ----------
        provider : str
            Faker provider method, such as ``"name"`` or ``"city"``.
        locale : str, default "en_US"
            Faker locale; an unsupported locale raises RandEngineError.
        pool_size : int, default 100
            Number of values to materialize; a positive integer.
        seed : int, optional
            Seed of the Faker instance; the same seed gives the same pool.

        Returns
        -------
        dict
            A ``distincts`` RandSpec whose ``distincts`` list holds the pool.

        Raises
        ------
        RandEngineError
            If Faker is not installed, the locale or provider is unsupported, or a value is not scalar.
        """
        if isinstance(pool_size, bool) or not isinstance(pool_size, int) or pool_size < 1:
            raise RandEngineError("pool_size must be a positive integer")

        try:
            from faker import Faker
        except ImportError as error:
            raise RandEngineError(
                "Faker is an optional dependency; install rand-engine[faker]"
            ) from error

        try:
            faker = Faker(locale)
        except Exception as error:
            raise RandEngineError("locale is not supported by Faker") from error

        try:
            faker.seed_instance(seed)
            factory = getattr(faker, provider)
        except (AttributeError, TypeError, ValueError) as error:
            raise RandEngineError("provider is not supported by Faker") from error
        if not callable(factory):
            raise RandEngineError("provider is not callable")

        try:
            values = [factory() for _ in range(pool_size)]
        except Exception as error:
            raise RandEngineError("provider failed while constructing the pool") from error
        if any(not is_declared_scalar(value) for value in values):
            raise RandEngineError("provider outputs must be scalar values")

        return {"method": "distincts", "kwargs": {"distincts": values}}

    @classmethod
    def from_schema(
        cls,
        schema: pa.Schema,
        overrides: dict[str, dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        """
        Build a validated RandSpec from Arrow field metadata only.

        Parameters
        ----------
        schema : pyarrow.Schema
            Arrow schema; each field's type picks a default generation recipe.
        overrides : dict, optional
            Per-field overrides keyed by field name. A ``method`` key replaces the recipe; ``kwargs`` merge into it.

        Returns
        -------
        dict
            RandSpec with one entry per schema field, validated before return.

        Raises
        ------
        SpecValidationError
            If the schema has duplicate fields, an override names a missing field, or a field type has no default recipe and no complete override with ``method``.
        """
        if not isinstance(schema, pa.Schema):
            raise SpecValidationError("from_schema requires a pyarrow.Schema")
        if overrides is None:
            overrides = {}
        if not isinstance(overrides, dict):
            raise SpecValidationError("overrides must be a dictionary")
        if any(not isinstance(value, dict) for value in overrides.values()):
            raise SpecValidationError("each field override must be a dictionary")

        names = schema.names
        duplicate_names = sorted({name for name in names if names.count(name) > 1})
        if duplicate_names:
            details = ", ".join(
                f"{name} ({', '.join(str(field.type) for field in schema if field.name == name)})"
                for name in duplicate_names
            )
            raise SpecValidationError(
                f"duplicate schema fields: {details}; rename or remove each duplicate"
            )

        unknown = sorted(set(overrides) - set(names))
        if unknown:
            raise SpecValidationError(
                f"override names missing schema fields: {', '.join(unknown)}"
            )

        copied_overrides = copy.deepcopy(overrides)
        result: Dict[str, Any] = {}
        for field in schema:
            override = copied_overrides.get(field.name, {})
            if "method" in override:
                result[field.name] = override
                continue

            recipe = cls._schema_recipe(field.type)
            if recipe is None:
                raise SpecValidationError(
                    f"field '{field.name}' type '{field.type}' requires a complete override with method"
                )

            column = copy.deepcopy(recipe)
            override_kwargs = override.get("kwargs", {})
            if not isinstance(override_kwargs, dict):
                raise SpecValidationError(
                    f"field '{field.name}' override kwargs must be a dictionary"
                )
            column["kwargs"].update(override_kwargs)
            column.update({key: value for key, value in override.items() if key != "kwargs"})
            result[field.name] = column

        AdvancedValidator.validate_and_raise(result)
        return result

    @staticmethod
    def _schema_recipe(arrow_type: pa.DataType) -> Dict[str, Any] | None:
        if pa.types.is_boolean(arrow_type):
            return {"method": "booleans", "kwargs": {"true_prob": 0.5}}
        if pa.types.is_integer(arrow_type):
            return {
                "method": "integers",
                "kwargs": {
                    "min": 0,
                    "max": min(100, 2 ** arrow_type.bit_width - 1),
                    "int_type": str(arrow_type),
                },
            }
        if pa.types.is_floating(arrow_type):
            return {
                "method": "floats",
                "kwargs": {"min": 0, "max": 1, "decimals": 2},
            }
        if pa.types.is_string(arrow_type) or pa.types.is_large_string(arrow_type):
            return {"method": "uuid4", "kwargs": {}}
        if pa.types.is_date(arrow_type):
            return {
                "method": "dates",
                "kwargs": {
                    "start": "2000-01-01",
                    "end": "2030-12-31",
                    "date_format": "%Y-%m-%d",
                },
            }
        if pa.types.is_timestamp(arrow_type) and arrow_type.tz is None:
            return {
                "method": "dates",
                "kwargs": {
                    "start": "2000-01-01",
                    "end": "2030-12-31",
                    "date_format": "%Y-%m-%d %H:%M:%S",
                },
            }
        if pa.types.is_null(arrow_type):
            return {"method": "constant", "kwargs": {"value": None}}
        return None

    @classmethod
    def customers(cls) -> Dict[str, Any]:
        """
        Return the customer profiles RandSpec (6 Fields).

        Returns
        -------
        dict
            RandSpec mapping each of the 6 fields to its method and kwargs.
        """
        return {
            "customer_id": {"method": "uuid4", "kwargs": {}},
            "age": {"method": "integers", "kwargs": {"min": 18, "max": 80, "int_type": "int32"}},
            "city": {
                "method": "distincts",
                "kwargs": {
                    "distincts": ["São Paulo", "Rio de Janeiro", "Belo Horizonte",
                                "Salvador", "Brasília", "Curitiba", "Porto Alegre"]
                }
            },
            "total_spent": {"method": "floats_normal", "kwargs": {"mean": 1500.0, "std": 500.0, "decimals": 2}},
            "is_premium": {"method": "booleans", "kwargs": {"true_prob": 0.15}},
            "registration_date": {
                "method": "dates",
                "kwargs": {"start": "2020-01-01", "end": "2025-10-30", "date_format": "%Y-%m-%d"}
            }
        }

    @classmethod
    def products(cls) -> Dict[str, Any]:
        """
        Return the product catalog RandSpec (7 Fields).

        Returns
        -------
        dict
            RandSpec mapping each of the 7 fields to its method and kwargs.
        """
        return {
            "product_id": {"method": "uuid4", "kwargs": {}},
            "sku": {"method": "int_zfilled", "kwargs": {"length": 8}},
            "name": {
                "method": "distincts",
                "kwargs": {
                    "distincts": ["Laptop Pro", "Wireless Mouse", "USB-C Cable",
                                "Mechanical Keyboard", "Monitor 27inch", "Webcam HD",
                                "Headset Gaming", "SSD 1TB", "RAM 16GB", "Charger USB"]
                }
            },
            "price": {"method": "floats", "kwargs": {"min": 9.99, "max": 2999.99, "decimals": 2}},
            "stock_quantity": {"method": "integers", "kwargs": {"min": 0, "max": 500, "int_type": "int32"}},
            "category": {
                "method": "distincts_prop",
                "kwargs": {
                    "distincts": {"Electronics": 40, "Accessories": 30, "Computers": 20, "Peripherals": 10}
                }
            },
            "is_active": {"method": "booleans", "kwargs": {"true_prob": 0.85}}
        }

    @classmethod
    def orders(cls) -> Dict[str, Any]:
        """
        Return the e-commerce orders RandSpec (6 Fields).

        Returns
        -------
        dict
            RandSpec mapping each of the 6 fields to its method and kwargs.
        """
        return {
            "order_id": {"method": "uuid4", "kwargs": {}},
            "customer_id": {"method": "uuid4", "kwargs": {}},
            "amount": {"method": "floats_normal", "kwargs": {"mean": 200.0, "std": 100.0, "decimals": 2}},
            "order_timestamp": {
                "method": "unix_timestamps",
                "kwargs": {"start": "2025-01-01", "end": "2025-10-30", "date_format": "%Y-%m-%d"}
            },
            "status": {
                "method": "distincts_prop",
                "kwargs": {"distincts": {"completed": 70, "pending": 20, "cancelled": 10}}
            },
            "payment_method": {
                "method": "distincts",
                "kwargs": {"distincts": ["credit_card", "debit_card", "pix", "boleto"]}
            }
        }

    @classmethod
    def transactions(cls) -> Dict[str, Any]:
        """
        Return the financial transactions RandSpec (7 Fields).

        Returns
        -------
        dict
            RandSpec mapping each of the 7 fields to its method and kwargs.
        """
        return {
            "transaction_id": {"method": "uuid4", "kwargs": {}},
            "account_id": {"method": "uuid4", "kwargs": {}},
            "amount": {"method": "floats", "kwargs": {"min": 10.0, "max": 5000.0, "decimals": 2}},
            "transaction_type": {
                "method": "distincts",
                "kwargs": {"distincts": ["deposit", "withdrawal", "transfer", "payment"]}
            },
            "timestamp": {
                "method": "unix_timestamps",
                "kwargs": {"start": "2025-01-01", "end": "2025-10-30", "date_format": "%Y-%m-%d"}
            },
            "is_approved": {"method": "booleans", "kwargs": {"true_prob": 0.90}},
            "fee": {"method": "floats", "kwargs": {"min": 0.0, "max": 50.0, "decimals": 2}}
        }

    @classmethod
    def employees(cls) -> Dict[str, Any]:
        """
        Return the employee records RandSpec (8 Fields).

        Returns
        -------
        dict
            RandSpec mapping each of the 8 fields to its method and kwargs.
        """
        return {
            "employee_id": {"method": "uuid4", "kwargs": {}},
            "department": {
                "method": "distincts_prop",
                "kwargs": {"distincts": {"Engineering": 50, "Product": 20, "Data": 15, "Operations": 15}}
            },
            "position": {
                "method": "distincts",
                "kwargs": {
                    "distincts": ["Software Engineer", "Data Analyst", "Product Manager",
                                "DevOps Engineer", "QA Engineer", "Designer"]
                }
            },
            "salary": {"method": "floats_normal", "kwargs": {"mean": 50000.0, "std": 15000.0, "decimals": 2}},
            "hire_date": {
                "method": "dates",
                "kwargs": {"start": "2018-01-01", "end": "2025-10-30", "date_format": "%Y-%m-%d"}
            },
            "age": {"method": "integers", "kwargs": {"min": 22, "max": 65, "int_type": "int32"}},
            "is_remote": {"method": "booleans", "kwargs": {"true_prob": 0.30}},
            "performance_score": {"method": "floats", "kwargs": {"min": 0.0, "max": 10.0, "decimals": 1}}
        }

    @classmethod
    def sensors(cls) -> Dict[str, Any]:
        """
        Return the IoT sensor readings RandSpec (7 Fields).

        Returns
        -------
        dict
            RandSpec mapping each of the 7 fields to its method and kwargs.
        """
        return {
            "sensor_id": {"method": "uuid4", "kwargs": {}},
            "device_name": {"method": "int_zfilled", "kwargs": {"length": 6}},
            "temperature": {"method": "floats_normal", "kwargs": {"mean": 25.0, "std": 5.0, "decimals": 1}},
            "humidity": {"method": "floats", "kwargs": {"min": 30.0, "max": 90.0, "decimals": 1}},
            "battery_level": {"method": "integers", "kwargs": {"min": 0, "max": 100, "int_type": "int32"}},
            "timestamp": {
                "method": "unix_timestamps",
                "kwargs": {"start": "2025-10-01", "end": "2025-10-30", "date_format": "%Y-%m-%d"}
            },
            "is_online": {"method": "booleans", "kwargs": {"true_prob": 0.95}}
        }

    @classmethod
    def users(cls) -> Dict[str, Any]:
        """
        Return the application users RandSpec (7 Fields).

        Returns
        -------
        dict
            RandSpec mapping each of the 7 fields to its method and kwargs.
        """
        return {
            "user_id": {"method": "uuid4", "kwargs": {}},
            "username": {"method": "int_zfilled", "kwargs": {"length": 10}},
            "signup_date": {
                "method": "dates",
                "kwargs": {"start": "2023-01-01", "end": "2025-10-30", "date_format": "%Y-%m-%d"}
            },
            "login_count": {"method": "integers", "kwargs": {"min": 0, "max": 1000, "int_type": "int32"}},
            "subscription_plan": {
                "method": "distincts_prop",
                "kwargs": {"distincts": {"free": 60, "basic": 25, "premium": 10, "enterprise": 5}}
            },
            "is_active": {"method": "booleans", "kwargs": {"true_prob": 0.80}},
            "engagement_score": {"method": "floats", "kwargs": {"min": 0.0, "max": 100.0, "decimals": 1}}
        }

    @classmethod
    def events(cls) -> Dict[str, Any]:
        """
        Return the system event logs RandSpec (6 Fields).

        Returns
        -------
        dict
            RandSpec mapping each of the 6 fields to its method and kwargs.
        """
        return {
            "event_id": {"method": "uuid4", "kwargs": {}},
            "event_type": {
                "method": "distincts",
                "kwargs": {
                    "distincts": ["user_login", "user_logout", "page_view",
                                "api_call", "database_query", "file_upload"]
                }
            },
            "timestamp": {
                "method": "unix_timestamps",
                "kwargs": {"start": "2025-10-01", "end": "2025-10-30", "date_format": "%Y-%m-%d"}
            },
            "duration_ms": {"method": "integers", "kwargs": {"min": 0, "max": 5000, "int_type": "int32"}},
            "is_error": {"method": "booleans", "kwargs": {"true_prob": 0.10}},
            "severity": {
                "method": "distincts_prop",
                "kwargs": {"distincts": {"info": 70, "warning": 20, "error": 8, "critical": 2}}
            }
        }

    @classmethod
    def sales(cls) -> Dict[str, Any]:
        """
        Return the sales records RandSpec (8 Fields).

        Returns
        -------
        dict
            RandSpec mapping each of the 8 fields to its method and kwargs.
        """
        return {
            "transaction_id": {"method": "uuid4", "kwargs": {}},
            "sale_id": {"method": "int_zfilled", "kwargs": {"length": 10}},
            "product_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
            "amount": {"method": "floats_normal", "kwargs": {"mean": 500.0, "std": 200.0, "decimals": 2}},
            "quantity": {"method": "integers", "kwargs": {"min": 1, "max": 50, "int_type": "int32"}},
            "sales_rep": {
                "method": "distincts",
                "kwargs": {
                    "distincts": ["Alice Smith", "Bob Johnson", "Carol Williams",
                                "David Brown", "Emma Davis", "Frank Miller"]
                }
            },
            "sale_date": {
                "method": "dates",
                "kwargs": {"start": "2025-01-01", "end": "2025-10-30", "date_format": "%Y-%m-%d"}
            },
            "is_wholesale": {"method": "booleans", "kwargs": {"true_prob": 0.20}}
        }

    @classmethod
    def devices(cls) -> Dict[str, Any]:
        """
        Return the device inventory RandSpec (7 Fields).

        Returns
        -------
        dict
            RandSpec mapping each of the 7 fields to its method and kwargs.
        """
        return {
            "device_id": {"method": "uuid4", "kwargs": {}},
            "serial_number": {"method": "int_zfilled", "kwargs": {"length": 12}},
            "firmware_version": {
                "method": "distincts",
                "kwargs": {"distincts": ["v1.0.0", "v1.1.0", "v1.2.0", "v2.0.0", "v2.1.0"]}
            },
            "uptime_hours": {"method": "floats_normal", "kwargs": {"mean": 500.0, "std": 200.0, "decimals": 1}},
            "status": {
                "method": "distincts_prop",
                "kwargs": {"distincts": {"online": 80, "offline": 10, "maintenance": 7, "error": 3}}
            },
            "is_critical": {"method": "booleans", "kwargs": {"true_prob": 0.15}},
            "last_seen": {
                "method": "unix_timestamps",
                "kwargs": {"start": "2025-10-01", "end": "2025-10-30", "date_format": "%Y-%m-%d"}
            }
        }
