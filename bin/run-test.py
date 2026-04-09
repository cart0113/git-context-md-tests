#!/usr/bin/env python3
"""
Test harness for comparing Claude Code performance with and without context-db.

Runs test prompts via `claude -p` in both subfolders, captures JSON output,
and compares token cost, duration, and tool call counts.

Usage:
    python3 bin/run-test.py --project fastapi --model opus --runs 1
    python3 bin/run-test.py --project oddo --prompt-id add-dashed-border-shape
"""

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
RESULTS_DIR = PROJECT_ROOT / "results"

PROJECTS = {
    "fastapi": {
        "with": PROJECT_ROOT / "fast-api-with-context-db",
        "without": PROJECT_ROOT / "fast-api-without-context-db",
    },
    "oddo": {
        "with": PROJECT_ROOT / "od-do-with-context-db",
        "without": PROJECT_ROOT / "od-do-without-context-db",
    },
    "gemini-cli": {
        "with": PROJECT_ROOT / "gemini-cli-with-context-db",
        "without": PROJECT_ROOT / "gemini-cli-without-context-db",
    },
}


def reset_folder(folder: Path) -> None:
    """Reset folder to clean git state and verify it worked."""
    name = folder.name

    # 1. Hard reset tracked files
    r = subprocess.run(
        ["git", "checkout", "--", "."],
        cwd=folder, capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"  ⚠ git checkout failed in {name}: {r.stderr.strip()}", flush=True)

    # 2. Remove untracked files (preserve .claude, context-db, node_modules)
    r = subprocess.run(
        ["git", "clean", "-fd",
         "--exclude=.claude", "--exclude=context-db/",
         "--exclude=node_modules/"],
        cwd=folder, capture_output=True, text=True,
    )
    if r.returncode != 0:
        print(f"  ⚠ git clean failed in {name}: {r.stderr.strip()}", flush=True)

    # 3. Verify — git status should show nothing dirty (except excluded dirs)
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=folder, capture_output=True, text=True,
    )
    dirty = [
        line for line in r.stdout.strip().splitlines()
        if line and not any(x in line for x in [".claude", "context-db/", "node_modules/"])
    ]
    if dirty:
        print(f"  ✗ RESET FAILED — {name} still has dirty files:", flush=True)
        for line in dirty:
            print(f"    {line}", flush=True)
        sys.exit(1)
    else:
        print(f"  ✓ {name} reset to clean state", flush=True)


def load_prompts(project: str) -> list[dict]:
    """Load prompts for a given project."""
    path = PROMPTS_DIR / project / "prompts.json"
    if not path.exists():
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        return json.load(f)


EDIT_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}


def run_claude(prompt: str, cwd: Path, model: str, budget: float) -> dict:
    """Run claude -p with stream-json, printing live activity and capturing metrics."""
    cmd = [
        "claude",
        "-p", prompt,
        "--output-format", "stream-json",
        "--verbose",
        "--model", model,
        "--no-session-persistence",
        "--dangerously-skip-permissions",
    ]

    if budget > 0:
        cmd.extend(["--max-budget-usd", str(budget)])

    start_time = time.time()
    first_edit_seconds = None
    result_event = None

    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Stream stderr in background (for any warnings/errors)
    def drain_stderr():
        for line in proc.stderr:
            print(line, end="", file=sys.stderr, flush=True)

    stderr_thread = threading.Thread(target=drain_stderr, daemon=True)
    stderr_thread.start()

    # Read stream-json events from stdout line by line
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        etype = event.get("type", "")
        elapsed = time.time() - start_time

        if etype == "assistant":
            msg = event.get("message", {})
            for block in msg.get("content", []):
                btype = block.get("type", "")
                if btype == "tool_use":
                    tool = block.get("name", "")
                    ts = f"[{elapsed:6.1f}s]"
                    if tool in EDIT_TOOLS:
                        fpath = block.get("input", {}).get("file_path", "")
                        short = os.path.basename(fpath) if fpath else ""
                        if first_edit_seconds is None:
                            first_edit_seconds = elapsed
                            print(f"  {ts}  ** FIRST EDIT ** {tool} {short}", flush=True)
                        else:
                            print(f"  {ts}  {tool} {short}", flush=True)
                    elif tool in ("Read", "Glob", "Grep", "Bash"):
                        target = ""
                        inp = block.get("input", {})
                        target = (inp.get("file_path") or inp.get("pattern")
                                  or inp.get("command", "") or "")
                        print(f"  {ts}  {tool} {target}", flush=True)
                    else:
                        print(f"  {ts}  {tool}", flush=True)
                elif btype == "text":
                    # Show first 120 chars of text responses
                    text = block.get("text", "")
                    if text:
                        preview = text[:120].replace("\n", " ")
                        print(f"  [{elapsed:6.1f}s]  ... {preview}", flush=True)

        elif etype == "result":
            result_event = event

    proc.wait()
    stderr_thread.join(timeout=5)

    wall_seconds = time.time() - start_time

    if result_event is None:
        return {
            "error": "no result event in stream",
            "returncode": proc.returncode,
            "_wall_seconds": wall_seconds,
            "_first_edit_seconds": first_edit_seconds,
        }

    # Reshape result_event to match what extract_metrics expects
    result_event["_wall_seconds"] = wall_seconds
    result_event["_first_edit_seconds"] = first_edit_seconds
    return result_event


