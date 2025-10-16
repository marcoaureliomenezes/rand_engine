from rand_engine.utils.distincts_utils import DistinctsUtils



def test_handle_distincts_lvl_1():
    distinct_prop = {"MEI": 6,"ME":3, "EPP": 1}
    result = DistinctsUtils.handle_distincts_lvl_1(distinct_prop, 1)
    assert result == ['MEI', 'MEI', 'MEI', 'MEI', 'MEI', 'MEI', 'ME', 'ME', 'ME', 'EPP']




def test_handle_distincts_lvl_2():
    distincts = {"OPC": ["C_OPC","V_OPC"], "SWP": ["C_SWP", "V_SWP"]}
    result = DistinctsUtils.handle_distincts_lvl_2(distincts, sep=";")
    assert result == ['OPC;C_OPC', 'OPC;V_OPC', 'SWP;C_SWP', 'SWP;V_SWP']
    #assert len(result) == 20

def test_handle_distincts_lvl_3():
    distinct_2 = {"OPC": [("C_OPC", 2),("V_OPC", 1)], "SWP": [("C_SWP", 2), ("V_SWP", 1)]}
    result = DistinctsUtils.handle_distincts_lvl_3(distinct_2, sep=";")
    assert result == ['OPC;C_OPC', 'OPC;C_OPC', 'OPC;V_OPC', 'SWP;C_SWP', 'SWP;C_SWP', 'SWP;V_SWP']

def test_handle_distincts_lvl_4():
    distincts = {"OPC": [[1, 2], ["IN"]], "SWP": [[1, 2], ["AF", "ME"]]}
    #distincts = {"OPC": [["C_OPC","V_OPC"], ["PF", "PJ"]], "SWP": (["C_SWP", "V_SWP"], ["None"])}
    #distinct = {"OPC": [{"C_OPC": ["PF", "PJ"]}, {"V_OPC": ["NA"]}], "SWP": ({"C_SWP": ["AP"]}, {"V_SWP": ["MA", "ME"]})}
    result = DistinctsUtils.handle_distincts_lvl_4(distincts, sep=";")
    assert result == ['OPC;1;IN', 'OPC;2;IN', 'SWP;1;AF', 'SWP;1;ME', 'SWP;2;AF', 'SWP;2;ME']
    #assert len(result) == 20


def test_handle_distincts_lvl_5():
    distincts = {
        "PF": [{"premium": ["platinum", "black, gold"]}, {"standard": ["simples"]}],
        "PJ": [{"premium": ["platinum", "black, gold"]}, {"standard": ["simples"]}]
    }
    result = DistinctsUtils.handle_distincts_lvl_5(distincts, sep=";")
    assert result == ['PF;premium;platinum', 'PF;premium;black, gold', 'PF;standard;simples', 'PJ;premium;platinum', 'PJ;premium;black, gold', 'PJ;standard;simples']
