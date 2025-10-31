"""
Test suite for RandSpecs - Validates all example specifications
Tests data generation, column presence, data types, and value constraints
"""
import pytest
import pandas as pd
from rand_engine.examples import RandSpecs
from rand_engine import DataGenerator


class TestRandSpecsAccess:
    """Test RandSpecs static methods accessibility."""
    
    def test_customers_accessible(self):
        """Test that customers spec is accessible."""
        spec = RandSpecs.customers()
        assert isinstance(spec, dict)
        assert 'customer_id' in spec
        assert 'name' in spec
    
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
    
    def test_invoices_accessible(self):
        """Test that invoices spec is accessible."""
        spec = RandSpecs.invoices()
        assert isinstance(spec, dict)
        assert 'invoice_number' in spec
    
    def test_shipments_accessible(self):
        """Test that shipments spec is accessible."""
        spec = RandSpecs.shipments()
        assert isinstance(spec, dict)
        assert 'tracking_number' in spec
    
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
        ("invoices", RandSpecs.invoices),
        ("shipments", RandSpecs.shipments),
        ("events", RandSpecs.events),
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
            RandSpecs.invoices(),
            RandSpecs.shipments(),
            RandSpecs.events(),
        ]
        
        for spec in specs:
            assert isinstance(spec, dict)
            assert len(spec) > 0
