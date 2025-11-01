from typing import Dict, Any


class CommonRandSpecs:
    """
    Cross-compatible specification examples for DataGenerator and SparkGenerator.
    
    All specs use the unified API with date_format parameter.
    """

    @classmethod
    def customers(cls) -> Dict[str, Any]:
        """Customer profiles (6 Fields)"""
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
        """Product catalog (7 Fields)"""
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
        """E-commerce orders (6 Fields)"""
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
        """Financial transactions (7 Fields)"""
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
        """Employee records (8 Fields)"""
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
        """IoT sensor readings (7 Fields)"""
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
        """Application users (7 Fields)"""
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
        """System event logs (6 Fields)"""
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
        """Sales records (8 Fields)"""
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
        """Device inventory (7 Fields)"""
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
