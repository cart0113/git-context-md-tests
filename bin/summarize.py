#!/usr/bin/env python3
"""
Compare two test runs and produce a qualitative report.

Takes two run folders and writes a comparison markdown file.

Usage:
    python3 bin/summarize.py \\
        results/gemini-cli/add-subagent-max-depth/opus/with-context-db/2026-04-09_12h19m \\
        results/gemini-cli/add-subagent-max-depth/opus/without-context-db/2026-04-09_12h20m
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent


def get_diff(repo_dir: Path) -> str:
    """Get git diff of agent's changes in the copied repo."""
    if not repo_dir.exists():
        return "(repo not on disk)"

    r = subprocess.run(
        ["git", "diff", "HEAD"], cwd=repo_dir,
        capture_output=True, text=True,
    )
    diff = r.stdout.strip()
    if not diff:
        # Check for untracked files too
        r2 = subprocess.run(
            ["git", "diff", "HEAD", "--stat"], cwd=repo_dir,
            capture_output=True, text=True,
        )
        r3 = subprocess.run(
            ["git", "status", "--porcelain"], cwd=repo_dir,
            capture_output=True, text=True,
        )
        status = r3.stdout.strip()
        if status:
            # Show diff including untracked
            subprocess.run(["git", "add", "-A"], cwd=repo_dir, capture_output=True)
            r4 = subprocess.run(
                ["git", "diff", "--cached"], cwd=repo_dir,
                capture_output=True, text=True,
            )
            diff = r4.stdout.strip() or f"(untracked files only)\n{status}"
            subprocess.run(["git", "reset", "HEAD"], cwd=repo_dir, capture_output=True)
        else:
            diff = "(no changes)"
    return diff


def load_run(run_dir: Path) -> dict:
    """Load metrics, result text, and diff from a run folder."""
    metrics_path = run_dir / "metrics.json"
    result_path = run_dir / "result.md"
    repo_path = run_dir / "repo"

    if not metrics_path.exists():
        print(f"Error: {metrics_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(metrics_path) as f:
        metrics = json.load(f)

    result_text = result_path.read_text() if result_path.exists() else "(no result)"
    diff = get_diff(repo_path)

    return {
        "metrics": metrics,
        "result_text": result_text,
        "diff": diff,
        "dir": run_dir,
    }


def build_judge_prompt(prompt_text: str, run_a: dict, run_b: dict) -> str:
    """Build the prompt for the judge model."""
    def fmt_metrics(m: dict) -> str:
        fe = m.get('first_edit_seconds')
        fe_str = f"{fe:.0f}s" if fe else "n/a"
        return (f"- Cost: ${m.get('cost_usd', 0):.4f}\n"
                f"- Wall time: {m.get('wall_seconds', 0):.0f}s\n"
                f"- First edit: {fe_str}\n"
                f"- Turns: {m.get('num_turns', 0)}\n"
                f"- Output tokens: {m.get('output_tokens', 0):,}")

    a_label = run_a["metrics"].get("variant", "run A")
    b_label = run_b["metrics"].get("variant", "run B")

    # Truncate diffs if huge
    a_diff = run_a["diff"][:12000]
    b_diff = run_b["diff"][:12000]

    return f"""You are comparing two attempts at the same coding task.

## Task

{prompt_text}

## {a_label}

### Metrics
{fmt_metrics(run_a["metrics"])}

### Agent summary
{run_a["result_text"]}

### Code diff
```diff
{a_diff}
```

## {b_label}

### Metrics
{fmt_metrics(run_b["metrics"])}

### Agent summary
{run_b["result_text"]}

### Code diff
```diff
{b_diff}
```

## Instructions

Write a comparison report in markdown. Cover:

1. **Metrics** — table comparing cost, speed, first-edit time, turns
2. **Completeness** — did both find all the files that needed changing? Any missed integration points?
3. **Correctness** — are the implementations correct? Any bugs, wrong types, missing error handling?
4. **Approach** — how did each explore the codebase? Did context-db change the strategy?
5. **Bottom line** — one paragraph, no score, just a qualitative assessment of whether context-db helped and how

Be specific. Reference file names from the diffs. Do not pad with generic observations."""


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 bin/summarize.py <run-dir-A> <run-dir-B>",
              file=sys.stderr)
        sys.exit(1)

    dir_a = Path(sys.argv[1])
    dir_b = Path(sys.argv[2])

    if not dir_a.exists() or not dir_b.exists():
        print(f"Error: one or both directories don't exist", file=sys.stderr)
        sys.exit(1)

    print(f"Run A: {dir_a}")
    print(f"Run B: {dir_b}")

    run_a = load_run(dir_a)
    run_b = load_run(dir_b)

    # Find prompt text — walk up to the prompt-id level
    # Structure: results/{project}/{prompt-id}/{model}/{variant}/{timestamp}/
    prompt_id_dir = dir_a.parent.parent.parent
    prompt_path = prompt_id_dir / "prompt.md"
    prompt_text = prompt_path.read_text() if prompt_path.exists() else "(prompt not found)"

    judge_prompt = build_judge_prompt(prompt_text, run_a, run_b)

    print(f"Calling Claude to judge...", flush=True)
    r = subprocess.run(
        ["claude", "-p", judge_prompt,
         "--model", "sonnet",
         "--no-session-persistence",
         "--output-format", "text"],
        capture_output=True, text=True, timeout=180,
    )

    if r.returncode != 0:
        print(f"ERROR: judge call failed: {r.stderr[:300]}", file=sys.stderr)
        sys.exit(1)

    report = r.stdout.strip()

    # Build output filename: {ts_a}_{variant_a}_vs_{ts_b}_{variant_b}.md
    ts_a = run_a["metrics"].get("timestamp", dir_a.name)
    var_a = run_a["metrics"].get("variant", "a")
    ts_b = run_b["metrics"].get("timestamp", dir_b.name)
    var_b = run_b["metrics"].get("variant", "b")

    filename = f"{ts_a}_{var_a}_vs_{ts_b}_{var_b}.md"

    # Write at the model level: results/{project}/{prompt-id}/{model}/
    model_dir = dir_a.parent.parent  # up from variant/timestamp to model
    out_path = model_dir / filename

    out_path.write_text(
        f"# Comparison: {var_a} vs {var_b}\n\n"
        f"**Prompt:** {prompt_id_dir.name}  \n"
        f"**Model:** {model_dir.name}  \n"
        f"**Run A:** {dir_a}  \n"
        f"**Run B:** {dir_b}\n\n"
        f"---\n\n{report}\n"
    )

    print(f"\nReport saved: {out_path.relative_to(PROJECT_ROOT)}")
    print()
    print(report)


if __name__ == "__main__":
    main()
