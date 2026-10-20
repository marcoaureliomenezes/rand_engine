"""from 
Unit tests for PyCore methods.

Tests the Python-based generation methods in rand_engine/core/_py_core.py.
These methods handle complex distinct value generation patterns.
"""
import pytest
import numpy as np
import pyarrow as pa
from rand_engine.core._py_core import PyCore
from rand_engine.core._np_core import NPCore
from rand_engine.main.data_generator import DataGenerator

RNG = np.random.default_rng(0)


def _levels(result):
  return [c.to_pylist() if isinstance(c, (pa.Array, pa.ChunkedArray)) else list(c) for c in result]


class TestPyCoreComplexDistincts:
    """Test complex distinct pattern generation."""
    
    def test_gen_complex_distincts_simple_pattern(self):
        """Test complex distincts with simple IP-like pattern."""
        size = 10
        pattern = "x.x.x.x"
        replacement = "x"
        templates = [
            {"method": NPCore.gen_distincts, "kwargs": {"distincts": ["192", "172"]}},
            {"method": NPCore.gen_distincts, "kwargs": {"distincts": ["168", "10"]}},
            {"method": NPCore.gen_ints, "kwargs": {"min": 0, "max": 255, "int_type": "int32"}},
            {"method": NPCore.gen_ints, "kwargs": {"min": 1, "max": 254, "int_type": "int32"}}
        ]
        
        result = PyCore.gen_complex_distincts(rng=RNG, 
            size=size,
            pattern=pattern,
            replacement=replacement,
            templates=templates
        )
        
        assert len(result) == size
        assert isinstance(result, (pa.Array, pa.ChunkedArray))
        
        # Check format (IP-like)
        for item in result.to_pylist():
            parts = str(item).split(".")
            assert len(parts) == 4
            assert parts[0] in ["192", "172"]
            assert parts[1] in ["168", "10"]
    
    def test_gen_complex_distincts_custom_pattern(self):
        """Test complex distincts with custom pattern."""
        size = 20
        pattern = "ID-x-x"
        replacement = "x"
        templates = [
            {"method": NPCore.gen_ints_zfilled, "kwargs": {"length": 4}},
            {"method": NPCore.gen_distincts, "kwargs": {"distincts": ["A", "B", "C"]}}
        ]
        
        result = PyCore.gen_complex_distincts(rng=RNG, 
            size=size,
            pattern=pattern,
            replacement=replacement,
            templates=templates
        )
        
        assert len(result) == size
        
        # Check format
        for item in result:
            item_str = str(item)
            assert item_str.startswith("ID-")
            parts = item_str.split("-")
            assert len(parts) == 3
            assert len(parts[1]) == 4  # Zero-filled 4 digits
            assert parts[2] in ["A", "B", "C"]
    
    def test_gen_complex_distincts_with_string_methods(self):
        """Test complex distincts using string method names."""
        size = 15
        pattern = "x-x-x"
        replacement = "x"
        templates = [
            {"method": "integers", "kwargs": {"min": 1, "max": 100, "int_type": "int32"}},
            {"method": "distincts", "kwargs": {"distincts": ["alpha", "beta", "gamma"]}},
            {"method": "int_zfilled", "kwargs": {"length": 6}}
        ]
        
        result = PyCore.gen_complex_distincts(rng=RNG, 
            size=size,
            pattern=pattern,
            replacement=replacement,
            templates=templates
        )
        
        assert len(result) == size
        
        # Check format
        for item in result:
            parts = str(item).split("-")
            assert len(parts) == 3
            assert parts[1] in ["alpha", "beta", "gamma"]
            assert len(parts[2]) == 6
    
    def test_gen_complex_distincts_mac_address_like(self):
        """Test complex distincts for MAC address-like pattern."""
        size = 10
        pattern = "x:x:x:x:x:x"
        replacement = "x"
        # MAC address uses hex (simulate with distincts)
        hex_values = [f"{i:02X}" for i in range(256)]
        templates = [
            {"method": NPCore.gen_distincts, "kwargs": {"distincts": hex_values}} for _ in range(6)
        ]
        
        result = PyCore.gen_complex_distincts(rng=RNG, 
            size=size,
            pattern=pattern,
            replacement=replacement,
            templates=templates
        )
        
        assert len(result) == size
        
        # Check format
        for item in result:
            parts = str(item).split(":")
            assert len(parts) == 6


