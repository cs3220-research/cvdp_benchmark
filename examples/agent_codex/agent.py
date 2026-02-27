#!/usr/bin/env python3

# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import os
import shlex
import shutil
import subprocess
import sys


def read_prompt(prompt_file="/code/prompt.json"):
    with open(prompt_file, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data.get("prompt", "")


def expand_path(path):
    return os.path.expandvars(os.path.expanduser(path))


def symlink_file(source_file, dest_file):
    source_file = expand_path(source_file)
    dest_file = expand_path(dest_file)
    if not os.path.isfile(source_file):
        return False
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
    if os.path.lexists(dest_file):
        os.remove(dest_file)
    os.symlink(source_file, dest_file)
    return True


def resolve_source_file(primary_env, default_path, legacy_env=None):
    primary = os.getenv(primary_env, "").strip()
    if primary:
        return expand_path(primary)
    if legacy_env:
        legacy = os.getenv(legacy_env, "").strip()
        if legacy:
            return expand_path(legacy)
    return expand_path(default_path)


def env_truthy(name):
    value = os.getenv(name, "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def sync_codex_auth():
    home_dir = expand_path(os.getenv("HOME", "/var/tmp/codex-home"))
    dest_dir = os.path.join(home_dir, ".codex")
    os.makedirs(dest_dir, exist_ok=True)

    legacy_source_dir = expand_path(os.getenv("CODEX_AUTH_SOURCE", "/host_auth/.codex"))
    source_map = {
        "auth.json": resolve_source_file("CODEX_AUTH_FILE", os.path.join(legacy_source_dir, "auth.json"), "CODEX_AUTH_SOURCE_FILE"),
        "config.toml": resolve_source_file("CODEX_CONFIG_FILE", os.path.join(legacy_source_dir, "config.toml")),
        "version.json": resolve_source_file("CODEX_VERSION_FILE", os.path.join(legacy_source_dir, "version.json")),
    }

    linked = []
    missing = []
    for name, src in source_map.items():
        dst = os.path.join(dest_dir, name)
        if os.path.isfile(dst):
            linked.append(f"{name} (mounted directly)")
            continue
        if symlink_file(src, dst):
            linked.append(name)
        else:
            missing.append(name)

    if linked:
        print(f"[INFO] Codex auth/config ready: {', '.join(linked)}")
    if missing:
        print(f"[INFO] Codex files not found (skipped): {', '.join(missing)}")


def add_codex_tuning_args(cmd):
    model = os.getenv("CODEX_MODEL", "").strip()
    if model:
        cmd.extend(["--model", model])

    reasoning_effort = os.getenv("CODEX_REASONING_EFFORT", "").strip()
    if reasoning_effort:
        escaped = reasoning_effort.replace("\\", "\\\\").replace('"', '\\"')
        cmd.extend(["-c", f'model_reasoning_effort="{escaped}"'])


def run_codex_json_result(cmd):
    process = subprocess.Popen(
        cmd,
        cwd="/code",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    events = []
    non_json_lines = 0
    assert process.stdout is not None
    for raw_line in process.stdout:
        line = raw_line.rstrip("\n")
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            non_json_lines += 1

    process.wait()

    summary = {
        "type": "result",
        "subtype": "codex_exec",
        "is_error": process.returncode != 0,
        "returncode": process.returncode,
        "event_count": len(events),
        "non_json_line_count": non_json_lines,
    }

    thread_started = next((event for event in events if event.get("type") == "thread.started"), None)
    if thread_started and thread_started.get("thread_id"):
        summary["thread_id"] = thread_started["thread_id"]

    turn_completed = [event for event in events if event.get("type") == "turn.completed"]
    if turn_completed:
        usage = turn_completed[-1].get("usage")
        if usage is not None:
            summary["usage"] = usage

    final_messages = []
    for event in events:
        if event.get("type") != "item.completed":
            continue
        item = event.get("item", {})
        if item.get("type") == "agent_message":
            text = item.get("text", "")
            if text:
                final_messages.append(text)
    if final_messages:
        summary["final_message"] = final_messages[-1]

    print(json.dumps(summary, ensure_ascii=True))
    return process.returncode


def main():
    # Keep tool home writable outside mounted benchmark directories.
    os.environ["HOME"] = "/var/tmp/codex-home"
    os.environ["XDG_CONFIG_HOME"] = "/var/tmp/codex-home/.config"
    os.makedirs(os.environ["HOME"], exist_ok=True)
    os.makedirs(os.environ["XDG_CONFIG_HOME"], exist_ok=True)

    # Optional read-only host auth mounts wired into writable HOME.
    sync_codex_auth()

    if shutil.which("codex") is None:
        print("[ERROR] codex CLI not found in PATH")
        return 1

    prompt = read_prompt()
    if not prompt:
        print("[ERROR] Empty prompt in /code/prompt.json")
        return 1

    instruction = prompt

    cmd = [
        "codex",
        "exec",
        "--skip-git-repo-check",
        "--dangerously-bypass-approvals-and-sandbox",
        "--ephemeral",
    ]
    add_codex_tuning_args(cmd)
    extra_args = os.getenv("CODEX_EXEC_ARGS", "").strip()
    if extra_args:
        cmd.extend(shlex.split(extra_args))

    json_mode = os.getenv("CODEX_JSON_MODE", "result").strip().lower()
    if json_mode not in {"result", "events", "off"}:
        json_mode = "result"

    # Trajectory mode takes precedence and emits raw event stream.
    if env_truthy("CODEX_TRAJECTORY"):
        json_mode = "events"

    if json_mode != "off" and "--json" not in cmd:
        cmd.append("--json")

    cmd.append(instruction)

    print(f"[INFO] Running: {' '.join(cmd[:-1])} <prompt>")
    if json_mode == "result":
        return run_codex_json_result(cmd)

    result = subprocess.run(cmd, cwd="/code", check=False)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
