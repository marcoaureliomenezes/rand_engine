from typing import Dict, Any


class SparkRandSpecs:
    """
    Pre-built Spark specification examples for SparkGenerator.
    
    SparkRandSpecs provides 10 ready-to-use data generation specifications for
    PySpark-based distributed data generation using SparkGenerator. These specs
    demonstrate Spark-specific methods and are optimized for distributed processing.
    
    IMPO        return {
            "shipment_id": dict(method="int_zfilled", kwargs=dict(length=10)),
            "origin": dict(method="distincts", kwargs=dict(distincts=["US", "CA", "EU", "UK", "MX"])),
            "destination": dict(method="distincts", kwargs=dict(distincts=["US", "CA", "EU", "UK", "MX"])),
            "weight": dict(method="floats", kwargs=dict(min=0.1, max=50, decimals=2)),
            "status": dict(method="distincts_prop", kwargs=dict(distincts={"In Transit": 40, "Delivered": 50, "Exception": 10})),
            "ship_date": dict(method="dates", kwargs=dict(start="2024-01-01", end="2024-10-01", date_format="%Y-%m-%d")),
            "estimated_delivery": dict(method="dates", kwargs=dict(start="2024-01-05", end="2024-10-18", date_format="%Y-%m-%d"))
        }ark API Differences from DataGenerator:
    ---------------------------------------------------
    - Use 'std' instead of 'stddev' in floats_normal
    - Use 'date_format' (unified API) in dates
    - No support for: distincts_map, distincts_multi_map, complex_distincts, distincts_map_prop
    
    Available Spark Specs:
    ---------------------
    - customers: Customer profiles with basic Spark methods
    - products: Product catalog with normal distributions
    - orders: E-commerce orders with timestamps and UUIDs
    - transactions: Financial transactions with various types
    - employees: Employee records with dates and departments
    - devices: IoT devices with metrics and status
    - users: Application users with activity tracking
    - invoices: Invoice records with amounts and status
    - shipments: Shipping records with weights and dates
    - events: Event logs with severity and timestamps
    
    Usage:
    ------
    >>> from pyspark.sql import SparkSession, functions as F
    >>> from rand_engine import SparkGenerator
    >>> from rand_engine.examples import SparkRandSpecs
    >>> 
    >>> spark = SparkSession.builder.getOrCreate()
    >>> df = SparkGenerator(spark, F, SparkRandSpecs.customers()).size(1000).get_df()
    >>> df.show(5)
    
    Notes:
    ------
    - All methods are @classmethod (no instantiation needed)
    - Specs are optimized for Spark distributed processing
    - Each spec demonstrates 5-7 Spark-compatible methods
    - Use SparkGenerator, not DataGenerator
    """

    @classmethod
    def customers(cls) -> Dict[str, Any]:
        """
        Customer profiles - Basic Spark methods.
        
        **Complexity Level: ★☆☆☆☆ (Basic)** - Perfect for learning Spark generation.
        
        Demonstrates:
        - int_zfilled: Zero-filled integers (Spark equivalent of int_zfilled)
        - distincts: Random selection
        - integers: Random integers
        - booleans: Boolean generation with probability
        - floats: Random floats with decimals
        
        Generated Columns (6):
        ---------------------
        - customer_id: Zero-filled integers (6 digits) using zint
        - name: Customer names from predefined list
        - age: Ages between 18-80
        - email_domain: Email domains
        - is_active: Boolean with 85% true probability
        - account_balance: Float amounts 0-10000 with 2 decimals
        
        Example:
        --------
        >>> from pyspark.sql import SparkSession, functions as F
        >>> from rand_engine import SparkGenerator
        >>> from rand_engine.examples import SparkRandSpecs
        >>> 
        >>> spark = SparkSession.builder.getOrCreate()
        >>> df = SparkGenerator(spark, F, SparkRandSpecs.customers()).size(1000).get_df()
        >>> df.select("customer_id", "name", "is_active").show(5)
        """
        return {
            "customer_id": dict(method="int_zfilled", kwargs=dict(length=6)),
            "name": dict(method="distincts", kwargs=dict(distincts=["John Smith", "Maria Garcia", "Li Wei", "Ahmed Hassan", "Sofia Rodriguez"])),
            "age": dict(method="integers", kwargs=dict(min=18, max=80)),
            "email_domain": dict(method="distincts", kwargs=dict(distincts=["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"])),
            "is_active": dict(method="booleans", kwargs=dict(true_prob=0.85)),
            "account_balance": dict(method="floats", kwargs=dict(min=0, max=10000, decimals=2))
        }

    @classmethod
    def products(cls) -> Dict[str, Any]:
        """
        Product catalog - Demonstrates normal distributions.
        
        **Complexity Level: ★★☆☆☆ (Intermediate)** - Shows floats_normal and distincts_prop.
        
        Demonstrates:
        - uuid4: UUID generation
        - distincts: Product names
        - distincts_prop: Weighted category distribution
        - floats: Price generation
        - integers: Stock levels
        - floats_normal: Ratings with normal distribution (std parameter)
        
        Generated Columns (6):
        ---------------------
        - product_id: UUID4 unique identifiers
        - product_name: Product names from catalog
        - category: Weighted categories (Electronics 50%, Clothing 30%, Food 20%)
        - price: Prices 5-500 with 2 decimals
        - stock: Stock levels 0-1000
        - rating: Normally distributed ratings (mean=4.0, std=0.8)
        
        Example:
        --------
        >>> df = SparkGenerator(spark, F, SparkRandSpecs.products()).size(500).get_df()
        >>> df.groupBy("category").count().show()  # Shows weighted distribution
        """
        return {
            "product_id": dict(method="int_zfilled", kwargs=dict(length=6)),
            "product_name": dict(method="distincts", kwargs=dict(distincts=["Laptop", "Mouse", "Keyboard", "Monitor", "Headset"])),
            "category": dict(method="distincts_prop", kwargs=dict(distincts={"Electronics": 50, "Clothing": 30, "Food": 20})),
            "price": dict(method="floats", kwargs=dict(min=10, max=1000, decimals=2)),
            "stock": dict(method="integers", kwargs=dict(min=0, max=500)),
            "rating": dict(method="floats_normal", kwargs=dict(mean=4.0, std=0.5, decimals=1))
        }

    @classmethod
    def orders(cls) -> Dict[str, Any]:
        """
        E-commerce orders - Demonstrates dates and timestamps.
        
        **Complexity Level: ★★★☆☆ (Advanced)** - Shows date generation with date_format parameter.
        
        Demonstrates:
        - uuid4: Order identifiers
        - dates: Date generation with date_format parameter (Spark-specific)
        - unix_timestamps: Timestamp generation
        - floats: Order amounts
        - distincts_prop: Weighted status distribution
        - distincts: Payment methods
        
        Generated Columns (6):
        ---------------------
        - order_id: UUID4 identifiers
        - order_date: Dates from 2023-2024 (date_format parameter)
        - order_timestamp: Unix timestamps
        - amount: Order amounts 10-5000 with 2 decimals
        - status: Order status (Pending 20%, Completed 70%, Cancelled 10%)
        - payment_method: Payment types
        
        Example:
        --------
        >>> df = SparkGenerator(spark, F, SparkRandSpecs.orders()).size(1000).get_df()
        >>> df.groupBy("status").count().show()  # Status distribution
        """
        return {
            "order_id": dict(method="int_zfilled", kwargs=dict(length=8)),
            "customer_id": dict(method="integers", kwargs=dict(min=1, max=1000)),
            "product_id": dict(method="integers", kwargs=dict(min=1, max=100)),
            "quantity": dict(method="integers", kwargs=dict(min=1, max=10)),
            "status": dict(method="distincts_prop", kwargs=dict(distincts={"Pending": 20, "Completed": 70, "Cancelled": 10}))
        }

    @classmethod
    def transactions(cls) -> Dict[str, Any]:
        """
        Financial transactions - Demonstrates negative values and timestamps.
        
        **Complexity Level: ★★☆☆☆ (Intermediate)** - Shows negative integers and timestamp handling.
        
        Demonstrates:
        - int_zfilled: Zero-filled transaction IDs
        - unix_timestamps: Transaction timestamps
        - integers: Amounts with negative values (withdrawals)
        - distincts_prop: Weighted transaction types
        - distincts: Currencies and descriptions
        
        Generated Columns (6):
        ---------------------
        - transaction_id: Zero-filled IDs (8 digits)
        - timestamp: Unix timestamps from 2024
        - amount: Amounts -1000 to 10000 (negatives for withdrawals)
        - type: Transaction types (Deposit 40%, Withdrawal 30%, Transfer 30%)
        - currency: Major currencies
        - description: Transaction descriptions
        
        Example:
        --------
        >>> df = SparkGenerator(spark, F, SparkRandSpecs.transactions()).size(1000).get_df()
        >>> df.filter(df.amount < 0).groupBy("type").count().show()  # Analyze withdrawals
        """
        return {
            "transaction_id": dict(method="uuid4", kwargs={}),
            "account_id": dict(method="integers", kwargs=dict(min=1000, max=9999)),
            "transaction_date": dict(method="dates", kwargs=dict(start="2024-01-01", end="2024-10-18", date_format="%Y-%m-%d")),
            "type": dict(method="distincts_prop", kwargs=dict(distincts={"Deposit": 40, "Withdrawal": 30, "Transfer": 30})),
            "amount": dict(method="floats", kwargs=dict(min=10, max=10000, decimals=2)),
            "balance": dict(method="floats", kwargs=dict(min=0, max=50000, decimals=2))
        }

    @classmethod
    def employees(cls) -> Dict[str, Any]:
        """
        Employee records - Demonstrates HR data patterns.
        
        **Complexity Level: ★★★☆☆ (Advanced)** - Shows salary distributions and date handling.
        
        Demonstrates:
        - int_zfilled: Employee identifiers
        - dates: Hire dates with date_format parameter
        - floats_normal: Salary distribution (mean=60000, std=15000)
        - distincts: Departments and roles
        - booleans: Remote work flags
        - floats: Bonus amounts
        
        Generated Columns (7):
        ---------------------
        - employee_id: Zero-filled IDs (5 digits)
        - hire_date: Dates from 2020-2024 (date_format parameter)
        - salary: Normally distributed salaries
        - department: Department names
        - role: Job roles
        - is_remote: Boolean with 40% true probability
        - bonus: Bonus amounts 0-20000 with 2 decimals
        
        Example:
        --------
        >>> df = SparkGenerator(spark, F, SparkRandSpecs.employees()).size(500).get_df()
        >>> df.select("department", "role", "salary").groupBy("department").avg("salary").show()
        """
        return {
            "employee_id": dict(method="int_zfilled", kwargs=dict(length=5)),
            "hire_date": dict(method="dates", kwargs=dict(start="2020-01-01", end="2024-12-31", date_format="%Y-%m-%d")),
            "salary": dict(method="floats_normal", kwargs=dict(mean=60000, std=15000, decimals=2)),
            "department": dict(method="distincts", kwargs=dict(distincts=["Engineering", "Sales", "Marketing", "HR", "Finance"])),
            "role": dict(method="distincts", kwargs=dict(distincts=["Junior", "Senior", "Lead", "Manager", "Director"])),
            "is_remote": dict(method="booleans", kwargs=dict(true_prob=0.4)),
            "bonus": dict(method="floats", kwargs=dict(min=0, max=20000, decimals=2))
        }

    @classmethod
    def devices(cls) -> Dict[str, Any]:
        """
        IoT devices - Demonstrates device monitoring patterns.
        
        **Complexity Level: ★★★★☆ (Expert)** - Shows complex IoT data generation.
        
        Demonstrates:
        - uuid4: Device identifiers
        - distincts_prop: Weighted device types
        - distincts: Status and priority
        - floats: Temperature readings
        - integers: Battery levels
        - unix_timestamps: Last communication time
        
        Generated Columns (7):
        ---------------------
        - device_id: UUID4 identifiers
        - device_type: Types (Sensor 50%, Gateway 30%, Controller 20%)
        - status: Operational status
        - priority: Priority levels
        - temperature: Temperature 15-45°C with 1 decimal
        - battery: Battery percentage 0-100
        - last_ping: Unix timestamps from 2024
        
        Example:
        --------
        >>> df = SparkGenerator(spark, F, SparkRandSpecs.devices()).size(1000).get_df()
        >>> df.groupBy("device_type", "status").count().show()
        """
        return {
            "device_id": dict(method="uuid4", kwargs={}),
            "device_type": dict(method="distincts_prop", kwargs=dict(distincts={"Sensor": 50, "Gateway": 30, "Controller": 20})),
            "status": dict(method="distincts", kwargs=dict(distincts=["Online", "Offline", "Maintenance"])),
            "priority": dict(method="distincts", kwargs=dict(distincts=["Low", "Medium", "High"])),
            "temperature": dict(method="floats", kwargs=dict(min=15, max=45, decimals=1)),
            "battery": dict(method="integers", kwargs=dict(min=0, max=100)),
            "last_ping": dict(method="dates", kwargs=dict(start="2024-10-01", end="2024-10-18", date_format="%Y-%m-%d"))
        }

    @classmethod
    def users(cls) -> Dict[str, Any]:
        """
        Application users - Demonstrates user activity patterns.
        
        **Complexity Level: ★★★☆☆ (Advanced)** - Shows activity distributions and plans.
        
        Demonstrates:
        - int_zfilled: User identifiers
        - distincts: Usernames
        - distincts_prop: Weighted subscription plans
        - dates: Signup dates with date_format parameter
        - floats_normal: Login count distribution (mean=50, std=20)
        - booleans: Verification status
        
        Generated Columns (6):
        ---------------------
        - user_id: Zero-filled IDs (7 digits)
        - username: Random usernames
        - plan: Subscription plans (Free 60%, Pro 30%, Enterprise 10%)
        - signup_date: Dates from 2022-2024 (date_format parameter)
        - login_count: Normally distributed logins (rounded to integers with decimals=0)
        - is_verified: Boolean with 75% true probability
        
        Example:
        --------
        >>> df = SparkGenerator(spark, F, SparkRandSpecs.users()).size(1000).get_df()
        >>> df.groupBy("plan").count().show()  # Plan distribution
        """
        return {
            "user_id": dict(method="int_zfilled", kwargs=dict(length=7)),
            "username": dict(method="distincts", kwargs=dict(distincts=["alex_123", "maria_dev", "john_qa", "sara_eng", "mike_pm"])),
            "plan": dict(method="distincts_prop", kwargs=dict(distincts={"free": 60, "pro": 30, "enterprise": 10})),
            "signup_date": dict(method="dates", kwargs=dict(start="2022-01-01", end="2024-12-31", date_format="%Y-%m-%d")),
            "login_count": dict(method="floats_normal", kwargs=dict(mean=50, std=20, decimals=0)),
            "is_verified": dict(method="booleans", kwargs=dict(true_prob=0.75))
        }

    @classmethod
    def invoices(cls) -> Dict[str, Any]:
        """
        Invoice records - Demonstrates financial document patterns.
        
        **Complexity Level: ★★★☆☆ (Advanced)** - Shows invoice tracking and amounts.
        
        Demonstrates:
        - int_zfilled: Invoice numbers
        - dates: Issue and due dates with date_format parameter
        - floats: Invoice amounts and tax rates
        - distincts_prop: Weighted payment status
        
        Generated Columns (6):
        ---------------------
        - invoice_number: Zero-filled numbers (8 digits)
        - issue_date: Dates from 2023 (date_format parameter)
        - due_date: Dates from 2024 (date_format parameter)
        - amount: Amounts 100-50000 with 2 decimals
        - status: Payment status (Paid 60%, Pending 30%, Overdue 10%)
        - tax_rate: Tax rates 0-25 with 2 decimals
        
        Example:
        --------
        >>> df = SparkGenerator(spark, F, SparkRandSpecs.invoices()).size(500).get_df()
        >>> df.groupBy("status").count().show()  # Payment status distribution
        """
        return {
            "invoice_number": dict(method="int_zfilled", kwargs=dict(length=8)),
            "issue_date": dict(method="dates", kwargs=dict(start="2023-01-01", end="2023-12-31", date_format="%Y-%m-%d")),
            "due_date": dict(method="dates", kwargs=dict(start="2024-01-01", end="2024-12-31", date_format="%Y-%m-%d")),
            "amount": dict(method="floats", kwargs=dict(min=100, max=50000, decimals=2)),
            "status": dict(method="distincts_prop", kwargs=dict(distincts={"Paid": 60, "Pending": 30, "Overdue": 10})),
            "tax_rate": dict(method="floats", kwargs=dict(min=0, max=25, decimals=2))
        }

    @classmethod
    def shipments(cls) -> Dict[str, Any]:
        """
        Shipping records - Demonstrates logistics patterns.
        
        **Complexity Level: ★★★☆☆ (Advanced)** - Shows tracking and weight data.
        
        Demonstrates:
        - int_zfilled: Tracking numbers
        - distincts: Carriers and destinations
        - floats: Weight measurements
        - distincts_prop: Weighted shipping status
        - dates: Ship and delivery dates with date_format parameter
        
        Generated Columns (7):
        ---------------------
        - tracking_number: Zero-filled tracking numbers (10 digits)
        - carrier: Shipping carriers
        - destination: Destination codes
        - weight: Weights 0.1-50 kg with 2 decimals
        - status: Shipping status (In Transit 40%, Delivered 50%, Exception 10%)
        - ship_date: Dates from Jan-Oct 2024 (date_format parameter)
        - estimated_delivery: Dates from Jan-Oct 2024 (date_format parameter)
        
        Example:
        --------
        >>> df = SparkGenerator(spark, F, SparkRandSpecs.shipments()).size(1000).get_df()
        >>> df.groupBy("carrier", "status").count().show()
        """
        return {
            "tracking_number": dict(method="int_zfilled", kwargs=dict(length=10)),
            "carrier": dict(method="distincts", kwargs=dict(distincts=["FedEx", "DHL", "USPS", "UPS"])),
            "destination": dict(method="distincts", kwargs=dict(distincts=["US", "CA", "EU", "UK", "MX"])),
            "weight": dict(method="floats", kwargs=dict(min=0.1, max=50, decimals=2)),
            "status": dict(method="distincts_prop", kwargs=dict(distincts_prop={"In Transit": 40, "Delivered": 50, "Exception": 10})),
            "ship_date": dict(method="dates", kwargs=dict(start="2024-01-01", end="2024-10-01", date_format="%Y-%m-%d")),
            "estimated_delivery": dict(method="dates", kwargs=dict(start="2024-01-05", end="2024-10-18", date_format="%Y-%m-%d"))
        }

    @classmethod
    def events(cls) -> Dict[str, Any]:
        """
        Event logs - Demonstrates logging patterns.
        
        **Complexity Level: ★★★☆☆ (Advanced)** - Shows event tracking and severity.
        
        Demonstrates:
        - uuid4: Event identifiers
        - unix_timestamps: Event timing
        - distincts_prop: Weighted event types and severity
        - distincts: Event sources and messages
        
        Generated Columns (6):
        ---------------------
        - event_id: UUID4 identifiers
        - timestamp: Unix timestamps from Oct 2024
        - event_type: Types (INFO 50%, WARNING 30%, ERROR 15%, CRITICAL 5%)
        - severity: Severity levels (Low 60%, Medium 30%, High 10%)
        - source: Event sources
        - message: Event messages
        
        Example:
        --------
        >>> df = SparkGenerator(spark, F, SparkRandSpecs.events()).size(1000).get_df()
        >>> df.groupBy("event_type").count().orderBy("count", ascending=False).show()
        """
        return {
            "event_id": dict(method="uuid4", kwargs={}),
            "timestamp": dict(method="dates", kwargs=dict(start="2024-10-01", end="2024-10-18", date_format="%Y-%m-%d")),
            "event_type": dict(method="distincts_prop", kwargs=dict(distincts={"INFO": 50, "WARNING": 30, "ERROR": 15, "CRITICAL": 5})),
            "severity": dict(method="distincts_prop", kwargs=dict(distincts={"Low": 60, "Medium": 30, "High": 10})),
            "source": dict(method="distincts", kwargs=dict(distincts=["API", "Database", "Frontend", "Backend"])),
            "message": dict(method="distincts", kwargs=dict(distincts=["Request processed", "Connection timeout", "Invalid input", "Server error", "Cache miss"]))
        }
