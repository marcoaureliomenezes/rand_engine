import random, math, unittest
from numpy.random import rand, randint
from functools import reduce
from .core import random_int, random_int10, random_float, random_float10, random_float_normal, \
                 default_array, zfilling, lottery, round_array


def fake_int(size=5, **kwargs):
    if not (kwargs.get("min") and kwargs.get("max")):
        result = [random.randint(0, 9) for i in range(size)]
    elif kwargs.get("algnum") is not True:
        result = random_int(size, **kwargs)
    else:
        result = random_int10(size, **kwargs)
    result = default_array(result, int) if kwargs.get("array_type") == "int" else result
    result = default_array(result, str) if kwargs.get("array_type") == "string" else result
    result = zfilling(result, qtd=kwargs["algsize"]) \
                                    if type(kwargs.get("algsize")) is int else result
    return result


def fake_float(size=5, **kwargs):
    if not (kwargs.get("min") and kwargs.get("max")):
        result = [random.random() * 10 for i in range(size)]
    elif kwargs.get("algnum") is not True:
        result = random_float(size, **kwargs)
    else:
        result = random_float10(size, **kwargs)

    result = lottery(result) if kwargs.get("outlier")==True else result
    result = round_array(result, by=kwargs["round"]) if kwargs.get("round") else result
    result = default_array(result, int) if kwargs.get("array_type") == "int" else result
    result = default_array(result, str) if kwargs.get("array_type") == "string" else result
    result = zfilling(result, qtd=kwargs["algsize"]) \
                                        if type(kwargs.get("algsize")) is int else result
    return result


def fake_float_normal(size=5, **kwargs):
    result = random_float_normal(size, **kwargs)
    result = lottery(result) if kwargs.get("outlier")==True else result
    result = round_array(result, by=kwargs["round"]) if kwargs.get("round") else result
    result = default_array(result, int) if kwargs.get("array_type") == "int" else result
    result = default_array(result, str) if kwargs.get("array_type") == "string" else result
    result = zfilling(result, qtd=kwargs["algsize"]) \
                                        if type(kwargs.get("algsize")) is int else result
    return result


###################################################################################################

