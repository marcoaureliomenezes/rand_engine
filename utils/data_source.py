dominios_email = ["gmail.com", "yahoo.com", "bol.com", "uol.com", "santander.com"]

empresas = dict(
    small_companies = ["kabana", "kabana's", "gourmet", "emporio", "tô maluco", "central", "pedi+", "perdido's",
                    "da esquina", "burguês", "tudi-bão", "tudo em dobro"])

address = dict(
    logradouros = ["rua", "praça", "avenida", "lameda"],
    logradouro_nomes = ["josé silvio", "consolação", "piedade", "tiradentes", "1º de maio", "7 de setembro"],
    bairros = ["Bela Vista", "primavera", "Centro", "Manga", "Vila Prado", "Vila Mariana", "Céu Azul"],
    cidades = [ "Inhaúma - MG", "Cachoeira da Prata - MG", "Paraopeba - MG", "Funilândia - MG", "Felixlândia - MG", 
    "Itabirito-MG", "Sete Lagoas - MG", "Belo Horizonte - MG", "São Carlos - SP", "Araraquara - SP", "Ibaté - SP"])

estado_civil = ["Solteiro/a", "Separado/a", "separado/a", "disquitado/a", "viúvo/a"]


tipo_produto = {
    "santander": ["conta_corrente", "poupança", "cartão de credito", "consorcio", "financiamento_carro",
                  "financiamento_emovel", "financiamento_rural", "investimentos", "seguros"
    ]
}

bancos = {
    "sant": dict (
        id = 1,
        name="santander",
        product = {
            "id": 1,
            "ticker":"SANT33",
            "nome": "conta_corrente",
            "data_inicio": "05-07-2006",
        }
    ),
    "caixa": dict (
        id = 1,
        name="caixa econômica",
        ticker="ITAU66",
        product = {
            "id": 1,
            "nome": "conta_corrente",
            "data_inicio": "05-07-2006",
        }
    ),
    "bradesco":dict (
        id = 1,
        name="bradesco",
        ticker="BRAD45",
        product = {
            "id": 1,
            "nome": "conta_corrente",
            "data_inicio": "05-07-2006",
        }
    ),
    "xp": dict (
        id = 1,
        name="xp_investimentos",
        ticker="XPIV11",
        product = {
            "id": 1,
            "nome": "conta_corrente",
            "data_inicio": "05-07-2020",
        }
    ),
}
