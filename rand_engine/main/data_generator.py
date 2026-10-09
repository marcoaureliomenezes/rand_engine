from dataclasses import dataclass
from functools import partial
import time
import pandas as pd
import numpy as np
import pyarrow as pa
from typing import List, Generator, Callable
from rand_engine.main._rand_generator import RandGenerator
from rand_engine.file_handlers._writer_batch import FileBatchWriter
from rand_engine.file_handlers._writer_stream import FileStreamWriter
from rand_engine.utils.stream_handler import StreamHandler
from rand_engine.validators.advanced_validator import AdvancedValidator
from rand_engine.validators.exceptions import RandEngineError
from rand_engine.validators.method_specs import METHOD_CATALOG


@dataclass(frozen=True)
class _EvaluatedBatch:
  frame: pd.DataFrame
  declared_schema_def: Callable[[], pa.Schema | None]


class DataGenerator:
      
  def __init__(self, random_spec: Callable[[], dict] | dict, seed: int = None):
    self.lazy_random_spec = random_spec
    self.__validate_spec()

    seed_sequence = np.random.SeedSequence(seed)
    self._rng = np.random.default_rng(seed_sequence)
    self._key_seed = int(seed_sequence.generate_state(1)[0])
    self._size = None
    self._transformers: List[Callable] = []
 

  def __evaluate_spec(self):
    if callable(self.lazy_random_spec): 
      return self.lazy_random_spec()
    return self.lazy_random_spec
  
  
  def __validate_spec(self):
    evaluated_spec = self.__evaluate_spec()
    AdvancedValidator.validate_and_raise(evaluated_spec)

  
  def _evaluated_batch(self, size: int, offset: int = 0) -> _EvaluatedBatch:
    evaluated_spec = self.__evaluate_spec()
    rand_generator = RandGenerator(evaluated_spec)

    frame = rand_generator.generate_first_level(size=size, rng=self._rng, key_seed=self._key_seed, offset=offset)
    frame = rand_generator.apply_embedded_transformers(frame)
    frame = rand_generator.apply_global_transformers(frame, self._transformers)
    if not isinstance(frame, pd.DataFrame) or len(frame.index) != size:
      actual = len(frame.index) if isinstance(frame, pd.DataFrame) else "non-DataFrame"
      raise RandEngineError(f"global transformers must preserve row count {size}; got {actual}")
    frame = rand_generator.apply_modifiers(frame, self._rng)
    return _EvaluatedBatch(
      frame,
      partial(self._declared_schema_for, evaluated_spec),
    )


  def wrapped_df_generator(
    self, size: int, offset: int = 0
  ) -> Callable[[], pd.DataFrame]:
    """Return one lazy generation/transform/modifier row-batch pipeline."""
    return lambda: self._evaluated_batch(size, offset).frame
  

  def transformers(self, transformers: List[Callable]):
    self._transformers = transformers
    return self
  

  def size(self, size: int | Callable[[], int]):
    self._size = size
    return self


  def _resolve_size(self) -> int:
    if self._size is None:
      raise RandEngineError("No size set: call .size(n) with an int or a callable returning one.")
    return self._size() if callable(self._size) else self._size


  def _declared_schema_for(self, evaluated_spec: dict) -> pa.Schema | None:
    if self._transformers or any(config.get("transformers") for config in evaluated_spec.values()):
      return None

    fields = []
    try:
      for spec_name, config in evaluated_spec.items():
        names = config.get("cols", [spec_name])
        types = METHOD_CATALOG[config["method"]].arrow_types(config.get("kwargs", {}))
        if len(names) != len(types):
          raise RandEngineError(
            f"method '{config['method']}' declares {len(types)} output types for {len(names)} columns"
          )
        fields.extend(pa.field(name, type_, nullable=True) for name, type_ in zip(names, types))
    except RandEngineError:
      raise
    except Exception as error:
      raise RandEngineError(f"empty output schema cannot be derived: {type(error).__name__}") from error
    return pa.schema(fields)


  def _declared_schema(self) -> pa.Schema:
    schema = self._declared_schema_for(self.__evaluate_spec())
    if schema is None:
      raise RandEngineError("empty output schema is indeterminate when transformers are configured")
    return schema
  

  def get_df(self):
    lazy_dataframe = self.wrapped_df_generator(size=self._resolve_size())
    assert lazy_dataframe is not None, "You need to generate a DataFrame first."
    assert callable(lazy_dataframe), "wrapped_df_generator must return a callable"
    return lazy_dataframe()


  def stream_dict(self, min_throughput: int=1, max_throughput: int = 10) -> Generator:
    size, offset = self._resolve_size(), 0
    while True:
      df_data_microbatch = self.wrapped_df_generator(size, offset)()
      offset += size
      df_data_parsed = StreamHandler.convert_dt_to_str(df_data_microbatch)
      list_of_records = df_data_parsed.to_dict('records')
      for record in list_of_records:
        record["timestamp_created"] = round(time.time(), 3)
        yield record
        StreamHandler.sleep_to_contro_throughput(min_throughput, max_throughput)
  

  @property
  def write(self):
    return FileBatchWriter(
      self._resolve_size,
      self.wrapped_df_generator,
      self._declared_schema,
      evaluated_batch_def=self._evaluated_batch,
    )


  @property
  def writeStream(self):
    return FileStreamWriter(self._resolve_size, self.wrapped_df_generator)
