# Agent evals

On-demand eval of how an agent uses rand-engine. Outside pytest, the `verify:` line and CI.

```bash
python evals/run.py --task e3-fix-by-error --k 3 \
  --rand-engine rand-engine==0.8.1 --model <full model id> --out ~/eval-results
```

- `--out` must be outside this repo; the runner refuses a path inside it. One JSON per trial: task, trial, passed, input and output tokens (input counts cache reads and writes), cost, duration, model id.
- `--rand-engine` is a pip requirement or a wheel path, installed into a fresh venv per trial; `--task` takes folder names under `evals/tasks/`.
- Each trial runs headless `claude -p` in a fresh temp directory with no settings sources, no MCP servers, no skills; the stream's init event is asserted and a leak fails the trial. Auth is whatever the caller's environment already holds; the runner never reads or stores it.
