"""Agent eval runner: each trial is a fresh temp dir and venv, then headless `claude -p`, then the task's check."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
FLAGS = ["--output-format", "stream-json", "--verbose", "--setting-sources", "",
         "--strict-mcp-config", '--mcp-config={"mcpServers":{}}', "--disable-slash-commands",
         "--no-session-persistence", "--permission-mode", "dontAsk",
         "--allowedTools", "Bash,Read,Write,Edit,Glob,Grep,WebSearch,WebFetch"]


def host_free_env(venv):
    """The caller's environment minus the host Claude session variables, with the trial venv active."""
    env = {k: v for k, v in os.environ.items()
           if not (k.startswith("CLAUDE_CODE_") or k in ("CLAUDECODE", "CLAUDE_PID", "CLAUDE_EFFORT"))}
    env["VIRTUAL_ENV"] = str(venv)
    env["PATH"] = f"{venv / ('Scripts' if os.name == 'nt' else 'bin')}{os.pathsep}{env.get('PATH', '')}"
    return env


def sandbox_settings(tmp):
    """--settings JSON: Bash in the native sandbox, writes confined to `tmp`, network to PyPI only, no escape."""
    return json.dumps({"sandbox": {
        "enabled": True, "failIfUnavailable": True, "allowUnsandboxedCommands": False,
        "autoAllowBashIfSandboxed": True,
        "filesystem": {"allowWrite": [str(tmp)]},
        "network": {"allowedDomains": ["pypi.org", "files.pythonhosted.org"]}}})


def assert_isolated(init):
    """Raise unless the init event lists no skill, slash command, MCP server or non-builtin plugin."""
    leaks = {"skills": init.get("skills"), "slash_commands": init.get("slash_commands"),
             "mcp_servers": init.get("mcp_servers"),
             "plugins": [p for p in init.get("plugins", []) if p.get("path") != "builtin"]}
    leaks = {k: v for k, v in leaks.items() if v}
    if leaks:
        raise RuntimeError(f"isolation violated: {leaks}")


def run_trial(task, n, args):
    """Run one trial and return its result dict; any failure lands in `error`, never raises."""
    task_dir = HERE / "tasks" / task
    res = {"task": task, "trial": n, "passed": False}
    work = Path(tempfile.mkdtemp(prefix=f"eval-{task}-"))
    t0 = time.monotonic()
    try:
        cfg = tomllib.loads((task_dir / "task.toml").read_text())
        venv, cwd = work / "venv", work / "work"
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
        py = venv / ("Scripts" if os.name == "nt" else "bin") / "python"
        if cfg.get("environment", {}).get("install_rand_engine", True):
            subprocess.run([str(py), "-m", "pip", "install", "-q", args.rand_engine],
                           check=True, stdin=subprocess.DEVNULL)
        shutil.copytree(task_dir / "environment", cwd) if (task_dir / "environment").is_dir() else cwd.mkdir()
        env = host_free_env(venv)
        try:
            p = subprocess.run(["claude", "-p", (task_dir / "instruction.md").read_text(), *FLAGS,
                                "--settings", sandbox_settings(work), "--model", args.model], cwd=cwd, env=env, text=True,
                               capture_output=True, stdin=subprocess.DEVNULL,
                               timeout=cfg["agent"]["timeout_sec"])
            stream, res["agent_exit"] = p.stdout, p.returncode
        except subprocess.TimeoutExpired as e:
            stream, res["agent_exit"] = (e.stdout or b"").decode(), "timeout"
        events = [json.loads(line) for line in stream.splitlines() if line.startswith("{")]
        init = next(e for e in events if e.get("subtype") == "init")
        assert_isolated(init)
        res["model"] = init["model"]
        done = next((e for e in events if e.get("type") == "result"), {})
        u = done.get("usage", {})
        res["input_tokens"] = sum(u.get(k, 0) for k in
                                  ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
        res["output_tokens"] = u.get("output_tokens", 0)
        res["cost_usd"] = done.get("total_cost_usd")
        check = subprocess.run([str(py), str(task_dir / "tests" / "check.py")], cwd=cwd, env=env,
                               stdin=subprocess.DEVNULL, capture_output=True, text=True,
                               timeout=cfg["verifier"]["timeout_sec"])
        res["passed"] = check.returncode == 0
        res["check_output"] = (check.stdout.strip().splitlines() or [""])[-1]
    except Exception as e:
        res["error"] = f"{type(e).__name__}: {e}"
    finally:
        res["duration_s"] = round(time.monotonic() - t0, 1)
        shutil.rmtree(work, ignore_errors=True)
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--task", nargs="+", required=True, help="folder names under evals/tasks")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--rand-engine", default="rand-engine", help="pip requirement or wheel path")
    ap.add_argument("--model", required=True, help="pinned full model id")
    ap.add_argument("--out", required=True, type=Path, help="result directory, outside the repo")
    args = ap.parse_args()
    out = args.out.resolve()
    if out == REPO or REPO in out.parents:
        ap.error(f"--out must be outside the repo ({REPO})")
    out.mkdir(parents=True, exist_ok=True)
    errors = 0
    for task in args.task:
        for n in range(1, args.k + 1):
            res = run_trial(task, n, args)
            (out / f"{task}-{n}.json").write_text(json.dumps(res, indent=2))
            print(f"{task} trial {n}: passed={res['passed']} error={res.get('error')}")
            errors += "error" in res
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
