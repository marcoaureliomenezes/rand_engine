"""Exception classes raised by Rand Engine.

The errors Rand Engine raises on purpose are subclasses of ``RandEngineError``,
so one ``except`` clause covers them. The narrower subclasses name the stage
that failed: spec validation, column generation, or a per-column transformer.
"""


class RandEngineError(Exception):
    """Base class of the errors Rand Engine raises on purpose.

    Raised directly for size faults, an fk column with no eligible parent, a
    modifier column that a global transformer dropped, anomaly values that
    cannot keep the dtype the column's transformers (embedded or global) left, a global transformer
    that changes the row count, an empty schema that cannot be derived, the pk
    index and sequence guards, ``RandSpecs.faker_pool``, and the writers. A
    failure in the generation step (the method call, the conversion, the
    multi-column unpack) surfaces as ``ColumnGenerationError``.

    Examples
    --------
    >>> from rand_engine import DataGenerator
    >>> from rand_engine.validators.exceptions import RandEngineError
    >>> try:
    ...     DataGenerator({"age": {"method": "integers", "kwargs": {"min": 1, "max": 9}}}).get_df()
    ... except RandEngineError as error:
    ...     print(str(error).startswith("No size set"))
    True
    """


class SpecValidationError(RandEngineError):
    """A RandSpec or Arrow schema failed validation before generation.

    Raised by the validators of ``DataGenerator`` and ``SparkGenerator``
    before any row is generated, and by the construction net; the message
    lists every problem found. ``RandSpecs.from_schema`` reports one problem
    per raise.

    Examples
    --------
    >>> from rand_engine import DataGenerator
    >>> from rand_engine.validators.exceptions import SpecValidationError
    >>> try:
    ...     DataGenerator({"age": {"method": "invalid"}})
    ... except SpecValidationError as error:
    ...     print("Column 'age'" in str(error))
    True
    """


class ColumnGenerationError(RandEngineError):
    """A column's generation step failed.

    Raised by ``DataGenerator`` when a column's method call, its conversion of
    the values, or the unpack of a multi-column result raises during generation,
    after the spec passed validation. The message names the column and the
    original error, which is chained as ``__cause__``.

    Examples
    --------
    >>> from rand_engine.validators.exceptions import ColumnGenerationError, RandEngineError
    >>> issubclass(ColumnGenerationError, RandEngineError)
    True
    """


class TransformerError(RandEngineError):
    """A per-column transformer raised while transforming its column.

    Raised by ``DataGenerator`` when a transformer in a column's
    ``transformers`` list raises. The message names the column and the
    transformer's zero-based position in that list, and the original error
    is chained as ``__cause__``. Global transformers are not wrapped: their
    errors propagate unchanged.

    Examples
    --------
    >>> from rand_engine import DataGenerator
    >>> from rand_engine.validators.exceptions import TransformerError
    >>> spec = {"age": {"method": "integers", "kwargs": {"min": 1, "max": 9}, "transformers": [lambda value: 1 / 0]}}
    >>> try:
    ...     DataGenerator(spec).size(3).get_df()
    ... except TransformerError as error:
    ...     print(error)
    Error applying transformer 0 to column 'age': ZeroDivisionError: division by zero
    """


class FileWriterError(RandEngineError):
    """A file writer failed. Writers raise ``RandEngineError`` instead.

    The class stays importable so callers can name it in their own handlers.

    Examples
    --------
    >>> from rand_engine.validators.exceptions import FileWriterError, RandEngineError
    >>> issubclass(FileWriterError, RandEngineError)
    True
    """
