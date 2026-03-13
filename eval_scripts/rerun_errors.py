#!/usr/bin/env python3

"""
Rerun erroring tasks from a previous CVDP Harbor benchmark run.

Reads previous run results, identifies tasks that had exceptions (and did not
pass), creates filtered registries, and launches reruns via run_harbor_terminus2.py.

Usage:
    python eval_scripts/rerun_errors.py --dry-run                    # preview what would rerun
    python eval_scripts/rerun_errors.py                              # rerun all models with errors
    python eval_scripts/rerun_errors.py --model openrouter/openai/gpt-5.4
    python eval_scripts/rerun_errors.py --include-passed-errors      # also rerun tasks that errored but still passed
    python eval_scripts/rerun_errors.py --n-concurrent 2             # lower concurrency
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_ROOT = REPO_ROOT / "output"
HARBOR_OUTPUT = REPO_ROOT / "harbor_output"
DEFAULT_REGISTRY = HARBOR_OUTPUT / "registry.local.json"
DEFAULT_AGENT = "terminus-2"
DEFAULT_DATASET = "cvdp_v1.0.4_agentic_code_generation_no_commercial"


def sanitize_path_component(name: str) -> str:
    return name.replace("/", "__")


def unsanitize_path_component(name: str) -> str:
    return name.replace("__", "/")


def short_model_name(model: str) -> str:
    parts = model.split("/")
    return parts[-1] if parts else model


def parse_run_timestamp(name: str) -> datetime | None:
    try:
        return datetime.strptime(name, "%Y-%m-%d__%H-%M-%S")
    except ValueError:
        return None


def find_latest_run_dir(model_dir: Path) -> Path | None:
    if not model_dir.is_dir():
        return None
    candidates = []
    for entry in model_dir.iterdir():
        if entry.is_dir():
            ts = parse_run_timestamp(entry.name)
            if ts is not None:
                candidates.append((ts, entry))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def discover_models(agent_dir: Path) -> list[str]:
    if not agent_dir.is_dir():
        return []
    return [
        unsanitize_path_component(entry.name)
        for entry in sorted(agent_dir.iterdir())
        if entry.is_dir()
    ]


def get_erroring_trial_ids(
    run_dir: Path,
    include_passed: bool = False,
) -> dict[str, list[str]]:
    """Return {exception_type: [trial_id, ...]} for trials that need reruns.

    By default, excludes trials that errored but still passed (reward 1.0).
    """
    result_path = run_dir / "result.json"
    if not result_path.exists():
        print(f"  WARNING: No result.json in {run_dir}", file=sys.stderr)
        return {}

    with result_path.open() as f:
        data = json.load(f)

    evals = data.get("stats", {}).get("evals", {})
    if not evals:
        return {}

    # There's typically one eval entry
    eval_data = next(iter(evals.values()))

    exception_stats = eval_data.get("exception_stats", {})
    if not exception_stats:
        return {}

    # Collect all exception trial IDs
    all_exception_ids: dict[str, str] = {}  # trial_id -> exception_type
    for exc_type, trial_ids in exception_stats.items():
        for tid in trial_ids:
            all_exception_ids[tid] = exc_type

    # Collect passed trial IDs
    passed_ids: set[str] = set()
    if not include_passed:
        reward_stats = eval_data.get("reward_stats", {}).get("reward", {})
        passed_ids = set(reward_stats.get("1.0", []))

    # Filter: only trials that errored AND did not pass
    result: dict[str, list[str]] = {}
    for tid, exc_type in all_exception_ids.items():
        if tid not in passed_ids:
            result.setdefault(exc_type, []).append(tid)

    return result


def resolve_task_names(run_dir: Path, trial_ids: list[str]) -> list[str]:
    """Map trial IDs (directory names) to full task names by reading trial result.json."""
    task_names = []
    for tid in trial_ids:
        trial_dir = run_dir / tid
        result_path = trial_dir / "result.json"
        if result_path.exists():
            try:
                with result_path.open() as f:
                    trial_data = json.load(f)
                task_name = trial_data.get("task_name")
                if task_name:
                    task_names.append(task_name)
                    continue
            except (json.JSONDecodeError, OSError):
                pass
        # Fallback: try to reconstruct from trial ID (strip the hash suffix)
        # Trial IDs look like "cvdp_agentic_foo_0001__ABC1234"
        parts = tid.rsplit("__", 1)
        if len(parts) == 2:
            print(f"  WARNING: Could not read result.json for {tid}, using prefix: {parts[0]}", file=sys.stderr)
            task_names.append(parts[0])
        else:
            print(f"  WARNING: Could not resolve task name for trial {tid}", file=sys.stderr)
    return task_names


def create_filtered_registry(
    original_registry: Path,
    task_names: list[str],
    output_path: Path,
    dataset_name: str,
) -> int:
    """Create a filtered registry.json containing only the specified tasks.

    Returns the number of tasks included.
    """
    with original_registry.open() as f:
        registry = json.load(f)

    task_name_set = set(task_names)
    filtered_registry = []

    for ds in registry:
        if ds["name"] != dataset_name:
            continue
        filtered_tasks = [t for t in ds["tasks"] if t["name"] in task_name_set]
        if filtered_tasks:
            filtered_ds = {**ds, "tasks": filtered_tasks}
            filtered_registry.append(filtered_ds)

    with output_path.open("w") as f:
        json.dump(filtered_registry, f, indent=2)
        f.write("\n")

    n_tasks = sum(len(ds["tasks"]) for ds in filtered_registry)
    return n_tasks


def print_dry_run(
    model: str,
    run_dir: Path,
    erroring_by_type: dict[str, list[str]],
    task_names: list[str],
) -> None:
    """Print a summary of what would be rerun."""
    print(f"\n{'=' * 60}")
    print(f"Model: {model}")
    print(f"Source run: {run_dir}")
    print(f"Erroring tasks to rerun: {len(task_names)}")
    print()

    for exc_type, trial_ids in sorted(erroring_by_type.items()):
        print(f"  {exc_type} ({len(trial_ids)}):")
        for tid in sorted(trial_ids):
            print(f"    - {tid}")

    print()
    print(f"  Task names:")
    for name in sorted(task_names):
        print(f"    - {name}")


def launch_rerun(
    model: str,
    registry_path: Path,
    n_concurrent: int,
    extra_args: list[str],
    agent: str,
) -> subprocess.Popen:
    """Launch run_harbor_terminus2.py for a single model and return the Popen."""
    cmd = [
        sys.executable,
        str(REPO_ROOT / "run_harbor_terminus2.py"),
        "--model", model,
        "--registry-path", str(registry_path),
        "--agent", agent,
        "--n-concurrent", str(n_concurrent),
        *extra_args,
    ]
    print(f"\nLaunching: {' '.join(cmd)}")
    return subprocess.Popen(cmd)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rerun erroring tasks from previous CVDP Harbor benchmark runs."
    )
    parser.add_argument(
        "--agent", type=str, default=DEFAULT_AGENT,
        help=f"Agent name for output dir discovery (default: {DEFAULT_AGENT})",
    )
    parser.add_argument(
        "--model", type=str, default=None,
        help="Filter to a single model (full OpenRouter ID). Default: all discovered models.",
    )
    parser.add_argument(
        "--source-dir", type=Path, default=OUTPUT_ROOT,
        help=f"Root output directory to scan (default: {OUTPUT_ROOT})",
    )
    parser.add_argument(
        "--registry-path", type=Path, default=DEFAULT_REGISTRY,
        help=f"Original registry path (default: {DEFAULT_REGISTRY})",
    )
    parser.add_argument(
        "--dataset", type=str, default=DEFAULT_DATASET,
        help=f"Dataset name in registry (default: {DEFAULT_DATASET})",
    )
    parser.add_argument(
        "--include-passed-errors", action="store_true",
        help="Also rerun tasks that errored but got reward 1.0.",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would rerun without launching.",
    )
    parser.add_argument(
        "--n-concurrent", type=int, default=4,
        help="Concurrency per model rerun (default: 4).",
    )
    parser.add_argument(
        "--sequential", action="store_true",
        help="Run models one at a time instead of in parallel.",
    )
    return parser.parse_known_args()


def main() -> None:
    args, extra_args = parse_args()

    agent_dir = args.source_dir / args.agent
    if not agent_dir.is_dir():
        print(f"Agent directory not found: {agent_dir}", file=sys.stderr)
        sys.exit(1)

    # Discover models
    if args.model:
        models = [args.model]
    else:
        models = discover_models(agent_dir)

    if not models:
        print("No models found.", file=sys.stderr)
        sys.exit(1)

    print(f"CVDP Harbor Error Rerun")
    print(f"  Agent:      {args.agent}")
    print(f"  Source dir: {args.source_dir}")
    print(f"  Models:     {', '.join(short_model_name(m) for m in models)}")
    print(f"  Include passed errors: {args.include_passed_errors}")

    # Gather rerun info per model
    rerun_plans: list[dict] = []

    for model in models:
        sanitized = sanitize_path_component(model)
        model_dir = agent_dir / sanitized
        run_dir = find_latest_run_dir(model_dir)

        if run_dir is None:
            print(f"\n  {short_model_name(model)}: No run directory found, skipping.")
            continue

        erroring_by_type = get_erroring_trial_ids(
            run_dir, include_passed=args.include_passed_errors
        )

        if not erroring_by_type:
            print(f"\n  {short_model_name(model)}: No erroring tasks to rerun.")
            continue

        # Flatten all erroring trial IDs
        all_erroring_ids = []
        for ids in erroring_by_type.values():
            all_erroring_ids.extend(ids)

        # Resolve to full task names
        task_names = resolve_task_names(run_dir, all_erroring_ids)

        if not task_names:
            print(f"\n  {short_model_name(model)}: Could not resolve any task names, skipping.")
            continue

        # Deduplicate (shouldn't happen, but be safe)
        task_names = list(dict.fromkeys(task_names))

        rerun_plans.append({
            "model": model,
            "run_dir": run_dir,
            "erroring_by_type": erroring_by_type,
            "task_names": task_names,
        })

    if not rerun_plans:
        print("\nNothing to rerun.")
        return

    # Dry run: just print
    if args.dry_run:
        for plan in rerun_plans:
            print_dry_run(
                plan["model"], plan["run_dir"],
                plan["erroring_by_type"], plan["task_names"],
            )
        print(f"\n{'=' * 60}")
        print(f"Total: {sum(len(p['task_names']) for p in rerun_plans)} tasks across {len(rerun_plans)} models")
        return

    # Create filtered registries and launch
    processes: list[tuple[str, subprocess.Popen]] = []

    for plan in rerun_plans:
        model = plan["model"]
        task_names = plan["task_names"]
        short = short_model_name(model)

        # Create filtered registry
        registry_filename = f"registry.rerun.{sanitize_path_component(short)}.json"
        registry_path = HARBOR_OUTPUT / registry_filename
        n_tasks = create_filtered_registry(
            args.registry_path, task_names, registry_path, args.dataset,
        )
        print(f"\n  {short}: Created {registry_path} with {n_tasks} tasks")

        proc = launch_rerun(
            model=model,
            registry_path=registry_path,
            n_concurrent=args.n_concurrent,
            extra_args=extra_args,
            agent=args.agent,
        )

        if args.sequential:
            print(f"\n  Waiting for {short} to complete...")
            proc.wait()
            if proc.returncode != 0:
                print(f"  WARNING: {short} exited with code {proc.returncode}", file=sys.stderr)
        else:
            processes.append((short, proc))

    # Wait for parallel processes
    if processes:
        print(f"\nWaiting for {len(processes)} parallel reruns to complete...")
        for short, proc in processes:
            proc.wait()
            status = "OK" if proc.returncode == 0 else f"EXIT {proc.returncode}"
            print(f"  {short}: {status}")

    print("\nAll reruns complete.")


if __name__ == "__main__":
    main()
