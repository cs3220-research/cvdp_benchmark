#!/usr/bin/env python3

"""
Orchestrate running Harbor's Terminus-2 agent on CVDP benchmark tasks.

Reads OPENROUTER_KEY from .env, discovers tasks from the Harbor registry,
and launches `harbor run` with Terminus-2 against all (or a subset of) tasks.

Usage:
    # Run all 92 tasks with default model
    python run_harbor_terminus2.py

    # Run a single task for testing
    python run_harbor_terminus2.py --task-name "cvdp_agentic_64b66b_codec_0001"

    # Run first N tasks
    python run_harbor_terminus2.py --n-tasks 5

    # Use a different model
    python run_harbor_terminus2.py --model openrouter/anthropic/claude-sonnet-4

    # Adjust concurrency and attempts
    python run_harbor_terminus2.py --n-concurrent 8 --n-attempts 3
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_REGISTRY = SCRIPT_DIR / "harbor_output" / "registry.local.json"
DEFAULT_DATASET = "cvdp_v1.0.4_agentic_code_generation_no_commercial@1.0"
DEFAULT_MODEL = "openrouter/openai/gpt-4o-mini"
DEFAULT_AGENT = "terminus-2"
DEFAULT_ENV_FILE = SCRIPT_DIR / ".env"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "output"


def sanitize_path_component(name: str) -> str:
    return name.replace("/", "__")


def load_env(env_path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not env_path.exists():
        return env
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()
    return env


def resolve_api_key(env_vars: dict[str, str]) -> str:
    for candidate in ("OPENROUTER_API_KEY", "OPENROUTER_KEY"):
        value = os.environ.get(candidate) or env_vars.get(candidate)
        if value:
            return value
    raise SystemExit(
        "No OpenRouter API key found. Set OPENROUTER_API_KEY in .env or environment."
    )


def list_tasks(registry_path: Path, dataset: str) -> list[str]:
    dataset_name = dataset.split("@")[0]
    with registry_path.open() as f:
        registry = json.load(f)
    for ds in registry:
        if ds["name"] == dataset_name:
            return [t["name"] for t in ds["tasks"]]
    raise SystemExit(f"Dataset '{dataset_name}' not found in {registry_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Terminus-2 agent on CVDP Harbor benchmark tasks."
    )
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=DEFAULT_REGISTRY,
        help=f"Path to Harbor registry JSON (default: {DEFAULT_REGISTRY})",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=DEFAULT_DATASET,
        help=f"Harbor dataset name@version (default: {DEFAULT_DATASET})",
    )
    parser.add_argument(
        "--agent",
        type=str,
        default=DEFAULT_AGENT,
        help=f"Harbor agent name (default: {DEFAULT_AGENT})",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"Model name for the agent (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Root output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--task-name",
        type=str,
        default=None,
        help="Run a single task by name (supports glob patterns).",
    )
    parser.add_argument(
        "--exclude-task-name",
        type=str,
        default=None,
        help="Exclude tasks by name (supports glob patterns).",
    )
    parser.add_argument(
        "--n-tasks",
        type=int,
        default=None,
        help="Limit to the first N tasks.",
    )
    parser.add_argument(
        "--n-concurrent",
        type=int,
        default=2,
        help="Number of concurrent trials (default: 4).",
    )
    parser.add_argument(
        "--n-attempts",
        type=int,
        default=1,
        help="Number of attempts per trial (default: 1).",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=1,
        help="Max retries on transient errors (default: 1).",
    )
    parser.add_argument(
        "--job-name",
        type=str,
        default=None,
        help="Custom job name (default: auto-generated timestamp).",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=DEFAULT_ENV_FILE,
        help=f"Path to .env file (default: {DEFAULT_ENV_FILE})",
    )
    parser.add_argument(
        "--agent-kwargs",
        type=str,
        nargs="*",
        default=[],
        help="Extra agent kwargs as key=value pairs (e.g. max_turns=200 temperature=0.5).",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable Harbor debug logging."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the harbor command without executing.",
    )
    return parser.parse_args()


def build_command(args: argparse.Namespace) -> list[str]:
    cmd = [
        "harbor",
        "run",
        "--agent",
        args.agent,
        "--model",
        args.model,
        "--registry-path",
        str(args.registry_path),
        "--dataset",
        args.dataset,
        "--env",
        "docker",
        "--n-concurrent",
        str(args.n_concurrent),
        "--n-attempts",
        str(args.n_attempts),
        "--max-retries",
        str(args.max_retries),
        "--jobs-dir",
        str(args.jobs_dir),
    ]

    if args.job_name:
        cmd.extend(["--job-name", args.job_name])

    if args.task_name:
        cmd.extend(["--task-name", args.task_name])

    if args.exclude_task_name:
        cmd.extend(["--exclude-task-name", args.exclude_task_name])

    if args.n_tasks is not None:
        cmd.extend(["--n-tasks", str(args.n_tasks)])

    for kv in args.agent_kwargs:
        cmd.extend(["--ak", kv])

    if args.debug:
        cmd.append("--debug")

    return cmd


def print_summary(jobs_dir: Path, job_name: str | None) -> None:
    if job_name:
        result_path = jobs_dir / job_name / "result.json"
    else:
        subdirs = sorted(jobs_dir.iterdir()) if jobs_dir.exists() else []
        if not subdirs:
            return
        result_path = subdirs[-1] / "result.json"

    if not result_path.exists():
        print(f"\nNo result.json found at {result_path}")
        return

    with result_path.open() as f:
        result = json.load(f)

    print(f"\n{'=' * 60}")
    print(f"Results: {result_path}")
    print(f"{'=' * 60}")

    stats = result.get("stats", {})
    n_total = stats.get("n_trials", 0)
    n_errors = stats.get("n_errors", 0)

    for eval_name, eval_data in stats.get("evals", {}).items():
        print(f"\nEval: {eval_name}")
        print(f"  Trials:    {eval_data.get('n_trials', 0)}")
        print(f"  Errors:    {eval_data.get('n_errors', 0)}")

        for metric in eval_data.get("metrics", []):
            mean = metric.get("mean")
            if mean is not None:
                print(f"  Mean:      {mean:.3f}")

        reward_stats = eval_data.get("reward_stats", {}).get("reward", {})
        n_passed = 0
        n_failed = 0
        for reward_val, trial_ids in reward_stats.items():
            count = len(trial_ids)
            if float(reward_val) > 0:
                n_passed += count
            else:
                n_failed += count

        print(f"  Passed:    {n_passed}")
        print(f"  Failed:    {n_failed}")
        if n_passed + n_failed > 0:
            print(f"  Pass rate: {n_passed / (n_passed + n_failed):.1%}")

        exceptions = eval_data.get("exception_stats", {})
        if exceptions:
            print(f"  Exceptions:")
            for exc_type, trial_ids in exceptions.items():
                print(f"    {exc_type}: {len(trial_ids)}")

    print(f"\nTotal: {n_total} trials, {n_errors} errors")
    print(f"Duration: {result.get('started_at', '?')} -> {result.get('finished_at', '?')}")


def main() -> None:
    args = parse_args()

    env_vars = load_env(args.env_file)
    api_key = resolve_api_key(env_vars)

    # Build output path: output/{agent_name}/{model_name}/
    # Harbor will create the timestamp subdirectory inside this.
    agent_dir = sanitize_path_component(args.agent)
    model_dir = sanitize_path_component(args.model)
    args.jobs_dir = args.output_dir / agent_dir / model_dir

    tasks = list_tasks(args.registry_path, args.dataset)
    n_selected = args.n_tasks if args.n_tasks is not None else len(tasks)
    if args.task_name:
        n_selected = f"matching '{args.task_name}'"

    print(f"CVDP Harbor Benchmark Runner")
    print(f"  Registry:    {args.registry_path}")
    print(f"  Dataset:     {args.dataset}")
    print(f"  Total tasks: {len(tasks)}")
    print(f"  Running:     {n_selected}")
    print(f"  Agent:       {args.agent}")
    print(f"  Model:       {args.model}")
    print(f"  Concurrency: {args.n_concurrent}")
    print(f"  Attempts:    {args.n_attempts}")
    print(f"  Output:      {args.jobs_dir}")
    print()

    cmd = build_command(args)
    run_env = {**os.environ, "OPENROUTER_API_KEY": api_key}

    if args.dry_run:
        safe_cmd = " ".join(cmd)
        print(f"OPENROUTER_API_KEY=*** {safe_cmd}")
        return

    print(f"Running: {' '.join(cmd)}")
    print(f"{'=' * 60}\n")

    try:
        proc = subprocess.run(cmd, env=run_env)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(130)

    print_summary(args.jobs_dir, args.job_name)
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()
