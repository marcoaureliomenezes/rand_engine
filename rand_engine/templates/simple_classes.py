from datetime import datetime as dt
import faker

from rand_engine.templates.i_random_spec import IRandomSpec
from rand_engine.utils.distincts_utils import DistinctsUtils


class CustomersGenerator(IRandomSpec):
    """
    Template para gerar dados de clientes.
    Campos: customer_id, name, email, phone, city, state, country, created_at, is_active
    """

    def __init__(self):
        self.fake = faker.Faker(locale="pt_BR")
        self.fake.seed_instance(42)

    def metadata(self):
        """Define os campos e métodos de geração para clientes."""
        return {
            "customer_id": dict(
                method="unique_ids", 
                kwargs=dict(strategy="zint")
            ),
            "name": dict(
                method="distincts",
                kwargs=dict(distincts=[self.fake.name() for _ in range(200)])
            ),
            "email": dict(
                method="distincts",
                kwargs=dict(distincts=[self.fake.email() for _ in range(200)])
            ),
            "phone": dict(
                method="distincts",
                kwargs=dict(distincts=[self.fake.phone_number() for _ in range(200)])
            ),
            "location": dict(
                method="distincts",
                splitable=True,
                cols=["city", "state", "country"],
                sep=";",
                kwargs=dict(distincts=DistinctsUtils.handle_distincts_lvl_2({
                    "Brasil": ["São Paulo;SP", "Rio de Janeiro;RJ", "Brasília;DF", "Belo Horizonte;MG"],
                    "Estados Unidos": ["New York;NY", "Los Angeles;CA", "Chicago;IL"],
                    "Portugal": ["Lisboa;Lisboa", "Porto;Porto", "Coimbra;Coimbra"]
                }, sep=";"))
            ),
            "customer_tier": dict(
                method="distincts",
                kwargs=dict(distincts=DistinctsUtils.handle_distincts_lvl_1({
                    "Bronze": 60,
                    "Silver": 30,
                    "Gold": 8,
                    "Platinum": 2
                }))
            ),
            "created_at": dict(
                method="unix_timestamps",
                kwargs=dict(start="01-01-2020", end="31-12-2024", format="%d-%m-%Y")
            ),
            "is_active": dict(
                method="distincts",
                kwargs=dict(distincts=DistinctsUtils.handle_distincts_lvl_1({
                    True: 85,
                    False: 15
                }))
            ),
        }

    def transformers(self):
        """Transforma timestamp em formato legível."""
        return [
            lambda df: df.assign(
                created_at=df["created_at"].apply(
                    lambda ts: dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
                )
            )
        ]


class ProductsGenerator(IRandomSpec):
    """
    Template para gerar dados de produtos.
    Campos: product_id, product_name, category, subcategory, price, stock, supplier, is_available
    """

    def __init__(self):
        self.fake = faker.Faker(locale="pt_BR")
        self.fake.seed_instance(123)

    def metadata(self):
        """Define os campos e métodos de geração para produtos."""
        return {
            "product_id": dict(
                method=Core.gen_unique_identifiers,
                kwargs=dict(strategy="zint")
            ),
            "product_name": dict(
                method="distincts",
                kwargs=dict(distincts=[
                    "Notebook Dell Inspiron", "Mouse Logitech MX Master",
                    "Teclado Mecânico Keychron", "Monitor LG 27 polegadas",
                    "Webcam Logitech C920", "Headset HyperX Cloud",
                    "SSD Samsung 1TB", "HD Externo Seagate 2TB",
                    "Cadeira Gamer DT3", "Mesa Escritório Madesa",
                    "Smartphone Samsung Galaxy", "Tablet Apple iPad",
                    "Smartwatch Xiaomi Band", "Fone Bluetooth JBL",
                    "Carregador Portátil Anker", "Hub USB-C Multilaser"
                ])
            ),
            "category_subcategory": dict(
                method="distincts",
                splitable=True,
                cols=["category", "subcategory"],
                sep=";",
                kwargs=dict(distincts=DistinctsUtils.handle_distincts_lvl_2({
                    "Eletrônicos": ["Computadores", "Periféricos", "Smartphones", "Tablets"],
                    "Móveis": ["Escritório", "Gaming", "Decoração"],
                    "Acessórios": ["Audio", "Carregamento", "Conectividade"]
                }, sep=";"))
            ),
            "price": dict(
                method=Core.gen_floats,
                kwargs=dict(min=50.0, max=5000.0, round=2)
            ),
            "stock": dict(
                method=Core.gen_ints,
                kwargs=dict(min=0, max=500)
            ),
            "supplier": dict(
                method="distincts",
                kwargs=dict(distincts=DistinctsUtils.handle_distincts_lvl_1({
                    "Fornecedor A": 40,
                    "Fornecedor B": 30,
                    "Fornecedor C": 20,
                    "Fornecedor D": 10
                }))
            ),
            "is_available": dict(
                method="distincts",
                kwargs=dict(distincts=DistinctsUtils.handle_distincts_lvl_1({
                    True: 90,
                    False: 10
                }))
            ),
        }

    def transformers(self):
        """Sem transformações necessárias para produtos."""
        return []


