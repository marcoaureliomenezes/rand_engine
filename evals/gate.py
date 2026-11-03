"""Decide the agent-eval gate from trial JSONs.

Inputs: `--results DIR` (`{task}-{leg}-{n}.json`), `--tasks DIR` (`<task>/task.toml`), `--k N`.
`--calibrate` also writes `<results>/ceilings.json`.
Output: `FAIL ...` lines, then the usage table, on stdout.
Exit: 0 when every usage task passes; 1 otherwise. Calibrate exits 0 once written.
"""
import argparse
import json
import math
import statistics
import tomllib
from pathlib import Path

LEGS = ("pypi", "wheel")
PROBES = ("import", "pip", "network")
HEADER = "task | wheel | pypi | tokens | cost_usd | layer | surface"


def median(values):
    # Token counts are discrete: each count stands for an interval one token wide.
    return statistics.median_grouped(values, interval=1)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, required=True)
    ap.add_argument("--tasks", type=Path, required=True)
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--calibrate", action="store_true")
    a = ap.parse_args(argv)

    specs = {}
    for f in sorted(a.tasks.glob("*/task.toml")):
        cfg = tomllib.loads(f.read_text(encoding="utf-8"))
        specs[f.parent.name] = {"round": cfg.get("task", {}).get("round"),
                                "legs": cfg.get("task", {}).get("legs", []),
                                "ceiling": cfg.get("limits", {}).get("ceiling_tokens")}

    def read(name, leg, n):
        f = a.results / f"{name}-{leg}-{n}.json"
        if not f.exists():
            return None, f.name
        return json.loads(f.read_text(encoding="utf-8")), None

    fails, rows, ceilings, voided = [], [], {}, set()

    for leg in LEGS:
        seen, red = set(), False
        for name, s in specs.items():
            if s["round"] != "canary" or leg not in s["legs"]:
                continue
            for n in range(1, a.k + 1):
                data, missing = read(name, leg, n)
                if missing:
                    fails.append(f"FAIL canary {leg}: trial {n} missing file {missing}")
                    red = True
                    continue
                if data.get("error"):
                    fails.append(f"FAIL canary {leg}: trial {n} harness error: {data['error']}")
                    red = True
                seen |= {line[len("probe:"):] for line in (data.get("check_output") or "").splitlines()
                         if line.startswith("probe:")}
        lost = [p for p in PROBES if p not in seen]
        if lost:
            fails.append(f"FAIL canary {leg}: the sandbox blocked a probe, missing: {', '.join(lost)}")
            red = True
        if red:
            voided.add(leg)

    need = a.k // 2 + 1
    for name, s in specs.items():
        if s["round"] != "usage":
            continue
        raw, eff, cost, tokens, layers, surfaces = {}, {}, 0.0, [], set(), set()
        for leg in s["legs"]:
            raw[leg] = 0
            for n in range(1, a.k + 1):
                data, missing = read(name, leg, n)
                if missing:
                    fails.append(f"FAIL {name}: {leg} trial {n} missing file {missing}")
                    continue
                cost += data.get("cost_usd") or 0
                if data.get("error"):
                    fails.append(f"FAIL {name}: {leg} trial {n} harness error: {data['error']}")
                if data.get("passed") and not data.get("error"):
                    raw[leg] += 1
                    tokens.append(data["input_tokens"] + data["output_tokens"])
                else:
                    layers.add(data.get("layer"))
                    surfaces |= set(data.get("surfaces") or [])
            eff[leg] = 0 if leg in voided else raw[leg]

        wheel, pypi = eff.get("wheel", 0), eff.get("pypi", 0)
        if wheel < need:
            fails.append(f"FAIL {name}: wheel passed {wheel} of {a.k} (need {need})")
        elif wheel < pypi:
            fails.append(f"FAIL {name}: wheel passed {wheel} of {a.k}, below pypi {pypi} of {a.k}")
        if s["ceiling"] is None:
            fails.append(f"FAIL {name}: no ceiling_tokens in task.toml")
        if tokens:
            ceilings[name] = math.ceil(2 * median(tokens))
        layer = ", ".join(sorted(str(x) for x in layers if x is not None)) or "-"
        rows.append(f"{name} | {wheel} | {pypi} | {round(median(tokens)) if tokens else '-'} | "
                    f"{cost:.2f} | {layer} | {', '.join(sorted(surfaces)) or '-'}")

    if a.calibrate:
        (a.results / "ceilings.json").write_text(json.dumps(ceilings, indent=2, sort_keys=True), encoding="utf-8")
        print(HEADER)
        print("\n".join(rows))
        return 0

    for line in [*fails, HEADER, *rows]:
        print(line)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
