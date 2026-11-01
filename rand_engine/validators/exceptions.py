"""Exception classes raised by Rand Engine.

The errors Rand Engine raises on purpose are subclasses of ``RandEngineError``,
so one ``except`` clause covers them. The narrower subclasses name the stage
that failed: spec validation, column generation, a per-column transformer, or
file output.
"""


class RandEngineError(Exception):
    """Base class of the errors Rand Engine raises on purpose.

    Raised directly when no narrower class applies: a generator or writer
    used out of order, a writer option with an invalid or unsupported value,
    a file or SQLite write that fails, a schema that changes between batches,
    or a primary or foreign key that cannot be generated. A column's failure
    surfaces as ``ColumnGenerationError``, which is also a ``RandEngineError``.

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

    Raised by ``DataGenerator`` and ``SparkGenerator`` when the spec is
    checked, before any row is generated, and by ``RandSpecs.from_schema``
    for a non-Arrow schema, a malformed override, or a field with no default
    recipe. The message lists every problem found.

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
    """A column's generator method failed while its values were built.

    Raised by ``DataGenerator`` when a column's method raises during
    generation, after the spec passed validation. The message names the
    column and the original error, which is chained as ``__cause__``.

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
    """A file writer failed. Declared, but raised nowhere in this release.

    No code path in this release raises ``FileWriterError``: file and SQLite
    write failures raise ``RandEngineError``. The class stays importable so
    callers can name it in their own handlers.

    Examples
    --------
    >>> from rand_engine.validators.exceptions import FileWriterError, RandEngineError
    >>> issubclass(FileWriterError, RandEngineError)
    True
    """
