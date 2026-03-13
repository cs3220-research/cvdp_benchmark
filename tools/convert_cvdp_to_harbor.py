#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Convert CVDP agentic datapoints into Harbor tasks.

This converter keeps the Harbor adaptation narrow:
- CVDP context and harness files are copied into Harbor `environment/`
- Harbor uses a plain Dockerfile task, not Docker Compose
- The original CVDP harness command(s) and env-file(s) are replayed by `tests/test.sh`
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
MERGE_IN_MEMORY_PATH = REPO_ROOT / "src" / "merge_in_memory.py"

_merge_spec = importlib.util.spec_from_file_location(
    "cvdp_merge_in_memory", MERGE_IN_MEMORY_PATH
)
if _merge_spec is None or _merge_spec.loader is None:
    raise RuntimeError(f"Unable to load merge helper from {MERGE_IN_MEMORY_PATH}")

_merge_module = importlib.util.module_from_spec(_merge_spec)
_merge_spec.loader.exec_module(_merge_module)
diff_apply = _merge_module.diff_apply


DEFAULT_OSS_SIM_IMAGE = os.environ.get("OSS_SIM_IMAGE", "ghcr.io/hdl/sim/osvb")


SOLVE_SH_TEMPLATE = """#!/usr/bin/env bash
set -euo pipefail

if [ -d /solution/files ]; then
  cp -R /solution/files/. /code/
fi
"""


@dataclass
class HarnessStep:
    service_name: str
    env_file: str | None
    working_dir: str | None
    command: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a CVDP agentic JSONL dataset into a Harbor dataset directory."
    )
    parser.add_argument(
        "input_jsonl",
        type=Path,
        help="Path to a CVDP JSONL dataset in agentic format.",
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        help="Output Harbor dataset directory.",
    )
    parser.add_argument(
        "--dataset-name",
        type=str,
        default=None,
        help="Harbor dataset name. Defaults to the JSONL stem.",
    )
    parser.add_argument(
        "--version",
        type=str,
        default="1.0",
        help="Harbor dataset version for generated registry files.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optionally convert only the first N datapoints.",
    )
    return parser.parse_args()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                rows.append(json.loads(stripped))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Failed to parse {path}:{line_number}: {exc}") from exc
    return rows


def ensure_agentic_rows(rows: list[dict[str, Any]], source: Path) -> None:
    if not rows:
        raise ValueError(f"No datapoints found in {source}")

    for row in rows:
        required = {"id", "categories", "context", "harness", "patch", "prompt"}
        missing = required - set(row)
        if missing:
            raise ValueError(
                f"Datapoint {row.get('id', '<unknown>')} is missing required fields: {sorted(missing)}"
            )


def apply_template_substitution(content: str) -> str:
    if content is None:
        return content
    return content.replace("__OSS_SIM_IMAGE__", DEFAULT_OSS_SIM_IMAGE)


def strip_inline_comment(value: str) -> str:
    in_single_quote = False
    in_double_quote = False
    escaped = False
    result: list[str] = []

    for char in value:
        if escaped:
            result.append(char)
            escaped = False
            continue
        if char == "\\":
            result.append(char)
            escaped = True
            continue
        if char == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
            result.append(char)
            continue
        if char == '"' and not in_single_quote:
            in_double_quote = not in_double_quote
            result.append(char)
            continue
        if char == "#" and not in_single_quote and not in_double_quote:
            break
        result.append(char)

    return "".join(result).rstrip()


