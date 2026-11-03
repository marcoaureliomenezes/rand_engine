"""evals/gate.py: the 2-of-3, no-regression and calibration decider, on literal fixtures with k = 3.

CLI under test: `main(["--results", DIR, "--tasks", DIR, "--k", "3"])` returns the exit code and prints
its messages and the table to stdout; `--calibrate` writes `<results>/ceilings.json`.
"""
import importlib.util
import json
from pathlib import Path

import pytest

GATE = Path(__file__).resolve().parents[2] / "evals" / "gate.py"
PROBES = "probe:import\nprobe:pip\nprobe:network"


def load_gate():
    spec = importlib.util.spec_from_file_location("eval_gate", GATE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write_task(tasks, name, rnd, legs, ceiling=None):
    d = tasks / name
    d.mkdir(parents=True)
    limits = f"\n[limits]\nceiling_tokens = {ceiling}\n" if ceiling else ""
    legs_toml = "[" + ", ".join(f'"{leg}"' for leg in legs) + "]"
    (d / "task.toml").write_text(f'[task]\nround = "{rnd}"\nlegs = {legs_toml}\n{limits}')


def write_trial(results, task, leg, n, tokens=1500, passed=True, **extra):
    res = {"task": task, "leg": leg, "trial": n, "k": 3, "passed": passed,
           "input_tokens": tokens - 500, "output_tokens": 500, "cost_usd": 0.25}
    if not passed:
        res.update(layer=2, surfaces=["generators"])
    res.update(extra)
    (results / f"{task}-{leg}-{n}.json").write_text(json.dumps(res))


@pytest.fixture
def env(tmp_path):
    """alpha (usage, ceiling 4000) all green, canary green on both legs, discovery all green."""
    tasks, results = tmp_path / "tasks", tmp_path / "results"
    results.mkdir()
    write_task(tasks, "alpha", "usage", ["pypi", "wheel"], ceiling=4000)
    write_task(tasks, "canary", "canary", ["pypi", "wheel"])
    write_task(tasks, "discovery", "discovery", ["pypi"])
    for leg in ("pypi", "wheel"):
        for n in (1, 2, 3):
            write_trial(results, "alpha", leg, n)
            write_trial(results, "canary", leg, n, check_output=PROBES if n == 1 else "")
    for n in (1, 2, 3):
        write_trial(results, "discovery", "pypi", n, passed=None)
    return tasks, results


def run_gate(env, capsys, *flags):
    tasks, results = env
    code = load_gate().main(["--results", str(results), "--tasks", str(tasks), "--k", "3", *flags])
    return code, capsys.readouterr().out.splitlines()


def test_all_green_exits_0_and_prints_the_table(env, capsys):
    code, out = run_gate(env, capsys)
    assert code == 0
    assert "task | wheel | pypi | tokens | cost_usd | layer | surface" in out
    assert "alpha | 3 | 3 | 1500 | 1.50 | - | -" in out


def test_one_of_three_on_the_wheel_fails(env, capsys):
    tasks, results = env
    for n in (2, 3):
        write_trial(results, "alpha", "wheel", n, passed=False)
        write_trial(results, "alpha", "pypi", n, passed=False)
    code, out = run_gate(env, capsys)
    assert code == 1
    assert "FAIL alpha: wheel passed 1 of 3 (need 2)" in out
    assert "alpha | 1 | 1 | 1500 | 1.50 | 2 | generators" in out


def test_wheel_two_of_three_against_pypi_three_of_three_is_a_regression(env, capsys):
    tasks, results = env
    write_trial(results, "alpha", "wheel", 3, passed=False)
    code, out = run_gate(env, capsys)
    assert code == 1
    assert "FAIL alpha: wheel passed 2 of 3, below pypi 3 of 3" in out
    assert not any("need 2" in line for line in out)


def test_wheel_equal_to_pypi_at_two_of_three_passes(env, capsys):
    tasks, results = env
    for leg in ("pypi", "wheel"):
        write_trial(results, "alpha", leg, 3, passed=False)
    code, out = run_gate(env, capsys)
    assert code == 0
    assert not any(line.startswith("FAIL") for line in out)


def test_red_canary_names_the_sandbox_and_voids_the_legs_usage_trials(env, capsys):
    tasks, results = env
    for n in (1, 2, 3):
        write_trial(results, "canary", "wheel", n, check_output="probe:import\nprobe:pip")
    code, out = run_gate(env, capsys)
    assert code == 1
    assert "FAIL canary wheel: the sandbox blocked a probe, missing: network" in out
    assert "FAIL alpha: wheel passed 0 of 3 (need 2)" in out


def test_probes_are_unioned_over_the_legs_canary_trials(env, capsys):
    tasks, results = env
    write_trial(results, "canary", "wheel", 1, check_output="probe:import")
    write_trial(results, "canary", "wheel", 2, check_output="probe:pip")
    write_trial(results, "canary", "wheel", 3, check_output="probe:network")
    code, out = run_gate(env, capsys)
    assert code == 0


def test_canary_harness_error_has_its_own_message_and_keeps_the_legs_usage_passes(env, capsys):
    tasks, results = env
    write_trial(results, "canary", "wheel", 2, check_output="", error="RuntimeError: boom")
    code, out = run_gate(env, capsys)
    assert code == 1
    assert "FAIL canary wheel: trial 2 harness error: RuntimeError: boom" in out
    assert not any("sandbox" in line or "need 2" in line or line.startswith("FAIL alpha") for line in out)


def test_missing_canary_file_has_its_own_message_and_keeps_the_legs_usage_passes(env, capsys):
    tasks, results = env
    (results / "canary-wheel-3.json").unlink()
    code, out = run_gate(env, capsys)
    assert code == 1
    assert "FAIL canary wheel: trial 3 missing file canary-wheel-3.json" in out
    assert not any("sandbox" in line or "need 2" in line or line.startswith("FAIL alpha") for line in out)


def test_usage_harness_error_fails(env, capsys):
    tasks, results = env
    write_trial(results, "alpha", "pypi", 2, passed=False, error="RuntimeError: boom")
    code, out = run_gate(env, capsys)
    assert code == 1
    assert "FAIL alpha: pypi trial 2 harness error: RuntimeError: boom" in out


def test_missing_file_is_a_failed_trial(env, capsys):
    tasks, results = env
    (results / "alpha-pypi-3.json").unlink()
    code, out = run_gate(env, capsys)
    assert code == 1
    assert "FAIL alpha: pypi trial 3 missing file alpha-pypi-3.json" in out


def test_usage_task_without_a_ceiling_fails(env, capsys):
    tasks, results = env
    write_task(tasks, "beta", "usage", ["pypi", "wheel"])
    for leg in ("pypi", "wheel"):
        for n in (1, 2, 3):
            write_trial(results, "beta", leg, n)
    code, out = run_gate(env, capsys)
    assert code == 1
    assert "FAIL beta: no ceiling_tokens in task.toml" in out
    assert not any(line.startswith("FAIL alpha") for line in out)


def test_discovery_failure_error_and_missing_file_change_nothing(env, capsys):
    tasks, results = env
    write_trial(results, "discovery", "pypi", 1, passed=False)
    write_trial(results, "discovery", "pypi", 2, passed=False, error="RuntimeError: boom")
    (results / "discovery-pypi-3.json").unlink()
    code, out = run_gate(env, capsys)
    assert code == 0
    assert not any(line.startswith("FAIL") for line in out)


HEADER = "task | wheel | pypi | tokens | cost_usd | layer | surface"


def test_calibrate_writes_ceil_of_twice_the_plain_median_and_prints_each_ceiling_before_the_table(env, capsys):
    tasks, results = env
    write_task(tasks, "beta", "usage", ["pypi", "wheel"])  # no ceiling: calibrate still writes one
    for leg in ("pypi", "wheel"):
        for n in (1, 2, 3):
            write_trial(results, "beta", leg, n, tokens=1001 if leg == "wheel" else 1000)
    # alpha passes with 1000 and 3000: median 2000, median_grouped 2999.5; the failed 90000 is excluded
    for n, tokens in ((1, 1000), (2, 3000), (3, 90000)):
        write_trial(results, "alpha", "wheel", n, tokens=tokens, passed=n != 3)
    for n in (1, 2, 3):
        write_trial(results, "alpha", "pypi", n, passed=False)
    code, out = run_gate(env, capsys, "--calibrate")
    assert code == 0
    # beta: median 1000.5, ceil(2001.0) pins the round-up
    assert json.loads((results / "ceilings.json").read_text()) == {"alpha": 4000, "beta": 2001}
    assert "ceiling alpha 4000" in out and "ceiling beta 2001" in out
    assert max(out.index("ceiling alpha 4000"), out.index("ceiling beta 2001")) < out.index(HEADER)
    assert "alpha | 2 | 0 | 2000 | 1.50 | 2 | generators" in out


def test_calibrate_excludes_the_passing_trials_of_a_canary_voided_leg(env, capsys):
    tasks, results = env
    for n in (1, 2, 3):
        write_trial(results, "canary", "wheel", n, check_output="probe:import\nprobe:pip")
        write_trial(results, "alpha", "wheel", n, tokens=9000)
        write_trial(results, "alpha", "pypi", n, tokens=1000)
    code, out = run_gate(env, capsys, "--calibrate")
    assert code == 0
    assert json.loads((results / "ceilings.json").read_text()) == {"alpha": 2000}
    assert "ceiling alpha 2000" in out
    assert "alpha | 0 | 3 | 1000 | 1.50 | - | -" in out


def test_calibrate_prints_the_fail_lines_and_still_exits_0(env, capsys):
    tasks, results = env
    write_task(tasks, "beta", "usage", ["pypi", "wheel"])
    for leg in ("pypi", "wheel"):
        for n in (1, 2, 3):
            write_trial(results, "beta", leg, n)
    code, out = run_gate(env, capsys, "--calibrate")
    assert code == 0
    assert "FAIL beta: no ceiling_tokens in task.toml" in out
    assert json.loads((results / "ceilings.json").read_text()) == {"alpha": 3000, "beta": 3000}


def test_a_passing_trial_with_unknown_tokens_is_not_a_pass_and_never_crashes(env, capsys):
    tasks, results = env
    for leg in ("pypi", "wheel"):
        for n in (1, 2, 3):
            write_trial(results, "alpha", leg, n, input_tokens=None, output_tokens=None)
    code, out = run_gate(env, capsys)
    assert code == 1
    assert "FAIL alpha: wheel passed 0 of 3 (need 2)" in out
    assert "alpha | 0 | 0 | - | 1.50 | - | -" in out


def test_calibrate_skips_passing_trials_with_unknown_tokens(env, capsys):
    tasks, results = env
    for leg in ("pypi", "wheel"):
        for n in (1, 2, 3):
            write_trial(results, "alpha", leg, n, input_tokens=None, output_tokens=None)
    code, out = run_gate(env, capsys, "--calibrate")
    assert code == 0
    assert json.loads((results / "ceilings.json").read_text()) == {}
    assert not any(line.startswith("ceiling") for line in out)
