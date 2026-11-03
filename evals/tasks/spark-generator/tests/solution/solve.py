"""Reference: write make.py, which builds the orders with rand_engine's SparkGenerator on local[1], then run it."""
import subprocess
import sys
from pathlib import Path

Path("make.py").write_text('''from pyspark.sql import SparkSession, functions as F

from rand_engine import SparkGenerator

spark = SparkSession.builder.master("local[1]").getOrCreate()
spec = {
    "order_id": {"method": "pk", "kwargs": {"style": "sequence", "start": 1}},
    "order_ref": {"method": "pk", "kwargs": {"style": "sequence", "start": 1, "format": "ORD-{:06d}"}},
}
df = SparkGenerator(spark, F, spec, seed=42).size(1000).get_df()
df.toPandas().to_parquet("orders.parquet", index=False)
spark.stop()
''')
subprocess.run([sys.executable, "make.py"], check=True)
