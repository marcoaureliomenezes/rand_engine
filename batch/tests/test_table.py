from batch.utils import *
import unittest

class TestCoreMethods(unittest.TestCase):

    size = 10
    metadata = dict(
        names=["email", "idade", "cpf", "cnpj", "tipo_pessoa", "saldo", "credito", "indexador", 
        "data_inicio", "data_vencimento", "numero_acoes", "valor_acao"],
        data=[
            dict(method="fake_discrete", format="x_xx@x", key="x", params=[
                                dict(how="fake_discrete", distinct=names),
                                dict(how="fake_discrete", distinct=last_names),
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
            dict(method="fake_discrete", distinct=["PF", "PJ"]),
            dict(method="fake_float", mean=10000., std=3000., type="normal", round=2, outlier=True),
            dict(method="fake_float", min=10000, max=30000, round=2),
            dict(method="fake_alphanum", format="a222", 
                    distinct=["vale","sant","petr","appl","msft","itub"], sep="-"),
            dict(method="fake_date", start="02-01-2015", end="06-06-2017"),
            dict(method="fake_date",start="2-6-2020", end="6-6-2021"),
            dict(method="fake_int", min=1, max=2000),
            dict(method="fake_float", min=30, max=320, round=2),
        ]
    )

if __name__ == '__main__':
    unittest.main()