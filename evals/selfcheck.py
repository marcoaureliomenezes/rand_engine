"""No-agent self-check: each usage task's reference passes its check, its decoy fails at layer 2.

Usage: python evals/selfcheck.py --rand-engine <wheel>. Exits 1 on any harness error, naming the task.
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

import run

HERE = Path(__file__).resolve().parent


def trial(task_dir, cfg, rand_engine, variant):
    """Prepare a fresh trial, run `tests/<variant>/solve.py` and the check; returns (exit code, RESULT dict, stdout)."""
    work = Path(tempfile.mkdtemp(prefix=f"selfcheck-{task_dir.name}-"))
    try:
        env, py, cwd = run.prepare_trial(task_dir, cfg, work, rand_engine)
        solve = cwd / "solve.py"
        shutil.copy(task_dir / "tests" / variant / "solve.py", solve)
        subprocess.run([str(py), str(solve)], cwd=cwd, env=env, stdin=subprocess.DEVNULL, check=True,
                       timeout=cfg["agent"]["timeout_sec"])
        check_env = {k: v for k, v in env.items() if not k.startswith("RAND_EVAL_")}
        check_env["PYTHONPATH"] = str(HERE)
        if (transcript := task_dir / "tests" / variant / "transcript.jsonl").is_file():
            check_env["RAND_EVAL_TRANSCRIPT"] = str(transcript)
        p = subprocess.run([str(py), str(task_dir / "tests" / "check.py")], cwd=cwd, env=check_env,
                           stdin=subprocess.DEVNULL, capture_output=True, text=True,
                           timeout=cfg["verifier"]["timeout_sec"])
        return p.returncode, run.check_result(p.stdout), p.stdout
    finally:
        shutil.rmtree(work, ignore_errors=True)


def selfcheck(task_dir, rand_engine):
    """Raises RuntimeError or any trial error when the reference or the decoy misbehaves."""
    cfg = tomllib.loads((task_dir / "task.toml").read_text(encoding="utf-8"))
    code, _, out = trial(task_dir, cfg, rand_engine, "solution")
    if code != 0:
        raise RuntimeError(f"reference check exited {code}: {out[-300:]}")
    code, result, out = trial(task_dir, cfg, rand_engine, "decoy")
    if code == 0 or result.get("layer") != "2":
        raise RuntimeError(f"decoy: exit {code}, RESULT {result}: {out[-300:]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rand-engine", required=True, help="the rand-engine wheel (or requirement) to install")
    args = ap.parse_args()
    bad = ran = 0
    for toml in sorted((HERE / "tasks").glob("*/task.toml")):
        task_dir = toml.parent
        try:
            if tomllib.loads(toml.read_text(encoding="utf-8")).get("task", {}).get("round") != "usage":
                continue
            selfcheck(task_dir, args.rand_engine)
            ran += 1
            print(f"{task_dir.name}: ok", flush=True)
        except Exception as e:
            bad += 1
            print(f"{task_dir.name}: HARNESS ERROR {type(e).__name__}: {e}", flush=True)
    if not ran:
        print("HARNESS ERROR: no usage task found", flush=True)
        bad += 1
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
