import subprocess
import sys

import numpy as np
import pytest

from rand_engine.core._keys import Keys
from rand_engine.main.data_generator import DataGenerator
from rand_engine.validators.exceptions import RandEngineError

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


PERMUTED = {"style": "permuted", "domain": 10**5, "start": 0}


def _pk(kwargs, size, seed=None):
  return DataGenerator({"id": {"method": "pk", "kwargs": kwargs}}, seed=seed).size(size).get_df()["id"]


def test_pk_permuted_is_unique_inside_the_domain_and_not_monotone():
  ids = _pk(PERMUTED, 10**4).to_numpy()
  assert np.unique(ids).size == 10**4
  assert ids.min() >= 0 and ids.max() < 10**5
  assert not (np.all(np.diff(ids) > 0) or np.all(np.diff(ids) < 0))


@pytest.mark.parametrize("domain, key, head", [
  (10**5, 7, [82034, 95789, 91538, 47114, 29996, 52242]),
  (2000, 3, [482, 1695, 1486, 1257, 722, 1526])])
def test_pk_permuted_matches_the_prototype_feistel(domain, key, head):
  assert _pk({"style": "permuted", "domain": domain, "key": key}, 6).tolist() == head


def test_pk_permuted_over_its_whole_domain_is_a_permutation_of_it():
  ids = _pk({"style": "permuted", "domain": 2000, "start": 5}, 2000).to_numpy()
  assert np.array_equal(np.sort(ids), np.arange(5, 2005))


@pytest.mark.stress
def test_pk_permuted_at_stress_size():
  ids = _pk({"style": "permuted", "domain": 10**7}, 10**6).to_numpy()
  assert np.unique(ids).size == 10**6 and ids.min() >= 0 and ids.max() < 10**7


def test_pk_permuted_near_int64_does_not_overflow():
  start, domain = 7, 10**15
  head = Keys.gen_pk(10**4, style="permuted", domain=domain, start=start)
  last = Keys.gen_pk(1, offset=10**15 - 1, style="permuted", domain=domain, start=start)
  ids = np.concatenate([head, last])
  assert np.unique(ids).size == 10**4 + 1
  assert ids.min() >= 7 and ids.max() < 7 + 10**15


@pytest.mark.parametrize("kwargs", [
  {"style": "sequence", "start": 1, "format": "C-{:08d}"},
  {**PERMUTED, "format": "C-{:08d}"}])
def test_pk_format_renders_unique_strings(kwargs):
  ids = _pk(kwargs, 10**4)
  assert ids.nunique() == 10**4
  assert ids.str.fullmatch(r"C-\d{8}").all()


@pytest.mark.stress
@pytest.mark.parametrize("kwargs", [{"start": 1}, {"style": "permuted", "domain": 10**7}])
def test_pk_format_at_stress_size(kwargs):
  assert _pk({**kwargs, "format": "C-{:08d}"}, 10**6).nunique() == 10**6


def test_pk_format_over_sequence_renders_the_literal_template():
  assert _pk({"start": 1, "format": "C-{:08d}"}, 3).tolist() == ["C-00000001", "C-00000002", "C-00000003"]


def test_pk_ignores_the_generator_seed_and_depends_on_the_key():
  seeded, unseeded = _pk(PERMUTED, 1000, seed=1), _pk(PERMUTED, 1000, seed=None)
  assert seeded.equals(unseeded)
  assert not seeded.equals(_pk({**PERMUTED, "key": 1}, 1000))


def test_pk_permuted_is_identical_across_processes():
  code = ("from rand_engine.main.data_generator import DataGenerator;"
          f"print(DataGenerator({{'id': {{'method': 'pk', 'kwargs': {PERMUTED!r}}}}}).size(1000).get_df()['id'].tolist())")
  other = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True).stdout
  assert other.strip() == str(_pk(PERMUTED, 1000, seed=3).tolist())


def test_pk_permuted_past_its_domain_raises_naming_column_and_domain():
  with pytest.raises(RandEngineError, match=r"(?s)'id'.*domain 10\b"):
    _pk({"style": "permuted", "domain": 10}, 11)


@pytest.mark.parametrize("offset, start, step", [(2, 2**62, 2**61), (0, 2**63 + 10, -100)])
def test_pk_sequence_leaving_int64_raises(offset, start, step):
  with pytest.raises(RandEngineError, match="int64"):
    Keys.gen_pk(3, offset=offset, start=start, step=step)
