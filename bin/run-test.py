#!/usr/bin/env python3
"""
Test harness for comparing Claude Code performance with and without context-db.

For each run, copies the source repo into results/ so the agent's edits stay on
disk for later inspection.  No in-place mutation of the canonical repos.

Usage:
    python3 bin/run-test.py --project fast-api --model opus
    python3 bin/run-test.py --project gemini-cli --prompt-id add-subagent-max-depth --variant with

Results land in:
    results/{project}/{prompt-id}/{model}/{variant}/{timestamp}/
        repo/           copied source with agent edits
        metrics.json    cost, tokens, timing
        result.md       agent's own summary
"""

import argparse
import json
import os
import shutil
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
    "fast-api": {
        "with": PROJECT_ROOT / "fast-api-with-context-db",
        "without": PROJECT_ROOT / "fast-api-without-context-db",
    },
    "gemini-cli": {
        "with": PROJECT_ROOT / "gemini-cli-with-context-db",
        "without": PROJECT_ROOT / "gemini-cli-without-context-db",
    },
}

# Dirs to skip when copying (large, not needed for judging)
COPY_SKIP = {"node_modules", ".git"}

EDIT_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}


def copy_repo(src: Path, dst: Path) -> None:
    """Copy source repo to destination, skipping node_modules and .git."""
    if dst.exists():
        shutil.rmtree(dst)

    def _ignore(directory, contents):
        return [c for c in contents if c in COPY_SKIP]

    shutil.copytree(src, dst, ignore=_ignore)

    # Initialize a fresh git repo so we can diff the agent's changes later
    subprocess.run(["git", "init"], cwd=dst, capture_output=True, text=True)
    subprocess.run(["git", "add", "-A"], cwd=dst, capture_output=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "clean baseline"],
        cwd=dst, capture_output=True, text=True,
        env={**os.environ,
             "GIT_AUTHOR_NAME": "harness", "GIT_AUTHOR_EMAIL": "harness@test",
             "GIT_COMMITTER_NAME": "harness", "GIT_COMMITTER_EMAIL": "harness@test"},
    )
    print(f"  Copied {src.name} -> {dst.relative_to(PROJECT_ROOT)}", flush=True)


