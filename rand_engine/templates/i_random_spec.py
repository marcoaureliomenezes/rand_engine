
from abc import ABC, abstractmethod
from typing import Dict, Callable, Any, List


class IRandomSpec(ABC):

  @abstractmethod
  def metadata(self) -> Dict:
    pass

  @abstractmethod
  def transformers(self) -> List[Callable]:
    pass



