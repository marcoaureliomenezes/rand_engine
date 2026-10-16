"""Synthetic data generation for Pandas and Spark dataframes."""
import importlib.metadata

from rand_engine.main.data_generator import DataGenerator
from rand_engine.main.spark_generator import SparkGenerator
from rand_engine.examples import RandSpecs

try:
    __version__ = importlib.metadata.version("rand-engine")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0+unknown"

# Define public API
__all__ = ["DataGenerator", "SparkGenerator", "RandSpecs"]