def extract_metrics(raw: dict) -> dict:
    """Pull the metrics we care about from Claude's JSON output."""
    if "error" in raw:
        return {
            "error": raw["error"],
            "wall_seconds": raw.get("_wall_seconds"),
            "first_edit_seconds": raw.get("_first_edit_seconds"),
        }

    usage = raw.get("usage", {})
    return {
        "cost_usd": raw.get("total_cost_usd", 0),
        "duration_ms": raw.get("duration_ms", 0),
        "duration_api_ms": raw.get("duration_api_ms", 0),
        "num_turns": raw.get("num_turns", 0),
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "cache_read_tokens": usage.get("cache_read_input_tokens", 0),
        "cache_create_tokens": usage.get("cache_creation_input_tokens", 0),
        "stop_reason": raw.get("stop_reason", ""),
        "result_text": raw.get("result", ""),
        "wall_seconds": raw.get("_wall_seconds"),
        "first_edit_seconds": raw.get("_first_edit_seconds"),
    }



def print_comparison(results: list[dict]) -> None:
    """Print a formatted comparison table."""
    print("\n" + "=" * 105)
    print(f"{'PROMPT':<30} {'VARIANT':<10} {'COST':>8} {'TOKENS IN':>10} "
          f"{'TOKENS OUT':>10} {'TURNS':>6} {'1ST EDIT':>9} {'TOTAL':>9}")
    print("=" * 105)

    for entry in results:
        prompt_id = entry["prompt_id"]

        for variant in ("with", "without"):
            metrics = entry.get(variant, {})
            if not metrics:
                continue
            if "error" in metrics:
                print(f"{prompt_id:<30} {variant:<10} {'ERROR':>8} "
                      f"{metrics['error']}")
                continue

            cost = f"${metrics['cost_usd']:.4f}"
            time_s = f"{metrics['duration_ms'] / 1000:.1f}"
            fe = metrics.get("first_edit_seconds")
            fe_s = f"{fe:.0f}s" if fe else "—"

            print(f"{prompt_id:<30} {variant:<10} {cost:>8} "
                  f"{metrics['input_tokens']:>10,} "
                  f"{metrics['output_tokens']:>10,} "
                  f"{metrics['num_turns']:>6} "
                  f"{fe_s:>9} "
                  f"{time_s:>9}")

        # Print delta row
        w = entry.get("with", {})
        wo = entry.get("without", {})
        if "error" not in w and "error" not in wo:
            cost_diff = w.get("cost_usd", 0) - wo.get("cost_usd", 0)
            token_diff = (w.get("input_tokens", 0) + w.get("output_tokens", 0)) - \
                         (wo.get("input_tokens", 0) + wo.get("output_tokens", 0))
            turn_diff = w.get("num_turns", 0) - wo.get("num_turns", 0)
            time_diff = (w.get("duration_ms", 0) - wo.get("duration_ms", 0)) / 1000

            # First-edit delta
            fe_w = w.get("first_edit_seconds")
            fe_wo = wo.get("first_edit_seconds")
            if fe_w and fe_wo:
                fe_diff = f"{fe_w - fe_wo:+.0f}s"
            else:
                fe_diff = ""

            sign = lambda v: f"+{v}" if v > 0 else str(v)
            print(f"  delta                        {'':>10} "
                  f"{'':>8} {sign(token_diff):>10} "
                  f"{'':>10} {sign(turn_diff):>6} "
                  f"{fe_diff:>9} "
                  f"{sign(round(time_diff, 1)):>9}")

        print("-" * 105)

    # Summary
    with_costs = [e["with"]["cost_usd"] for e in results
                  if "error" not in e.get("with", {"error": True})]
    without_costs = [e["without"]["cost_usd"] for e in results
                     if "error" not in e.get("without", {"error": True})]

    if with_costs and without_costs:
        print(f"\nTotal cost  — with: ${sum(with_costs):.4f}  "
              f"without: ${sum(without_costs):.4f}  "
              f"delta: ${sum(with_costs) - sum(without_costs):+.4f}")


