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
BASE = ["--output-format", "stream-json", "--verbose", "--setting-sources", "",
        "--strict-mcp-config", '--mcp-config={"mcpServers":{}}', "--disable-slash-commands",
        "--no-session-persistence", "--permission-mode", "dontAsk"]
TOOLS = ["Bash", "Read", "Write", "Edit", "Glob", "Grep"]


def _usage_flags(work):
    """Usage and canary: no web tools, and the sandbox and permissions deny of the trial dir `work`."""
    sandbox = {"enabled": True, "failIfUnavailable": True, "allowUnsandboxedCommands": False,
               "network": {"allowedDomains": []},
               "filesystem": {"denyRead": [str(Path.home())], "allowRead": [str(work)]}}
    # sandbox denyRead covers Bash only; the permissions deny covers the Read, Glob and Grep tools
    settings = {"sandbox": sandbox, "permissions": {"deny": ["Read(~/**)", "Glob(~/**)", "Grep(~/**)"]}}
    return ["--disallowedTools", "WebSearch,WebFetch", "--settings", json.dumps(settings)]


ROUNDS = {"usage": {"tools": TOOLS, "flags": _usage_flags},
          "canary": {"tools": TOOLS, "flags": _usage_flags},
          "discovery": {"tools": [*TOOLS, "WebSearch", "WebFetch"], "flags": lambda work: []}}


def round_flags(rnd, work):
    """The claude flags of a round: `--tools` sets the init tool list, `--allowedTools` the permission."""
    r = ROUNDS[rnd]
    tools = ",".join(r["tools"])
    return [*BASE, "--tools", tools, "--allowedTools", tools, *r["flags"](work)]


def trial_env(venv):
    """The caller's environment minus every host Claude session variable (the OAuth token too), the trial venv active."""
    env = {k: v for k, v in os.environ.items()
           if not (k.startswith("CLAUDE_CODE_") or k in ("CLAUDECODE", "CLAUDE_PID", "CLAUDE_EFFORT"))}
    env["VIRTUAL_ENV"] = str(venv)
    env["PATH"] = f"{venv / 'bin'}{os.pathsep}{env['PATH']}"
    return env


def assert_isolated(init, mode, tools):
    """Raise unless the init event lists no skill, slash command, MCP server or non-builtin plugin,
    reports permission mode `mode` and exactly the tools `tools`."""
    leaks = {"skills": init.get("skills"), "slash_commands": init.get("slash_commands"),
             "mcp_servers": init.get("mcp_servers"),
             "plugins": [p for p in init.get("plugins", []) if p.get("path") != "builtin"]}
    leaks = {k: v for k, v in leaks.items() if v}
    if init.get("permissionMode") != mode:
        leaks["permissionMode"] = init.get("permissionMode")
    if sorted(init.get("tools", [])) != sorted(tools):
        leaks["tools"] = init.get("tools")
    if leaks:
        raise RuntimeError(f"isolation violated: {leaks}")


def prepare_trial(task_dir, cfg, work, rand_engine):
    """The trial venv with the rand-engine requirement and the task's `[environment] requirements`
    pip-installed, then the task's `environment/` as the agent's cwd; returns (env, python, cwd)."""
    venv, cwd = work / "venv", work / "work"
    env = trial_env(venv)
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True, env=env)
    py = venv / "bin" / "python"
    envcfg = cfg.get("environment", {})
    pkgs = ([rand_engine] if envcfg.get("install_rand_engine", True) else []) + list(envcfg.get("requirements", []))
    if pkgs:
        subprocess.run([str(py), "-m", "pip", "install", "-q", *pkgs],
                       check=True, stdin=subprocess.DEVNULL, env=env)
    if (task_dir / "environment").is_dir():
        shutil.copytree(task_dir / "environment", cwd)
    else:
        cwd.mkdir()
    return env, py, cwd


def check_result(stdout):
    """The JSON object on the check's last `RESULT ` line; {} when it prints none; ValueError when malformed."""
    lines = [line for line in stdout.splitlines() if line.startswith("RESULT ")]
    if not lines:
        return {}
    try:
        result = json.loads(lines[-1][len("RESULT "):])
    except json.JSONDecodeError as e:
        raise ValueError(f"malformed RESULT line: {e}") from e
    if not isinstance(result, dict):
        raise ValueError("RESULT line is not a JSON object")
    return result


