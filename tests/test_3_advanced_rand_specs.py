"""
Test suite for AdvancedRandSpecs - Validates advanced example specifications
Tests data generation using examples from rand_engine/examples/advanced_rand_specs.py
"""
import pytest
import pandas as pd
from rand_engine.examples import RandSpecs, AdvancedRandSpecs
from rand_engine import DataGenerator


class TestAdvancedRandSpecsAccess:
    """Test AdvancedRandSpecs static methods accessibility."""
    
    def test_customers_accessible(self):
        """Test that customers spec is accessible."""
        spec = RandSpecs.customers()
        assert isinstance(spec, dict)
        assert 'customer_id' in spec
        assert 'age' in spec
        assert 'city' in spec
    
    def test_products_accessible(self):
        """Test that products spec is accessible."""
        spec = RandSpecs.products()
        assert isinstance(spec, dict)
        assert 'sku' in spec
    
    def test_orders_accessible(self):
        """Test that orders spec is accessible."""
        spec = RandSpecs.orders()
        assert isinstance(spec, dict)
        assert 'order_id' in spec
    
    def test_transactions_accessible(self):
        """Test that transactions spec is accessible."""
        spec = RandSpecs.transactions()
        assert isinstance(spec, dict)
        assert 'transaction_id' in spec
    
    def test_employees_accessible(self):
        """Test that employees spec is accessible."""
        spec = RandSpecs.employees()
        assert isinstance(spec, dict)
        assert 'employee_id' in spec
    
    def test_devices_accessible(self):
        """Test that devices spec is accessible."""
        spec = RandSpecs.devices()
        assert isinstance(spec, dict)
        assert 'device_id' in spec
    
    def test_users_accessible(self):
        """Test that users spec is accessible."""
        spec = RandSpecs.users()
        assert isinstance(spec, dict)
        assert 'user_id' in spec
    
    def test_events_accessible(self):
        """Test that events spec is accessible."""
        spec = RandSpecs.events()
        assert isinstance(spec, dict)
        assert 'event_id' in spec


class TestAllSpecsGeneration:
    """Test that all specs can generate valid DataFrames."""
    
    @pytest.mark.parametrize("spec_name,spec_method", [
        ("customers", RandSpecs.customers),
        ("products", RandSpecs.products),
        ("orders", RandSpecs.orders),
        ("transactions", RandSpecs.transactions),
        ("employees", RandSpecs.employees),
        ("devices", RandSpecs.devices),
        ("users", RandSpecs.users),
        ("events", RandSpecs.events),
        ("sensors", RandSpecs.sensors),
        ("sales", RandSpecs.sales),
    ])
    def test_spec_generates_dataframe(self, spec_name, spec_method):
        """Test that each spec can generate a valid DataFrame."""
        spec = spec_method()
        generator = DataGenerator(spec, seed=42)
        df = generator.size(10).get_df()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 10
        assert len(df.columns) > 0
    
    def test_all_specs_return_dicts(self):
        """Test that all specs return dictionaries."""
        specs = [
            RandSpecs.customers(),
            RandSpecs.products(),
            RandSpecs.orders(),
            RandSpecs.transactions(),
            RandSpecs.employees(),
            RandSpecs.devices(),
            RandSpecs.users(),
            RandSpecs.events(),
            RandSpecs.sensors(),
            RandSpecs.sales(),
        ]
        
        for spec in specs:
            assert isinstance(spec, dict)
            assert len(spec) > 0


ADVANCED_SPEC_NAMES = [n for n in vars(AdvancedRandSpecs) if not n.startswith('_')]


@pytest.mark.parametrize("name", ADVANCED_SPEC_NAMES)
def test_every_advanced_spec_generates(name):
    """Every advertised AdvancedRandSpecs spec validates and generates its columns."""
    spec = getattr(AdvancedRandSpecs, name)()
    df = DataGenerator(spec, seed=42).size(100).get_df()
    expected = [c for k, v in spec.items() for c in (v["cols"] if v.get("splitable") else [k])]
    assert list(df.columns) == expected
    assert len(df) == 100
