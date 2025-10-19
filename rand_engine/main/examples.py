from typing import Dict, Any


class RandSpecs:
    """
    Pre-built specification examples for learning and quick prototyping.
    
    RandSpecs provides 10 ready-to-use data generation specifications based on
    real-world entities. Each spec is simple (max 6 fields), demonstrates different
    generation methods, and is accessible as a class method (no instantiation needed).
    
    Available Specs:
    ---------------
    - customers: Customer profiles with unique IDs, demographics, and status
    - products: Product catalog with SKUs, names, prices, and categories
    - orders: E-commerce orders with timestamps, amounts, and payment methods
    - transactions: Financial transactions with amounts, currencies, and types
    - employees: Employee records with salaries, departments, and hire dates
    - devices: IoT devices with IDs, types, statuses, and metrics
    - users: Application users with accounts, plans, and activity flags
    - invoices: Invoice records with numbers, amounts, due dates, and status
    - shipments: Shipping records with tracking, weights, and destinations
    - events: Event logs with timestamps, types, severity, and messages
    
    Usage:
    ------
    >>> from rand_engine import DataGenerator, RandSpecs
    >>> 
    >>> # Generate data using a pre-built spec (no instantiation needed)
    >>> df = DataGenerator(RandSpecs.customers(), seed=42).size(1000).get_df()
    >>> print(df.head())
    >>> 
    >>> # Or access spec directly to customize
    >>> my_spec = RandSpecs.products().copy()
    >>> my_spec['price']['kwargs']['max'] = 500  # Customize price range
    >>> df = DataGenerator(my_spec).size(100).get_df()
    
    Notes:
    ------
    - Static class - no instantiation required
    - All methods are @classmethod
    - Specs are returned as dictionaries, safe to modify
    - Each spec demonstrates 2-3 different generation patterns
    - Maximum 6 fields per spec for simplicity
    """

    @classmethod
    def customers(cls) -> Dict[str, Any]:
        """
        Customer profiles with demographics and account status.
        
        Use this spec to:
        - Generate customer datasets for testing
        - Learn unique ID generation and basic types
        - Understand boolean probability
        
        Generated Columns (6):
        ---------------------
        - customer_id: Unique zero-filled integers (e.g., "000001", "000002")
        - name: Random selection from common customer names
        - age: Random integers between 18-80
        - email: Email addresses with common domains
        - is_active: Boolean with 85% probability of True
        - account_balance: Floats 0-10000 with 2 decimal places
        
        Generation Methods:
        ------------------
        - unique_ids: Generates unique customer identifiers
        - distincts: Random selection from predefined lists
        - integers: Random integers in range
        - booleans: Boolean values with probability
        - floats: Random floats with precision
        
        Example:
        --------
        >>> from rand_engine import RandSpecs, DataGenerator
        >>> df = DataGenerator(RandSpecs.customers(), seed=42).size(100).get_df()
        >>> print(df.columns.tolist())
        ['customer_id', 'name', 'age', 'email', 'is_active', 'account_balance']
        """
        return {
            "customer_id": dict(method="unique_ids", kwargs=dict(strategy="zint", length=6)),
            "name": dict(method="distincts", kwargs=dict(distincts=["John Smith", "Maria Garcia", "Li Wei", "Ahmed Hassan", "Sofia Rodriguez"])),
            "age": dict(method="integers", kwargs=dict(min=18, max=80)),
            "email": dict(method="distincts", kwargs=dict(distincts=["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"])),
            "is_active": dict(method="booleans", kwargs=dict(true_prob=0.85)),
            "account_balance": dict(method="floats", kwargs=dict(min=0, max=10000, round=2))
        }

    @classmethod
    def products(cls) -> Dict[str, Any]:
        """
        Product catalog with SKUs, pricing, and categories.
        
        Use this spec to:
        - Generate product inventories
        - Understand weighted distributions (distincts_prop)
        - Learn complex pattern generation
        
        Generated Columns (6):
        ---------------------
        - sku: Product codes following pattern "PRD-XXXX" (e.g., "PRD-1234")
        - product_name: Random product names from catalog
        - category: Weighted categories (Electronics 50%, Clothing 30%, Food 20%)
        - price: Floats 5-500 with 2 decimal places
        - stock: Random integers 0-1000
        - rating: Normally distributed ratings (mean=4.0, std=0.8)
        
        Generation Methods:
        ------------------
        - complex_distincts: Pattern-based generation
        - distincts: Simple random selection
        - distincts_prop: Weighted random selection
        - floats: Random floats with precision
        - integers: Random integers in range
        - floats_normal: Normally distributed values
        
        Example:
        --------
        >>> from rand_engine import RandSpecs
        >>> df = DataGenerator(RandSpecs.products, seed=42).size(100).get_df()
        >>> df['category'].value_counts()  # Shows weighted distribution
        """
        return {
                "sku": dict(method="complex_distincts", kwargs=dict(
                    pattern="PRD-x",
                    replacement="x",
                    templates=[
                        dict(method="int_zfilled", parms=dict(length=4))
                    ]
                )),
                "product_name": dict(method="distincts", kwargs=dict(distincts=["Laptop", "Smartphone", "T-Shirt", "Jeans", "Coffee", "Bread"])),
                "category": dict(method="distincts_prop", kwargs=dict(distincts={"Electronics": 50, "Clothing": 30, "Food": 20})),
                "price": dict(method="floats", kwargs=dict(min=5, max=500, round=2)),
                "stock": dict(method="integers", kwargs=dict(min=0, max=1000)),
                "rating": dict(method="floats_normal", kwargs=dict(mean=4.0, std=0.8, round=1))
            }

    @classmethod
    def orders(cls) -> Dict[str, Any]:
        """
        E-commerce orders with timestamps and payment methods.
        
        Use this spec to:
        - Generate order transaction data
        - Learn timestamp generation
        - Understand correlated data (distincts_map)
        
        Generated Columns (6):
        ---------------------
        - order_id: UUID4 unique identifiers
        - order_date: Unix timestamps from 2023 onwards
        - amount: Order amounts 10-5000 with 2 decimal places
        - status: Order status (Pending 20%, Completed 70%, Cancelled 10%)
        - payment_method: Payment types (Credit, Debit, PayPal, Crypto)
        - currency_country: Correlated currency-country pairs (USD-US, EUR-DE, etc.)
        
        Generation Methods:
        ------------------
        - unique_ids: UUID generation
        - unix_timestamps: Timestamps in date range
        - floats: Random floats with precision
        - distincts_prop: Weighted random selection
        - distincts: Simple random selection
        - distincts_map: Correlated pair generation
        
        Example:
        --------
        >>> from rand_engine import RandSpecs
        >>> df = DataGenerator(RandSpecs.orders, seed=42).size(100).get_df()
        >>> df[['currency', 'country']].drop_duplicates()  # Shows correlations
        """
        return {
                "order_id": dict(method="unique_ids", kwargs=dict(strategy="uuid4")),
                "order_date": dict(method="unix_timestamps", kwargs=dict(start="2023-01-01", end="2024-12-31", format="%Y-%m-%d")),
                "amount": dict(method="floats", kwargs=dict(min=10, max=5000, round=2)),
                "status": dict(method="distincts_prop", kwargs=dict(distincts={"Pending": 20, "Completed": 70, "Cancelled": 10})),
                "payment_method": dict(method="distincts", kwargs=dict(distincts=["Credit Card", "Debit Card", "PayPal", "Crypto"])),
                "currency_country": dict(method="distincts_map", splitable=True, cols=["currency", "country"], sep=";", 
                                        kwargs=dict(distincts={"US": ["USD"], "DE": ["EUR"], "BR": ["BRL"], "JP": ["JPY"]}))
            }

    @classmethod
    def transactions(cls) -> Dict[str, Any]:
        """
        Financial transactions with types and descriptions.
        
        Use this spec to:
        - Generate financial transaction logs
        - Learn args syntax (positional arguments)
        - Understand transaction patterns
        
        Generated Columns (6):
        ---------------------
        - transaction_id: Zero-filled unique IDs (8 digits)
        - timestamp: Unix timestamps from 2024
        - amount: Transaction amounts -1000 to 10000 (negatives for withdrawals)
        - type: Transaction types (Deposit 40%, Withdrawal 30%, Transfer 30%)
        - currency: Major currencies (USD, EUR, GBP, JPY)
        - description: Transaction descriptions
        
        Generation Methods:
        ------------------
        - unique_ids: Using args syntax
        - unix_timestamps: Using args syntax
        - integers: Negative and positive values
        - distincts_prop: Weighted types
        - distincts: Simple selection
        
        Example:
        --------
        >>> from rand_engine import RandSpecs
        >>> df = DataGenerator(RandSpecs.transactions, seed=42).size(100).get_df()
        >>> df[df['amount'] < 0]['type'].value_counts()  # Analyze withdrawals
        """
        return {
                "transaction_id": dict(method="unique_ids", args=["zint", 8]),
                "timestamp": dict(method="unix_timestamps", args=["2024-01-01", "2024-12-31", "%Y-%m-%d"]),
                "amount": dict(method="integers", kwargs=dict(min=-1000, max=10000)),
                "type": dict(method="distincts_prop", kwargs=dict(distincts={"Deposit": 40, "Withdrawal": 30, "Transfer": 30})),
                "currency": dict(method="distincts", kwargs=dict(distincts=["USD", "EUR", "GBP", "JPY"])),
                "description": dict(method="distincts", kwargs=dict(distincts=["Online Purchase", "ATM Withdrawal", "Salary", "Refund", "Bill Payment"]))
            }

    @classmethod
    def employees(cls) -> Dict[str, Any]:
        """
        Employee records with departments and compensation.
        
        Use this spec to:
        - Generate HR datasets
        - Understand multi-level correlations (distincts_multi_map)
        - Learn salary distributions
        
        Generated Columns (6):
        ---------------------
        - employee_id: Zero-filled IDs (5 digits)
        - hire_date: Unix timestamps from 2020
        - salary: Normally distributed salaries (mean=60000, std=15000)
        - department_level_role: Multi-level hierarchy (Dept → Level → Role)
        - is_remote: Boolean with 40% probability of True
        - bonus: Floats 0-20000 with 2 decimal places
        
        Generation Methods:
        ------------------
        - unique_ids: Employee identifiers
        - unix_timestamps: Historical dates
        - floats_normal: Realistic salary distribution
        - distincts_multi_map: 3-level cartesian product
        - booleans: Remote work flags
        - floats: Bonus amounts
        
        Example:
        --------
        >>> from rand_engine import RandSpecs
        >>> df = DataGenerator(RandSpecs.employees, seed=42).size(100).get_df()
        >>> df[['department', 'level', 'role']].drop_duplicates()  # Shows all combinations
        """
        return {
                "employee_id": dict(method="unique_ids", kwargs=dict(strategy="zint", length=5)),
                "hire_date": dict(method="unix_timestamps", kwargs=dict(start="2020-01-01", end="2024-12-31", format="%Y-%m-%d")),
                "salary": dict(method="floats_normal", kwargs=dict(mean=60000, std=15000, round=2)),
                "department_level_role": dict(method="distincts_multi_map", splitable=True, cols=["department", "level", "role"], sep=";",
                                             kwargs=dict(distincts={"Engineering": [["Junior", "Senior"], ["Developer", "QA"]], 
                                                                  "Sales": [["Junior", "Senior"], ["Rep", "Manager"]]})),
                "is_remote": dict(method="booleans", kwargs=dict(true_prob=0.4)),
                "bonus": dict(method="floats", kwargs=dict(min=0, max=20000, round=2))
            }

    @classmethod
    def devices(cls) -> Dict[str, Any]:
        """
        IoT devices with metrics and operational status.
        
        Use this spec to:
        - Generate IoT device data
        - Understand device monitoring patterns
        - Learn correlated attributes (distincts_map_prop)
        
        Generated Columns (6):
        ---------------------
        - device_id: UUID1 unique identifiers
        - device_type: Types (Sensor 50%, Gateway 30%, Controller 20%)
        - status_priority: Weighted status-priority pairs
        - temperature: Floats 15-45 degrees
        - battery: Integers 0-100 (percentage)
        - last_ping: Unix timestamps from 2024
        
        Generation Methods:
        ------------------
        - unique_ids: UUID1 for device tracking
        - distincts_prop: Weighted device types
        - distincts_map_prop: Correlated status-priority with weights
        - floats: Temperature readings
        - integers: Battery levels
        - unix_timestamps: Last communication time
        
        Example:
        --------
        >>> from rand_engine import RandSpecs
        >>> df = DataGenerator(RandSpecs.devices, seed=42).size(100).get_df()
        >>> df.groupby(['status', 'priority']).size()  # Shows weighted correlations
        """
        return {
                "device_id": dict(method="unique_ids", kwargs=dict(strategy="uuid1")),
                "device_type": dict(method="distincts_prop", kwargs=dict(distincts={"Sensor": 50, "Gateway": 30, "Controller": 20})),
                "status_priority": dict(method="distincts_map_prop", splitable=True, cols=["status", "priority"], sep=";",
                                       kwargs=dict(distincts={"Online": [("Low", 70), ("Medium", 20), ("High", 10)],
                                                            "Offline": [("Low", 30), ("Medium", 40), ("High", 30)]})),
                "temperature": dict(method="floats", kwargs=dict(min=15, max=45, round=1)),
                "battery": dict(method="integers", kwargs=dict(min=0, max=100)),
                "last_ping": dict(method="unix_timestamps", kwargs=dict(start="2024-10-01", end="2024-10-18", format="%Y-%m-%d"))
            }

    @classmethod
    def users(cls) -> Dict[str, Any]:
        """
        Application users with plans and activity metrics.
        
        Use this spec to:
        - Generate user account data
        - Learn transformer usage for data formatting
        - Understand subscription patterns
        
        Generated Columns (6):
        ---------------------
        - user_id: Zero-filled IDs (7 digits)
        - username: Random usernames
        - plan: Subscription plans (Free 60%, Pro 30%, Enterprise 10%)
        - signup_date: Unix timestamps from 2022
        - login_count: Normally distributed logins (mean=50, std=20)
        - is_verified: Boolean with 75% probability of True
        
        Generation Methods:
        ------------------
        - unique_ids: User identifiers
        - distincts: Username selection
        - distincts_prop: Weighted subscription plans (with transformer to uppercase)
        - unix_timestamps: Account creation dates
        - floats_normal: Realistic login distribution
        - booleans: Verification status
        
        Example:
        --------
        >>> from rand_engine import RandSpecs
        >>> df = DataGenerator(RandSpecs.users, seed=42).size(100).get_df()
        >>> df['plan'].value_counts()  # Shows plan distribution (uppercase)
        """
        return {
                "user_id": dict(method="unique_ids", kwargs=dict(strategy="zint", length=7)),
                "username": dict(method="distincts", kwargs=dict(distincts=["alex_123", "maria_dev", "john_qa", "sara_eng", "mike_pm"])),
                "plan": dict(method="distincts_prop", kwargs=dict(distincts={"free": 60, "pro": 30, "enterprise": 10}),
                           transformers=[lambda x: x.upper()]),
                "signup_date": dict(method="unix_timestamps", kwargs=dict(start="2022-01-01", end="2024-12-31", format="%Y-%m-%d")),
                "login_count": dict(method="floats_normal", kwargs=dict(mean=50, std=20, round=0)),
                "is_verified": dict(method="booleans", kwargs=dict(true_prob=0.75))
            }

    @classmethod
    def invoices(cls) -> Dict[str, Any]:
        """
        Invoice records with amounts and payment status.
        
        Use this spec to:
        - Generate invoice datasets
        - Learn invoice numbering patterns
        - Understand payment tracking
        
        Generated Columns (6):
        ---------------------
        - invoice_number: Pattern-based "INV-YYYY-XXXXX"
        - issue_date: Unix timestamps from 2023
        - due_date: Unix timestamps from 2024
        - amount: Floats 100-50000 with 2 decimal places
        - status: Payment status (Paid 60%, Pending 30%, Overdue 10%)
        - tax_rate: Floats 0-0.25 with 3 decimal places
        
        Generation Methods:
        ------------------
        - complex_distincts: Invoice number pattern
        - unix_timestamps: Date tracking
        - floats: Amount and tax calculations
        - distincts_prop: Weighted payment status
        
        Example:
        --------
        >>> from rand_engine import RandSpecs
        >>> df = DataGenerator(RandSpecs.invoices, seed=42).size(100).get_df()
        >>> df['status'].value_counts()  # Payment status distribution
        """
        return {
                "invoice_number": dict(method="complex_distincts", kwargs=dict(
                    pattern="INV-x-x",
                    replacement="x",
                    templates=[
                        dict(method="distincts", parms=dict(distincts=["2023", "2024"])),
                        dict(method="int_zfilled", parms=dict(length=5))
                    ]
                )),
                "issue_date": dict(method="unix_timestamps", kwargs=dict(start="2023-01-01", end="2023-12-31", format="%Y-%m-%d")),
                "due_date": dict(method="unix_timestamps", kwargs=dict(start="2024-01-01", end="2024-12-31", format="%Y-%m-%d")),
                "amount": dict(method="floats", kwargs=dict(min=100, max=50000, round=2)),
                "status": dict(method="distincts_prop", kwargs=dict(distincts={"Paid": 60, "Pending": 30, "Overdue": 10})),
                "tax_rate": dict(method="floats", kwargs=dict(min=0, max=25, round=2))
            }

    @classmethod
    def shipments(cls) -> Dict[str, Any]:
        """
        Shipping records with tracking and logistics data.
        
        Use this spec to:
        - Generate shipping/logistics data
        - Learn tracking number patterns
        - Understand carrier-destination correlations
        
        Generated Columns (6):
        ---------------------
        - tracking_number: Pattern "TRK-XXXXXXXXXX"
        - carrier_destination: Correlated carrier-destination pairs
        - weight: Floats 0.1-50 kg with 2 decimal places
        - status: Shipping status (In Transit 40%, Delivered 50%, Exception 10%)
        - ship_date: Unix timestamps from 2024
        - estimated_delivery: Unix timestamps from 2024
        
        Generation Methods:
        ------------------
        - complex_distincts: Tracking number generation
        - distincts_map: Carrier-destination correlation
        - floats: Weight measurements
        - distincts_prop: Weighted shipping status
        - unix_timestamps: Date tracking
        
        Example:
        --------
        >>> from rand_engine import RandSpecs
        >>> df = DataGenerator(RandSpecs.shipments, seed=42).size(100).get_df()
        >>> df.groupby(['carrier', 'destination']).size()  # Shows correlations
        """
        return {
                "tracking_number": dict(method="complex_distincts", kwargs=dict(
                    pattern="TRK-x",
                    replacement="x",
                    templates=[
                        dict(method="int_zfilled", parms=dict(length=10))
                    ]
                )),
                "carrier_destination": dict(method="distincts_map", splitable=True, cols=["carrier", "destination"], sep=";",
                                           kwargs=dict(distincts={"FedEx": ["US", "CA"], "DHL": ["EU", "UK"], "USPS": ["US"], "UPS": ["US", "MX"]})),
                "weight": dict(method="floats", kwargs=dict(min=0.1, max=50, round=2)),
                "status": dict(method="distincts_prop", kwargs=dict(distincts={"In Transit": 40, "Delivered": 50, "Exception": 10})),
                "ship_date": dict(method="unix_timestamps", kwargs=dict(start="2024-01-01", end="2024-10-01", format="%Y-%m-%d")),
                "estimated_delivery": dict(method="unix_timestamps", kwargs=dict(start="2024-01-05", end="2024-10-18", format="%Y-%m-%d"))
            }

    @classmethod
    def events(cls) -> Dict[str, Any]:
        """
        Event logs with timestamps, types, and severity levels.
        
        Use this spec to:
        - Generate application/system event logs
        - Learn event logging patterns
        - Understand severity distributions
        
        Generated Columns (6):
        ---------------------
        - event_id: UUID4 unique identifiers
        - timestamp: Unix timestamps from recent dates
        - event_type: Types (INFO 50%, WARNING 30%, ERROR 15%, CRITICAL 5%)
        - severity: Severity levels (Low 60%, Medium 30%, High 10%)
        - source: Event sources (API, Database, Frontend, Backend)
        - message: Event message descriptions
        
        Generation Methods:
        ------------------
        - unique_ids: Event identifiers
        - unix_timestamps: Event timing
        - distincts_prop: Weighted event types and severity
        - distincts: Source and message selection
        
        Example:
        --------
        >>> from rand_engine import RandSpecs
        >>> df = DataGenerator(RandSpecs.events, seed=42).size(100).get_df()
        >>> df['event_type'].value_counts()  # Event type distribution
        """
        return {
                "event_id": dict(method="unique_ids", kwargs=dict(strategy="uuid4")),
                "timestamp": dict(method="unix_timestamps", kwargs=dict(start="2024-10-01", end="2024-10-18", format="%Y-%m-%d")),
                "event_type": dict(method="distincts_prop", kwargs=dict(distincts={"INFO": 50, "WARNING": 30, "ERROR": 15, "CRITICAL": 5})),
                "severity": dict(method="distincts_prop", kwargs=dict(distincts={"Low": 60, "Medium": 30, "High": 10})),
                "source": dict(method="distincts", kwargs=dict(distincts=["API", "Database", "Frontend", "Backend"])),
                "message": dict(method="distincts", kwargs=dict(distincts=["Request processed", "Connection timeout", "Invalid input", "Server error", "Cache miss"]))
            }
