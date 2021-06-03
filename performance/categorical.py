from numpy.random import randint

def fake_categorical_data(size=10, distinct=[]):
    aux = randint(0, len(distinct), size)
    return [distinct[i] for i in aux]

def fake_categorical_data2(size, **kwargs):
    if(kwargs.get("distinct") is not None):
        aux = randint(0, len(kwargs["distinct"]), size)
        return [kwargs["distinct"][i] for i in aux]