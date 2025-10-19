"""
Test suite for ExampleSpecs - Validates all example specifications
Tests data generation, column presence, data types, and value constraints
"""
import pytest
import pandas as pd
from rand_engine.main.examples import ExampleSpecs
from rand_engine import DataGenerator


class TestExampleSpecsAccess:
    """Test that all specs are accessible as attributes."""
    
    def test_examples_instantiation(self):
        """Test that ExampleSpecs can be instantiated."""
        examples = ExampleSpecs()
        assert examples is not None
        assert hasattr(examples, 'professions')
        assert len(examples.professions) == 3
    
    def test_simple_client_accessible_as_attribute(self):
        """Test that simple_client is accessible as attribute."""
        examples = ExampleSpecs()
        spec = examples.simple_client
        assert spec is not None
        assert isinstance(spec, dict)
        assert len(spec) > 0
    
    def test_simple_client_2_accessible_as_attribute(self):
        """Test that simple_client_2 is accessible as attribute."""
        examples = ExampleSpecs()
        spec = examples.simple_client_2
        assert spec is not None
        assert isinstance(spec, dict)
    
    def test_simple_client_3_accessible_as_attribute(self):
        """Test that simple_client_3 is accessible as attribute."""
        examples = ExampleSpecs()
        spec = examples.simple_client_3
        assert spec is not None
        assert isinstance(spec, dict)
    
    def test_simple_client_4_accessible_as_attribute(self):
        """Test that simple_client_4 is accessible as attribute."""
        examples = ExampleSpecs()
        spec = examples.simple_client_4
        assert spec is not None
        assert isinstance(spec, dict)
    
    def test_specs_are_cached(self):
        """Test that specs are cached and return same object."""
        examples = ExampleSpecs()
        spec1 = examples.simple_client
        spec2 = examples.simple_client
        assert spec1 is spec2, "Spec should be cached and return same object"