def main():
    parser = argparse.ArgumentParser(description="Context-db A/B test harness")
    parser.add_argument(
        "--project",
        choices=list(PROJECTS.keys()),
        default="fastapi",
        help="Which project to test (default: fastapi)",
    )
    parser.add_argument(
        "--prompt-id",
        help="Run only a specific prompt by ID",
    )
    parser.add_argument(
        "--model",
        default="sonnet",
        help="Claude model alias (default: sonnet)",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of runs per prompt (default: 1)",
    )
    parser.add_argument(
        "--budget",
        type=float,
        default=0,
        help="Max budget per run in USD (default: 0 = no limit)",
    )
    parser.add_argument(
        "--variant",
        choices=["with", "without", "both"],
        default="both",
        help="Which variant to run (default: both)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would run without executing",
    )
    args = parser.parse_args()

    project_config = PROJECTS[args.project]
    folders = {
        "with": project_config["with"],
        "without": project_config["without"],
    }
    prompts = load_prompts(args.project)

    if args.prompt_id:
        prompts = [p for p in prompts if p["id"] == args.prompt_id]
        if not prompts:
            print(f"Error: prompt ID '{args.prompt_id}' not found", file=sys.stderr)
            sys.exit(1)

    variants = ["with", "without"] if args.variant == "both" else [args.variant]

    timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%Mm")

    print(f"Test run: {timestamp}")
    budget_str = f"${args.budget}/run" if args.budget > 0 else "no limit"
    print(f"Model: {args.model}  |  Budget: {budget_str}  |  Runs: {args.runs}")
    print(f"Prompts: {len(prompts)}  |  Variants: {', '.join(variants)}")
    print(f"Results: results/{args.project}/\n")

    if args.dry_run:
        for prompt in prompts:
            for variant in variants:
                print(f"  Would run: [{variant}] {prompt['id']} "
                      f"({prompt['id']})")
        return

    harness_start = time.time()
    all_results = []

    for run_num in range(1, args.runs + 1):
        if args.runs > 1:
            print(f"\n--- Run {run_num}/{args.runs} ---\n")

        run_results = []

        for prompt_idx, prompt_info in enumerate(prompts):
            entry = {
                "prompt_id": prompt_info["id"],
                "prompt": prompt_info["prompt"],
                "model": args.model,
                "run": run_num,
                "timestamp": datetime.now().isoformat(),
            }

            # Print the prompt being tested
            print(f"\n{'─' * 80}")
            print(f"Prompt [{prompt_info['id']}]:")
            print(f"  {prompt_info['prompt']}")
            print(f"{'─' * 80}")

            # Result dir: results/{project}/{prompt-id}/
            prompt_dir = RESULTS_DIR / args.project / prompt_info["id"]
            prompt_dir.mkdir(parents=True, exist_ok=True)

            # Save the prompt text (once)
            with open(prompt_dir / "prompt.md", "w") as f:
                f.write(f"# {prompt_info['id']}\n\n{prompt_info['prompt']}\n")

            for variant in variants:
                folder = folders[variant]
                reset_folder(folder)
                print(f"\n▶ Running [{variant}] {prompt_info['id']} ...",
                      flush=True)

                raw = run_claude(prompt_info["prompt"], folder, args.model, args.budget)
                metrics = extract_metrics(raw)
                entry[variant] = metrics
                entry[f"{variant}_raw"] = raw

                if "error" in metrics:
                    print(f"  ✗ ERROR: {metrics['error']}")
                else:
                    fe = metrics.get("first_edit_seconds")
                    fe_str = f" | first edit: {fe:.0f}s" if fe else ""
                    print(f"  ✓ Done: ${metrics['cost_usd']:.4f} | "
                          f"{metrics['num_turns']} turns | "
                          f"{metrics['duration_ms'] / 1000:.1f}s"
                          f"{fe_str}")

                # Save result .md and metrics — one file per variant+model+timestamp
                variant_name = "with-context-db" if variant == "with" else "without-context-db"
                prefix = f"{timestamp}_{args.model}_{variant_name}"

                if "error" not in metrics and metrics.get("result_text"):
                    result_file = prompt_dir / f"{prefix}.md"
                    with open(result_file, "w") as f:
                        f.write(metrics["result_text"])
                    print(f"  Saved: {result_file.relative_to(PROJECT_ROOT)}")

                metrics_out = {
                    "timestamp": timestamp,
                    "model": args.model,
                    "variant": variant_name,
                    **{k: v for k, v in metrics.items() if k != "result_text"},
                }
                with open(prompt_dir / f"{prefix}_metrics.json", "w") as f:
                    json.dump(metrics_out, f, indent=2)

            run_results.append(entry)

        all_results.extend(run_results)
        print_comparison(run_results)

    # Print total time
    harness_elapsed = time.time() - harness_start
    minutes = int(harness_elapsed // 60)
    seconds = int(harness_elapsed % 60)
    print(f"\nResults saved to results/{args.project}/")
    print(f"Total elapsed time: {minutes}m {seconds}s")


if __name__ == "__main__":
    main()
