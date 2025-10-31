"""
Examples Module - Pre-built Specifications for DataGenerator and SparkGenerator

This module provides ready-to-use data generation specifications:
- RandSpecs: Backward compatible alias for CommonRandSpecs (recommended)
- CommonRandSpecs: Cross-compatible specs (DataGenerator and SparkGenerator)
- AdvancedRandSpecs: PyCore-exclusive methods (DataGenerator only)
- SparkRandSpecs: Legacy Spark-specific examples

Usage:
------
    from rand_engine import DataGenerator, SparkGenerator, RandSpecs
    
    # Cross-compatible (works with both generators)
    df_pandas = DataGenerator(RandSpecs.customers(), seed=42).size(1000).get_df()
    df_spark = SparkGenerator(spark, F, RandSpecs.customers()).size(1000).get_df()
    
    # Advanced patterns (DataGenerator only)
    from rand_engine.examples import AdvancedRandSpecs
    df_advanced = DataGenerator(AdvancedRandSpecs.products(), seed=42).size(1000).get_df()
"""

# Import advanced specs
from rand_engine.examples.advanced_rand_specs import AdvancedRandSpecs

# Import cross-compatible specs
from rand_engine.examples.spark_rand_specs import CommonRandSpecs

# Import legacy Spark specs
from rand_engine.examples.spark_examples import SparkRandSpecs

# Backward compatibility - RandSpecs now points to CommonRandSpecs (cross-compatible)
RandSpecs = CommonRandSpecs

__all__ = ["RandSpecs", "AdvancedRandSpecs", "CommonRandSpecs", "SparkRandSpecs"]
