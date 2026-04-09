---
description:
  Default flags and conventions for running the test harness (bin/run-test.py)
---

# Harness Defaults

## Model

Always use `--model opus` unless explicitly told otherwise.

## Running a single prompt

```bash
python3 bin/run-test.py --project gemini-cli --prompt-id <id> --variant with --model opus
python3 bin/run-test.py --project gemini-cli --prompt-id <id> --variant without --model opus
```

## Output

Results go to `outputs/{project}/prompt-{N}/` with:

- `prompt.md` — the prompt text
- `with-context-db.md` — agent solution (with context-db)
- `without-context-db.md` — agent solution (without context-db)
- `metrics.json` — cost, tokens, timing, first-edit time

Raw JSON also saved to `results/{timestamp}/`.

See also:

- [../gemini-cli/hooks.md](../gemini-cli/hooks.md) — hook system gotchas and
  event reference (test prompts target hook implementations)
- [../gemini-cli/architecture.md](../gemini-cli/architecture.md) — monorepo
  package map and subsystem entry points
