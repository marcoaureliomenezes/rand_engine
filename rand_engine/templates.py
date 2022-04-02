
nomes = ["abel", "abelardo", "adrian", "adriana", "adriano", "aecio", "alberto", "alecio", "alexandre", "alice", "ana", "ana clara", "ana cristina", "ana flávia", "ana júlia", "ana luiza", "ana luísa", "andre", "angela", "antônio", "apolo", "arcadio", "arthur", "artur", "bejamin", "benedito", "bento", "breno", "bruno", "caio", "camila", "carla", "carlos", "carolina", "caroline", "cassandra", "cassia", "celia", "celina", "luis", "celso", "charles", "cibele", "cibely", "crislene", "cristiana", "cristiane", "cristiano", "cristina", "cícero", "daiana", "daiane", "daniel", "danilo", "davi", "david", "diego", "diogo", "douglas", "edigar", "edilson", "edimar", "eduardo", "emanuel", "everton", "fabia", "fabiano", "fabio", "fabricio", "felipe", "fernanda", "fernando", "filipe", "flavia", "flaviane", "flavio", "fábio", "gabriel", "geraldo", "gilberto", "guilherme", "gustavo", "jesus", "josé roberto", "karla", "korahi", "leandro", "leonardo", "licia", "lislaine", "luan", "luana", "lucas", "lucia", "luis", "luis fernando", "luisa", "luiz", "luiza", "luma", "magna", "marcela", "marcelo", "marcio", "marco", "maria", "maria alice", "maria cecília", "maria clara", "maria eduarda", "maria helena", "maria júlia", "maria luísa", "mariana", "marina", "marlon", "marlone", "marlucia", "monique", "paulo", "pedro", "pedro henrique", "renato", "rian", "ricardo", "richard", "rildo", "roberta", "roberto", "rodrigo", "rosemberg", "ruan", "tauan", "vanessa", "wanessa"]
sobrenomes = ["abreu", "adorno", "adães", "aguiar", "albuquerque", "alcântara", "aleluia", "alencar", "almeida", "altamirano", "alvarenga", "alves", "alvim", "amaral", "amigo", "amor", "amorim", "anchieta", "andrada", "andrade", "andrioli", "andré", "anes", "anjos", "antunes", "anunciação", "apolinário", "aragão", "araújo", "arruda", "ascensão", "assis", "asvilla", "auth", "azeredo", "azevedo", "bandeira", "barbosa", "barreto", "barros", "barroso", "baseggio", "bastos", "batista", "bermudes", "bernades", "bernardes", "bicalho", "bispo", "bizzo", "bocaiuva", "borba", "borges", "borsoi", "botelho", "braga", "bragança", "brandão", "campos", "cardoso", "carvalho", "castro", "costa", "de lucca", "dias", "duarte", "faria", "fernandes", "ferreira", "freitas", "garcia", "gomes", "gonçalves", "guimarães", "lima", "lopes", "lumes", "macedo", "machado", "magalhães", "marques", "martins", "medeiros", "mendes", "miranda", "monteiro", "moraes", "moreira", "morreti", "moura", "nascimento", "oliveira", "pereira", "perez", "pinheiro", "pires", "ramos", "reis", "ribas", "ribeiro", "rocha", "rodrigues", "santana", "santos", "schetinni", "soares", "souza", "teixeira", "vieira", "álvares"]
email_providers = ["gmail.com", "yahoo.com.br", "bol.com", "uol.com", "santander.com"]



######################################    TEMPLATE STREAMING    ########################################

def template_streaming(tipo):
    cpf = dict(formato="x.x.x-x", sep="x", 
            params=[
                {"how": "gen_str_num", 'params': {"length": 3}},
                {"how": "gen_str_num", 'params': {"length": 3}},
                {"how": "gen_str_num", 'params': {"length": 3}},
                {"how": "gen_str_num", 'params': {"length": 2}}])

    cnpj = dict(formato="x.x.x/0001-x", sep="x", 
            params=[
                {"how": "gen_str_num", 'params': {"length": 2}},
                {"how": "gen_str_num", 'params': {"length": 3}},
                {"how": "gen_str_num", 'params': {"length": 3}},
                {"how": "gen_str_num", 'params': {"length": 2}}])


    email = dict(formato="x_xx@x", sep="x", 
            params=[
                {"how": "gen_distinct", 'params': {"distinct": nomes}},
                {"how": "gen_distinct", 'params': {"distinct": sobrenomes}},
                {"how": "gen_str_num", 'params': {"length": 4}},
                {"how": "gen_distinct", 'params': {"distinct": email_providers}}
            ])
    return locals().get(tipo)


def template_batch(tipo):
    email = dict(method="fake_discrete", format="x_xx@x", key="x", 
            params=[
                {'how': "fake_discrete", 'distinct': nomes},
                {'how': "fake_discrete", 'distinct': sobrenomes},
                {'how': "fake_int", 'min': 12, 'max':2000, 'algsize': 4},
                {'how':  "fake_discrete", 'distinct': email_providers}
    ])
    
    cpf = dict(method="fake_discrete", format="x.x.x-x", key="x",
            params=[
                {"how": "fake_int", "min": 0, "max": 999, "algsize": 3},
                {"how": "fake_int", "min": 0, "max": 999, "algsize": 3},
                {"how": "fake_int", "min": 0, "max": 999, "algsize": 3},
                {"how": "fake_int", "min": 0, "max": 99, "algsize": 2}
    ])

    cnpj = dict(method="fake_discrete", format="x.x.x/0001-x", key="x",
            params=[
                {"how": "fake_int", "min": 0, "max": 99, "algsize": 2},
                {"how": "fake_int", "min": 0, "max": 999, "algsize": 3},
                {"how": "fake_int", "min": 0, "max": 999, "algsize": 3},
                {"how": "fake_int", "min": 0, "max": 99, "algsize": 2},
    ])
    return locals().get(tipo)


if __name__ == '__main__':
    print(template_batch('cpf2'))
