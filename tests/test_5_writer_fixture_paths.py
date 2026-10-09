from pathlib import Path

import pandas as pd
import pytest

from rand_engine import DataGenerator
from tests.fixtures.f3_integrations import base_path_files_test, create_output_dir


@pytest.mark.xfail(strict=True, reason="J5.S1.T3 RED: writer fixtures still use persistent tests/test_outputs")
def test_writer_fixture_keeps_generated_outputs_under_pytest_tmp_path(
    base_path_files_test,
    tmp_path,
):
    output = Path(base_path_files_test) / "fixture_contract" / "rows"
    (
        DataGenerator({"value": {"method": "integers", "kwargs": {"min": 7, "max": 7}}})
        .size(2)
        .write.format("csv")
        .mode("overwrite")
        .save(str(output))
    )

    [generated] = output.parent.glob("rows*")
    assert pd.read_csv(generated)["value"].tolist() == [7, 7]
    assert Path(base_path_files_test).resolve().is_relative_to(tmp_path.resolve())
