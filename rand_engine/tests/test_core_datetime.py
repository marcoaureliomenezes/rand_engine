from rand_engine.bulk.core_datetime import CoreDatetime


def test_gen_timestamps():
  result = CoreDatetime.gen_timestamps(10**1, '01-01-1970', '01-01-2021', '%d-%m-%Y')
  print(result)


def test_gen_unix_timestamps():
  result = CoreDatetime.gen_unix_timestamps(10**1, '01-01-1970', '01-01-2021', '%d-%m-%Y')
  print(result)
  assert len(result) == 10**1
  assert min(result) >= 0
  assert max(result) <= 1609459200


def test_gen_unix_timestamps_with_invalid_bottom_limit():
  try:
    CoreDatetime.gen_unix_timestamps(10**1, '01-01-1969', '01-01-2021', '%d-%m-%Y')
  except ValueError as e:
    assert str(e) == "Start date must be greater than 01-01-1970"

