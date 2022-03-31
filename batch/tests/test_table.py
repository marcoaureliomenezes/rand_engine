from utils import *
from table import create_table
import unittest, csv

class TestCoreMethods(unittest.TestCase):

    size = 10
    with open('/home/dadaia/workspace/data_engineering/rand_engine/utils/names.csv') as f:
        csvreader = csv.reader(f)
        nomes = [row[0].split(";")[0] for row in csvreader] 
    with open('/home/dadaia/workspace/data_engineering/rand_engine/utils/sobrenomes.csv') as f:
        csvreader = csv.reader(f)
        sobrenomes = [row[0].split(";")[0] for row in csvreader] 

    with open('/home/dadaia/workspace/data_engineering/rand_engine/utils/email_providers.csv') as f:
        csvreader = csv.reader(f)
        email_providers = [row[0].split(";")[0] for row in csvreader]

    metadata = dict(
        names=["email", "idade", "cpf", "cnpj", "saldo", "indexador", 
        "data_inicio", "data_vencimento"],
        data=[
            dict(method="fake_discrete", format="x_xx@x", key="x", params=[
                                dict(how="fake_discrete", distinct=nomes),
                                dict(how="fake_discrete", distinct=sobrenomes),
                                dict(how="fake_int", min=12, max=2000, algsize=4),
                                dict(how= "fake_discrete", distinct=email_providers)
            ]),
            dict(method="fake_int", min=10, max=20),
            dict(method="fake_discrete", format="x.x.x-x", key="x", params=[
                {"how": "fake_int", "min": 0, "max": 999, "algsize": 3},
                {"how": "fake_int", "min": 0, "max": 999, "algsize": 3},
                {"how": "fake_int", "min": 0, "max": 999, "algsize": 3},
                {"how": "fake_int", "min": 0, "max": 99, "algsize": 2}
            ]),
            dict(method="fake_discrete", format="x.x.x/0001-x", key="x", params=[
                {"how": "fake_int", "min": 0, "max": 99, "algsize": 2},
                {"how": "fake_int", "min": 0, "max": 999, "algsize": 3},
                {"how": "fake_int", "min": 0, "max": 999, "algsize": 3},
                {"how": "fake_int", "min": 0, "max": 99, "algsize": 2},
            ]),
            dict(method="fake_float", min=10000, max=30000, round=2),
            dict(method="fake_alphanum", format="a222", 
                    distinct=["vale","sant","petr","appl","msft","itub"], sep="-"),
            dict(method="fake_date", start="02-01-2015", end="06-06-2017"),
            dict(method="fake_date",start="2-6-2020", end="6-6-2021")
        ]
    )

    def test_create_table(self):
        res = create_table(size=20, **self.metadata)
        print(res)

if __name__ == '__main__':
    unittest.main()