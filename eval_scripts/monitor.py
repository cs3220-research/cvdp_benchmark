#!/usr/bin/env python3

"""
Monitor CVDP Harbor benchmark progress across model runs.

Auto-detects agents and models from output/ and displays a live
progress table showing completed trials, pass/fail rates, and errors.

Usage:
    python3 eval_scripts/monitor.py                          # auto-detect all agents+models, poll every 60s
    python3 eval_scripts/monitor.py --agent terminus-2       # filter to one agent
    python3 eval_scripts/monitor.py --interval 30            # poll every 30s
    python3 eval_scripts/monitor.py --once                   # print once and exit
    python3 eval_scripts/monitor.py --models openrouter/openai/gpt-5.4 openrouter/anthropic/claude-opus-4.6
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_ROOT = REPO_ROOT / "output"


def sanitize_path_component(name: str) -> str:
    return name.replace("/", "__")


def unsanitize_path_component(name: str) -> str:
    return name.replace("__", "/")


def short_model_name(model: str) -> str:
    """Extract the short model name from a full model ID."""
    parts = model.split("/")
    return parts[-1] if parts else model


def discover_agents() -> list[str]:
    """Auto-discover all agents with output directories."""
    if not OUTPUT_ROOT.is_dir():
        return []
    return [
        entry.name
        for entry in sorted(OUTPUT_ROOT.iterdir())
        if entry.is_dir()
    ]


def discover_models(agent_dir: Path) -> list[str]:
    """Auto-discover all models with output directories under an agent."""
    if not agent_dir.is_dir():
        return []
    return [
        unsanitize_path_component(entry.name)
        for entry in sorted(agent_dir.iterdir())
        if entry.is_dir()
    ]


@dataclass
class TrialStats:
    total: int = 0
    done: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0


@dataclass
class RunStatus:
    agent: str
    model: str
    short_name: str
    run_dir: str = ""
    stats: TrialStats = field(default_factory=TrialStats)
    elapsed: str = ""
    status: str = "WAITING"
    started_at: datetime | None = None


def parse_run_timestamp(name: str) -> datetime | None:
    """Parse a run directory name like '2026-03-11__19-34-50' to datetime."""
    try:
        return datetime.strptime(name, "%Y-%m-%d__%H-%M-%S")
    except ValueError:
        return None


def find_latest_run_dir(model_dir: Path) -> Path | None:
    """Find the latest timestamp subdirectory in a model output dir."""
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


def get_start_time(run_dir: Path) -> datetime | None:
    """Get start time from config.json job_name or directory name."""
    config_path = run_dir / "config.json"
    if config_path.exists():
        try:
            with config_path.open() as f:
                config = json.load(f)
            job_name = config.get("job_name", "")
            ts = parse_run_timestamp(job_name)
            if ts is not None:
                return ts
        except (json.JSONDecodeError, OSError):
            pass
    return parse_run_timestamp(run_dir.name)


def scan_trials(run_dir: Path) -> TrialStats:
    """Scan trial subdirectories and tally results."""
    stats = TrialStats()
    for entry in run_dir.iterdir():
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        stats.total += 1
        result_path = entry / "result.json"
        exception_path = entry / "exception.txt"
        if not result_path.exists():
            continue
        stats.done += 1
        if exception_path.exists():
            stats.errors += 1
        try:
            with result_path.open() as f:
                result = json.load(f)
            vr = result.get("verifier_result")
            reward = vr.get("rewards", {}).get("reward") if isinstance(vr, dict) else None
            if reward is not None:
                if float(reward) >= 1.0:
                    stats.passed += 1
                else:
                    stats.failed += 1
            else:
                stats.failed += 1
        except (json.JSONDecodeError, OSError):
            stats.errors += 1
    return stats


def format_elapsed(start: datetime | None) -> str:
    """Format elapsed time as 'Xh Ym Zs' or 'Ym Zs'."""
    if start is None:
        return "-"
    delta = datetime.now() - start
    total_seconds = int(delta.total_seconds())
    if total_seconds < 0:
        return "-"
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if hours > 0:
        return f"{hours}h {minutes:02d}m {seconds:02d}s"
    return f"{minutes}m {seconds:02d}s"


def is_job_finished(run_dir: Path) -> bool:
    """Check if the job-level result.json exists (job complete)."""
    return (run_dir / "result.json").exists()


def gather_statuses(agents: list[str], models: list[str] | None) -> list[RunStatus]:
    """Gather status for all agent/model combinations."""
    statuses = []
    for agent in agents:
        agent_dir = OUTPUT_ROOT / agent
        agent_models = models if models else discover_models(agent_dir)
        for model in agent_models:
            sanitized = sanitize_path_component(model)
            model_dir = agent_dir / sanitized
            rs = RunStatus(agent=agent, model=model, short_name=short_model_name(model))

            run_dir = find_latest_run_dir(model_dir)
            if run_dir is None:
                rs.status = "WAITING"
                statuses.append(rs)
                continue

            rs.run_dir = run_dir.name
            rs.started_at = get_start_time(run_dir)
            rs.elapsed = format_elapsed(rs.started_at)
            rs.stats = scan_trials(run_dir)

            if is_job_finished(run_dir):
                rs.status = "DONE"
            elif rs.stats.total > 0:
                rs.status = "RUNNING"
            else:
                rs.status = "STARTING"

            statuses.append(rs)
    return statuses


def print_table(statuses: list[RunStatus], poll_interval: int) -> None:
    """Print the progress table."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.system("clear" if os.name != "nt" else "cls")

    print(f"CVDP Harbor Benchmark Monitor \u2014 {now}")
    print(f"Polling every {poll_interval}s (Ctrl+C to exit)\n")

    # Show agent column only when multiple agents are present
    agents_shown = {rs.agent for rs in statuses}
    show_agent = len(agents_shown) > 1

    if show_agent:
        header = (
            f"{'Agent':<16} {'Model':<26} {'Run Dir':<22} "
            f"{'Total':>5} {'Done':>5} {'Pass':>5} {'Fail':>5} {'Err':>5}  "
            f"{'Elapsed':>12}  {'Status':<8}"
        )
    else:
        agent_label = next(iter(agents_shown)) if agents_shown else "?"
        print(f"Agent: {agent_label}\n")
        header = (
            f"{'Model':<26} {'Run Dir':<22} "
            f"{'Total':>5} {'Done':>5} {'Pass':>5} {'Fail':>5} {'Err':>5}  "
            f"{'Elapsed':>12}  {'Status':<8}"
        )
    sep = "\u2500" * len(header)
    print(header)
    print(sep)

    totals = TrialStats()
    for rs in statuses:
        s = rs.stats
        totals.total += s.total
        totals.done += s.done
        totals.passed += s.passed
        totals.failed += s.failed
        totals.errors += s.errors

        cols = (
            f"{s.total:>5} {s.done:>5} {s.passed:>5} {s.failed:>5} {s.errors:>5}  "
            f"{rs.elapsed:>12}  {rs.status:<8}"
        )
        if show_agent:
            print(f"{rs.agent:<16} {rs.short_name:<26} {rs.run_dir:<22} {cols}")
        else:
            print(f"{rs.short_name:<26} {rs.run_dir:<22} {cols}")

    print(sep)
    total_prefix = f"{'':16} " if show_agent else ""
    print(
        f"{total_prefix}{'TOTAL':<26} {'':<22} "
        f"{totals.total:>5} {totals.done:>5} {totals.passed:>5} {totals.failed:>5} {totals.errors:>5}"
    )
    print()


def all_finished(statuses: list[RunStatus]) -> bool:
    return all(rs.status == "DONE" for rs in statuses)


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor CVDP Harbor benchmark progress.")
    parser.add_argument(
        "--interval", type=int, default=60, help="Polling interval in seconds (default: 60)"
    )
    parser.add_argument(
        "--once", action="store_true", help="Print status once and exit."
    )
    parser.add_argument(
        "--agent",
        type=str,
        default=None,
        help="Agent name (e.g. terminus-2). Default: auto-detect all agents.",
    )
    parser.add_argument(
        "--models",
        nargs="*",
        default=None,
        help="Model list (full OpenRouter IDs). Default: auto-detect from output dir.",
    )
    args = parser.parse_args()

    agents = [args.agent] if args.agent else discover_agents()
    if not agents:
        print("No agents found. Specify --agent or wait for output directories to appear.")
        sys.exit(1)

    def handle_signal(sig, frame):
        print("\n\nFinal status:")
        statuses = gather_statuses(agents, args.models)
        print_table(statuses, args.interval)
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    while True:
        statuses = gather_statuses(agents, args.models)
        print_table(statuses, args.interval)

        if args.once:
            break

        if all_finished(statuses):
            print("All jobs finished.")
            # break

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