def load_prompts(project: str) -> list[dict]:
    """Load prompts for a given project."""
    path = PROMPTS_DIR / project / "prompts.json"
    if not path.exists():
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def run_claude(prompt: str, cwd: Path, model: str, budget: float) -> dict:
    """Run claude -p with stream-json, printing live activity and capturing metrics."""
    cmd = [
        "claude", "-p", prompt,
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

    # Disable auto-memory so runs can't leak context to each other
    env = {**os.environ, "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}

    proc = subprocess.Popen(
        cmd, cwd=cwd, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )

    def drain_stderr():
        for line in proc.stderr:
            print(line, end="", file=sys.stderr, flush=True)

    stderr_thread = threading.Thread(target=drain_stderr, daemon=True)
    stderr_thread.start()

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
                        inp = block.get("input", {})
                        target = (inp.get("file_path") or inp.get("pattern")
                                  or inp.get("command", "") or "")
                        print(f"  {ts}  {tool} {target}", flush=True)
                    else:
                        print(f"  {ts}  {tool}", flush=True)
                elif btype == "text":
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


def print_summary(results: list[dict]) -> None:
    """Print a formatted summary table."""
    print("\n" + "=" * 105)
    print(f"{'PROMPT':<35} {'VARIANT':<10} {'COST':>8} "
          f"{'TURNS':>6} {'1ST EDIT':>9} {'TOTAL':>9}")
    print("=" * 105)

    for entry in results:
        prompt_id = entry["prompt_id"]
        for variant in ("with", "without"):
            metrics = entry.get(variant, {})
            if not metrics:
                continue
            if "error" in metrics:
                print(f"{prompt_id:<35} {variant:<10} {'ERROR':>8} "
                      f"{metrics['error']}")
                continue

            cost = f"${metrics['cost_usd']:.4f}"
            time_s = f"{metrics['duration_ms'] / 1000:.1f}s"
            fe = metrics.get("first_edit_seconds")
            fe_s = f"{fe:.0f}s" if fe else "n/a"

            print(f"{prompt_id:<35} {variant:<10} {cost:>8} "
                  f"{metrics['num_turns']:>6} "
                  f"{fe_s:>9} "
                  f"{time_s:>9}")

        print("-" * 105)


def main():
    parser = argparse.ArgumentParser(description="Context-db A/B test harness")
    parser.add_argument(
        "--project", choices=list(PROJECTS.keys()),
        default="fast-api",
    )
    parser.add_argument("--prompt-id", help="Run only a specific prompt by ID")
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--budget", type=float, default=0)
    parser.add_argument("--variant", choices=["with", "without", "both"], default="both")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project_config = PROJECTS[args.project]
    source_folders = {
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
    print()

    if args.dry_run:
        for prompt in prompts:
            for variant in variants:
                vname = "with-context-db" if variant == "with" else "without-context-db"
                dest = f"results/{args.project}/{prompt['id']}/{args.model}/{vname}/{timestamp}/"
                print(f"  Would run: {dest}")
        return

    harness_start = time.time()
    all_results = []

    for run_num in range(1, args.runs + 1):
        if args.runs > 1:
            print(f"\n--- Run {run_num}/{args.runs} ---\n")

        run_results = []

        for prompt_info in prompts:
            entry = {
                "prompt_id": prompt_info["id"],
                "prompt": prompt_info["prompt"],
                "model": args.model,
                "run": run_num,
            }

            print(f"\n{'─' * 80}")
            print(f"Prompt [{prompt_info['id']}]:")
            print(f"  {prompt_info['prompt'][:120]}")
            print(f"{'─' * 80}")

            # Save prompt text at the prompt-id level
            prompt_level_dir = RESULTS_DIR / args.project / prompt_info["id"]
            prompt_level_dir.mkdir(parents=True, exist_ok=True)
            with open(prompt_level_dir / "prompt.md", "w") as f:
                f.write(f"# {prompt_info['id']}\n\n{prompt_info['prompt']}\n")

            for variant in variants:
                variant_name = "with-context-db" if variant == "with" else "without-context-db"

                # results/{project}/{prompt-id}/{model}/{variant}/{timestamp}/
                run_dir = (RESULTS_DIR / args.project / prompt_info["id"]
                           / args.model / variant_name / timestamp)
                run_dir.mkdir(parents=True, exist_ok=True)

                # Copy source repo into run_dir/repo/
                src = source_folders[variant]
                repo_dir = run_dir / "repo"
                print(f"\n▶ [{variant_name}] {prompt_info['id']}", flush=True)
                copy_repo(src, repo_dir)

                # Run the agent
                raw = run_claude(prompt_info["prompt"], repo_dir, args.model, args.budget)
                metrics = extract_metrics(raw)
                entry[variant] = metrics

                if "error" in metrics:
                    print(f"  ✗ ERROR: {metrics['error']}")
                else:
                    fe = metrics.get("first_edit_seconds")
                    fe_str = f" | first edit: {fe:.0f}s" if fe else ""
                    print(f"  Done: ${metrics['cost_usd']:.4f} | "
                          f"{metrics['num_turns']} turns | "
                          f"{metrics['duration_ms'] / 1000:.1f}s"
                          f"{fe_str}")

                # Save result.md
                if "error" not in metrics and metrics.get("result_text"):
                    (run_dir / "result.md").write_text(metrics["result_text"])

                # Save metrics.json
                metrics_out = {
                    "timestamp": timestamp,
                    "model": args.model,
                    "variant": variant_name,
                    **{k: v for k, v in metrics.items() if k != "result_text"},
                }
                with open(run_dir / "metrics.json", "w") as f:
                    json.dump(metrics_out, f, indent=2)

                print(f"  Saved: {run_dir.relative_to(PROJECT_ROOT)}/", flush=True)

            run_results.append(entry)

        all_results.extend(run_results)
        print_summary(run_results)

    harness_elapsed = time.time() - harness_start
    minutes = int(harness_elapsed // 60)
    seconds = int(harness_elapsed % 60)
    print(f"\nTotal elapsed time: {minutes}m {seconds}s")


if __name__ == "__main__":
    main()
