import time
import pandas as pd
import numpy as np
from typing import List, Optional, Generator, Callable
from rand_engine.main._rand_generator import RandGenerator
from rand_engine.file_handlers._writer_batch import FileBatchWriter
from rand_engine.file_handlers._writer_stream import FileStreamWriter
from rand_engine.utils.stream_handler import StreamHandler
from rand_engine.validators.advanced_validator import AdvancedValidator
from rand_engine.validators.exceptions import SpecValidationError, RandEngineError
  
class DataGenerator:
      
  def __init__(self, random_spec: Callable[[], dict] | dict, seed: int = None):
    # Valida a spec SEMPRE - obrigatório para prevenir erros durante geração
    self.lazy_random_spec = random_spec
    self.__validate_spec()
    
    # Configura gerador após validação bem-sucedida
    np.random.seed(seed)
    self._key_seed = int(np.random.SeedSequence(seed).generate_state(1)[0])
    self._size = None
    self._transformers: List[Optional[Callable]] = []
 

  def __evaluate_spec(self):
    if callable(self.lazy_random_spec): 
      return self.lazy_random_spec()
    return self.lazy_random_spec
  
  
  def __validate_spec(self):
    evaluated_spec = self.__evaluate_spec()
    AdvancedValidator.validate_and_raise(evaluated_spec)

  
  def wrapped_df_generator(self, size: int) -> pd.DataFrame:
    """
    This method generates a pandas DataFrame based on random data specified in the metadata parameter.
    :param size: int: Number of rows to be generated.
    :param transformer: Optional[Callable]: Function to transform the generated data.
    :return: pd.DataFrame: DataFrame with the generated data.
    """
    def wrapped_lazy_dataframe():
      evaluated_spec = self.__evaluate_spec()
      rand_generator = RandGenerator(evaluated_spec)
      
      df_pandas = rand_generator.generate_first_level(size=size, key_seed=self._key_seed)
      df_pandas = rand_generator.apply_embedded_transformers(df_pandas)
      df_pandas = rand_generator.apply_global_transformers(df_pandas, self._transformers)
      return df_pandas
    return wrapped_lazy_dataframe
  

  def transformers(self, transformers: List[Optional[Callable]]):
    self._transformers = transformers
    return self
  

  def size(self, size: int | Callable[[], int]):
    self._size = size
    return self


  def _resolve_size(self) -> int:
    if self._size is None:
      raise RandEngineError("No size set: call .size(n) with an int or a callable returning one.")
    return self._size() if callable(self._size) else self._size
  

  def get_df(self):
    lazy_dataframe = self.wrapped_df_generator(size=self._resolve_size())
    assert lazy_dataframe is not None, "You need to generate a DataFrame first."
    assert callable(lazy_dataframe), "wrapped_df_generator must return a callable"
    return lazy_dataframe()


  def stream_dict(self, min_throughput: int=1, max_throughput: int = 10) -> Generator:
    lazy_dataframe = self.wrapped_df_generator(size=self._resolve_size())
    assert lazy_dataframe is not None, "You need to generate a DataFrame first."
    assert callable(lazy_dataframe), "wrapped_df_generator must return a callable"
    while True:
      df_data_microbatch = lazy_dataframe()
      df_data_parsed = StreamHandler.convert_dt_to_str(df_data_microbatch)
      list_of_records = df_data_parsed.to_dict('records')
      for record in list_of_records:
        record["timestamp_created"] = round(time.time(), 3)
        yield record
        StreamHandler.sleep_to_contro_throughput(min_throughput, max_throughput)
  

  @property
  def write(self):
    return FileBatchWriter(self._resolve_size, self.wrapped_df_generator)


  @property
  def writeStream(self):
    return FileStreamWriter(self._resolve_size, self.wrapped_df_generator)



if __name__ == '__main__':

  pass
