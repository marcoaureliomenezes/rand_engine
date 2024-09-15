import random
from functools import reduce
from typing import List, Any, Generator, Iterator
from core_numeric import CoreNumeric
import numpy as np
import pandas as pd


class CoreDistincts:
    
    
  @classmethod
  def gen_distincts_typed(self, size: int, distinct: List[Any]) -> np.ndarray:
    assert len(list(set([type(x) for x in distinct]))) == 1
    return np.random.choice(distinct, size)
    
  @classmethod
  def gen_distincts_untyped(self, size: int, distinct: List[Any]) -> Iterator:
    return map(lambda x: distinct[x], np.random.randint(0, len(distinct), size))
  
  @classmethod
  def gen_complex_distincts(self, size: int, pattern="x.x.x-x", replacement="x", templates=[]):
    assert pattern.count(replacement) == len(templates)
    list_of_lists, counter = [], 0
    for replacer_cursor in range(len(pattern)):
      if pattern[replacer_cursor] == replacement:
        list_of_lists.append(templates[counter]["method"](size, **templates[counter]["parms"]))
        counter += 1
      else:
        list_of_lists.append(np.array([pattern[replacer_cursor] for i in range(size)]))
    return reduce(lambda a, b: a+b, list_of_lists)
  

  
if __name__ == '__main__':
  res = CoreDistincts.gen_complex_distincts(
    size=10**1, 
    pattern="x.x.x-x", 
    replacement="x", 
    templates=[
      {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=3)},
      {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=3)},
      {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=3)},
      {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=2)}
    ])

  res_2 = CoreDistincts.gen_complex_distincts(
    size=10**1,
    pattern="x.x.x/0001-x",
    replacement="x",
    templates=[
      {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=2)},
      {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=3)},
      {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=3)},
      {"method": CoreNumeric.gen_ints_zfilled, "parms": dict(length=2)}
    ])


  print(res_2)

  # @classmethod
  # def gen_distincts_untyped_baseline_1(self, size: int, distinct: List[Any]) -> Generator:
  #   return (random.choice(distinct) for i in range(size))
  
  # @classmethod
  # def gen_distincts_untyped_baseline_2(self, size: int, distinct: List[Any]) -> List[Any]:
  #   return map(lambda x: distinct[x], [random.randint(0, len(distinct)-1) for _ in range(size)])
  
  
  # @classmethod
  # def gen_distincts_typed_baseline_1(self, size: int, distinct: List[Any]) -> List[Any]:
  #   return [distinct[i] for i in np.random.randint(0, len(distinct), size)]
  

  # @classmethod
  # def gen_distincts_typed_baseline_2(self, size: int, distinct: List[Any]) -> np.ndarray:
  #   return np.vectorize(lambda x: random.choice(distinct))(np.arange(size))
  
  
  # @classmethod
  # def gen_distincts_typed_baseline_3(self, size: int, distinct: List[Any]) -> np.ndarray:
  #   return np.vectorize(lambda x: distinct[x])(np.random.randint(0, len(distinct), size))
  

