from rand_engine.core.distinct_utils import DistinctUtils


def test_handle_distincts_lvl_1():
    distinct_prop = {"MEI": 6,"ME":3, "EPP": 1}
    result = DistinctUtils.handle_distincts_lvl_1(distinct_prop, 1)
    print(result)
    assert len(result) == 10

def test_handle_distincts_lvl_2():
    distincts = {"OPC": ["C_OPC","V_OPC"], "SWP": ["C_SWP", "V_SWP"]}
    result = DistinctUtils.handle_distincts_lvl_2(distincts, sep=";")
    print(result)
    assert len(result) == 4
    assert result[0] == "OPC;C_OPC"
    assert result[1] == "OPC;V_OPC"
    assert result[2] == "SWP;C_SWP"
    assert result[3] == "SWP;V_SWP"


def test_handle_distincts_lvl_3():
    distinct_2 = {"OPC": [("C_OPC", 8),("V_OPC", 2)], "SWP": [("C_SWP", 6), ("V_SWP", 4)]}
    result = DistinctUtils.handle_distincts_lvl_3(distinct_2, sep=";")
    print(result)
    assert len(result) == 20


def test_handle_distincts_lvl_4():
    distinct = {"OPC": [["C_OPC","V_OPC"], ["PF", "PJ"]], "SWP": (["C_SWP", "V_SWP"], [None])}
    result = DistinctUtils.handle_distincts_lvl_4(distinct, sep=";")
    print(result)
    assert len(result) == 20


# def test_handle_distincts_lvl_5():
#     distinct = {"OPC": [{"C_OPC": ["PF", "PJ"]}, {"V_OPC": ["NA"]}], "SWP": ({"C_SWP": ["AP"]}, {"V_SWP": ["MA", "ME"]})}
#     result = DistinctUtils.handle_distincts_lvl_5(distinct, sep=";")
#     print(result)
#     assert len(result) == 20