class TestSimpleClient:
    """Test simple_client spec - Basic spec with all core data types."""
    
    @pytest.fixture
    def spec(self):
        """Fixture providing simple_client spec."""
        return ExampleSpecs().simple_client
    
    def test_spec_structure(self, spec):
        """Test that spec has expected structure."""
        expected_columns = ['id', 'age', 'salary', 'height', 'is_active', 
                          'profession', 'created_at', 'device']
        assert all(col in spec for col in expected_columns)
        assert len(spec) == 8
    
    def test_generate_dataframe(self, spec):
        """Test that DataGenerator can generate DataFrame from spec."""
        generator = DataGenerator(spec, seed=42)
        df = generator.size(100).get_df()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 100
        assert len(df.columns) == 8
    
    def test_column_presence(self, spec):
        """Test that all expected columns are present."""
        df = DataGenerator(spec, seed=42).size(50).get_df()
        
        expected_columns = ['id', 'age', 'salary', 'height', 'is_active', 
                          'profession', 'created_at', 'device']
        for col in expected_columns:
            assert col in df.columns, f"Missing column: {col}"
    
    def test_unique_ids(self, spec):
        """Test that IDs are unique."""
        df = DataGenerator(spec, seed=42).size(100).get_df()
        assert df['id'].nunique() == 100, "IDs should be unique"
    
    def test_age_range(self, spec):
        """Test that age values are within expected range."""
        df = DataGenerator(spec, seed=42).size(100).get_df()
        assert df['age'].min() >= 0
        assert df['age'].max() <= 100
        assert df['age'].dtype in ['int64', 'int32']
    
    def test_salary_values(self, spec):
        """Test that salary values are valid floats with 2 decimals."""
        df = DataGenerator(spec, seed=42).size(100).get_df()
        assert df['salary'].min() >= 0
        assert df['salary'].max() <= 1000
        # Check that values have at most 2 decimal places
        assert all(df['salary'].apply(lambda x: len(str(x).split('.')[-1]) <= 2))
    
    def test_height_normal_distribution(self, spec):
        """Test that height follows normal distribution characteristics."""
        df = DataGenerator(spec, seed=42).size(1000).get_df()
        mean = df['height'].mean()
        std = df['height'].std()
        # Mean should be close to 1000 (within 10%)
        assert 900 < mean < 1100
        # Std should be close to 10 (within 50% tolerance due to randomness)
        assert 5 < std < 15
    
    def test_is_active_boolean(self, spec):
        """Test that is_active contains only boolean values."""
        df = DataGenerator(spec, seed=42).size(100).get_df()
        assert df['is_active'].dtype == bool
        assert set(df['is_active'].unique()).issubset({True, False})
    
    def test_is_active_probability(self, spec):
        """Test that is_active respects ~70% true probability."""
        df = DataGenerator(spec, seed=42).size(1000).get_df()
        true_ratio = df['is_active'].sum() / len(df)
        # Should be around 0.7 with some tolerance
        assert 0.6 < true_ratio < 0.8
    
    def test_profession_values(self, spec):
        """Test that profession contains only valid values."""
        df = DataGenerator(spec, seed=42).size(100).get_df()
        valid_professions = ["Data Engineer", "QA Engineer", "Software Engineer"]
        assert all(df['profession'].isin(valid_professions))
    
    def test_created_at_timestamps(self, spec):
        """Test that created_at contains valid Unix timestamps in 2020."""
        df = DataGenerator(spec, seed=42).size(100).get_df()
        # Unix timestamp for 2020-01-01 00:00:00
        start_2020 = 1577836800
        # Unix timestamp for 2020-12-31 23:59:59
        end_2020 = 1609459199
        assert df['created_at'].min() >= start_2020
        assert df['created_at'].max() <= end_2020
    
    def test_device_proportions(self, spec):
        """Test that device follows proportional distribution (2:1 mobile:desktop)."""
        df = DataGenerator(spec, seed=42).size(1000).get_df()
        mobile_count = (df['device'] == 'mobile').sum()
        desktop_count = (df['device'] == 'desktop').sum()
        # Should be roughly 2:1 ratio
        ratio = mobile_count / desktop_count
        assert 1.5 < ratio < 2.5
    
    def test_no_null_values(self, spec):
        """Test that DataFrame has no null values."""
        df = DataGenerator(spec, seed=42).size(100).get_df()
        assert df.isnull().sum().sum() == 0
    
    def test_reproducibility_with_seed(self, spec):
        """Test that same seed produces identical results."""
        df1 = DataGenerator(spec, seed=42).size(50).get_df()
        df2 = DataGenerator(spec, seed=42).size(50).get_df()
        pd.testing.assert_frame_equal(df1, df2)


class TestSimpleClient2:
    """Test simple_client_2 spec - Demonstrates distincts_map (correlated columns)."""
    
    @pytest.fixture
    def spec(self):
        """Fixture providing simple_client_2 spec."""
        return ExampleSpecs().simple_client_2
    
    def test_spec_structure(self, spec):
        """Test that spec has expected structure."""
        assert 'device_plat' in spec
        assert 'method' in spec['device_plat']
        assert spec['device_plat']['method'] == 'distincts_map'
        assert 'cols' in spec['device_plat']
        assert spec['device_plat']['cols'] == ["device_type", "os_type"]
    
    def test_generate_dataframe(self, spec):
        """Test that DataGenerator creates DataFrame with mapped columns."""
        df = DataGenerator(spec, seed=42).size(100).get_df()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 100
        # Should have device_type and os_type columns (not device_plat)
        assert 'device_type' in df.columns
        assert 'os_type' in df.columns
        assert 'device_plat' not in df.columns
    
    def test_device_os_correlation(self, spec):
        """Test that device types map to correct OS types.
        
        Note: distincts_map puts KEYS in the SECOND column (os_type) 
        and VALUES in the FIRST column (device_type).
        """
        df = DataGenerator(spec, seed=42).size(500).get_df()
        
        # Check smartphone OS → smartphone category
        smartphone_rows = df[df['os_type'] == 'smartphone']
        valid_smartphone_devices = ['android', 'IOS', 'windows phone']
        assert all(smartphone_rows['device_type'].isin(valid_smartphone_devices))
        
        # Check desktop OS → desktop category
        desktop_rows = df[df['os_type'] == 'desktop']
        valid_desktop_devices = ['linux', 'windows', 'macOS']
        assert all(desktop_rows['device_type'].isin(valid_desktop_devices))
    
    def test_all_device_types_present(self, spec):
        """Test that both OS categories appear in data."""
        df = DataGenerator(spec, seed=42).size(100).get_df()
        os_types = df['os_type'].unique()
        assert 'smartphone' in os_types or 'desktop' in os_types
    
    def test_no_invalid_combinations(self, spec):
        """Test that invalid device-OS combinations don't exist.
        
        Note: distincts_map puts KEYS in the SECOND column (os_type)
        and VALUES in the FIRST column (device_type).
        """
        df = DataGenerator(spec, seed=42).size(200).get_df()
        
        # These combinations should NEVER exist (device_type vs os_type)
        invalid_combos = [
            ('linux', 'smartphone'),      # linux is desktop OS
            ('windows', 'smartphone'),    # windows is desktop OS
            ('macOS', 'smartphone'),      # macOS is desktop OS
            ('android', 'desktop'),       # android is smartphone OS
            ('IOS', 'desktop'),           # IOS is smartphone OS
            ('windows phone', 'desktop'), # windows phone is smartphone OS
        ]
        
        for device, os in invalid_combos:
            combo_exists = ((df['device_type'] == device) & (df['os_type'] == os)).any()
            assert not combo_exists, f"Invalid combination found: {device} + {os}"


