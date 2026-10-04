import numpy as np
import pytest

from rand_engine.main.data_generator import DataGenerator

PK = {"method": "pk", "kwargs": {"style": "sequence", "start": 1, "step": 1}}


@pytest.mark.parametrize("size, start, step", [
  (10**4, 1, 1), (10**3, 10, 3), pytest.param(10**6, 1, 1, marks=pytest.mark.stress)])
def test_pk_sequence_is_start_plus_row_index(size, start, step):
  spec = {"id": {"method": "pk", "kwargs": {"style": "sequence", "start": start, "step": step}}}
  df = DataGenerator(spec).size(size).get_df()
  assert np.issubdtype(df["id"].dtype, np.integer)
  assert np.array_equal(df["id"].to_numpy(), start + np.arange(size) * step)


@pytest.mark.parametrize("parent_size, child_size", [(10**3, 10**4), pytest.param(10**4, 10**6, marks=pytest.mark.stress)])
def test_fk_values_sit_in_the_parent_pk_set(parent_size, child_size):
  parent = DataGenerator({"id": PK}, seed=1).size(parent_size).get_df()
  child_spec = {"parent_id": {"method": "fk", "kwargs": {"parent": PK, "parent_size": parent_size}}}
  child = DataGenerator(child_spec, seed=2).size(child_size).get_df()
  assert child["parent_id"].isin(parent["id"]).all()
  assert child["parent_id"].nunique() > 1


def test_fk_depends_on_the_generator_seed():
  spec = {"parent_id": {"method": "fk", "kwargs": {"parent": PK, "parent_size": 100}}}
  one, two = (DataGenerator(spec, seed=s).size(1000).get_df()["parent_id"] for s in (1, 2))
  assert not one.equals(two)


def test_two_get_df_calls_return_identical_keys():
  spec = {"id": PK, "parent_id": {"method": "fk", "kwargs": {"parent": PK, "parent_size": 100}}}
  generator = DataGenerator(spec).size(1000)
  first, second = generator.get_df(), generator.get_df()
  assert first["id"].equals(second["id"])
  assert first["parent_id"].equals(second["parent_id"])
