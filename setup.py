from setuptools import setup
from setuptools import find_packages


with open(file="README.md", mode="r") as readme_handle:
    long_description = readme_handle.read()

setup(

    name="rand_engine",
    author = "Marco Menezes",
    author_email = "marcoaurelioreislima@gmail.com",

    version = "0.0.2",
    description = "Engine to create random data with different formats, to use with spark and others.",
    long_description = long_description,
    url = "https://github.com/marcoaureliomenezes/rand_engine",

    install_requires = [
        "numpy==1.20.3",
        "pandas==1.4.1"
    ],

    keywords = ["random-data, data creation, random data, random data for data engineers"],

    packages = find_packages(),

    python_requires = ">=3.7"
)