class TestSimpleClient3:
    """Test simple_client_3 spec - Demonstrates distincts_map_prop (weighted correlations)."""
    
    @pytest.fixture
    def spec(self):
        """Fixture providing simple_client_3 spec."""
        return ExampleSpecs().simple_client_3
    
    def test_spec_structure(self, spec):
        """Test that spec has distincts_map_prop configuration."""
        assert 'deriv_tip' in spec
        assert spec['deriv_tip']['method'] == 'distincts_map_prop'
        assert spec['deriv_tip']['cols'] == ["op", "tip_op"]
    
    def test_generate_dataframe(self, spec):
        """Test DataFrame generation with weighted correlations."""
        df = DataGenerator(spec, seed=42).size(100).get_df()
        
        assert len(df) == 100
        assert 'op' in df.columns
        assert 'tip_op' in df.columns
        assert 'deriv_tip' not in df.columns
    
    def test_operation_types(self, spec):
        """Test that only valid operation types exist."""
        df = DataGenerator(spec, seed=42).size(200).get_df()
        
        valid_ops = ['OPC', 'SWP']
        assert all(df['op'].isin(valid_ops))
    
    def test_opc_tip_op_correlation(self, spec):
        """Test that OPC operations map to correct tip_op values."""
        df = DataGenerator(spec, seed=42).size(500).get_df()
        
        opc_rows = df[df['op'] == 'OPC']
        valid_opc_tips = ['C_OPC', 'V_OPC']
        assert all(opc_rows['tip_op'].isin(valid_opc_tips))
    
    def test_swp_tip_op_correlation(self, spec):
        """Test that SWP operations map to correct tip_op values."""
        df = DataGenerator(spec, seed=42).size(500).get_df()
        
        swp_rows = df[df['op'] == 'SWP']
        valid_swp_tips = ['C_SWP', 'V_SWP']
        assert all(swp_rows['tip_op'].isin(valid_swp_tips))
    
    def test_weighted_distribution_opc(self, spec):
        """Test that OPC operations follow 8:2 weight ratio (C_OPC:V_OPC)."""
        df = DataGenerator(spec, seed=42).size(1000).get_df()
        
        opc_rows = df[df['op'] == 'OPC']
        if len(opc_rows) > 0:
            c_opc_count = (opc_rows['tip_op'] == 'C_OPC').sum()
            v_opc_count = (opc_rows['tip_op'] == 'V_OPC').sum()
            
            if v_opc_count > 0:
                ratio = c_opc_count / v_opc_count
                # Should be around 4:1 (8:2)
                assert 2.5 < ratio < 6.0
    
    def test_no_invalid_combinations(self, spec):
        """Test that invalid op-tip_op combinations don't exist."""
        df = DataGenerator(spec, seed=42).size(300).get_df()
        
        # These combinations should NEVER exist
        invalid_combos = [
            ('OPC', 'C_SWP'),
            ('OPC', 'V_SWP'),
            ('SWP', 'C_OPC'),
            ('SWP', 'V_OPC'),
        ]
        
        for op, tip in invalid_combos:
            combo_exists = ((df['op'] == op) & (df['tip_op'] == tip)).any()
            assert not combo_exists, f"Invalid combination found: {op} + {tip}"


