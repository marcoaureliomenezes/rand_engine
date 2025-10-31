"""from 
Unit tests for PyCore methods.

Tests the Python-based generation methods in rand_engine/core/_py_core.py.
These methods handle complex distinct value generation patterns.
"""
import pytest
import numpy as np
from rand_engine.core._py_core import PyCore
from rand_engine.core._np_core import NPCore


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
        
        result = PyCore.gen_complex_distincts(
            size=size,
            pattern=pattern,
            replacement=replacement,
            templates=templates
        )
        
        assert len(result) == size
        assert isinstance(result, np.ndarray)
        
        # Check format (IP-like)
        for item in result:
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
        
        result = PyCore.gen_complex_distincts(
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
        
        result = PyCore.gen_complex_distincts(
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
        
        result = PyCore.gen_complex_distincts(
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


class TestPyCoreDistinctsUntyped:
    """Test untyped distinct generation."""
    
    def test_gen_distincts_untyped_strings(self):
        """Test untyped distinct generation with strings."""
        size = 50
        distinct = ["apple", "banana", "cherry", "date"]
        result = PyCore.gen_distincts_untyped(size=size, distinct=distinct)
        
        assert len(result) == size
        assert isinstance(result, list)
        assert all(item in distinct for item in result)
    
    def test_gen_distincts_untyped_mixed_types(self):
        """Test untyped distinct generation with mixed types."""
        size = 30
        distinct = [1, "two", 3.0, True, None]
        result = PyCore.gen_distincts_untyped(size=size, distinct=distinct)
        
        assert len(result) == size
        assert all(item in distinct for item in result)
    
    def test_gen_distincts_untyped_tuples(self):
        """Test untyped distinct generation with tuples."""
        size = 40
        distinct = [("A", 1), ("B", 2), ("C", 3)]
        result = PyCore.gen_distincts_untyped(size=size, distinct=distinct)
        
        assert len(result) == size
        assert all(item in distinct for item in result)


class TestPyCoreDistinctsMap:
    """Test mapped distinct generation."""
    
    def test_gen_distincts_map_simple(self):
        """Test simple category mapping."""
        size = 100
        distincts = {
            "Fruit": ["apple", "banana", "orange"],
            "Vegetable": ["carrot", "lettuce", "tomato"]
        }
        result = PyCore.gen_distincts_map(size=size, distincts=distincts)
        
        assert len(result) == size
        assert isinstance(result, list)
        
        # Check all results are valid category-value pairs
        expected_pairs = [
            ("apple", "Fruit"), ("banana", "Fruit"), ("orange", "Fruit"),
            ("carrot", "Vegetable"), ("lettuce", "Vegetable"), ("tomato", "Vegetable")
        ]
        assert all(item in expected_pairs for item in result)
    
    def test_gen_distincts_map_single_category(self):
        """Test mapping with single category."""
        size = 50
        distincts = {
            "Color": ["red", "green", "blue"]
        }
        result = PyCore.gen_distincts_map(size=size, distincts=distincts)
        
        assert len(result) == size
        # All should be from Color category
        expected_pairs = [("red", "Color"), ("green", "Color"), ("blue", "Color")]
        assert all(item in expected_pairs for item in result)


class TestPyCoreDistinctsMultiMap:
    """Test multi-level mapped distinct generation."""
    
    def test_gen_distincts_multi_map_basic(self):
        """Test multi-map with nested lists."""
        size = 100
        distincts = {
            "PF": [["premium", "standard"], ["gold", "silver"]],
            "PJ": [["premium", "standard"], ["platinum", "basic"]]
        }
        result = PyCore.gen_distincts_multi_map(size=size, distincts=distincts)
        
        assert len(result) == size
        assert isinstance(result, list)
        
        # Each result should be a list with category + combinations
        for item in result:
            assert isinstance(item, list)
            assert len(item) == 3  # category + 2 levels
            assert item[0] in ["PF", "PJ"]
    
    def test_gen_distincts_multi_map_simple(self):
        """Test multi-map with simple structure."""
        size = 50
        distincts = {
            "Type1": [["A"], ["X"]],
            "Type2": [["B"], ["Y"]]
        }
        result = PyCore.gen_distincts_multi_map(size=size, distincts=distincts)
        
        assert len(result) == size
        
        # Check structure
        for item in result:
            assert isinstance(item, list)
            assert item[0] in ["Type1", "Type2"]


class TestPyCoreDistinctsMapProp:
    """Test proportional mapped distinct generation."""
    
    def test_gen_distincts_map_prop_basic(self):
        """Test proportional category-value mapping."""
        size = 1000
        distincts = {
            "Junior": [("basic", 70), ("intermediate", 30)],
            "Senior": [("advanced", 60), ("expert", 40)]
        }
        result = PyCore.gen_distincts_map_prop(size=size, distincts=distincts)
        
        assert len(result) == size
        assert isinstance(result, list)
        
        # Check all are valid tuples
        expected_values = [
            ("Junior", "basic"),
            ("Junior", "intermediate"),
            ("Senior", "advanced"),
            ("Senior", "expert")
        ]
        assert all(item in expected_values for item in result)
    
    def test_gen_distincts_map_prop_distribution(self):
        """Test that proportional distribution is approximately correct."""
        size = 10000
        distincts = {
            "A": [("A1", 80), ("A2", 20)],
            "B": [("B1", 50), ("B2", 50)]
        }
        result = PyCore.gen_distincts_map_prop(size=size, distincts=distincts)
        
        # Count occurrences
        from collections import Counter
        counts = Counter(result)
        
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
        result = PyCore.gen_distincts_map_prop(size=size, distincts=distincts)
        
        assert len(result) == size
        
        # All should be from Status category
        for item in result:
            assert item[0] == "Status"
            assert item[1] in ["active", "inactive", "suspended"]


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
            PyCore.gen_complex_distincts(
                size=size,
                pattern=pattern,
                replacement=replacement,
                templates=templates
            )
    
    def test_gen_distincts_untyped_empty_list(self):
        """Test untyped generation with empty list."""
        size = 10
        distinct = []
        
        with pytest.raises((ValueError, IndexError)):
            PyCore.gen_distincts_untyped(size=size, distinct=distinct)
    
    def test_gen_distincts_untyped_single_element(self):
        """Test untyped generation with single element."""
        size = 20
        distinct = ["only_one"]
        result = PyCore.gen_distincts_untyped(size=size, distinct=distinct)
        
        assert len(result) == size
        assert all(item == "only_one" for item in result)


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
        
        result = PyCore.gen_complex_distincts(
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
