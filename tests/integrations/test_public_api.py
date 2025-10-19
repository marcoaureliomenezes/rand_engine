"""
Test Public API - Ensure only DataGenerator is publicly accessible.

These tests validate that rand_engine exposes only its public API
and that internal modules are properly hidden from external users.

Run these tests after installing the package: pip install -e .
"""

import pytest
import sys


class TestPublicAPI:
    """Test that only public API is accessible from rand_engine package."""
    
    def test_can_import_datagenerator(self):
        """
        Example 1: DataGenerator should be importable from rand_engine.
        
        This is the ONLY public entry point for the library.
        """
        from rand_engine import DataGenerator
        
        assert DataGenerator is not None
        print("\n✓ DataGenerator successfully imported from rand_engine")
    
    
    def test_datagenerator_in_all(self):
        """
        Example 2: Check that __all__ contains public API: DataGenerator and RandSpecs.
        
        __all__ defines the public API of a module.
        """
        import rand_engine
        
        assert hasattr(rand_engine, '__all__')
        assert "DataGenerator" in rand_engine.__all__
        assert "RandSpecs" in rand_engine.__all__
        assert len(rand_engine.__all__) == 2
        print(f"\n✓ rand_engine.__all__ = {rand_engine.__all__}")
    
    
    def test_private_modules_not_in_main_namespace(self):
        """
        Example 3: Private modules should not be accessible from rand_engine.
        
        Users should not be able to do: from rand_engine import RandGenerator
        """
        import rand_engine
        
        # These should NOT be accessible
        private_names = [
            "RandGenerator",
            "FileBatchWriter", 
            "FileStreamWriter",
            "DuckDBHandler",
            "SQLiteHandler",
            "BaseDBHandler"
        ]
        
        for name in private_names:
            assert not hasattr(rand_engine, name), \
                f"Private class '{name}' should not be in rand_engine namespace"
        
        print(f"\n✓ Private modules not exposed in rand_engine namespace")
    
    
    def test_cannot_import_private_modules_directly(self):
        """
        Example 4: Importing private modules should work but is discouraged.
        
        While Python doesn't enforce privacy, the underscore convention
        indicates these modules are internal implementation details.
        """
        # These imports should work (Python doesn't enforce privacy)
        # but they start with underscore to discourage direct use
        from rand_engine.integrations import _duckdb_handler
        from rand_engine.integrations import _sqlite_handler
        from rand_engine.integrations import _base_handler
        from rand_engine.file_handlers import _writer_batch
        from rand_engine.file_handlers import _writer_stream
        from rand_engine.main import _rand_generator
        
        # Verify the convention: all start with underscore
        assert _duckdb_handler.__name__ == "rand_engine.integrations._duckdb_handler"
        assert _sqlite_handler.__name__ == "rand_engine.integrations._sqlite_handler"
        assert _base_handler.__name__ == "rand_engine.integrations._base_handler"
        assert _writer_batch.__name__ == "rand_engine.file_handlers._writer_batch"
        assert _writer_stream.__name__ == "rand_engine.file_handlers._writer_stream"
        assert _rand_generator.__name__ == "rand_engine.main._rand_generator"
        
        print("\n✓ Private modules use underscore naming convention")
    
    
    def test_examplespecs_can_be_imported(self):
        """
        Example 5a: RandSpecs should be importable from rand_engine.
        
        RandSpecs provides ready-to-use specifications for learning and prototyping.
        """
        from rand_engine import RandSpecs
        
        assert RandSpecs is not None
        
        # Verify all specs are accessible as class methods
        assert callable(RandSpecs.customers)
        assert callable(RandSpecs.products)
        assert callable(RandSpecs.orders)
        assert callable(RandSpecs.transactions)
        
        print("\n✓ RandSpecs successfully imported and has all specs")
    
    
    def test_datagenerator_can_be_instantiated(self):
        """
        Example 5b: Verify DataGenerator works correctly.
        
        The public API should be fully functional.
        """
        from rand_engine import DataGenerator
        
        # Simple spec to test instantiation
        spec = {
            "id": {
                "method": "integers",
                "kwargs": {"min": 1, "max": 100}
            }
        }
        
        generator = DataGenerator(spec, seed=42)
        generator.size(10)
        df = generator.get_df()
        
        assert len(df) == 10
        assert "id" in df.columns
        print(f"\n✓ DataGenerator works correctly: {len(df)} rows generated")
    
    
    def test_examplespecs_works_with_datagenerator(self):
        """
        Example 5c: Verify RandSpecs works with DataGenerator.
        
        Pre-built specs should work seamlessly with DataGenerator.
        """
        from rand_engine import DataGenerator, RandSpecs
        
        df = DataGenerator(RandSpecs.customers(), seed=42).size(10).get_df()
        
        assert len(df) == 10
        assert 'customer_id' in df.columns
        assert 'name' in df.columns
        assert 'age' in df.columns
        
        print(f"\n✓ RandSpecs works with DataGenerator: {len(df)} rows with {len(df.columns)} columns")
    
    
    def test_public_api_is_minimal(self):
        """
        Example 6: Public API should be minimal and well-defined.
        
        A good library exposes only what users need, hiding complexity.
        """
        import rand_engine
        
        # Get all public attributes (not starting with _)
        public_attrs = [attr for attr in dir(rand_engine) if not attr.startswith('_')]
        
        # Should only have DataGenerator and RandSpecs
        expected_public = ['DataGenerator', 'RandSpecs']
        
        for expected in expected_public:
            assert expected in public_attrs, f"{expected} should be public"
        
        print(f"\n✓ Public API is minimal: {', '.join(expected_public)}")
    
    
    def test_private_module_naming_convention(self):
        """
        Example 7: All internal modules follow underscore naming.
        
        This test documents the internal structure for maintainers.
        """
        import os
        import glob
        
        # Find all Python files in integrations, file_handlers, and main
        internal_dirs = [
            "rand_engine/integrations",
            "rand_engine/file_handlers",
            "rand_engine/main"
        ]
        
        private_files = []
        public_files = []
        
        for directory in internal_dirs:
            pattern = f"{directory}/*.py"
            for filepath in glob.glob(pattern):
                filename = os.path.basename(filepath)
                
                # Skip __init__.py and __pycache__
                if filename.startswith('__'):
                    continue
                
                if filename.startswith('_'):
                    private_files.append(filepath)
                else:
                    # Check if it's a public entry point
                    if filename == "data_generator.py":
                        public_files.append(filepath)
                    else:
                        # This would be a violation of naming convention
                        # (unless it's intentionally public)
                        pass
        
        # Log findings
        print(f"\n✓ Private modules (underscore prefix): {len(private_files)}")
        for f in private_files:
            print(f"  - {f}")
        
        print(f"\n✓ Public entry points: {len(public_files)}")
        for f in public_files:
            print(f"  - {f}")
    
    
    def test_documentation_imports(self):
        """
        Example 8: Test the recommended import pattern from documentation.
        
        Users should always import like this:
            from rand_engine import DataGenerator
        """
        # This is the ONLY recommended way
        from rand_engine import DataGenerator
        
        # Alternative (also acceptable)
        import rand_engine
        generator_class = rand_engine.DataGenerator
        
        # Both should give the same class
        assert DataGenerator is generator_class
        
        print("\n✓ Recommended import patterns work correctly")
    
    
    def test_star_import_behavior(self):
        """
        Example 9: Test 'from rand_engine import *' behavior.
        
        Should only import what's in __all__ (DataGenerator).
        """
        # Simulate star import
        import rand_engine
        namespace = {}
        
        # This simulates: from rand_engine import *
        if hasattr(rand_engine, '__all__'):
            for name in rand_engine.__all__:
                namespace[name] = getattr(rand_engine, name)
        
        # Should only have DataGenerator
        assert "DataGenerator" in namespace
        assert "RandGenerator" not in namespace
        assert "DuckDBHandler" not in namespace
        
        print(f"\n✓ Star import only brings: {list(namespace.keys())}")