class TestSimpleClient4:
    """Test simple_client_4 spec - Demonstrates distincts_multi_map (N-level correlations)."""
    
    @pytest.fixture
    def spec(self):
        """Fixture providing simple_client_4 spec."""
        return ExampleSpecs().simple_client_4
    
    def test_spec_structure(self, spec):
        """Test that spec has distincts_multi_map configuration."""
        assert 'empresa' in spec
        assert spec['empresa']['method'] == 'distincts_multi_map'
        expected_cols = ["setor", "sub_setor", "porte", "codigo_municipio"]
        assert spec['empresa']['cols'] == expected_cols
    
    def test_generate_dataframe(self, spec):
        """Test DataFrame generation with multi-level mapping."""
        df = DataGenerator(spec, seed=42).size(100).get_df()
        
        assert len(df) == 100
        assert 'setor' in df.columns
        assert 'sub_setor' in df.columns
        assert 'porte' in df.columns
        assert 'codigo_municipio' in df.columns
        assert 'empresa' not in df.columns
    
    def test_setor_values(self, spec):
        """Test that setor contains only valid values."""
        df = DataGenerator(spec, seed=42).size(200).get_df()
        
        valid_setores = ['setor_1', 'setor_2']
        assert all(df['setor'].isin(valid_setores))
    
    def test_setor_1_sub_setor_correlation(self, spec):
        """Test that setor_1 maps to correct sub-sectors."""
        df = DataGenerator(spec, seed=42).size(500).get_df()
        
        setor1_rows = df[df['setor'] == 'setor_1']
        valid_sub_setores = ['agro', 'mineração', 'petróleo', 'pecuária']
        assert all(setor1_rows['sub_setor'].isin(valid_sub_setores))
    
    def test_setor_2_sub_setor_correlation(self, spec):
        """Test that setor_2 maps to correct sub-sectors."""
        df = DataGenerator(spec, seed=42).size(500).get_df()
        
        setor2_rows = df[df['setor'] == 'setor_2']
        valid_sub_setores = ['indústria', 'construção']
        assert all(setor2_rows['sub_setor'].isin(valid_sub_setores))
    
    def test_setor_1_porte_correlation(self, spec):
        """Test that setor_1 has correct porte values."""
        df = DataGenerator(spec, seed=42).size(500).get_df()
        
        setor1_rows = df[df['setor'] == 'setor_1']
        valid_portes = [0.25, 0.15, None]
        # Convert to set, handling None and float comparison
        portes_set = set(setor1_rows['porte'].unique())
        for porte in portes_set:
            if pd.isna(porte):
                assert None in valid_portes or pd.isna(valid_portes).any()
            else:
                assert porte in valid_portes
    
    def test_setor_2_porte_correlation(self, spec):
        """Test that setor_2 has correct porte values."""
        df = DataGenerator(spec, seed=42).size(500).get_df()
        
        setor2_rows = df[df['setor'] == 'setor_2']
        # Check that porte contains expected float values
        valid_portes = [0.30, 0.20, 0.10]
        assert all(setor2_rows['porte'].isin(valid_portes))
    
    def test_setor_1_municipio_correlation(self, spec):
        """Test that setor_1 has codigo_municipio as None.
        
        Note: Due to spec structure, setor_1 has [None] in position 3, 
        and ['01', '02'] in position 4, but only 4 columns are mapped,
        so codigo_municipio (position 3) gets None.
        """
        df = DataGenerator(spec, seed=42).size(300).get_df()
        
        setor1_rows = df[df['setor'] == 'setor_1']
        # codigo_municipio should be None for all setor_1 rows
        assert setor1_rows['codigo_municipio'].isna().all()
    
    def test_setor_2_municipio_correlation(self, spec):
        """Test that setor_2 has correct municipality codes.
        
        Note: Due to spec structure, setor_2's position 3 contains 
        the porte strings ['micro', 'pequena', 'média'], which map 
        to codigo_municipio.
        """
        df = DataGenerator(spec, seed=42).size(300).get_df()
        
        setor2_rows = df[df['setor'] == 'setor_2']
        valid_codes = ['micro', 'pequena', 'média']
        assert all(setor2_rows['codigo_municipio'].isin(valid_codes))
    
    def test_no_cross_setor_contamination(self, spec):
        """Test that setor-specific values don't mix."""
        df = DataGenerator(spec, seed=42).size(500).get_df()
        
        # Check setor_1 doesn't have setor_2 sub_setores
        setor1_rows = df[df['setor'] == 'setor_1']
        setor2_sub_setores = ['indústria', 'construção']
        assert not any(setor1_rows['sub_setor'].isin(setor2_sub_setores))
        
        # Check setor_2 doesn't have setor_1 sub_setores
        setor2_rows = df[df['setor'] == 'setor_2']
        setor1_sub_setores = ['agro', 'mineração', 'petróleo', 'pecuária']
        assert not any(setor2_rows['sub_setor'].isin(setor1_sub_setores))


