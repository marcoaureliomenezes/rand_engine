
from batch.fake_gen import *
import pandas as pd


def fake_data(size, **kwargs):
    methods_dict = {
        "fake_discrete": fake_discrete, "fake_int": fake_int, "fake_float": fake_float,
        "fake_alphanum": fake_alphanum,"fake_date": fake_date,"fake_partition": fake_partition
        }
    return methods_dict[kwargs["method"]](size=size, **kwargs) \
        if kwargs.get("method") else [None for i in range(size)]

# This method creates a pandas random dataframe as you pass metadata to it.
def create_table(size=5, **kwargs):
    names, data = (kwargs["names"], kwargs["data"])
    return pd.DataFrame({names[i]: fake_data(size, **data[i]) for i in range(len(data))})



if __name__ == '__main__':
    pass
 