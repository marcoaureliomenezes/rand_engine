
import itertools
from typing import Any, Dict, List, Tuple

from rand_engine.integrations.duckdb_handler import DuckDBHandler


class DistinctsUtils:

  @classmethod
  def handle_distincts_lvl_1(self, distinct_prop: Dict[Any, int], precision=1):
    """
    This method generates a list of distinct values based on a dictionary of distinct values and their respective frequencies.
    :param distinct_prop: dict: Dictionary containing the distinct values and their respective frequencies.
    :param precision: int: Precision of the distinct values.
    :return: List: List of distinct values.
    """
    return [ key for key, value in distinct_prop.items() for i in range(value * precision )]

  @classmethod
  def handle_distincts_lvl_2(self, distincts: Dict[Any, List[Any]], sep=";"):
    #distincts = {"smartphone": ["android","IOS"], "desktop": ["linux", "windows"]}
    data_flatted = [f"{j}{sep}{i}" for j in distincts for i in distincts[j]]
    return data_flatted


  @classmethod
  def handle_distincts_lvl_3(self, distincts: Dict[Any, List[Tuple[Any, int]]], sep=";"):
    # distincts = {"OPC": [("C_OPC", 8),("V_OPC", 2)], "SWP": [("C_SWP", 6), ("V_SWP", 4)]}
    parm_paired_distincts = {k: list(map(lambda x: f"{x[0]}@!{x[1]}", v)) for k, v in distincts.items()}
    data_flatted = self.handle_distincts_lvl_2(parm_paired_distincts, sep)
    result = []
    for i in data_flatted:
      value, size = i.split("@!")
      result.extend([value for _ in range(int(size))])
    return result
  
  @classmethod
  def handle_distincts_lvl_4(self, distincts: Dict[Any, List[List[Any]]], sep=";"):
    #distincts = {"OPC": [["C_OPC","V_OPC"], ["PF", "PJ"]], "SWP": (["C_SWP", "V_SWP"], [None])}
    combinations = [list(itertools.product([k], *v)) for k, v in distincts.items()]
    combinations = [[[str(i) for i in tupla] for tupla in sublist] for sublist in combinations]
    result = [sep.join(i) for i in list(itertools.chain(*combinations))]
    return result
  
  @classmethod
  def handle_distincts_lvl_5(self, distincts: Dict[Any, List[Dict[Any, List[Any]]]], sep=";"):
    return [
        f"{lvl1}{sep}{lvl2}{sep}{lvl3}"
        for lvl1, lvl2_list in distincts.items()
        for lvl2_dict in lvl2_list
        for lvl2, lvl3_list in lvl2_dict.items()
        for lvl3 in lvl3_list
    ]
  

  @classmethod
  def handle_foreign_keys(self, table, pk_fields, db_path=":memory:"):
    db = DuckDBHandler(db_path=db_path)
    df = db.select_all(f"checkpoint_{table}", pk_fields)
    cat_ids = df[pk_fields[0]].to_list()
    return cat_ids
  


if __name__ == '__main__':
  pass