def parse_harness_steps(raw_text: str, task_id: str) -> list[HarnessStep]:
    steps: list[HarnessStep] = []
    in_services = False
    service_indent: int | None = None
    current_service_name: str | None = None
    current_env_file: str | None = None
    current_working_dir: str | None = None
    current_command: str | None = None

    def flush_current() -> None:
        nonlocal current_service_name
        nonlocal current_env_file
        nonlocal current_working_dir
        nonlocal current_command

        if current_service_name is None:
            return
        if current_command is None:
            raise ValueError(
                f"Unable to parse service command for {current_service_name} in {task_id}"
            )
        steps.append(
            HarnessStep(
                service_name=current_service_name,
                env_file=current_env_file,
                working_dir=current_working_dir,
                command=current_command,
            )
        )
        current_service_name = None
        current_env_file = None
        current_working_dir = None
        current_command = None

    for raw_line in raw_text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))

        if stripped == "services:":
            in_services = True
            continue

        if not in_services:
            continue

        if service_indent is None:
            if indent > 0 and stripped.endswith(":") and not stripped.startswith("-"):
                service_indent = indent
                current_service_name = stripped[:-1].strip()
            continue

        if indent < service_indent:
            flush_current()
            break

        if indent == service_indent and stripped.endswith(":") and not stripped.startswith("-"):
            flush_current()
            current_service_name = stripped[:-1].strip()
            continue

        if current_service_name is None or indent <= service_indent or ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = strip_inline_comment(value.strip())
        if key == "env_file":
            current_env_file = value
        elif key == "working_dir":
            current_working_dir = value
        elif key == "command":
            current_command = value

    flush_current()

    if not steps:
        raise ValueError(f"Unable to parse any services from docker-compose.yml for {task_id}")

    return steps


def normalize_env_text(raw_text: str) -> dict[str, str]:
    env: dict[str, str] = {}
    for raw_line in raw_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()
    return env


def resolve_env_path(env_file: str | None) -> str | None:
    if env_file is None:
        return None
    cleaned = strip_inline_comment(env_file.strip())
    if not cleaned:
        return None
    if cleaned.startswith("/code/"):
        return cleaned
    if cleaned.startswith("./"):
        return f"/code/{cleaned[2:]}"
    if cleaned.startswith("/"):
        return cleaned
    return f"/code/{cleaned}"


def render_harbor_dockerfile(harness_files: dict[str, str]) -> str:
    original = harness_files.get("Dockerfile")
    if original:
        prefix = apply_template_substitution(original).rstrip()
    else:
        prefix = f"FROM {DEFAULT_OSS_SIM_IMAGE}"

    return (
        f"{prefix}\n\n"
        "# Harbor adaptation: copy the converted task workspace into /code.\n"
        "WORKDIR /code\n"
        "COPY . /code\n"
        "RUN chmod +x /code/cvdp_harness_env.sh\n"
        "RUN mkdir -p /code/rundir\n"
        "RUN [ -e /src ] || ln -s /code/src /src\n"
        "RUN [ -e /rundir ] || ln -s /code/rundir /rundir\n"
        "ENV HOME=/code/rundir\n"
        "RUN printf '. /code/cvdp_harness_env.sh\\n' >> /root/.bashrc\n"
    )


def render_env_loader_sh(
    env_sources: dict[str, dict[str, str]],
    default_env_path: str | None,
) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "",
        f'target_env="${{1:-{default_env_path or ""}}}"',
        "",
    ]

    if not env_sources:
        lines.append(":")
        lines.append("")
        return "\n".join(lines)

    keys_to_unset = sorted({key for values in env_sources.values() for key in values})
    if keys_to_unset:
        lines.append(f"unset {' '.join(keys_to_unset)} 2>/dev/null || true")
        lines.append("")

    lines.append('case "$target_env" in')
    for env_path in sorted(env_sources):
        lines.append(f"  {shlex.quote(env_path)})")
        for key in sorted(env_sources[env_path]):
            lines.append(f"    export {key}={shlex.quote(env_sources[env_path][key])}")
        lines.append("    ;;")
    lines.append('  "")')
    lines.append("    ;;")
    lines.append("  *)")
    lines.append('    echo "Unknown harness env file: $target_env" >&2')
    lines.append("    return 1 2>/dev/null || exit 1")
    lines.append("    ;;")
    lines.append("esac")
    lines.append("")
    return "\n".join(lines)


