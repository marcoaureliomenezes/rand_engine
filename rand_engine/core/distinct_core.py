from functools import reduce
from typing import List, Any, Iterator
import numpy as np


class DistinctCore:
    
  @classmethod
  def gen_distincts_typed(self, size: int, distinct: List[Any]) -> np.ndarray:
    """
    This method generates an array of random distinct values.
    :param size: int: Number of elements to be generated.
    :param distinct: List[Any]: List of distinct values to be generated.
    :return: np.ndarray: Array of random distinct values.
    """
    assert len(list(set([type(x) for x in distinct]))) == 1
    return np.random.choice(distinct, size)
    

  @classmethod
  def gen_distincts_untyped(self, size: int, distinct: List[Any]) -> List[Any]:
    """
    This method generates an array of random distinct values.
    :param size: int: Number of elements to be generated.
    :param distinct: List[Any]: List of distinct values to be generated.
    :return: Iterator: Iterator of random distinct values.
    """
    return list(map(lambda x: distinct[x], np.random.randint(0, len(distinct), size)))
  
  @classmethod
  def gen_complex_distincts(self, size: int, pattern="x.x.x-x", replacement="x", templates=[]):
    """
    This method generates an array of random distinct values.
    :param size: int: Number of elements to be generated.
    :param pattern: str: Pattern to be replaced.
    :param replacement: str: Replacement of the pattern.
    :param templates: List[Dict]: List of dictionaries containing the method and parameters to be used in the replacement.
    :return: np.ndarray: Array of random distinct values.
    """
    assert pattern.count(replacement) == len(templates)
    list_of_lists, counter = [], 0
    for replacer_cursor in range(len(pattern)):
      if pattern[replacer_cursor] == replacement:
        list_of_lists.append(templates[counter]["method"](size, **templates[counter]["parms"]))
        counter += 1
      else:
        list_of_lists.append(np.array([pattern[replacer_cursor] for i in range(size)]))
    return reduce(lambda a, b: a.astype('str') + b.astype('str'), list_of_lists)
  
  
  
if __name__ == '__main__':
  pass



# def replace_duplicate(array_input, replace):
#     result = list(set(array_input))
#     result.extend([replace for i in range(len(array_input)-len(list(set(array_input))))])
#     random.shuffle(result)
#     return result

# def handle_string_format(array_input, **kwargs): 
#     return replace_duplicate(array_input, np.nan) \
#                 if kwargs.get("rm_dupl") else array_input