
import itertools
from typing import Dict

from rand_engine.integrations.duckdb_handler import DuckDBHandler


class DistinctUtils:

  @classmethod
  def handle_distincts_lvl_1(self, distinct_prop, precision=1):
    """
    This method generates a list of distinct values based on a dictionary of distinct values and their respective frequencies.
    :param distinct_prop: dict: Dictionary containing the distinct values and their respective frequencies.
    :param precision: int: Precision of the distinct values.
    :return: List: List of distinct values.
    """
    return [ key for key, value in distinct_prop.items() for i in range(value * precision )]

  @classmethod
  def handle_distincts_lvl_2(self, distincts, sep=";"):
    """
    This method generates a list of distinct values based on a dictionary of distinct values and their respective frequencies.
    :param distincts: dict: Dictionary containing the distinct values and their respective frequencies."""
    data_flatted = [f"{j}{sep}{i}" for j in distincts for i in distincts[j]]
    return data_flatted

  @classmethod
  def handle_distincts_lvl_22(self, distincts):
    """
    This method generates a list of distinct values based on a dictionary of distinct values and their respective frequencies.
    :param distincts: dict: Dictionary containing the distinct values and their respective frequencies."""
    data_flatted = [(j, i) for j in distincts for i in distincts[j]]
    return data_flatted

  @classmethod
  def handle_distincts_lvl_3(self, distincts, sep=";"):
    parm_paired_distincts = {k: list(map(lambda x: f"{x[0]}@!{x[1]}", v)) for k, v in distincts.items()}
    data_flatted = self.handle_distincts_lvl_2(parm_paired_distincts, sep)
    result = []
    for i in data_flatted:
      value, size = i.split("@!")
      result.extend([value for _ in range(int(size))])
    return result
  
  @classmethod
  def handle_distincts_lvl_4(self, distincts, sep=";"):
    combinations = [list(itertools.product([k], *v)) for k, v in distincts.items()]
    result = [sep.join(i) for i in list(itertools.chain(*combinations))]
    return result
  

  @classmethod
  def handle_foreign_keys(self, table, pk_fields, db_path="clientes_ddb.db"):
    db = DuckDBHandler(db_path=db_path)
    df = db.select_all(f"checkpoint_{table}", pk_fields)
    cat_ids = df[pk_fields[0]].to_list()
    return cat_ids
  


if __name__ == '__main__':
  pass
  # distincts = {"OPC": ["C_OPC","V_OPC"], "SWP": ["C_SWP", "V_SWP"]}
  # distinct_1 = {"OPC": [["C_OPC","V_OPC"], ["PF", "PJ"], ["IN"]], "SWP": [["C_SWP", "V_SWP"], ["AF", "ME"], ["NULL"]]}
  # distinct_2 = {"OPC": [{"C_OPC": ["PF", "PJ"]}, {"V_OPC": ["NA"]}], "SWP": [{"C_SWP": ["AP"]}, {"V_SWP": ["MA", "ME"]}]}
  # #print(DistinctUtils.handle_distincts_lvl_5(distinct_2)[]
  # def rec(structure):
  #   if isinstance(structure, list):
  #     return [rec(i) for i in structure]
  #   if isinstance(structure, dict):
  #     return [[[k], rec(v)] for k, v in structure.items()]
  #   return structure
  # import numpy as np
  # result = rec(distinct_2)
  # combinations = np.array(list(itertools.product(*result)))