def render_test_sh(steps: list[HarnessStep]) -> str:
    lines = [
        "#!/usr/bin/env bash",
        "set -uo pipefail",
        "",
        "mkdir -p /logs/verifier",
        "mkdir -p /code/rundir",
        "mkdir -p /code/rundir/.cache",
        "mkdir -p /code/rundir/harness/.cache",
        "mkdir -p /rundir",
        "mkdir -p /rundir/.cache",
        "mkdir -p /rundir/harness/.cache",
        "",
        "status=0",
        "",
    ]

    for step in steps:
        env_path = resolve_env_path(step.env_file)
        working_dir = step.working_dir or "/code"
        lines.extend(
            [
                f'echo "Running service: {step.service_name}"',
                "if ! (",
                "  set -e",
            ]
        )
        if env_path:
            lines.append(f"  source /code/cvdp_harness_env.sh {shlex.quote(env_path)}")
        lines.extend(
            [
                f"  cd {shlex.quote(working_dir)}",
                f"  sh -lc {shlex.quote(step.command)}",
                "); then",
                "  status=1",
                "fi",
                "",
            ]
        )

    lines.extend(
        [
            'if [ "$status" -eq 0 ]; then',
            '  echo 1 > /logs/verifier/reward.txt',
            "else",
            '  echo 0 > /logs/verifier/reward.txt',
            "fi",
            "",
            'exit "$status"',
            "",
        ]
    )
    return "\n".join(lines)


def write_text(path: Path, content: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | 0o111)


def write_tree(base: Path, files: dict[str, str]) -> None:
    for relative_path, content in files.items():
        target = base / relative_path
        write_text(target, content)


def apply_cvdp_patch(original_content: str, patch_text: str) -> str:
    return diff_apply(original_content or "", patch_text)


def reconstruct_solution_files(row: dict[str, Any]) -> dict[str, str]:
    solution_files: dict[str, str] = {}
    context = row.get("context", {})

    for file_path, patch_text in row["patch"].items():
        if not patch_text:
            continue
        original_content = context.get(file_path, "")
        solution_files[file_path] = apply_cvdp_patch(original_content, patch_text)

    return solution_files


def render_instruction(row: dict[str, Any]) -> str:
    return f"{row['prompt'].rstrip()}\n"


def render_task_toml(row: dict[str, Any]) -> str:
    difficulty = row["categories"][1]
    cid = row["categories"][0]
    tags = json.dumps(["cvdp", "rtl", "harbor-converted", cid, difficulty])
    return f"""version = "1.0"

[metadata]
author_name = "NVIDIA"
author_email = "unknown"
difficulty = "{difficulty}"
category = "hardware_verification"
tags = {tags}
expert_time_estimate_min = 20.0
junior_time_estimate_min = 90.0

[verifier]
timeout_sec = 1200.0

[agent]
timeout_sec = 1200.0

[environment]
build_timeout_sec = 1200.0
cpus = 2
memory_mb = 4096
storage_mb = 10240

[verifier.env]

[solution.env]
"""


def task_dir_name(task_id: str) -> str:
    return task_id.lower()


def get_repo_root() -> Path | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
    except subprocess.CalledProcessError:
        return None

    return Path(result.stdout.strip())


def build_local_registry(
    dataset_name: str,
    version: str,
    description: str,
    task_dirs: list[Path],
) -> list[dict[str, Any]]:
    return [
        {
            "name": dataset_name,
            "version": version,
            "description": description,
            "tasks": [
                {
                    "name": task_dir.name,
                    "path": str(task_dir.resolve()),
                }
                for task_dir in task_dirs
            ],
        }
    ]


def build_remote_registry_template(
    dataset_name: str,
    version: str,
    description: str,
    task_dirs: list[Path],
) -> list[dict[str, Any]]:
    repo_root = get_repo_root()
    tasks: list[dict[str, Any]] = []

    for task_dir in task_dirs:
        if repo_root is not None:
            try:
                relative_path = task_dir.resolve().relative_to(repo_root.resolve())
                path_value = relative_path.as_posix()
            except ValueError:
                path_value = task_dir.name
        else:
            path_value = task_dir.name

        tasks.append(
            {
                "name": task_dir.name,
                "git_url": "__REPLACE_WITH_GIT_URL__",
                "git_commit_id": "__REPLACE_WITH_GIT_COMMIT__",
                "path": path_value,
            }
        )

    return [
        {
            "name": dataset_name,
            "version": version,
            "description": description,
            "tasks": tasks,
        }
    ]


def write_dataset_readme(
    output_dir: Path,
    dataset_name: str,
    version: str,
    input_jsonl: Path,
    task_count: int,
) -> None:
    readme = f"""# {dataset_name}

Converted from `{input_jsonl}` into Harbor task format.

- Version: `{version}`
- Tasks: `{task_count}`
- Source format: `CVDP agentic JSONL`

Local Harbor usage:

```bash
harbor run \\
  --registry-path {output_dir / "registry.local.json"} \\
  --dataset {dataset_name}@{version} \\
  --agent oracle \\
  --n-concurrent 1
```

Remote registry submission:

- Fill in `registry.remote.template.json` with the final git URL and commit.
- Publish the generated task directories in a git repository.
"""
    write_text(output_dir / "README.md", readme)


