from random import randint
from datetime import timedelta, datetime as dt
import time, random
import numpy as np
from rand_engine.bulk.templates import template_streaming



def gen_int(min, max):
    return randint(min, max)

def gen_int10(min, max):
    return randint(min, max)

def gen_value(min, max, chance=1, factor=1):
    rand_num = randint(min, max)
    return rand_num if random.random() > chance else rand_num * factor

def gen_str_num(length):
    return str(randint(0, 10**length - 1)).zfill(length)
    
################################################################################


def gen_float(min, max, decimals):
    return round(np.uniform(min, max), decimals)


def gen_money(min, max, chance=1, factor=1):
    random_money = randint(min, max) + (randint(0, 100) / 100)
    return round(random_money, 2) if random.random() > chance else round(random_money * factor, 2)
#################################################################################

def gen_distinct(distinct=[]):
    return random.choice(list(distinct)) if len(list(distinct)) > 0 else None


def gen_discrete(params, formato, sep):
    values = [globals()[i['how']](**i['params']) for i in params]
    return formato.replace(sep, '{}').format(*values)

#####################################################################################################


def gen_date(start, formato):
    start, end = (dt.timestamp(dt.strptime(start, formato)), dt.timestamp(dt.fromtimestamp(time.time())))
    return dt.strftime(dt.fromtimestamp(randint(start, int(end))), formato)

def gen_date_oper(now=True, formato="%Y-%m-%d", **kwargs):
    start_date = kwargs["start_date"] if kwargs.get("start_date") else "2010-01-01"
    if now:
        return gen_date(start=start_date, formato=formato)
    return dt.strftime(dt.fromtimestamp(time.time()), formato)
    
def gen_diff_day(now=True, diff_day=0, formato="%Y-%m-%d", **kwargs):
    initial_date = kwargs.get("start_date")
    date = dt.fromtimestamp(time.time()) if now else dt.strptime(initial_date, formato) 
    return dt.strftime(date + timedelta(days=diff_day), formato)    
        
def gen_diff_random_day(diff_day, formato="%Y-%m-%d"):
    signal = 1 if diff_day >= 0 else -1
    return dt.strftime(dt.fromtimestamp(time.time()) + (signal * timedelta(days=randint(0, abs(diff_day)))), formato)


###################################################################################################

def create_message(**kwargs):
    pass



if __name__ == '__main__':
    for i in range(10):
        msg = dict(
            email = gen_discrete(**template_streaming('email')),
            cpf = gen_discrete(**template_streaming('cpf')),
            endereco = gen_discrete(**template_streaming('endereco')),
            idade = gen_int(18, 100),
        )
        print(msg)