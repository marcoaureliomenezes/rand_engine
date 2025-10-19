
import itertools
from typing import Any, Dict, List, Tuple

from rand_engine.integrations._duckdb_handler import DuckDBHandler


class DistinctsUtils:

  
  @classmethod
  def handle_distincts_lvl_5(self, distincts: Dict[Any, List[Dict[Any, List[Any]]]], sep=";"):
    return [
        f"{lvl1}{sep}{lvl2}{sep}{lvl3}"
        for lvl1, lvl2_list in distincts.items()
        for lvl2_dict in lvl2_list
        for lvl2, lvl3_list in lvl2_dict.items()
        for lvl3 in lvl3_list
    ]
  