class OrdersGenerator(IRandomSpec):
    """
    Template para gerar dados de vendas.
    Campos: sale_id, customer_id, product_id, quantity, unit_price, total_price, 
            payment_method, status, sale_date
    
    Nota: customer_id e product_id devem ser populados com IDs reais de CustomersGenerator 
    e ProductsGenerator para manter relacionamento.
    """

    def __init__(self, customer_ids=None, product_ids=None):
        """
        Args:
            customer_ids: Lista de IDs de clientes existentes (opcional)
            product_ids: Lista de IDs de produtos existentes (opcional)
        """
        self.customer_ids = customer_ids if customer_ids else list(range(1, 101))
        self.product_ids = product_ids if product_ids else list(range(1, 51))

    def metadata(self):
        """Define os campos e métodos de geração para vendas."""
        return {
            "sale_id": dict(
                method=Core.gen_unique_identifiers,
                kwargs=dict(strategy="zint")
            ),
            "customer_id": dict(
                method="distincts",
                kwargs=dict(distinct=self.customer_ids)
            ),
            "product_id": dict(
                method="distincts",
                kwargs=dict(distinct=self.product_ids)
            ),
            "quantity": dict(
                method=Core.gen_ints,
                kwargs=dict(min=1, max=10)
            ),
            "unit_price": dict(
                method=Core.gen_floats,
                kwargs=dict(min=50.0, max=5000.0, round=2)
            ),
            "discount_percent": dict(
                method=Core.gen_floats,
                kwargs=dict(min=0.0, max=30.0, round=2)
            ),
            "payment_status": dict(
                method="distincts",
                splitable=True,
                cols=["payment_method", "status"],
                sep=";",
                kwargs=dict(distincts=DistinctsUtils.handle_distincts_lvl_3({
                    "credit_card": [("completed", 8), ("pending", 1), ("failed", 1)],
                    "debit_card": [("completed", 9), ("pending", 1)],
                    "pix": [("completed", 9), ("failed", 1)],
                    "boleto": [("completed", 7), ("pending", 2), ("cancelled", 1)]
                }))
            ),
            "sale_date": dict(
                method="unix_timestamps",
                kwargs=dict(start="01-01-2023", end="31-12-2024", format="%d-%m-%Y")
            ),
        }

    def transformers(self):
        """
        Calcula total_price e formata sale_date.
        Formula: total_price = quantity * unit_price * (1 - discount_percent/100)
        """
        return [
            lambda df: df.assign(
                total_price=lambda x: (
                    x["quantity"] * x["unit_price"] * (1 - x["discount_percent"] / 100)
                ).round(2)
            ),
            lambda df: df.assign(
                sale_date=df["sale_date"].apply(
                    lambda ts: dt.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
                )
            )
        ]
