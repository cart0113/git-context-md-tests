#!/usr/bin/env python3
"""
Test harness for comparing Claude Code performance with and without context-db.

Runs test prompts via `claude -p` in both subfolders, captures JSON output,
and compares token cost, duration, and tool call counts.

Usage:
    python3 bin/run-test.py --difficulty easy --model sonnet --runs 1
    python3 bin/run-test.py --difficulty all --model haiku --runs 3
    python3 bin/run-test.py --difficulty medium --prompt-id rate-limiter-dependency
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
RESULTS_DIR = PROJECT_ROOT / "results"

FOLDERS = {
    "with": PROJECT_ROOT / "with-context-db",
    "without": PROJECT_ROOT / "without-context-db",
}


def reset_folder(folder: Path) -> None:
    """Reset any file changes the agent made, preserving .claude/ and context-db/."""
    subprocess.run(
        ["git", "checkout", "--", str(folder)],
        cwd=PROJECT_ROOT,
        capture_output=True,
    )
    # Also clean up any untracked files the agent created
    subprocess.run(
        ["git", "clean", "-fd", str(folder)],
        cwd=PROJECT_ROOT,
        capture_output=True,
    )


def load_prompts(difficulty: str) -> list[dict]:
    """Load prompts for a given difficulty level."""
    if difficulty == "all":
        prompts = []
        for level in ("easy", "medium", "hard"):
            prompts.extend(load_prompts(level))
        return prompts

    path = PROMPTS_DIR / f"{difficulty}.json"
    if not path.exists():
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        data = json.load(f)

    for item in data:
        item["difficulty"] = difficulty
    return data


def run_claude(prompt: str, cwd: Path, model: str, budget: float) -> dict:
    """Run a single claude -p invocation and return parsed JSON result."""
    cmd = [
        "claude",
        "-p", prompt,
        "--output-format", "json",
        "--model", model,
        "--no-session-persistence",
        "--dangerously-skip-permissions",
    ]

    if budget > 0:
        cmd.extend(["--max-budget-usd", str(budget)])


    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return {
            "error": "non-zero exit",
            "returncode": result.returncode,
            "stderr": result.stderr[:500],
        }

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {
            "error": "invalid JSON",
            "stdout_preview": result.stdout[:500],
        }


def extract_metrics(raw: dict) -> dict:
    """Pull the metrics we care about from Claude's JSON output."""
    if "error" in raw:
        return {"error": raw["error"]}

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
    }