def convert_row(row: dict[str, Any], task_dir: Path) -> None:
    context_files = {
        relative_path: apply_template_substitution(content)
        for relative_path, content in row["context"].items()
    }
    harness_files = {
        relative_path: apply_template_substitution(content)
        for relative_path, content in row["harness"].items()
    }
    steps = parse_harness_steps(harness_files["docker-compose.yml"], row["id"])
    harness_files_without_special = {
        relative_path: content
        for relative_path, content in harness_files.items()
        if relative_path not in {"Dockerfile", "docker-compose.yml"}
    }

    env_sources: dict[str, dict[str, str]] = {}
    for step in steps:
        env_path = resolve_env_path(step.env_file)
        if env_path is None:
            continue
        relative_env_path = env_path.removeprefix("/code/")
        raw_env_text = harness_files.get(relative_env_path)
        if raw_env_text is None:
            raise ValueError(f"Missing harness env file {relative_env_path} for {row['id']}")
        env_sources[env_path] = normalize_env_text(raw_env_text)
    default_env_path = resolve_env_path(steps[0].env_file)

    solution_files = reconstruct_solution_files(row)

    write_text(task_dir / "instruction.md", render_instruction(row))
    write_text(task_dir / "task.toml", render_task_toml(row))
    write_tree(task_dir / "environment", context_files)
    write_tree(task_dir / "environment", harness_files_without_special)
    write_text(task_dir / "environment" / "Dockerfile", render_harbor_dockerfile(harness_files))
    write_text(
        task_dir / "environment" / "cvdp_harness_env.sh",
        render_env_loader_sh(env_sources, default_env_path),
        executable=True,
    )
    write_text(task_dir / "tests" / "test.sh", render_test_sh(steps), executable=True)
    if solution_files:
        write_text(task_dir / "solution" / "solve.sh", SOLVE_SH_TEMPLATE, executable=True)
        write_tree(task_dir / "solution" / "files", solution_files)

    # Fix known upstream bug: cocotb_tools.runner -> cocotb.runner
    task_env_src_dir = task_dir / "environment" / "src"
    if task_env_src_dir.is_dir():
        for py_file in task_env_src_dir.rglob("*.py"):
            content = py_file.read_text()
            if "cocotb_tools.runner" in content:
                py_file.write_text(content.replace("cocotb_tools.runner", "cocotb.runner"))


def main() -> None:
    args = parse_args()

    rows = read_jsonl(args.input_jsonl)
    ensure_agentic_rows(rows, args.input_jsonl)

    if args.limit is not None:
        rows = rows[: args.limit]

    dataset_name = args.dataset_name or args.input_jsonl.stem
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    task_dirs: list[Path] = []
    for row in rows:
        task_dir = output_dir / task_dir_name(row["id"])
        task_dirs.append(task_dir)
        convert_row(row, task_dir)

    description = f"Harbor conversion of {args.input_jsonl.name}"
    local_registry = build_local_registry(
        dataset_name=dataset_name,
        version=args.version,
        description=description,
        task_dirs=task_dirs,
    )
    remote_registry = build_remote_registry_template(
        dataset_name=dataset_name,
        version=args.version,
        description=description,
        task_dirs=task_dirs,
    )

    write_text(output_dir / "registry.local.json", json.dumps(local_registry, indent=2))
    write_text(
        output_dir / "registry.remote.template.json",
        json.dumps(remote_registry, indent=2),
    )
    write_dataset_readme(
        output_dir=output_dir,
        dataset_name=dataset_name,
        version=args.version,
        input_jsonl=args.input_jsonl,
        task_count=len(task_dirs),
    )

    print(f"Converted {len(task_dirs)} CVDP datapoints into Harbor tasks at {output_dir}")
    print(f"Local registry: {output_dir / 'registry.local.json'}")
    print(f"Remote template: {output_dir / 'registry.remote.template.json'}")


if __name__ == "__main__":
    main()
