from numpy.random import randint

def fake_discrete_1(size=10, distinct=[]):
    aux = randint(0, len(distinct), size)
    return [distinct[i] for i in aux]

def fake_discrete_2(size=5, **kwargs):
    if(kwargs.get("distinct") is not None):
        aux = randint(0, len(kwargs["distinct"]), size)
        return [kwargs["distinct"][i] for i in aux]