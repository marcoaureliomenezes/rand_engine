"""
Validators package for Rand Engine.

This package provides validation for random data generation specifications.

Architecture:
- CommonValidator: Validates methods shared between DataGenerator and SparkGenerator
- AdvancedValidator: Validates methods specific to DataGenerator (PyCore)
- SpecValidator: Main validator for DataGenerator specs (uses Common + Advanced)
- SparkSpecValidator: Main validator for SparkGenerator specs (uses Common + dummy methods)

Usage:
    from rand_engine.validators import SpecValidator, SparkSpecValidator
    
    # Validate DataGenerator spec
    SpecValidator.validate_and_raise(data_spec)
    
    # Validate SparkGenerator spec
    SparkSpecValidator.validate_and_raise(spark_spec)
"""

from rand_engine.validators.common_validator import CommonValidator
from rand_engine.validators.advanced_validator import AdvancedValidator
from rand_engine.validators.spec_validator import SpecValidator
from rand_engine.validators.spark_spec_validator import SparkSpecValidator

__all__ = [
    "CommonValidator",
    "AdvancedValidator",
    "SpecValidator",
    "SparkSpecValidator"
]