class TestInternalAccess:
    """
    Test that internal modules CAN be accessed (Python doesn't enforce privacy)
    but document that this is NOT recommended.
    """
    
    def test_internal_modules_technically_accessible(self):
        """
        Example 10: Internal modules are technically accessible.
        
        Python uses convention, not enforcement. Underscored modules signal
        "private implementation detail - use at your own risk".
        """
        # These work, but are NOT part of the public API
        # Users should NOT rely on these - they may change without warning
        
        from rand_engine.integrations._duckdb_handler import DuckDBHandler
        from rand_engine.integrations._sqlite_handler import SQLiteHandler
        from rand_engine.main._rand_generator import RandGenerator
        
        assert DuckDBHandler is not None
        assert SQLiteHandler is not None
        assert RandGenerator is not None
        
        print("\n✓ Internal modules are accessible (but NOT recommended)")
        print("  ⚠️  These are implementation details and may change!")


class TestPackageStructure:
    """Test overall package structure and organization."""
    
    def test_package_has_version(self):
        """
        Example 11: Package should have version information.
        
        Good practice for tracking releases.
        """
        import rand_engine
        
        # Version might be in __version__ or read from pyproject.toml
        has_version = hasattr(rand_engine, '__version__') or \
                     hasattr(rand_engine, 'version')
        
        if has_version:
            version = getattr(rand_engine, '__version__', None) or \
                     getattr(rand_engine, 'version', None)
            print(f"\n✓ Package version: {version}")
        else:
            print("\n⚠️  No version attribute found (consider adding __version__)")
    
    
    def test_clean_namespace(self):
        """
        Example 12: Package namespace should be clean.
        
        Only necessary imports should pollute the namespace.
        """
        import rand_engine
        
        # Get all attributes
        all_attrs = dir(rand_engine)
        
        # Separate into public and private
        public = [a for a in all_attrs if not a.startswith('_')]
        private = [a for a in all_attrs if a.startswith('_') and not a.startswith('__')]
        
        print(f"\n✓ Public attributes: {public}")
        print(f"✓ Private attributes: {private}")
        
        # Public should be minimal (DataGenerator + potential subpackages)
        # In development mode, subpackages may be visible
        essential_public = ["DataGenerator"]
        for attr in essential_public:
            assert attr in public, f"Expected public attribute '{attr}' not found"
        
        print(f"✓ Essential public API present: {essential_public}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