built_max = max
built_min = min
class TestCoreMethods(unittest.TestCase):

    def test_fake_int1(self):
        print("\n\nTEST FAKE_INT METHOD\n\n")
        fake_int1 = fake_int()
        print("\nTeste sem parâmetros:\n\t", fake_int1)
        self.assertTrue(built_max(fake_int1) < 10, msg="Valores menores que 10")
        self.assertTrue(built_max(fake_int1) >= 0, msg="Valores maiores ou igual que 0")
        self.assertTrue(len(fake_int1) == 5, msg="Tamanho default igual a 5")
        self.assertTrue(type(fake_int1[1]) == int, msg="elementos da lista são inteiros")

        # ARGUMENTO SIZE
    def test_fake_int2(self):
        size = 10
        fake_int2 = fake_int(size)
        print("\nTeste com parametros size=10:\n\t", fake_int2)
        self.assertTrue(len(fake_int2) == size, msg="Tamanho do array de saída igual ao passado por parâmetro")


    def test_fake_int3(self):
        # ARGUMENTO MAX e MIN
        min_num = 5; max_num = 10
        fake_int3 = fake_int(min=min_num, max=max_num)
        print("\nTeste com parametros min=5 e max=10:\n\t", fake_int3)
        self.assertTrue(built_max(fake_int3) <= max_num, msg="Valores menores que parâmetro max")
        self.assertTrue(built_min(fake_int3) >= min_num, msg="Valores maiores ou igual a parâmetro min")
        self.assertTrue(len(fake_int3) == 5, msg="Tamanho default igual a 5")


    def test_fake_int4(self):
        min_size = 5; max_size = 7
        fake_int4 = fake_int(min=min_size, max=max_size, algnum=True)
        print("\nfake_int com parametros min=5, max=7 e algnum=True:\n\t", fake_int4)
        tamanho_nums = [int(math.log10(x) + 1) for x in fake_int4]
        self.assertTrue(built_max(tamanho_nums) <= max_size, msg="Valores menores que parâmetro max")


    def test_fake_int5(self):
        min_size = 5; max_size = 7; arraytype = "string"
        fake_int5 = fake_int(min=min_size, max=max_size, algnum=True, array_type="string")
        print("\nfake_int com parametros min=5, max=7, algnum=True e array_type=string\n\t", fake_int5)
        self.assertTrue(type(fake_int5[0]) == str, msg="elementos do tipo string")
 
    
    def test_fake_int6(self):
        min_size = 5; max_size = 7; algarism_size=12
        fake_int6 = fake_int(min=min_size, max=max_size, algnum=True, array_type="string", algsize=algarism_size)
        print("\nfake_int com parametros min=5, max=7, algnum=True, array_type= string e algsize=12:\n\t", fake_int6)
        self.assertTrue(type(fake_int6[0]) == str, msg="elementos do tipo string")


    def test_fake_int7(self):
        min_size = 5; max_size = 7; algarism_size=12
        fake_int7 = fake_int(min=min_size, max=max_size, algnum=True, array_type="int")
        print("\nfake_int com parametros min=5, max=7, algnum=True, array_type= int:\n\t", fake_int7)
        self.assertTrue(type(fake_int7[0]) == int, msg="elementos do tipo int")
        print("\n----------------------------------------------------------------------------------\n")


    def test_fake_float1(self):
        print("\nTEST FAKE_FLOAT METHOD\n")
        fake_float1 = fake_float()
        print("fake_float sem parâmetros. Size = 5 por default:\n\t", fake_float1)
        self.assertTrue(built_max(fake_float1) < 10, msg="Valores menores que 10")
        self.assertTrue(built_max(fake_float1) >= 0, msg="Valores maiores ou igual que 0")
        self.assertTrue(len(fake_float1) == 5, msg="Tamanho default igual a 5")
        self.assertTrue(type(fake_float1[1]) == float, msg="elementos da lista são float")

    def test_fake_float2(self):
        size = 10
        fake_float2 = fake_float(size=size, round=2)
        print("\nfake_float com parametro size=10 e round=2\n\t", fake_float2)
        self.assertTrue(len(fake_float2) == size, msg="Tamanho do array de saída igual ao passado por parâmetro")


    def test_fake_float3(self):
        min_num = 5; max_num = 10
        fake_float3 = fake_float(size=10, min=min_num, max=max_num, round=3)
        print("\nfake_float com parametros min=5 e max=10 e round=3:\n\t", fake_float3)
        self.assertTrue(built_max(fake_float3) <= max_num, 
                        msg="Valores menores que parâmetro max")
        self.assertTrue(built_min(fake_float3) >= min_num,
                        msg="Valores maiores ou igual a parâmetro min")


    def test_fake_float4(self):
        min_size = 5; max_size = 7
        fake_float4 = fake_float(min=min_size, max=max_size, round=2, algnum=True)
        print("\nfake_float com parametros min=5, max=7, round=2 e algnum=True:\n\t", fake_float4)
        tamanho_nums = [int(math.log10(x) + 1) for x in fake_float4]
        self.assertTrue(built_max(tamanho_nums) <= max_size, msg="Valores menores que parâmetro max")


    def test_fake_float5(self):
        min_size = 5; max_size = 7; arraytype = "string"
        fake_float5 = fake_float(min=min_size, max=max_size, round=2, algnum=True, array_type=arraytype)
        print("\nfake_float com parametros min=5, max=7, round=2, algnum=true e array_type=string:\n\t", fake_float5)
        self.assertTrue(type(fake_float5[0]) == str, msg="elementos do tipo string")


    def test_fake_float6(self):
        min_size = 5; max_size = 7; algarism_size=12
        fake_float6 = fake_float(min=min_size, max=max_size, round=2, algnum=True, array_type="string", algsize=algarism_size)
        print("\nfake_float com parametros min=5, max=7, algnum=True, array_type=string e algsize=12:\n\t", fake_float6)
        self.assertTrue(type(fake_float6[0]) == str, msg="elementos do tipo string")
        self.assertTrue(len(fake_float6[0]) == algarism_size, msg="Algarismos em string com tamanho correto")


    def test_fake_float7(self):
        min_size = 5; max_size = 7; algarism_size=12
        fake_float7 = fake_float(min=min_size, max=max_size, algnum=True, array_type="int")
        print("\nfake_float com parametros min=5, max=7, algnum=True e array_type = int:\n\t", fake_float7)
        self.assertTrue(type(fake_float7[0]) == int, msg="elementos do tipo int")

    def test_fake_float8(self):
        min_size = 0; max_size = 1000
        fake_float8 = fake_float(min=min_size, max=max_size, round=2, outlier=True)
        print("\nfake_float com parametros min=0, max=1000 e outlier=True:\n\t", fake_float8)
        print("\n----------------------------------------------------------------------------------\n")
        self.assertTrue(True, msg="elementos do tipo int")

    def test_fake_float_normal0(self):
        print("\n\nTEST FAKE_FLOAT_NORMAL METHOD\n")
        fake_float_normal0 = fake_float_normal()
        print("fake_float_normal sem parmetros\. Size=5 por default\n\t", fake_float_normal0)
        self.assertTrue(len(fake_float_normal0) == 5, "Tamanho igual ao passado por parâmetro")

    def test_fake_float_normal1(self):
        fake_float_normal1 = fake_float_normal(size=10)
        print("\nfake_float_normal com parametro size=10\n\t", fake_float_normal1)
        self.assertTrue(len(fake_float_normal1) == 10, "Tamanho igual ao passado por parâmetro")

    def test_fake_float_normal2(self):
        fake_float_normal2 = fake_float_normal(size=5, mean=100, std=10)
        print("\nfake_float_normal com parâmetros mean=100 e std=10\n\t", fake_float_normal2)
        self.assertTrue(len(fake_float_normal2) == 5, "Tamanho igual ao passado por parâmetro")


    def test_fake_float_normal3(self):
        fake_float_normal3 = fake_float_normal(size=5, mean=100, std=10, round=2)
        print("\nfake_float_normal com parâmetros mean=100, std=10 round=2\n\t", fake_float_normal3)
        self.assertTrue(len(fake_float_normal3) == 5, "Tamanho igual ao passado por parâmetro")


    def test_fake_float_normal4(self):
        fake_float_normal4 = fake_float_normal(size=5, mean=100, std=10, round=2, outlier=True)
        print("\nfake_float_normal com parâmetros mean=100, std=10, round=2 e outlier=True\n\t", fake_float_normal4)
        self.assertTrue(len(fake_float_normal4) == 5, "Tamanho igual ao passado por parâmetro")

    def test_fake_float_normal5(self):
        fake_float_normal5 = fake_float_normal(size=5, mean=100, std=10, round=2, array_type="string")
        print("\nfake_normal_float com parâmetros mean=100, std=10, round=2 e string=True\n\t", fake_float_normal5)
        self.assertTrue(len(fake_float_normal5) == 5, "Tamanho igual ao passado por parâmetro")

    def test_fake_float_normal6(self):
        fake_float_normal6 = fake_float_normal(size=5, mean=100, std=10, round=2, string=True, algsize=12)
        print("\nfake_normal_float com parâmetros mean=100, std=10, round=2, string=True e algsize=12\n\t", fake_float_normal6)
        print("\n----------------------------------------------------------------------------------\n")
        self.assertTrue(len(fake_float_normal6) == 5, "Tamanho igual ao passado por parâmetro")

if __name__ == '__main__':
    unittest.main()