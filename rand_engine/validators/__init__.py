"""
Validators package for Rand Engine.

This package provides validation for random data generation specifications.

Architecture (Simplified):
- CommonValidator: Validates methods shared between DataGenerator and SparkGenerator
  * Includes validate_spark_spec() and validate_spark_and_raise() for SparkGenerator
- AdvancedValidator: Validates methods specific to DataGenerator (PyCore)
  * Includes validate() and validate_and_raise() for DataGenerator
  * Handles constraints validation (PK/FK)

Usage:
    from rand_engine.validators import AdvancedValidator, CommonValidator
    
    # Validate DataGenerator spec (common + advanced methods + constraints)
    AdvancedValidator.validate_and_raise(data_spec)
    
    # Validate SparkGenerator spec (common methods only)
    CommonValidator.validate_spark_and_raise(spark_spec)
"""

from rand_engine.validators.common_validator import CommonValidator
from rand_engine.validators.advanced_validator import AdvancedValidator

__all__ = [
    "CommonValidator",
    "AdvancedValidator"
]
