from random import randint
from datetime import timedelta, datetime as dt
import time, math, random

tickers = ["CAB91", "GAA77", "PETR4"]
banks = ["xp", "itau", "santander", "bradesco"]

def gen_distinct(distinct=[]):
    return random.choice(list(distinct)) if len(list(distinct)) > 0 else None

def gen_str_num(length):
    return str(randint(0, 10**length - 1)).zfill(length)


def gen_cpf():
    return f"{gen_str_num(3)}.{gen_str_num(3)}.{gen_str_num(3)}-{gen_str_num(2)}"

def gen_money(min, max, chance=1, factor=1):
    random_money = randint(min, max) + (randint(0, 100) / 100)
    return round(random_money, 2) if random.random() > chance else round(random_money * factor, 2)

def gen_value(min, max, chance=1, factor=1):
    rand_num = randint(min, max)
    return rand_num if random.random() > chance else rand_num * factor


def gen_date(start, formato):
    start, end = (dt.timestamp(dt.strptime(start, formato)), dt.timestamp(dt.fromtimestamp(time.time())))
    return dt.strftime(dt.fromtimestamp(randint(start, int(end))), formato)

def gen_date_oper(initial_batch=True, formato="%Y-%m-%d", **kwargs):
    start_date = kwargs["start_date"] if kwargs.get("start_date") else "2010-01-01"
    if initial_batch:
        return gen_date(start=start_date, formato=formato)
    return dt.strftime(dt.fromtimestamp(time.time()), formato)
    
def gen_diff_day(initial_offer=False, diff_day=0, formato="%Y-%m-%d", **kwargs):
    initial_date = kwargs.get("start_date")
    date = dt.strptime(initial_date, formato) if initial_offer else dt.fromtimestamp(time.time())
    return dt.strftime(date + timedelta(days=diff_day), formato)    
        
def gen_diff_random_day(diff_day, formato="%Y-%m-%d"):
    signal = 1 if diff_day >= 0 else -1
    return dt.strftime(dt.fromtimestamp(time.time()) + (signal * timedelta(days=randint(0, abs(diff_day)))), formato)


if __name__ == '__main__':
    pass