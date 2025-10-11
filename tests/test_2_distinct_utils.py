from rand_engine.utils.distincts import DistinctUtils



def test_handle_distincts_lvl_1():
    distinct_prop = {"MEI": 6,"ME":3, "EPP": 1}
    result = DistinctUtils.handle_distincts_lvl_1(distinct_prop, 1)
    assert len(result) == 10




# def test_handle_distincts_lvl_3():
    
#     result = DistinctUtils.handle_distincts_lvl_3(distinct_2, sep=";")
#     print(result)
#     assert len(result) == 20


# def test_handle_distincts_lvl_4():
#     distinct = {"OPC": [["C_OPC","V_OPC"], ["PF", "PJ"]], "SWP": (["C_SWP", "V_SWP"], [None])}
#     distinct_2 = {"OPC": [("C_OPC", 8),("V_OPC", 2)], "SWP": [("C_SWP", 6), ("V_SWP", 4)]}
#     distinct = {"OPC": [{"C_OPC": ["PF", "PJ"]}, {"V_OPC": ["NA"]}], "SWP": ({"C_SWP": ["AP"]}, {"V_SWP": ["MA", "ME"]})}

#     result = DistinctUtils.handle_distincts_lvl_4(distinct, sep=";")
#     print(result)
#     assert len(result) == 20


# def test_handle_distincts_lvl_5():
#     distinct = {"OPC": [{"C_OPC": ["PF", "PJ"]}, {"V_OPC": ["NA"]}], "SWP": ({"C_SWP": ["AP"]}, {"V_SWP": ["MA", "ME"]})}
#     result = DistinctUtils.handle_distincts_lvl_5(distinct, sep=";")
#     print(result)
#     assert len(result) == 20