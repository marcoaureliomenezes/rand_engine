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


@pytest.mark.parametrize("offset, start, step", [(2, 2**62, 2**61), (0, 2**63 + 10, -100), (0, 2**63 - 2, 1), (0, -2**63 + 1, -1), (np.int64(2), 2**62, 2**61)])
def test_pk_sequence_leaving_int64_raises(offset, start, step):
  with pytest.raises(RandEngineError, match="int64"):
    Keys.gen_pk(3, offset=offset, start=start, step=step)


SEQ, PERM = {"start": 1}, {"style": "permuted", "domain": 10**5, "key": 9}
FMT = {"start": 1, "format": "C-{:08d}"}


def _fk(parent_kwargs, parent_size, size, seed=2, skew=None, col="parent_id"):
  kw = {"parent": {"method": "pk", "kwargs": parent_kwargs}, "parent_size": parent_size}
  if skew is not None:
    kw["skew"] = skew
  return DataGenerator({col: {"method": "fk", "kwargs": kw}}, seed=seed).size(size).get_df()[col]


@pytest.mark.parametrize("parent_kwargs, parent_size, child_size", [
  (PERM, 10**3, 10**4), ({"style": "permuted", "domain": 10**3}, 10**3, 10**4), ({**PERM, "format": "C-{:08d}"}, 10**3, 10**4), (FMT, 10**3, 10**4),
  pytest.param(PERM, 10**4, 10**6, marks=pytest.mark.stress)])
def test_fk_over_permuted_and_string_parents_sits_in_the_parent_pk_set(parent_kwargs, parent_size, child_size):
  """AC2.1 (permuted), AC2.2 (format)."""
  parent = _pk(parent_kwargs, parent_size, seed=1)
  child = _fk(parent_kwargs, parent_size, child_size)
  assert child.isin(parent).all() and child.nunique() > 1


@pytest.mark.parametrize("parent_kwargs", [SEQ, PERM, FMT])
@pytest.mark.parametrize("parent_seed, child_seed", [(1, 2), (None, 2), (1, None)])
def test_fk_holds_across_generator_seeds(parent_kwargs, parent_seed, child_seed):
  """AC2.7."""
  assert _fk(parent_kwargs, 500, 10**4, seed=child_seed).isin(_pk(parent_kwargs, 500, seed=parent_seed)).all()


@pytest.mark.parametrize("parent_size, child_size", [(10**2, 10**4), pytest.param(10**3, 10**6, marks=pytest.mark.stress)])
def test_fk_uniform_references_every_parent(parent_size, child_size):
  """AC2.4."""
  assert set(_fk(SEQ, parent_size, child_size)) == set(range(1, parent_size + 1))


@pytest.mark.parametrize("parent_size, child_size, uniform_max", [
  (10**3, 10**4, 0.03), pytest.param(10**4, 10**6, 0.02, marks=pytest.mark.stress)])
def test_fk_skew_sends_children_to_scattered_hot_parents(parent_size, child_size, uniform_max):
  """AC2.5: the top 1% of parents by references; parent index = value - start."""
  top = parent_size // 100
  skewed = _fk(SEQ, parent_size, child_size, skew=1.2).value_counts()
  uniform = _fk(SEQ, parent_size, child_size).value_counts()
  assert skewed.iloc[:top].sum() >= 0.20 * child_size
  assert uniform.iloc[:top].sum() <= uniform_max * child_size
  hot_index = skewed.index[:top].to_numpy() - 1
  assert (hot_index < top).sum() < top / 2
  assert set(skewed.index) <= set(range(1, parent_size + 1))


def test_two_fk_columns_with_identical_kwargs_differ():
  """AC2.8: the column name enters the parent-index hash."""
  kw = {"parent": PK, "parent_size": 1000}
  df = DataGenerator({"a": {"method": "fk", "kwargs": kw}, "b": {"method": "fk", "kwargs": dict(kw)}}, seed=1).size(1000).get_df()
  assert (df["a"] != df["b"]).mean() > 0.9


@pytest.mark.parametrize("skew, head", [(0, [267, 786, 227, 987, 287, 297]), (1.2, [927, 6, 6, 46, 580, 6]), (1.0, [1, 427, 657, 992, 566, 392])])
def test_fk_matches_the_prototype_parent_index(skew, head):
  """Pins from proto/core.py (cell_hash, index, zipf_index) + proto/feistel.py, seed crc32(key_seed/column/canonical kwargs)."""
  parent = {"method": "pk", "kwargs": {"start": 0}}
  assert Keys.gen_fk(6, parent=parent, parent_size=1000, skew=skew, key_seed=5, column="c").tolist() == head


@pytest.mark.parametrize("n, rank", [(1, 0), (2, 1), (10, 9)])
def test_zipf_rank_at_the_top_uniform_stays_inside_the_domain(n, rank):
  """u = 1 - 2**-53 lands on n unclamped and would hang the Feistel cycle-walk; literals from proto zipf_index."""
  assert Keys._zipf_rank(np.array([2**53 - 1], dtype=np.int64), n, 1.2).tolist() == [rank]


def test_fk_seed_mixes_the_fk_kwargs():
  """Parents differing only in start: without the kwargs in the seed, every value would shift by exactly 1."""
  zero, one = (Keys.gen_fk(1000, parent={"method": "pk", "kwargs": {"start": s}}, parent_size=1000, key_seed=5, column="c") for s in (0, 1))
  assert ((one - zero) != 1).mean() > 0.9


def test_fk_child_from_a_second_process_joins_the_parent_parquet(tmp_path):
  """AC2.3: parent written to Parquet by one process, child generated by another."""
  parent_kwargs = {**PERM, "format": "C-{:08d}"}
  pk = {"method": "pk", "kwargs": parent_kwargs}
  fk = {"method": "fk", "kwargs": {"parent": pk, "parent_size": 1000, "skew": 1.2}}
  head = "from rand_engine.main.data_generator import DataGenerator as G;"
  for spec, seed, name in [({"id": pk}, 1, "parent"), ({"pid": fk}, 2, "child")]:
    code = head + f"G({spec!r}, seed={seed}).size({1000 if name == 'parent' else 10**4}).get_df().to_parquet({str(tmp_path / name)!r})"
    subprocess.run([sys.executable, "-c", code], check=True)
  import pandas as pd
  parent, child = pd.read_parquet(tmp_path / "parent")["id"], pd.read_parquet(tmp_path / "child")["pid"]
  assert len(child) == 10**4 and child.isin(parent).all()


def test_pk_permuted_empty_batch_past_the_domain_is_empty():
  assert Keys.gen_pk(0, offset=20, style="permuted", domain=10).tolist() == []


def test_pk_sequence_empty_batch_at_the_int64_edge_is_empty():
  assert Keys.gen_pk(0, start=-2**63).tolist() == []


def test_pk_sequence_reaches_the_int64_minimum_exactly():
  assert Keys.gen_pk(3, start=-2**63 + 2, step=-1).tolist() == [-2**63 + 2, -2**63 + 1, -2**63]


def test_pk_sequence_numpy_int_size_leaving_int64_raises():
  with pytest.raises(RandEngineError, match="int64"):
    DataGenerator({"id": {"method": "pk", "kwargs": {"start": 2**63 - 2}}}).size(np.int64(3)).get_df()


def test_fk_over_a_parent_leaving_int64_raises():
  with pytest.raises(RandEngineError, match="int64"):
    _fk({"start": 2**63 - 5}, 100, 10)
