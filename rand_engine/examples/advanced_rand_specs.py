from typing import Dict, Any


class AdvancedRandSpecs:
    """
    Advanced specification examples showcasing PyCore-exclusive methods for DataGenerator.
    
    AdvancedRandSpecs demonstrates sophisticated data generation patterns using methods
    that are currently only available in DataGenerator (not yet in SparkGenerator).
    These specs focus on correlated data, complex patterns, and hierarchical relationships.
    
    PyCore-Exclusive Methods:
    ------------------------
    - distincts_map: Generate correlated pairs (e.g., currency-country)
    - distincts_multi_map: Generate hierarchical correlations (3+ levels)
    - distincts_map_prop: Weighted correlated pairs with nested probabilities
    - complex_distincts: Pattern-based generation with template replacement
    
    Available Specs:
    ---------------
    - products: Product catalog with complex SKU patterns
    - orders: E-commerce orders with currency-country correlations
    - employees: Employee hierarchy with department-level-role correlations
    - devices: IoT devices with status-priority weighted correlations
    - invoices: Invoice records with pattern-based numbering
    - shipments: Shipping data with carrier-destination correlations
    - network_devices: Network infrastructure with IP patterns
    - vehicles: Vehicle fleet with make-model-year correlations
    - real_estate: Property listings with location-type correlations
    - healthcare: Patient records with diagnosis-treatment patterns
    
    Usage Examples:
    --------------
    
    # Basic usage
    >>> from rand_engine import DataGenerator
    >>> from rand_engine.examples.advanced_rand_specs import AdvancedRandSpecs
    >>> 
    >>> df = DataGenerator(AdvancedRandSpecs.products(), seed=42).size(1000).get_df()
    >>> print(df.head())
    
    # Exploring correlations
    >>> df = DataGenerator(AdvancedRandSpecs.employees(), seed=42).size(500).get_df()
    >>> print(df[['department', 'level', 'role']].drop_duplicates())
    
    # Pattern-based generation
    >>> df = DataGenerator(AdvancedRandSpecs.network_devices(), seed=42).size(100).get_df()
    >>> print(df['ip_address'].unique()[:5])  # Shows generated IPs like "192.168.1.45"
    
    Notes:
    ------
    - These specs work ONLY with DataGenerator (pandas)
    - For cross-compatible specs, use CommonRandSpecs from common_rand_specs.py
    - Static class - no instantiation required
    - Each spec demonstrates 1-2 advanced patterns
    - Specs range from 5-8 fields for realistic complexity
    """

    @classmethod
    def products(cls) -> Dict[str, Any]:
        """
        Product catalog with complex SKU patterns.
        
        **Advanced Pattern**: complex_distincts for SKU generation (PRD-XXXX format)
        
        Fields (6):
        ----------
        - sku: Pattern-based SKU "PRD-1234" using complex_distincts
        - product_name: Random product names
        - category: Weighted categories (Electronics 50%, Clothing 30%, Food 20%)
        - price: Product prices 5-500
        - stock: Inventory levels 0-1000
        - rating: Normally distributed ratings (mean=4.0, std=0.8)
        
        Key Learning:
        ------------
        - complex_distincts: Pattern "PRD-x" where x is replaced by template (integers 1000-9999)
        - Templates use "kwargs" dict for parameters
        - Useful for generating codes, IDs, serial numbers
        
        Returns:
        -------
        Dict[str, Any]: Specification for advanced product catalog
        """
        return {
            "sku": {
                "method": "complex_distincts",
                "kwargs": {
                    "pattern": "PRD-x",
                    "replacement": "x",
                    "templates": [
                        {"method": "integers", "kwargs": {"min": 1000, "max": 9999, "dtype": "int32"}}
                    ]
                }
            },
            "product_name": {
                "method": "distincts",
                "kwargs": {
                    "distincts": ["Laptop", "Smartphone", "T-Shirt", "Jeans", "Coffee", "Bread"]
                }
            },
            "category": {
                "method": "distincts_prop",
                "kwargs": {"distincts": {"Electronics": 50, "Clothing": 30, "Food": 20}}
            },
            "price": {
                "method": "floats",
                "kwargs": {"min": 5.0, "max": 500.0, "decimals": 2}
            },
            "stock": {
                "method": "integers",
                "kwargs": {"min": 0, "max": 1000, "dtype": "int32"}
            },
            "rating": {
                "method": "floats_normal",
                "kwargs": {"mean": 4.0, "std": 0.8, "decimals": 1}
            }
        }

    @classmethod
    def orders(cls) -> Dict[str, Any]:
        """
        E-commerce orders with currency-country correlations.
        
        **Advanced Pattern**: distincts_map for currency-country pairs
        
        Fields (7):
        ----------
        - order_id: UUID4 unique identifiers
        - order_date: Unix timestamps from 2023
        - amount: Order amounts 10-5000
        - status: Order status (Pending 20%, Completed 70%, Cancelled 10%)
        - payment_method: Payment types
        - currency, country: Correlated pairs via distincts_map (splits into 2 columns)
        
        Key Learning:
        ------------
        - distincts_map: Maps countries to currencies (US→USD, DE→EUR, BR→BRL, JP→JPY)
        - splitable=True: Generates single column then splits into multiple
        - sep=";": Delimiter for splitting
        - cols=[]: Resulting column names after split
        
        Returns:
        -------
        Dict[str, Any]: Specification for orders with currency-country correlation
        """
        return {
            "order_id": {
                "method": "uuid4",
                "kwargs": {}
            },
            "order_date": {
                "method": "unix_timestamps",
                "kwargs": {"start": "2023-01-01", "end": "2024-12-31"}
            },
            "amount": {
                "method": "floats",
                "kwargs": {"min": 10.0, "max": 5000.0, "decimals": 2}
            },
            "status": {
                "method": "distincts_prop",
                "kwargs": {"distincts": {"Pending": 20, "Completed": 70, "Cancelled": 10}}
            },
            "payment_method": {
                "method": "distincts",
                "kwargs": {"distincts": ["Credit Card", "Debit Card", "PayPal", "Crypto"]}
            },
            "currency_country": {
                "method": "distincts_map",
                "splitable": True,
                "cols": ["currency", "country"],
                "sep": ";",
                "kwargs": {
                    "distincts": {
                        "US": ["USD"],
                        "DE": ["EUR"],
                        "BR": ["BRL"],
                        "JP": ["JPY"]
                    }
                }
            }
        }

    @classmethod
    def employees(cls) -> Dict[str, Any]:
        """
        Employee records with department-level-role hierarchical correlations.
        
        **Advanced Pattern**: distincts_multi_map for 3-level cartesian product
        
        Fields (6):
        ----------
        - employee_id: Zero-padded IDs (6 digits)
        - hire_date: Employment start dates
        - salary: Normally distributed salaries (mean=6500, std=2000)
        - department, level, role: 3-level hierarchy via distincts_multi_map
        - is_remote: Remote work flag
        - performance_score: Performance ratings 1-5
        
        Key Learning:
        ------------
        - distincts_multi_map: Cartesian product of nested lists
        - Engineering→[Junior,Senior]×[Developer,QA] = 4 combinations
        - Sales→[Junior,Senior]×[Rep,Manager] = 4 combinations
        - Generates all valid combinations respecting hierarchy
        
        Returns:
        -------
        Dict[str, Any]: Specification for employees with hierarchical roles
        """
        return {
            "employee_id": {
                "method": "int_zfilled",
                "kwargs": {"length": 6}
            },
            "hire_date": {
                "method": "dates",
                "kwargs": {"start": "2015-01-01", "end": "2025-10-30", "date_format": "%Y-%m-%d"}
            },
            "salary": {
                "method": "floats_normal",
                "kwargs": {"mean": 6500.0, "std": 2000.0, "decimals": 2}
            },
            "department_level_role": {
                "method": "distincts_multi_map",
                "splitable": True,
                "cols": ["department", "level", "role"],
                "sep": ";",
                "kwargs": {
                    "distincts": {
                        "Engineering": [
                            ["Junior", "Senior"],
                            ["Developer", "QA"]
                        ],
                        "Sales": [
                            ["Junior", "Senior"],
                            ["Rep", "Manager"]
                        ],
                        "Marketing": [
                            ["Junior", "Mid", "Senior"],
                            ["Analyst", "Coordinator"]
                        ]
                    }
                }
            },
            "is_remote": {
                "method": "booleans",
                "kwargs": {"prob_true": 0.4}
            },
            "performance_score": {
                "method": "floats",
                "kwargs": {"min": 1.0, "max": 5.0, "decimals": 1}
            }
        }

    @classmethod
    def devices(cls) -> Dict[str, Any]:
        """
        IoT devices with status-priority weighted correlations.
        
        **Advanced Pattern**: distincts_map_prop for weighted correlated pairs
        
        Fields (7):
        ----------
        - device_id: UUID4 unique identifiers
        - device_type: Device types (Sensor 50%, Gateway 30%, Controller 20%)
        - status, priority: Weighted pairs via distincts_map_prop (splits into 2)
        - temperature: Temperature readings 15-45°C
        - battery_level: Battery percentage 0-100
        - last_ping: Last communication timestamp
        
        Key Learning:
        ------------
        - distincts_map_prop: Maps status to priority with nested weights
        - Online→[(Low,70%), (Medium,20%), (High,10%)]
        - Offline→[(Low,30%), (Medium,40%), (High,30%)]
        - Allows realistic conditional distributions
        
        Returns:
        -------
        Dict[str, Any]: Specification for IoT devices with conditional priorities
        """
        return {
            "device_id": {
                "method": "uuid4",
                "kwargs": {}
            },
            "device_type": {
                "method": "distincts_prop",
                "kwargs": {"distincts": {"Sensor": 50, "Gateway": 30, "Controller": 20}}
            },
            "status_priority": {
                "method": "distincts_map_prop",
                "splitable": True,
                "cols": ["status", "priority"],
                "sep": ";",
                "kwargs": {
                    "distincts": {
                        "Online": [("Low", 70), ("Medium", 20), ("High", 10)],
                        "Offline": [("Low", 30), ("Medium", 40), ("High", 30)]
                    }
                }
            },
            "temperature": {
                "method": "floats",
                "kwargs": {"min": 15.0, "max": 45.0, "decimals": 1}
            },
            "battery_level": {
                "method": "integers",
                "kwargs": {"min": 0, "max": 100, "dtype": "int16"}
            },
            "last_ping": {
                "method": "unix_timestamps",
                "kwargs": {"start": "2025-10-01", "end": "2025-10-30"}
            }
        }

    @classmethod
    def invoices(cls) -> Dict[str, Any]:
        """
        Invoice records with pattern-based invoice numbering.
        
        **Advanced Pattern**: complex_distincts with multiple templates (INV-YYYY-XXXXX)
        
        Fields (6):
        ----------
        - invoice_number: Pattern "INV-2023-00001" using 2 templates
        - issue_date: Invoice issue date
        - due_date: Payment due date
        - amount: Invoice amount 100-50000
        - status: Payment status (Paid 60%, Pending 30%, Overdue 10%)
        - tax_rate: Tax percentage 0-25%
        
        Key Learning:
        ------------
        - complex_distincts: Pattern "INV-x-x" with 2 replacements
        - First x→year (2023 or 2024)
        - Second x→5-digit zero-filled number
        - Templates processed left-to-right in order
        
        Returns:
        -------
        Dict[str, Any]: Specification for invoices with structured numbering
        """
        return {
            "invoice_number": {
                "method": "complex_distincts",
                "kwargs": {
                    "pattern": "INV-x-x",
                    "replacement": "x",
                    "templates": [
                        {"method": "distincts", "kwargs": {"distincts": ["2023", "2024"]}},
                        {"method": "int_zfilled", "kwargs": {"length": 5}}
                    ]
                }
            },
            "issue_date": {
                "method": "dates",
                "kwargs": {"start": "2023-01-01", "end": "2023-12-31", "date_format": "%Y-%m-%d"}
            },
            "due_date": {
                "method": "dates",
                "kwargs": {"start": "2024-01-01", "end": "2024-12-31", "date_format": "%Y-%m-%d"}
            },
            "amount": {
                "method": "floats",
                "kwargs": {"min": 100.0, "max": 50000.0, "decimals": 2}
            },
            "status": {
                "method": "distincts_prop",
                "kwargs": {"distincts": {"Paid": 60, "Pending": 30, "Overdue": 10}}
            },
            "tax_rate": {
                "method": "floats",
                "kwargs": {"min": 0.0, "max": 25.0, "decimals": 2}
            }
        }

    @classmethod
    def shipments(cls) -> Dict[str, Any]:
        """
        Shipping records with carrier-destination correlations.
        
        **Advanced Pattern**: distincts_map for carrier routing rules
        
        Fields (7):
        ----------
        - tracking_number: Pattern "TRK-XXXXXXXXXX" (10 digits)
        - carrier, destination: Correlated via distincts_map (FedEx→US/CA only)
        - weight: Package weight 0.1-50 kg
        - status: Shipping status (In Transit 40%, Delivered 50%, Exception 10%)
        - ship_date: Shipment date
        - estimated_delivery: Expected delivery date
        
        Key Learning:
        ------------
        - distincts_map: Models real-world constraints (carriers serve specific regions)
        - FedEx→[US,CA], DHL→[EU,UK], USPS→[US], UPS→[US,MX]
        - Ensures generated data respects business rules
        
        Returns:
        -------
        Dict[str, Any]: Specification for shipments with routing rules
        """
        return {
            "tracking_number": {
                "method": "complex_distincts",
                "kwargs": {
                    "pattern": "TRK-x",
                    "replacement": "x",
                    "templates": [
                        {"method": "int_zfilled", "kwargs": {"length": 10}}
                    ]
                }
            },
            "carrier_destination": {
                "method": "distincts_map",
                "splitable": True,
                "cols": ["carrier", "destination"],
                "sep": ";",
                "kwargs": {
                    "distincts": {
                        "FedEx": ["US", "CA"],
                        "DHL": ["EU", "UK"],
                        "USPS": ["US"],
                        "UPS": ["US", "MX"]
                    }
                }
            },
            "weight": {
                "method": "floats",
                "kwargs": {"min": 0.1, "max": 50.0, "decimals": 2}
            },
            "status": {
                "method": "distincts_prop",
                "kwargs": {"distincts": {"In Transit": 40, "Delivered": 50, "Exception": 10}}
            },
            "ship_date": {
                "method": "dates",
                "kwargs": {"start": "2024-01-01", "end": "2024-10-01", "date_format": "%Y-%m-%d"}
            },
            "estimated_delivery": {
                "method": "dates",
                "kwargs": {"start": "2024-01-05", "end": "2024-10-18", "date_format": "%Y-%m-%d"}
            }
        }

    @classmethod
    def network_devices(cls) -> Dict[str, Any]:
        """
        Network infrastructure devices with IP address patterns.
        
        **Advanced Pattern**: complex_distincts for IP address generation (x.x.x.x)
        
        Fields (7):
        ----------
        - device_id: UUID4 unique identifiers
        - hostname: Zero-padded hostname IDs
        - ip_address: Pattern "192.168.x.x" using 4 templates
        - subnet: Network subnet addresses
        - device_type: Network device types (Router, Switch, Firewall, AP)
        - uptime_hours: Hours since last reboot
        - is_active: Device active status
        
        Key Learning:
        ------------
        - complex_distincts: Pattern "x.x.x.x" with 4 replacements
        - First two octets: Fixed (192, 168)
        - Last two octets: Random integers 0-255
        - Generates realistic private IP addresses
        
        Returns:
        -------
        Dict[str, Any]: Specification for network devices with IP patterns
        """
        return {
            "device_id": {
                "method": "uuid4",
                "kwargs": {}
            },
            "hostname": {
                "method": "int_zfilled",
                "kwargs": {"length": 6}
            },
            "ip_address": {
                "method": "complex_distincts",
                "kwargs": {
                    "pattern": "x.x.x.x",
                    "replacement": "x",
                    "templates": [
                        {"method": "distincts", "kwargs": {"distincts": ["192", "172", "10"]}},
                        {"method": "distincts", "kwargs": {"distincts": ["168", "16", "0"]}},
                        {"method": "integers", "kwargs": {"min": 0, "max": 255, "dtype": "int16"}},
                        {"method": "integers", "kwargs": {"min": 1, "max": 254, "dtype": "int16"}}
                    ]
                }
            },
            "subnet": {
                "method": "distincts",
                "kwargs": {"distincts": ["255.255.255.0", "255.255.0.0", "255.0.0.0"]}
            },
            "device_type": {
                "method": "distincts",
                "kwargs": {"distincts": ["Router", "Switch", "Firewall", "Access Point"]}
            },
            "uptime_hours": {
                "method": "floats_normal",
                "kwargs": {"mean": 720.0, "std": 200.0, "decimals": 1}
            },
            "is_active": {
                "method": "booleans",
                "kwargs": {"prob_true": 0.95}
            }
        }

    @classmethod
    def vehicles(cls) -> Dict[str, Any]:
        """
        Vehicle fleet with make-model-year correlations.
        
        **Advanced Pattern**: distincts_multi_map for vehicle hierarchy
        
        Fields (8):
        ----------
        - vehicle_id: UUID4 unique identifiers
        - license_plate: Pattern "XXX-XXXX" (letters-numbers)
        - make, model, year: Correlated hierarchy via distincts_multi_map
        - mileage: Odometer reading
        - fuel_type: Fuel types (Gasoline 60%, Diesel 30%, Electric 10%)
        - is_active: Fleet active status
        
        Key Learning:
        ------------
        - distincts_multi_map: Make→Model→Year hierarchy
        - Toyota→[Corolla,Camry]×[2020,2021,2022]
        - Ford→[F150,Mustang]×[2019,2020,2021]
        - Ensures only valid make-model-year combinations
        
        Returns:
        -------
        Dict[str, Any]: Specification for vehicle fleet with valid combinations
        """
        return {
            "vehicle_id": {
                "method": "uuid4",
                "kwargs": {}
            },
            "license_plate": {
                "method": "complex_distincts",
                "kwargs": {
                    "pattern": "x-x",
                    "replacement": "x",
                    "templates": [
                        {"method": "distincts", "kwargs": {"distincts": ["ABC", "DEF", "GHI", "JKL"]}},
                        {"method": "int_zfilled", "kwargs": {"length": 4}}
                    ]
                }
            },
            "make_model_year": {
                "method": "distincts_multi_map",
                "splitable": True,
                "cols": ["make", "model", "year"],
                "sep": ";",
                "kwargs": {
                    "distincts": {
                        "Toyota": [
                            ["Corolla", "Camry", "RAV4"],
                            ["2020", "2021", "2022", "2023"]
                        ],
                        "Ford": [
                            ["F150", "Mustang", "Explorer"],
                            ["2019", "2020", "2021", "2022"]
                        ],
                        "Honda": [
                            ["Civic", "Accord", "CR-V"],
                            ["2020", "2021", "2022"]
                        ]
                    }
                }
            },
            "mileage": {
                "method": "integers",
                "kwargs": {"min": 0, "max": 200000, "dtype": "int32"}
            },
            "fuel_type": {
                "method": "distincts_prop",
                "kwargs": {"distincts": {"Gasoline": 60, "Diesel": 30, "Electric": 10}}
            },
            "is_active": {
                "method": "booleans",
                "kwargs": {"prob_true": 0.9}
            }
        }

    @classmethod
    def real_estate(cls) -> Dict[str, Any]:
        """
        Property listings with location-type correlations.
        
        **Advanced Pattern**: distincts_map_prop for location-based pricing
        
        Fields (8):
        ----------
        - property_id: UUID4 unique identifiers
        - address: Property street addresses
        - city, type: Correlated via distincts_map (city determines available types)
        - bedrooms: Number of bedrooms 1-5
        - bathrooms: Number of bathrooms 1-4
        - price: Property price (normal distribution by type)
        - is_available: Availability status
        
        Key Learning:
        ------------
        - distincts_map: City→PropertyTypes mapping
        - Manhattan→[Apartment,Condo], Brooklyn→[Apartment,Townhouse]
        - Models geographic constraints on property types
        
        Returns:
        -------
        Dict[str, Any]: Specification for real estate with location constraints
        """
        return {
            "property_id": {
                "method": "uuid4",
                "kwargs": {}
            },
            "address": {
                "method": "int_zfilled",
                "kwargs": {"length": 4}
            },
            "city_type": {
                "method": "distincts_map",
                "splitable": True,
                "cols": ["city", "type"],
                "sep": ";",
                "kwargs": {
                    "distincts": {
                        "Manhattan": ["Apartment", "Condo"],
                        "Brooklyn": ["Apartment", "Townhouse"],
                        "Queens": ["House", "Apartment"],
                        "Bronx": ["House", "Apartment"]
                    }
                }
            },
            "bedrooms": {
                "method": "integers",
                "kwargs": {"min": 1, "max": 5, "dtype": "int16"}
            },
            "bathrooms": {
                "method": "integers",
                "kwargs": {"min": 1, "max": 4, "dtype": "int16"}
            },
            "square_feet": {
                "method": "integers",
                "kwargs": {"min": 500, "max": 5000, "dtype": "int32"}
            },
            "price": {
                "method": "floats_normal",
                "kwargs": {"mean": 500000.0, "std": 150000.0, "decimals": 2}
            },
            "is_available": {
                "method": "booleans",
                "kwargs": {"prob_true": 0.3}
            }
        }

    @classmethod
    def healthcare(cls) -> Dict[str, Any]:
        """
        Patient records with diagnosis-treatment patterns.
        
        **Advanced Pattern**: distincts_map_prop for diagnosis-treatment correlations
        
        Fields (7):
        ----------
        - patient_id: UUID4 unique identifiers
        - age: Patient age 0-100
        - diagnosis, treatment: Correlated via distincts_map_prop (weighted by diagnosis)
        - admission_date: Hospital admission date
        - discharge_date: Hospital discharge date
        - bill_amount: Medical bill amount
        - is_emergency: Emergency admission flag
        
        Key Learning:
        ------------
        - distincts_map_prop: Diagnosis→Treatment with probabilities
        - Flu→[(Medication,80%), (Hospitalization,20%)]
        - Fracture→[(Surgery,60%), (Cast,40%)]
        - Models medical decision patterns
        
        Returns:
        -------
        Dict[str, Any]: Specification for healthcare with realistic treatment paths
        """
        return {
            "patient_id": {
                "method": "uuid4",
                "kwargs": {}
            },
            "age": {
                "method": "integers",
                "kwargs": {"min": 0, "max": 100, "dtype": "int16"}
            },
            "diagnosis_treatment": {
                "method": "distincts_map_prop",
                "splitable": True,
                "cols": ["diagnosis", "treatment"],
                "sep": ";",
                "kwargs": {
                    "distincts": {
                        "Flu": [("Medication", 80), ("Hospitalization", 20)],
                        "Fracture": [("Surgery", 60), ("Cast", 40)],
                        "Hypertension": [("Medication", 90), ("Lifestyle", 10)],
                        "Diabetes": [("Insulin", 50), ("Medication", 40), ("Diet", 10)]
                    }
                }
            },
            "admission_date": {
                "method": "dates",
                "kwargs": {"start": "2024-01-01", "end": "2024-10-01", "date_format": "%Y-%m-%d"}
            },
            "discharge_date": {
                "method": "dates",
                "kwargs": {"start": "2024-01-05", "end": "2024-10-30", "date_format": "%Y-%m-%d"}
            },
            "bill_amount": {
                "method": "floats_normal",
                "kwargs": {"mean": 5000.0, "std": 2000.0, "decimals": 2}
            },
            "is_emergency": {
                "method": "booleans",
                "kwargs": {"prob_true": 0.25}
            }
        }
