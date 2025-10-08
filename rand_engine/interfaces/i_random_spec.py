
from abc import ABC, abstractmethod
from typing import Dict, Callable, Any


class IRandomSpec(ABC):

  @abstractmethod
  def metadata(self) -> Dict:
    pass

  @abstractmethod
  def transformer(self) -> Callable:
    pass

  @abstractmethod
  def debugger(self) -> Any:
    pass


