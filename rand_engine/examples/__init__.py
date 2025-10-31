"""
Examples Module - Pre-built Specifications for DataGenerator and SparkGenerator

This module provides ready-to-use data generation specifications:
- RandSpecs: For DataGenerator (Pandas-based generation)
- SparkRandSpecs: For SparkGenerator (PySpark-based generation)

Usage:
------
    from rand_engine.examples import RandSpecs, SparkRandSpecs
    from rand_engine import DataGenerator, SparkGenerator
    
    # Pandas generation
    df_pandas = DataGenerator(RandSpecs.customers(), seed=42).size(1000).get_df()
    
    # Spark generation (requires PySpark)
    df_spark = SparkGenerator(spark, F, SparkRandSpecs.customers()).size(1000).get_df()
"""

from rand_engine.examples.simple_examples import RandSpecs
from rand_engine.examples.spark_examples import SparkRandSpecs

__all__ = ["RandSpecs", "SparkRandSpecs"]