class TestPyCoreDistinctsMap:
    """Test mapped distinct generation."""
    
    def test_gen_distincts_map_simple(self):
        """Test simple category mapping."""
        size = 100
        distincts = {
            "Fruit": ["apple", "banana", "orange"],
            "Vegetable": ["carrot", "lettuce", "tomato"]
        }
        result = PyCore.gen_distincts_map(rng=RNG, size=size, distincts=distincts)
        
        category, value = _levels(result)
        assert len(result) == 2
        assert len(category) == len(value) == size
        
        # Check all results are valid category-value pairs
        expected_pairs = [
            ("Fruit", "apple"), ("Fruit", "banana"), ("Fruit", "orange"),
            ("Vegetable", "carrot"), ("Vegetable", "lettuce"), ("Vegetable", "tomato")
        ]
        assert all(item in expected_pairs for item in zip(category, value))
    
    def test_gen_distincts_map_single_category(self):
        """Test mapping with single category."""
        size = 50
        distincts = {
            "Color": ["red", "green", "blue"]
        }
        result = PyCore.gen_distincts_map(rng=RNG, size=size, distincts=distincts)
        
        category, value = _levels(result)
        assert len(category) == len(value) == size
        # All should be from Color category
        expected_pairs = [("Color", "red"), ("Color", "green"), ("Color", "blue")]
        assert all(item in expected_pairs for item in zip(category, value))


class TestPyCoreDistinctsMultiMap:
    """Test multi-level mapped distinct generation."""
    
    def test_gen_distincts_multi_map_basic(self):
        """Test multi-map with nested lists."""
        size = 100
        distincts = {
            "PF": [["premium", "standard"], ["gold", "silver"]],
            "PJ": [["premium", "standard"], ["platinum", "basic"]]
        }
        result = PyCore.gen_distincts_multi_map(rng=RNG, size=size, distincts=distincts)
        
        assert len(result) == 3  # category + 2 levels
        assert all(len(col) == size for col in result)
        assert set(_levels(result)[0]) <= {"PF", "PJ"}
    
    def test_gen_distincts_multi_map_simple(self):
        """Test multi-map with simple structure."""
        size = 50
        distincts = {
            "Type1": [["A"], ["X"]],
            "Type2": [["B"], ["Y"]]
        }
        result = PyCore.gen_distincts_multi_map(rng=RNG, size=size, distincts=distincts)
        
        assert len(result) == 3
        assert all(len(col) == size for col in result)
        assert set(_levels(result)[0]) <= {"Type1", "Type2"}


class TestPyCoreDistinctsMapProp:
    """Test proportional mapped distinct generation."""
    
    def test_gen_distincts_map_prop_basic(self):
        """Test proportional category-value mapping."""
        size = 1000
        distincts = {
            "Junior": [("basic", 70), ("intermediate", 30)],
            "Senior": [("advanced", 60), ("expert", 40)]
        }
        result = PyCore.gen_distincts_map_prop(rng=RNG, size=size, distincts=distincts)
        
        category, value = _levels(result)
        assert len(result) == 2
        assert len(category) == len(value) == size
        
        # Check all are valid tuples
        expected_values = [
            ("Junior", "basic"),
            ("Junior", "intermediate"),
            ("Senior", "advanced"),
            ("Senior", "expert")
        ]
        assert all(item in expected_values for item in zip(category, value))
    
    def test_gen_distincts_map_prop_distribution(self):
        """Test that proportional distribution is approximately correct."""
        size = 10000
        distincts = {
            "A": [("A1", 80), ("A2", 20)],
            "B": [("B1", 50), ("B2", 50)]
        }
        result = PyCore.gen_distincts_map_prop(rng=RNG, size=size, distincts=distincts)
        
        # Count occurrences
        from collections import Counter
        counts = Counter(zip(*_levels(result)))
        
        # Check proportions exist
        assert ("A", "A1") in counts
        assert ("A", "A2") in counts
        assert ("B", "B1") in counts
        assert ("B", "B2") in counts
    
    def test_gen_distincts_map_prop_single_category(self):
        """Test proportional mapping with single category."""
        size = 500
        distincts = {
            "Status": [("active", 70), ("inactive", 20), ("suspended", 10)]
        }
        result = PyCore.gen_distincts_map_prop(rng=RNG, size=size, distincts=distincts)
        
        category, value = _levels(result)
        assert len(category) == len(value) == size
        
        # All should be from Status category
        for cat, val in zip(category, value):
            assert cat == "Status"
            assert val in ["active", "inactive", "suspended"]


class TestPyCoreEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_gen_complex_distincts_template_count_mismatch(self):
        """Test that assertion fails when template count doesn't match replacements."""
        size = 10
        pattern = "x.x.x"
        replacement = "x"
        templates = [
            {"method": NPCore.gen_ints, "kwargs": {"min": 0, "max": 255, "int_type": "int32"}},
            {"method": NPCore.gen_ints, "kwargs": {"min": 0, "max": 255, "int_type": "int32"}}
            # Missing one template!
        ]
        
        with pytest.raises(AssertionError):
            PyCore.gen_complex_distincts(rng=RNG, 
                size=size,
                pattern=pattern,
                replacement=replacement,
                templates=templates
            )
    


class TestPyCoreIntegration:
    """Integration tests combining multiple PyCore methods."""
    
    def test_complex_distincts_with_multiple_types(self):
        """Test complex pattern combining different NPCore methods."""
        size = 50
        pattern = "USER-x-x-x"
        replacement = "x"
        templates = [
            {"method": NPCore.gen_ints_zfilled, "kwargs": {"length": 8}},
            {"method": NPCore.gen_distincts, "kwargs": {"distincts": ["ACTIVE", "INACTIVE", "PENDING"]}},
            {"method": NPCore.gen_ints, "kwargs": {"min": 1, "max": 999, "int_type": "int32"}}
        ]
        
        result = PyCore.gen_complex_distincts(rng=RNG, 
            size=size,
            pattern=pattern,
            replacement=replacement,
            templates=templates
        )
        
        assert len(result) == size
        
        # Verify pattern
        for item in result:
            item_str = str(item)
            assert item_str.startswith("USER-")
            parts = item_str.split("-")
            assert len(parts) == 4
            assert len(parts[1]) == 8  # Zero-filled
            assert parts[2] in ["ACTIVE", "INACTIVE", "PENDING"]


def test_gen_distincts_map_puts_category_first():
    """Operator ruling G9: (category, value), like distincts_map_prop."""
    result = PyCore.gen_distincts_map(rng=RNG, size=50, distincts={"smartphone": ["android", "ios"]})
    category, value = _levels(result)
    assert category == ["smartphone"] * 50
    assert set(value) == {"android", "ios"}


def _int(**kw):
    return {"method": "integers", "kwargs": kw}


@pytest.mark.parametrize("pattern, templates, expected", [
    ("x.x.x.x",
     [{"method": "distincts", "kwargs": {"distincts": ["192", "172", "10"]}}, _int(min=0, max=255), _int(min=0, max=255), _int(min=1, max=254)],
     [".".join(p) for p in (("10", "229", "213", "77"), ("172", "148", "57", "73"), ("10", "198", "14", "222"))]),
    ("n-x", [_int(min=0, max=100)], ["n-95", "n-63", "n-69"]),
    ("x|x", [{"method": "floats", "kwargs": {"min": 0, "max": 10, "decimals": 2}}, _int(min=1, max=9)],
     ["9.45|9", "6.25|6", "6.84|7"]),
    ("x/x/x", [{"method": "booleans", "kwargs": {}}] * 3, ["False/True/True", "False/True/False", "False/False/False"]),
    ("#x", [_int(min=0, max=10**12, int_type="int64")], ["#625095466605", "#897213800970", "#775685690245"]),
    ("ID-x", [{"method": "int_zfilled", "kwargs": {"length": 5}}], ["ID-94490", "ID-62509", "ID-68417"]),
    ("u:x", [{"method": "uuid4", "kwargs": {}}],
     ["u:8b4ae5f1-a941-46a0-956a-26afbccdafe5", "u:62f90a94-5f56-43c6-8227-6ad5ab2da739", "u:4551370e-99b2-474c-b427-fa48d732a1df"]),
], ids=["ci_ip", "int", "float", "bool", "bigint", "zfilled", "uuid4"])
def test_gen_complex_distincts_arrow_text_matches_080(pattern, templates, expected):
    result = PyCore.gen_complex_distincts(size=3, pattern=pattern, replacement="x", templates=templates,
                                          rng=np.random.default_rng(7))
    assert isinstance(result, (pa.Array, pa.ChunkedArray))
    assert result.type == pa.string()
    assert result.to_pylist() == expected