def judge_solutions(prompt: str, what_it_tests: str, with_result: str,
                    without_result: str, model: str) -> dict:
    """Use Claude to judge solution quality for both variants."""
    judge_prompt = f"""You are judging two solutions to the same coding task.
Rate each solution on a 1-10 scale across three dimensions:

1. **Correctness** — Does it solve the task correctly? Would it work?
2. **Architecture** — Does it follow the project's patterns and conventions?
3. **Completeness** — Does it handle edge cases, cleanup, testing as asked?

## Task
{prompt}

## What this tests
{what_it_tests}

## Solution A (with context-db)
{with_result[:8000]}

## Solution B (without context-db)
{without_result[:8000]}

Respond in EXACTLY this JSON format, nothing else:
{{"solution_a": {{"correctness": N, "architecture": N, "completeness": N, "notes": "brief"}}, "solution_b": {{"correctness": N, "architecture": N, "completeness": N, "notes": "brief"}}}}"""

    cmd = [
        "claude", "-p", judge_prompt,
        "--output-format", "json",
        "--model", model,
        "--no-session-persistence",
        "--dangerously-skip-permissions",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        raw = json.loads(result.stdout)
        # The result text should be JSON — parse it
        judge_text = raw.get("result", "")
        # Try to extract JSON from the result
        start = judge_text.find("{")
        end = judge_text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(judge_text[start:end])
    except Exception as e:
        return {"error": str(e)}

    return {"error": "could not parse judge response"}


def print_comparison(results: list[dict]) -> None:
    """Print a formatted comparison table."""
    print("\n" + "=" * 100)
    print(f"{'PROMPT':<30} {'VARIANT':<10} {'COST':>8} {'TOKENS IN':>10} "
          f"{'TOKENS OUT':>10} {'TURNS':>6} {'TIME (s)':>9} {'QUALITY':>8}")
    print("=" * 100)

    for entry in results:
        prompt_id = entry["prompt_id"]
        difficulty = entry["difficulty"]

        for variant in ("with", "without"):
            metrics = entry.get(variant, {})
            if "error" in metrics:
                print(f"{prompt_id:<30} {variant:<10} {'ERROR':>8} "
                      f"{metrics['error']}")
                continue

            cost = f"${metrics['cost_usd']:.4f}"
            time_s = f"{metrics['duration_ms'] / 1000:.1f}"

            # Get quality score from judgment
            quality = ""
            judgment = entry.get("judgment", {})
            if "error" not in judgment:
                key = "solution_a" if variant == "with" else "solution_b"
                scores = judgment.get(key, {})
                if scores:
                    avg = (scores.get("correctness", 0)
                           + scores.get("architecture", 0)
                           + scores.get("completeness", 0)) / 3
                    quality = f"{avg:.1f}/10"

            print(f"{prompt_id:<30} {variant:<10} {cost:>8} "
                  f"{metrics['input_tokens']:>10,} "
                  f"{metrics['output_tokens']:>10,} "
                  f"{metrics['num_turns']:>6} "
                  f"{time_s:>9} "
                  f"{quality:>8}")

        # Print delta row
        w = entry.get("with", {})
        wo = entry.get("without", {})
        if "error" not in w and "error" not in wo:
            cost_diff = w.get("cost_usd", 0) - wo.get("cost_usd", 0)
            token_diff = (w.get("input_tokens", 0) + w.get("output_tokens", 0)) - \
                         (wo.get("input_tokens", 0) + wo.get("output_tokens", 0))
            turn_diff = w.get("num_turns", 0) - wo.get("num_turns", 0)
            time_diff = (w.get("duration_ms", 0) - wo.get("duration_ms", 0)) / 1000

            sign = lambda v: f"+{v}" if v > 0 else str(v)
            print(f"  [{difficulty}] delta         {'':>10} "
                  f"{'':>8} {sign(token_diff):>10} "
                  f"{'':>10} {sign(turn_diff):>6} "
                  f"{sign(round(time_diff, 1)):>9}")

        print("-" * 100)

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
        "--difficulty",
        choices=["easy", "medium", "hard", "all"],
        default="easy",
        help="Prompt difficulty level (default: easy)",
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
    parser.add_argument(
        "--skip-judge",
        action="store_true",
        help="Skip LLM judging of solution quality",
    )
    parser.add_argument(
        "--judge-model",
        default=None,
        help="Model for judging (defaults to same as --model)",
    )
    args = parser.parse_args()

    if args.judge_model is None:
        args.judge_model = args.model

    prompts = load_prompts(args.difficulty)

    if args.prompt_id:
        prompts = [p for p in prompts if p["id"] == args.prompt_id]
        if not prompts:
            print(f"Error: prompt ID '{args.prompt_id}' not found", file=sys.stderr)
            sys.exit(1)

    variants = ["with", "without"] if args.variant == "both" else [args.variant]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RESULTS_DIR / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Test run: {timestamp}")
    budget_str = f"${args.budget}/run" if args.budget > 0 else "no limit"
    print(f"Model: {args.model}  |  Budget: {budget_str}  |  Runs: {args.runs}")
    print(f"Prompts: {len(prompts)}  |  Variants: {', '.join(variants)}")
    print(f"Results: {run_dir}\n")

    if args.dry_run:
        for prompt in prompts:
            for variant in variants:
                print(f"  Would run: [{variant}] {prompt['id']} "
                      f"({prompt['difficulty']})")
        return

    all_results = []

    for run_num in range(1, args.runs + 1):
        if args.runs > 1:
            print(f"\n--- Run {run_num}/{args.runs} ---\n")

        run_results = []

        for prompt_info in prompts:
            entry = {
                "prompt_id": prompt_info["id"],
                "difficulty": prompt_info["difficulty"],
                "prompt": prompt_info["prompt"],
                "model": args.model,
                "run": run_num,
                "timestamp": datetime.now().isoformat(),
            }

            for variant in variants:
                folder = FOLDERS[variant]
                reset_folder(folder)
                print(f"Running [{variant}] {prompt_info['id']} "
                      f"({prompt_info['difficulty']})...", end=" ", flush=True)

                raw = run_claude(prompt_info["prompt"], folder, args.model, args.budget)
                metrics = extract_metrics(raw)
                entry[variant] = metrics
                entry[f"{variant}_raw"] = raw

                if "error" in metrics:
                    print(f"ERROR: {metrics['error']}")
                else:
                    print(f"${metrics['cost_usd']:.4f} | "
                          f"{metrics['num_turns']} turns | "
                          f"{metrics['duration_ms'] / 1000:.1f}s")

            # Save solution text to files
            for variant in variants:
                metrics = entry.get(variant, {})
                if "error" not in metrics and metrics.get("result_text"):
                    solution_file = run_dir / f"{prompt_info['id']}_{variant}.md"
                    with open(solution_file, "w") as f:
                        f.write(f"# {prompt_info['id']} — {variant}\n\n")
                        f.write(metrics["result_text"])

            # Judge solutions if both variants ran successfully
            if (not args.skip_judge
                    and len(variants) == 2
                    and "error" not in entry.get("with", {"error": True})
                    and "error" not in entry.get("without", {"error": True})):
                print(f"Judging [{prompt_info['id']}]...", end=" ", flush=True)
                judgment = judge_solutions(
                    prompt_info["prompt"],
                    prompt_info.get("what_it_tests", ""),
                    entry["with"].get("result_text", ""),
                    entry["without"].get("result_text", ""),
                    args.judge_model,
                )
                entry["judgment"] = judgment
                if "error" not in judgment:
                    a = judgment.get("solution_a", {})
                    b = judgment.get("solution_b", {})
                    a_avg = (a.get("correctness", 0) + a.get("architecture", 0)
                             + a.get("completeness", 0)) / 3
                    b_avg = (b.get("correctness", 0) + b.get("architecture", 0)
                             + b.get("completeness", 0)) / 3
                    print(f"with={a_avg:.1f}/10  without={b_avg:.1f}/10")
                else:
                    print(f"ERROR: {judgment['error']}")

            run_results.append(entry)

        all_results.extend(run_results)
        print_comparison(run_results)

    # Save results
    results_file = run_dir / "results.json"
    with open(results_file, "w") as f:
        # Don't save _raw in the summary (too large) — save separately
        summary = []
        for entry in all_results:
            clean = {k: v for k, v in entry.items() if not k.endswith("_raw")}
            summary.append(clean)

        json.dump(summary, f, indent=2)

    # Save raw results separately for debugging
    raw_file = run_dir / "raw_results.json"
    with open(raw_file, "w") as f:
        json.dump(all_results, f, indent=2)

    # Save judgment summary
    judgments = [{
        "prompt_id": e["prompt_id"],
        "difficulty": e["difficulty"],
        "judgment": e.get("judgment", {}),
    } for e in all_results if "judgment" in e]
    if judgments:
        judge_file = run_dir / "judgments.json"
        with open(judge_file, "w") as f:
            json.dump(judgments, f, indent=2)

    print(f"\nResults saved to {results_file}")

    # If multiple runs, show aggregated stats
    if args.runs > 1 and len(variants) == 2:
        print("\n" + "=" * 60)
        print("AGGREGATED RESULTS (mean across runs)")
        print("=" * 60)

        prompt_ids = list(dict.fromkeys(e["prompt_id"] for e in all_results))
        for pid in prompt_ids:
            entries = [e for e in all_results if e["prompt_id"] == pid]
            for variant in variants:
                costs = [e[variant]["cost_usd"] for e in entries
                         if "error" not in e.get(variant, {"error": True})]
                turns = [e[variant]["num_turns"] for e in entries
                         if "error" not in e.get(variant, {"error": True})]
                if costs:
                    mean_cost = sum(costs) / len(costs)
                    mean_turns = sum(turns) / len(turns)
                    print(f"  {pid:<30} {variant:<10} "
                          f"avg ${mean_cost:.4f}  avg {mean_turns:.1f} turns  "
                          f"(n={len(costs)})")


if __name__ == "__main__":
    main()
