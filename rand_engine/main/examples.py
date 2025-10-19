from typing import Dict, Any


class ExampleSpecs:
    """
    Pre-built specification examples for learning and quick prototyping.
    
    ExampleSpecs provides ready-to-use data generation specifications that demonstrate
    different generation methods and patterns. Each spec is accessible as an attribute
    and is cached for efficiency.
    
    Available Specs:
    ---------------
    - simple_client: Basic spec with 8 common data types
    - simple_client_2: Demonstrates distincts_map (correlated pairs)
    - simple_client_3: Demonstrates distincts_map_prop (weighted correlations)
    - simple_client_4: Demonstrates distincts_multi_map (N-level cartesian products)
    
    Usage:
    ------
    >>> from rand_engine import DataGenerator, ExampleSpecs
    >>> examples = ExampleSpecs()
    >>> 
    >>> # Generate data using a pre-built spec
    >>> df = DataGenerator(examples.simple_client, seed=42).size(1000).get_df()
    >>> print(df.head())
    >>> 
    >>> # Or access spec directly to customize
    >>> my_spec = examples.simple_client.copy()
    >>> my_spec['age']['kwargs']['max'] = 50  # Customize age range
    >>> df = DataGenerator(my_spec).size(100).get_df()
    
    Notes:
    ------
    - All specs are cached after first access for performance
    - Specs are returned as dictionaries, safe to modify
    - Each spec demonstrates different generation patterns
    """

    def __init__(self):
        self.professions = ["Data Engineer", "QA Engineer", "Software Engineer"]
        
        # Cache specs as attributes for direct access
        self._simple_client = None
        self._simple_client_2 = None
        self._simple_client_3 = None
        self._simple_client_4 = None

    @property
    def simple_client(self) -> Dict[str, Any]:
        """
        Basic client spec demonstrating core generation methods.
        
        Use this spec to:
        - Learn the basic structure of specifications
        - Test simple data generation
        - Understand common generation methods
        
        Generated Columns:
        -----------------
        - id: Unique zero-filled integers (e.g., "00000001", "00000002")
        - age: Random integers between 0-100
        - salary: Random floats 0-1000 with 2 decimal places
        - height: Normally distributed floats (mean=1000, std=10)
        - is_active: Boolean with 70% probability of True
        - profession: Random selection from ["Data Engineer", "QA Engineer", "Software Engineer"]
        - created_at: Unix timestamps from year 2020
        - device: Weighted random selection (mobile:desktop = 2:1)
        
        Generation Methods Used:
        -----------------------
        - unique_ids: Generates unique identifiers
        - integers: Random integers in range
        - floats: Random floats with precision
        - floats_normal: Normally distributed floats
        - booleans: Boolean values with probability
        - distincts: Random selection from list
        - unix_timestamps: Timestamps in date range
        - distincts_prop: Weighted random selection
        
        Example:
        --------
        >>> from rand_engine import DataGenerator, ExampleSpecs
        >>> examples = ExampleSpecs()
        >>> df = DataGenerator(examples.simple_client, seed=42).size(100).get_df()
        >>> print(df.columns.tolist())
        ['id', 'age', 'salary', 'height', 'is_active', 'profession', 'created_at', 'device']
        >>> print(df.head())
        """
        if self._simple_client is None:
            self._simple_client = {
                "id":        dict(method="unique_ids", kwargs=dict(strategy="zint")),
                "age":         dict(method="integers", kwargs=dict(min=0, max=100)),
                "salary":      dict(method="floats", kwargs=dict(min=0, max=10**3, round=2)),
                "height":      dict(method="floats_normal", kwargs=dict(mean=10**3, std=10**1, round=2)),
                "is_active":   dict(method="booleans", kwargs=dict(true_prob=0.7)),
                "profession":  dict(method="distincts", kwargs=dict(distincts=self.professions)),
                "created_at":  dict(method="unix_timestamps", kwargs=dict(start="01-01-2020", end="31-12-2020", format="%d-%m-%Y")),
                "device":     dict(method="distincts_prop", kwargs=dict(distincts={"mobile": 2, "desktop": 1})),
            }
        return self._simple_client
    
    @property
    def simple_client_2(self) -> Dict[str, Any]:
        """
        Client spec demonstrating device-platform correlation using distincts_map.
        
        Use this spec to:
        - Learn how distincts_map creates correlated 2-column pairs
        - Understand mapping between categories and their values
        - Generate realistic device-OS combinations
        
        Generated Columns:
        -----------------
        - id: Unique zero-filled integers
        - profession: Random selection from professions list
        - created_at: Unix timestamps from year 2020
        - device: Weighted selection (mobile:desktop = 2:1)
        - device_type: OS name (android, IOS, linux, windows, macOS, windows phone)
        - os_type: OS category (smartphone or desktop)
        
        Correlation Pattern (distincts_map):
        -----------------------------------
        Note: distincts_map puts dictionary KEYS in the SECOND column (os_type)
        and VALUES in the FIRST column (device_type).
        
        - os_type="smartphone" → device_type in ["android", "IOS", "windows phone"]
        - os_type="desktop" → device_type in ["linux", "windows", "macOS"]
        
        Invalid combinations NEVER occur:
        - (android, desktop), (IOS, desktop), (windows phone, desktop)
        - (linux, smartphone), (windows, smartphone), (macOS, smartphone)
        
        Generation Methods Used:
        -----------------------
        - distincts_map: Creates correlated pairs from nested dictionary
        
        Example:
        --------
        >>> from rand_engine import DataGenerator, ExampleSpecs
        >>> examples = ExampleSpecs()
        >>> df = DataGenerator(examples.simple_client_2, seed=42).size(100).get_df()
        >>> 
        >>> # Check correlations
        >>> print(df[df['os_type'] == 'smartphone']['device_type'].unique())
        ['android' 'IOS' 'windows phone']
        >>> 
        >>> print(df[df['os_type'] == 'desktop']['device_type'].unique())
        ['linux' 'windows' 'macOS']
        """
        if self._simple_client_2 is None:
            self._simple_client_2 = {
                "id":        dict(method="unique_ids", kwargs=dict(strategy="zint")),
                "profession":  dict(method="distincts", kwargs=dict(distincts=self.professions)),
                "created_at":  dict(method="unix_timestamps", kwargs=dict(start="01-01-2020", end="31-12-2020", format="%d-%m-%Y")),
                "device":     dict(method="distincts_prop", kwargs=dict(distincts={"mobile": 2, "desktop": 1})),
                "device_plat": dict(
                                method="distincts_map", cols = ["device_type", "os_type"],
                                kwargs=dict(distincts={
                                "smartphone": ["android","IOS", "windows phone"], 
                                "desktop": ["linux", "windows", "macOS"]
                })),
            }
        return self._simple_client_2

    @property
    def simple_client_3(self) -> Dict[str, Any]:
        """
        Client spec demonstrating weighted correlations using distincts_map_prop.
        
        Use this spec to:
        - Learn how distincts_map_prop creates weighted correlated pairs
        - Control relative frequencies of category-value combinations
        - Model realistic business scenarios with weighted distributions
        
        Generated Columns:
        -----------------
        - id: Unique zero-filled integers
        - profession: Random selection from professions list
        - device: Weighted selection (mobile:desktop = 2:1)
        - op: Operation type ("OPC" or "SWP")
        - tip_op: Operation subtype with weights
        
        Weighted Correlation Pattern (distincts_map_prop):
        -------------------------------------------------
        - op="OPC" → tip_op in ["C_OPC" (80%), "V_OPC" (20%)]
        - op="SWP" → tip_op in ["C_SWP" (60%), "V_SWP" (40%)]
        
        The weights control relative frequencies:
        - C_OPC appears 8x more than V_OPC within OPC operations
        - C_SWP appears 6x more than V_SWP (but 4x is closer to 60/40)
        
        Generation Methods Used:
        -----------------------
        - distincts_map_prop: Creates weighted correlated pairs
        
        Example:
        --------
        >>> from rand_engine import DataGenerator, ExampleSpecs
        >>> examples = ExampleSpecs()
        >>> df = DataGenerator(examples.simple_client_3, seed=42).size(1000).get_df()
        >>> 
        >>> # Check weighted distribution for OPC
        >>> opc_data = df[df['op'] == 'OPC']
        >>> print(opc_data['tip_op'].value_counts(normalize=True))
        C_OPC    0.80  # Approximately 80%
        V_OPC    0.20  # Approximately 20%
        """
        if self._simple_client_3 is None:
            self._simple_client_3 = {
                "id":        dict(method="unique_ids", kwargs=dict(strategy="zint")),
                "profession":  dict(method="distincts", kwargs=dict(distincts=self.professions)),
                "device":     dict(method="distincts_prop", kwargs=dict(distincts={"mobile": 2, "desktop": 1})),
                "deriv_tip": dict(
                                method="distincts_map_prop", cols = ["op", "tip_op"],
                                kwargs=dict(distincts={
                                "OPC": [ ("C_OPC", 8), ("V_OPC", 2)], 
                                "SWP": [ ("C_SWP", 6), ("V_SWP", 4)]
                })),
            }
        return self._simple_client_3
    
    @property
    def simple_client_4(self) -> Dict[str, Any]:
        """
        Client spec demonstrating multi-level correlations using distincts_multi_map.
        
        Use this spec to:
        - Learn how distincts_multi_map creates N-level cartesian product correlations
        - Model complex hierarchical relationships (e.g., Company → Sector → Size → Location)
        - Generate all possible combinations from multiple levels
        
        Generated Columns:
        -----------------
        - id: Unique zero-filled integers
        - profession: Random selection from professions list
        - device: Weighted selection (mobile:desktop = 2:1)
        - setor: Business sector ("setor_1" or "setor_2")
        - sub_setor: Industry subsector (varies by sector)
        - porte: Company size indicator
        - codigo_municipio: Municipality code
        
        Multi-Level Correlation Pattern (distincts_multi_map):
        -----------------------------------------------------
        The spec generates cartesian products of all value combinations:
        
        **setor_1 (Primary Sector):**
        - sub_setor: ["agro", "mineração", "petróleo", "pecuária"]
        - porte: [0.25, 0.15]
        - [None]  # Extra level causing current mapping
        - ["01", "02"]
        
        Total combinations: 4 × 2 × 1 × 2 = 16 combinations
        
        **setor_2 (Secondary Sector):**
        - sub_setor: ["indústria", "construção"]
        - porte: [0.30, 0.20, 0.10]
        - ["micro", "pequena", "média"]
        - ["03", "04", "05"]
        
        Total combinations: 2 × 3 × 3 × 3 = 54 combinations
        
        Current Behavior (Due to Spec Structure):
        ----------------------------------------
        Note: The spec has an extra [None] array, causing unexpected mapping:
        - setor_1: codigo_municipio is always None (porte values are 0.25, 0.15)
        - setor_2: codigo_municipio contains ["micro", "pequena", "média"] 
                   (porte values are 0.30, 0.20, 0.10)
        
        This demonstrates how array positions map to columns in distincts_multi_map.
        
        Generation Methods Used:
        -----------------------
        - distincts_multi_map: Creates N-level cartesian product combinations
        
        Example:
        --------
        >>> from rand_engine import DataGenerator, ExampleSpecs
        >>> examples = ExampleSpecs()
        >>> df = DataGenerator(examples.simple_client_4, seed=42).size(200).get_df()
        >>> 
        >>> # Check setor_1 structure
        >>> s1 = df[df['setor'] == 'setor_1']
        >>> print(s1[['setor', 'sub_setor', 'porte', 'codigo_municipio']].drop_duplicates())
        >>> 
        >>> # Check setor_2 structure  
        >>> s2 = df[df['setor'] == 'setor_2']
        >>> print(s2[['setor', 'sub_setor', 'porte', 'codigo_municipio']].drop_duplicates().head(10))
        """
        if self._simple_client_4 is None:
            self._simple_client_4 = {
                "id":        dict(method="unique_ids", kwargs=dict(strategy="zint")),
                "profession":  dict(method="distincts", kwargs=dict(distincts=self.professions)),
                "device":     dict(method="distincts_prop", kwargs=dict(distincts={"mobile": 2, "desktop": 1})),
                "empresa": dict(
                        method="distincts_multi_map", cols = ["setor", "sub_setor", "porte", "codigo_municipio"],
                        kwargs=dict(distincts={
                        "setor_1": [
                            ["agro", "mineração", "petróleo", "pecuária"],
                            [0.25, 0.15],
                            [None],
                            ["01", "02"]
                        ], 
                        "setor_2": [
                            ["indústria", "construção"],
                            [0.30, 0.20, 0.10],
                            ["micro", "pequena", "média"],
                            ["03", "04", "05"]
                        ]
                })),
            }
        return self._simple_client_4