@pytest.mark.parametrize("kwargs, head, tail", [
    (dict(min=-100, max=100, int_type="int8"), ["n:79", "n:89", "n:32"], ["n:48", "n:57", "n:-67"]),
    (dict(min=-20000, max=20000, int_type="int16"), ["n:-8353", "n:17796", "n:-9741"], ["n:3938", "n:-11889", "n:520"]),
], ids=["int8", "int16"])
def test_gen_complex_distincts_narrow_int_part_crossing_signed_max_renders_080_text(kwargs, head, tail):
    result = PyCore.gen_complex_distincts(300, pattern="n:x", replacement="x", templates=[_int(**kwargs)],
                                          rng=np.random.default_rng(7)).to_pylist()
    assert (len(result), result[:3], result[-3:]) == (300, head, tail)


def test_gen_complex_distincts_templateless_pattern_repeats_literal():
    result = PyCore.gen_complex_distincts(3, pattern="ABC", replacement="x", templates=[], rng=np.random.default_rng(7))
    assert result.type == pa.string()
    assert result.to_pylist() == ["ABC"] * 3


_MAP_080 = {
    "map": ({"mobile": ["android", "ios"], "desktop": ["windows", "macos", "linux"]}, [
        ["desktop", "mobile", "mobile", "mobile", "mobile", "desktop", "desktop", "desktop"],
        ["linux", "android", "android", "ios", "android", "linux", "linux", "windows"]]),
    "multi_map": ({"tech": [["software", "hardware"], ["small", "medium", "large"]]}, [
        ["tech"] * 8,
        ["hardware", "software", "software", "software", "software", "hardware", "hardware", "hardware"],
        ["medium", "small", "medium", "medium", "medium", "medium", "large", "small"]]),
    "map_prop": ({"EQUITY": [("BUY", 6), ("SELL", 4)], "FX": [("BUY", 5), ("SELL", 5)]}, [
        ["FX", "EQUITY", "EQUITY", "EQUITY", "EQUITY", "FX", "FX", "FX"],
        ["SELL", "BUY", "BUY", "BUY", "BUY", "SELL", "SELL", "BUY"]]),
}


@pytest.mark.parametrize("name", list(_MAP_080))
def test_map_family_returns_one_arrow_text_column_per_level_as_080(name):
    distincts, expected = _MAP_080[name]
    result = getattr(PyCore, f"gen_distincts_{name}")(size=8, distincts=distincts, rng=np.random.default_rng(3))
    assert len(result) == len(expected)
    assert all(isinstance(c, (pa.Array, pa.ChunkedArray)) and c.type == pa.string() for c in result)
    assert _levels(result) == expected


@pytest.mark.parametrize("level, expected", [
    ([1, "a"], ["a", 1, 1, 1, 1, "a", "a", "a"]),
    (["a", None], [None, "a", "a", "a", "a", None, None, None]),
], ids=["mixed_int_str", "str_and_none"])
def test_distincts_map_non_text_level_keeps_object_dtype_and_values_as_080(level, expected):
    spec = {"x": {"method": "distincts_map", "cols": ["k", "v"], "kwargs": {"distincts": {"x": level}}}}
    df = DataGenerator(spec, seed=3).size(8).get_df()
    assert df["v"].dtype == object
    assert df["v"].tolist() == expected
    assert df["k"].tolist() == ["x"] * 8
