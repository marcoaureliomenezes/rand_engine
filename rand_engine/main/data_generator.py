"""Generate pandas DataFrames, dict streams and files from one RandSpec and one seed."""
from functools import cache, partial
import time
from datetime import date
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


def _stream_records_are_arrow_compatible(dataframe: pd.DataFrame) -> bool:
  """Return whether Arrow preserves this frame's public record representation."""
  if any(type(column) is not str for column in dataframe.columns):
    return False

  lossless_object_types = {str, int, float, bool, date}
  for column in dataframe.columns:
    values = dataframe[column]
    if values.dtype == object:
      present = [value for value in values if value is not None]
      value_types = {type(value) for value in present}
      if len(value_types) > 1 or not value_types <= lossless_object_types:
        return False
      if value_types == {int} and any(not -(2 ** 63) <= value < 2 ** 63 for value in present):
        return False
    elif isinstance(values.dtype, (pd.CategoricalDtype, pd.StringDtype)):
      return False
    elif pd.api.types.is_complex_dtype(values.dtype) or (
      pd.api.types.is_float_dtype(values.dtype) and values.dtype.itemsize > 8
    ):
      return False
  return True


class DataGenerator:
  """
  Generate pandas DataFrames, dict streams or files from a RandSpec.

  Parameters
  ----------
  random_spec : dict or callable
      RandSpec mapping each column to ``{"method": ..., "kwargs": ...}``, or a
      zero-argument callable returning one. Validated at construction.
  seed : int, optional
      Seed of this generator's own random state; the same spec, seed and size
      give the same output.

  Raises
  ------
  SpecValidationError
      If the evaluated spec is invalid.

  Examples
  --------
  >>> from rand_engine import DataGenerator
  >>> spec = {
  ...     "user_id": {"method": "int_zfilled", "kwargs": {"length": 8}},
  ...     "age": {"method": "integers", "kwargs": {"min": 18, "max": 80}},
  ... }
  >>> df = DataGenerator(spec, seed=42).size(100).get_df()
  >>> list(df.columns)
  ['user_id', 'age']
  >>> bool(df["age"].between(18, 80).all())
  True
  """
      
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

  
  def _file_seam(self) -> tuple[Callable[..., pa.Schema], Callable[[int, int], pd.DataFrame]]:
    """Evaluate the spec once; return its catalog schema and a batch factory over that mapping."""
    evaluated_spec = self.__evaluate_spec()
    rand_generator = RandGenerator(evaluated_spec)

    def batch(size: int, offset: int = 0) -> pd.DataFrame:
      frame = rand_generator.generate_first_level(size=size, rng=self._rng, key_seed=self._key_seed, offset=offset)
      frame = rand_generator.apply_embedded_transformers(frame)
      frame = rand_generator.apply_global_transformers(frame, self._transformers)
      if not isinstance(frame, pd.DataFrame) or len(frame.index) != size:
        actual = len(frame.index) if isinstance(frame, pd.DataFrame) else "non-DataFrame"
        raise RandEngineError(f"global transformers must preserve row count {size}; got {actual}")
      return rand_generator.apply_modifiers(frame, self._rng)

    return cache(partial(self._catalog_schema, evaluated_spec)), batch


  def wrapped_df_generator(
    self, size: int, offset: int = 0
  ) -> Callable[[], pd.DataFrame]:
    """
    Return a zero-argument callable that generates one batch of ``size`` rows.

    The callable runs generation, embedded transformers, global transformers and
    modifiers, in that order.

    Parameters
    ----------
    size : int
        Rows in the batch.
    offset : int, default 0
        Row index of the batch's first row, so streamed and multi-part rows
        continue one index.

    Returns
    -------
    callable
        ``() -> pandas.DataFrame``; each call generates a new batch.

    Raises
    ------
    RandEngineError
        When called, if a global transformer changes the row count.

    Examples
    --------
    >>> from rand_engine import DataGenerator
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> batch = DataGenerator(spec, seed=42).wrapped_df_generator(size=4)
    >>> batch().shape
    (4, 1)
    """
    return lambda: self._file_seam()[1](size, offset)
  

  def transformers(self, transformers: List[Callable]):
    """
    Set the functions that transform each generated batch, in order.

    Parameters
    ----------
    transformers : list of callable
        Functions ``DataFrame -> DataFrame``; each must keep the batch's row count.

    Returns
    -------
    DataGenerator
        This generator, for chaining.

    Raises
    ------
    RandEngineError
        When a batch is generated, if a transformer changes its row count.

    Examples
    --------
    >>> from rand_engine import DataGenerator
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> gen = DataGenerator(spec, seed=42).transformers([lambda df: df.assign(double=df["age"] * 2)]).size(10)
    >>> list(gen.get_df().columns)
    ['age', 'double']
    """
    self._transformers = transformers
    return self
  

  def size(self, size: int | Callable[[], int]):
    """
    Set the rows per batch and return this generator.

    Parameters
    ----------
    size : int or callable
        Rows per ``get_df`` call, total rows of a ``write``, or rows per stream
        microbatch. A callable returns an int and is called once per ``get_df``,
        ``write.save`` or ``stream_dict`` call, and once per pass of ``writeStream``.

    Returns
    -------
    DataGenerator
        This generator, for chaining.

    Examples
    --------
    >>> from rand_engine import DataGenerator
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> DataGenerator(spec, seed=42).size(lambda: 5).get_df().shape
    (5, 1)
    """
    self._size = size
    return self


  def _resolve_size(self) -> int:
    if self._size is None:
      raise RandEngineError("No size set: call .size(n) with an int or a callable returning one.")
    return self._size() if callable(self._size) else self._size


  def _catalog_schema(self, evaluated_spec: dict, exact: bool = False) -> pa.Schema:
    """Return the spec's declared columns as a schema; `exact` (an empty file) refuses when transformers can change it."""
    if exact and (self._transformers or any(config.get("transformers") for config in evaluated_spec.values())):
      raise RandEngineError("empty output schema is indeterminate when transformers are configured")
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


  def get_df(self):
    """
    Return one DataFrame of ``size`` rows generated from the spec.

    Returns
    -------
    pandas.DataFrame
        ``size`` rows with the spec's columns, plus any columns the transformers add.

    Raises
    ------
    RandEngineError
        If ``size`` was not set.

    Examples
    --------
    >>> from rand_engine import DataGenerator, RandSpecs
    >>> df = DataGenerator(RandSpecs.customers(), seed=42).size(10).get_df()
    >>> len(df)
    10
    """
    lazy_dataframe = self.wrapped_df_generator(size=self._resolve_size())
    assert lazy_dataframe is not None, "You need to generate a DataFrame first."
    assert callable(lazy_dataframe), "wrapped_df_generator must return a callable"
    return lazy_dataframe()


  def stream_dict(self, min_throughput: int=1, max_throughput: int = 10) -> Generator:
    """
    Yield the rows of an endless stream as dicts, one microbatch of ``size`` rows at a time.

    Each record gains a ``timestamp_created`` key (epoch seconds, 3 decimals); datetime
    columns are strings. After each record the generator sleeps
    ``1 / uniform(min_throughput, max_throughput)`` seconds.

    Parameters
    ----------
    min_throughput : int, default 1
        Lower bound of the uniform draw that sets the sleep after each record.
    max_throughput : int, default 10
        Upper bound of the uniform draw that sets the sleep after each record.

    Yields
    ------
    dict
        One row of the spec's columns plus ``timestamp_created``.

    Raises
    ------
    RandEngineError
        On the first ``next()``, if ``size`` was not set.

    Examples
    --------
    >>> from itertools import islice
    >>> from rand_engine import DataGenerator
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> stream = DataGenerator(spec, seed=42).size(5).stream_dict(min_throughput=500, max_throughput=1000)
    >>> sorted(next(stream))
    ['age', 'timestamp_created']
    """
    size, offset = self._resolve_size(), 0
    while True:
      df_data_microbatch = self.wrapped_df_generator(size, offset)()
      offset += size
      df_data_parsed = StreamHandler.convert_dt_to_str(df_data_microbatch)
      if _stream_records_are_arrow_compatible(df_data_parsed):
        try:
          list_of_records = pa.Table.from_pandas(df_data_parsed, preserve_index=False).to_pylist()
        except (pa.ArrowInvalid, pa.ArrowTypeError):
          list_of_records = df_data_parsed.to_dict('records')
      else:
        list_of_records = df_data_parsed.to_dict('records')
      for record in list_of_records:
        record["timestamp_created"] = round(time.time(), 3)
        yield record
        StreamHandler.sleep_to_contro_throughput(min_throughput, max_throughput)
  

  @property
  def write(self):
    """
    Return the batch file writer of this generator.

    Chain ``format``, ``mode``, ``option`` or ``options``, then call ``save(path)``:
    it generates ``size`` rows and writes them to ``path`` (one file, or ``numFiles``
    parts). Nothing is written until ``save`` runs.

    Returns
    -------
    FileBatchWriter
        Writer whose ``save(path)`` writes files at the relative or absolute ``path``.

    Examples
    --------
    >>> import os, tempfile
    >>> from rand_engine import DataGenerator
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> out = tempfile.mkdtemp()
    >>> DataGenerator(spec, seed=42).size(10).write.format("csv").save(os.path.join(out, "ages.csv"))
    >>> os.path.isfile(os.path.join(out, "ages.csv"))
    True
    """
    return FileBatchWriter(self._resolve_size, self.wrapped_df_generator, self._file_seam)


  @property
  def writeStream(self):
    """
    Return the stream file writer of this generator.

    Chain ``format``, ``trigger(frequency)`` and ``option("timeout", seconds)`` (default
    20), then call ``start(path)``: each pass writes one microbatch of ``size`` rows to
    ``path/part-<uuid>.<ext>``, sleeps ``frequency`` seconds, and repeats until
    ``timeout`` seconds have passed. ``start`` blocks for that duration.

    Returns
    -------
    FileStreamWriter
        Writer whose ``start(path)`` writes files under ``path`` and returns ``None``.

    Examples
    --------
    >>> import os, tempfile
    >>> from rand_engine import DataGenerator
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 18, "max": 80}}}
    >>> out = tempfile.mkdtemp()
    >>> target = os.path.join(out, "ages")
    >>> stream = DataGenerator(spec, seed=42).size(10).writeStream
    >>> stream.format("json").trigger(frequency=0.1).option("timeout", 0.3).start(target)
    >>> bool(os.listdir(target))
    True
    """
    return FileStreamWriter(self._resolve_size, self.wrapped_df_generator)