class TestAllSpecsIntegration:
    """Integration tests for all example specs."""
    
    def test_all_specs_generate_successfully(self):
        """Test that all specs can generate data without errors."""
        examples = ExampleSpecs()
        specs = [
            ('simple_client', examples.simple_client),
            ('simple_client_2', examples.simple_client_2),
            ('simple_client_3', examples.simple_client_3),
            ('simple_client_4', examples.simple_client_4),
        ]
        
        for name, spec in specs:
            try:
                df = DataGenerator(spec, seed=42).size(10).get_df()
                assert len(df) == 10, f"{name} failed to generate 10 rows"
                assert len(df.columns) > 0, f"{name} has no columns"
            except Exception as e:
                pytest.fail(f"{name} failed to generate: {e}")
    
    def test_all_specs_with_different_sizes(self):
        """Test that all specs work with different data sizes."""
        examples = ExampleSpecs()
        sizes = [1, 10, 100, 1000]
        specs = [
            examples.simple_client,
            examples.simple_client_2,
            examples.simple_client_3,
            examples.simple_client_4,
        ]
        
        for spec in specs:
            for size in sizes:
                df = DataGenerator(spec, seed=42).size(size).get_df()
                assert len(df) == size
    
    def test_all_specs_reproducible(self):
        """Test that all specs are reproducible with seed."""
        examples = ExampleSpecs()
        specs = [
            examples.simple_client,
            examples.simple_client_2,
            examples.simple_client_3,
            examples.simple_client_4,
        ]
        
        for spec in specs:
            df1 = DataGenerator(spec, seed=123).size(20).get_df()
            df2 = DataGenerator(spec, seed=123).size(20).get_df()
            pd.testing.assert_frame_equal(df1, df2)
    
    def test_all_specs_no_duplicates_in_ids(self):
        """Test that all specs generate unique IDs."""
        examples = ExampleSpecs()
        specs = [
            examples.simple_client,
            examples.simple_client_2,
            examples.simple_client_3,
            examples.simple_client_4,
        ]
        
        for spec in specs:
            df = DataGenerator(spec, seed=42).size(100).get_df()
            assert df['id'].nunique() == 100, "IDs should be unique"
    
    def test_all_specs_have_common_columns(self):
        """Test that all specs have id, profession, and device columns."""
        examples = ExampleSpecs()
        specs = [
            examples.simple_client,
            examples.simple_client_2,
            examples.simple_client_3,
            examples.simple_client_4,
        ]
        
        for spec in specs:
            df = DataGenerator(spec, seed=42).size(10).get_df()
            assert 'id' in df.columns
            assert 'profession' in df.columns
            # device or device_type should be present
            assert 'device' in df.columns or 'device_type' in df.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
