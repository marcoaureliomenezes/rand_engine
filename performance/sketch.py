from functools import reduce
import numpy as np
from numpy.random import randint
import pandas as pd
from performance import *
import pandas as pd
# dict_letters = {
#     "a":"b","b":"c","c":"d","d":"e","e":"f","g":"h","h":"i","i":"j","j":"k","k":"l",
#     "l":"m","m":"n","n":"p","o":"q","p":"r","q":"s","r":"t","s":"u","t":"v","u":"x",
#     "v":"y","y":"z","z":"a",


# }
# def random_alphanum1(size, format):
#     return reduce(lambda a, b: [a[i] + b[i] for i in range(len(b))], 
#     np.array([np.array([chr(i) for i in randint(97,123, size)]
#                 if i.isalpha() else [chr(i) for i in randint(48,57, size)]) 
#                 for i in format], dtype=object))



# def random_alphanum2(size, format):
#     def aux_method(format):
#         ra = randint(0, len(format))
#         res = chr(randint(48,57)) if format[ra].isdigit() else chr(randint(97, 123)) \
#             if format[ra].isalpha() else format[ra]
#         return format[0:ra] + res + format[ra+1:]
#     return  [aux_method(format) for i in range(size)]

# def normalize_param(dic, arg, tipo, default): 
#     return dic[arg] if type(dic.get(arg)) is tipo else default


# def normalize_all_params(dic, *args):
#     return tuple([normalize_param(dic, *i) for i in args])


# def fake_int(size=5, **kwargs):
#     min, max, algnum = normalize_all_params(kwargs, ("min", int, 0), ("max", int, 10), ("algnum", bool, False))
#     print(min, max, algnum)

# fake_int(size=5)
# fake_int(size=5, min=20, max="2")
# fake_int(size=5, min=[2], max=1, algnum=3)
# fake_int(size=5, min=20, max=40, algnum=True)


first_name, last_name, email, dominio = (["marco", "pedro","thiago"], ["guedes","pereira","lima"],
 ["gmail","yahoo","bol","santander"], ["org","com","com.br","gov"])

first_name1, last_name1, email1, dominio1 = (
    ["marco", "pedro","thiago", "roberto","ian","ruan","juan", "paulo","ricardo", "maria","ana"], ["guedes","pereira","lima", "reis","lopes","lira","souza","perez","rodrigues","gutierres"],
    ["gmail","yahoo","bol","santander", "uol","facebook","msn","outlook","terra","ufop"],
    ["org","com","com.br","gov"])


def fake_discrete1(size, distinct):
    return list(map(lambda x: distinct[x], randint(0, len(distinct), size)))

def fake_discrete_format(size, params, format, key):
    def rand_word():
        count = 0
        word = ""
        for i in range(len(format)):
            if format[i] == key:
                word += params[count][np.random.randint(0,len(params[count]))]
                count += 1
            else:
                word += format[i]
        return word
    return [rand_word() for i in range(size)]


def fake_discrete_format2(size, params, format, key):
    df, counter = (pd.DataFrame(), 0)
    for l in format:
        if l == key:
            df[counter] = fake_discrete1(size, distinct=params[0])
            params.pop(0)
        else:
            df[counter] = np.array([l for i in range(size)])
        counter += 1
    return reduce(lambda a, b: a+b, [df[i] for i in df.columns]).values

def fake_discrete_full_refact(size, params, format, key):
    df, counter = (pd.DataFrame(), 0)
    df = pd.DataFrame({l: fake_discrete1(size, distinct=params[0]) if format[l] == key    
    else [format[l] for i in range(size)] for l in range(len(format))})
    return


def fake_discrete_full(size, params, format, key):
    pass
    # Cria uma coluna de strings format.
    # replace cada indice de um grupo (x por exemplo) por um item de params



print(fake_discrete_format2(size = 10, params=[first_name1, last_name1, email1, dominio1], format="x_x@x.x", key="x"))

print(fake_discrete_format2(size = 10, params=[first_name1, last_name1, email1, dominio1, 
first_name1, last_name1, email1, dominio1], format="x_x@x.x & x_x@x.x ", key="x"))


print("time 1.2")
loop_complexity(fake_discrete_format2, size = 1000000, params=[first_name1, last_name1, email1, dominio1], format="x_x@x.x", key="x")
loop_complexity(fake_discrete_format2, size = 1000000, params=[first_name1, last_name1, email1, dominio1, first_name1, last_name1, email1, dominio1], format="x_x@x.x & x_x@x.x", key="x")
loop_complexity(fake_discrete_format2, size = 1000000, params=[first_name1, last_name1, email1, dominio1, first_name1, last_name1, email1, dominio1], format="x_x@x.x &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& x_x@x.x", key="x") # FAIL

# df = fake_discrete_format_part1(size = 1000000, params=[first_name1, last_name1, email1, dominio1], format="x_x@x.x", key="x")
# print("time 2")
# loop_complexity(fake_discrete_format2, df)

# res = fake_discrete_format2(size = 10, params=[first_name, last_name, email, dominio], format="x_x@x.x", key="x")
# # print(res)

# loop_complexity(fake_discrete_format, size = 1000000, params=[first_name, last_name, email, dominio], format="x_x@x.x", key="x")

# loop_complexity(fake_discrete_format, size = 1000000, params=[first_name1, last_name1, email1, dominio1], format="x_x@x.x", key="x")

# loop_complexity(fake_discrete_format, size = 1000000, params=[first_name1, last_name1, email1, dominio1, first_name1, last_name1, email1, dominio1], format="x_x@x.x e x_x@x.x", key="x")





# loop_complexity(fake_discrete_format2, size = 1000000, params=[first_name, last_name, email, dominio], format="x_x@x.x", key="x")
# loop_complexity(fake_discrete_format2, size = 1000000, params=[first_name1, last_name1, email1, dominio1], format="x_x@x.x", key="x")
# loop_complexity(fake_discrete_format2, size = 1000000, params=[first_name1, last_name1, email1, dominio1, first_name1, last_name1, email1, dominio1], format="x_x@x.x e x_x@x.x", key="x")