def run_trial(task, n, args):
    """Run one trial and return its result dict; any failure lands in `error`, never raises."""
    task_dir = HERE / "tasks" / task
    res = {"task": task, "trial": n, "leg": args.leg, "k": args.k, "passed": False}
    work = Path(tempfile.mkdtemp(prefix=f"eval-{task}-"))
    t0 = time.monotonic()
    try:
        cfg = tomllib.loads((task_dir / "task.toml").read_text(encoding="utf-8"))
        rnd = cfg["task"]["round"]
        res["round"] = rnd
        env, py, cwd = prepare_trial(task_dir, cfg, work, args.rand_engine)
        try:
            prompt = (task_dir / "instruction.md").read_text(encoding="utf-8")
            p = subprocess.run(["claude", "-p", prompt, *round_flags(rnd, work), "--model", args.model], cwd=cwd, text=True,
                               env={**env, "CLAUDE_CODE_SUBPROCESS_ENV_SCRUB": "1",
                                    **{k: v for k, v in os.environ.items() if k == "CLAUDE_CODE_OAUTH_TOKEN"}},
                               capture_output=True, stdin=subprocess.DEVNULL,
                               timeout=cfg["agent"]["timeout_sec"])
            stream, res["agent_exit"] = p.stdout, p.returncode
        except subprocess.TimeoutExpired as e:
            stream, res["agent_exit"] = (e.stdout or b"").decode(), "timeout"
        trial_dir = args.out / f"{task}-{args.leg}-{n}"
        trial_dir.mkdir(parents=True, exist_ok=True)
        transcript = trial_dir / "transcript.jsonl"
        transcript.write_text(stream, encoding="utf-8")
        events = []
        for line in stream.splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:  # a timeout can cut the last line
                pass
        done = next((e for e in events if e.get("type") == "result"), {})
        init = next((e for e in events if e.get("subtype") == "init"), None)
        if init is None:
            if not done:
                raise RuntimeError("no result event in the agent stream")
            raise RuntimeError(f"no init event: {done.get('errors') or done.get('startup_failure_reason')}")
        assert_isolated(init, "default", ROUNDS[rnd]["tools"])
        res["model"], res["final_message"] = init["model"], done.get("result")
        if done.get("is_error"):
            raise RuntimeError(f"agent run failed: {str(done.get('result'))[:300]}")
        u = done.get("usage")  # no result event (a timeout): tokens and cost are unknown, null
        res["input_tokens"] = u and sum(u.get(k, 0) for k in
                                        ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
        res["output_tokens"] = u and u.get("output_tokens", 0)
        res["cost_usd"] = done.get("total_cost_usd")
        check_env = {**env, "PYTHONPATH": str(HERE), "RAND_EVAL_TRANSCRIPT": str(transcript)}
        if u:
            check_env["RAND_EVAL_TOKENS"] = str(res["input_tokens"] + res["output_tokens"])
        try:
            check = subprocess.run([str(py), str(task_dir / "tests" / "check.py")], cwd=cwd, env=check_env,
                                   stdin=subprocess.DEVNULL, capture_output=True, text=True,
                                   timeout=cfg["verifier"]["timeout_sec"])
            res["check_output"] = check.stdout
            res["first_failure"] = None if check.returncode == 0 else check.stdout.partition("\n")[0]
            res.update({k: v for k, v in check_result(check.stdout).items() if k not in res})
            res["passed"] = check.returncode == 0
        except subprocess.TimeoutExpired:
            res["check_output"] = "timeout"
    except Exception as e:
        res["error"] = f"{type(e).__name__}: {e}"
    finally:
        res["duration_s"] = round(time.monotonic() - t0, 1)
        if res.get("round") == "discovery":
            res["passed"] = None
        shutil.rmtree(work, ignore_errors=True)
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--task", nargs="+", required=True, help="folder names under evals/tasks")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--rand-engine", default="rand-engine", help="pip requirement or wheel path")
    ap.add_argument("--leg", required=True, choices=["pypi", "wheel"], help="install leg, named in the results")
    ap.add_argument("--model", required=True, help="pinned full model id")
    ap.add_argument("--out", required=True, type=Path, help="result directory, outside the repo")
    args = ap.parse_args()
    out = args.out.resolve()
    if out == REPO or REPO in out.parents:
        ap.error(f"--out must be outside the repo ({REPO})")
    out.mkdir(parents=True, exist_ok=True)
    args.out = out
    errors = 0
    for task in args.task:
        for n in range(1, args.k + 1):
            res = run_trial(task, n, args)
            (out / f"{task}-{args.leg}-{n}.json").write_text(json.dumps(res, indent=2, ensure_ascii=False),
                                                             encoding="utf-8")
            print(f"{task} trial {n}: passed={res['passed']} error={res.get('error')}")
            errors += "error" in res
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
