from setuptools import setup
from setuptools import find_packages


with open(file="README.md", mode="r") as readme_handle:
    long_description = readme_handle.read()

setup(

    name="data_engine",
    author = "Marco Menezes",
    author_email = "marcoaurelioreislima@gmail.com",

    version = "1.0.1",
    description = "Engine to create random data with different formats, to use with spark and others.",
    long_description = long_description,
    url = "https://github.com/marcoaureliomenezes/data-engine",

    install_requires = [
        "numpy==1.20.3"
    ],

    keywords = ["data-engine, data creation, tabular data for bigdata"],

    packages = find_packages(),

    python_requires = ">=3.7"
)