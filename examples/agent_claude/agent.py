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


def sync_claude_auth():
    home_dir = expand_path(os.getenv("HOME", "/var/tmp/claude-home"))
    os.makedirs(os.path.join(home_dir, ".claude"), exist_ok=True)

    legacy_dir = expand_path(os.getenv("CLAUDE_AUTH_SOURCE_DIR", "/host_auth/.claude"))
    source_map = {
        ".claude.json": resolve_source_file("CLAUDE_AUTH_FILE", "/host_auth/.claude.json", "CLAUDE_AUTH_SOURCE_FILE"),
        ".claude/settings.json": resolve_source_file("CLAUDE_SETTINGS_FILE", os.path.join(legacy_dir, "settings.json")),
    }

    linked = []
    missing = []
    for rel_dest, src in source_map.items():
        dst = os.path.join(home_dir, rel_dest)
        if os.path.isfile(dst):
            linked.append(f"{rel_dest} (mounted directly)")
            continue
        if symlink_file(src, dst):
            linked.append(rel_dest)
        else:
            missing.append(rel_dest)

    if linked:
        print(f"[INFO] Claude auth/config ready: {', '.join(linked)}")
    if missing:
        print(f"[INFO] Claude files not found (skipped): {', '.join(missing)}")


def main():
    # Keep tool home writable outside mounted benchmark directories.
    os.environ["HOME"] = "/var/tmp/claude-home"
    os.environ["XDG_CONFIG_HOME"] = "/var/tmp/claude-home/.config"
    os.makedirs(os.environ["HOME"], exist_ok=True)
    os.makedirs(os.environ["XDG_CONFIG_HOME"], exist_ok=True)

    # Optional read-only host auth mounts wired into writable HOME.
    sync_claude_auth()

    effort_level = os.getenv("CLAUDE_CODE_EFFORT_LEVEL", "").strip().lower()
    if effort_level not in {"low", "medium", "high"}:
        if effort_level:
            print(f"[WARNING] Invalid CLAUDE_CODE_EFFORT_LEVEL '{effort_level}', defaulting to high")
        effort_level = "high"
    os.environ["CLAUDE_CODE_EFFORT_LEVEL"] = effort_level
    print(f"[INFO] Claude effort level: {effort_level}")

    if shutil.which("claude") is None:
        print("[ERROR] claude CLI not found in PATH")
        return 1

    prompt = read_prompt()
    if not prompt:
        print("[ERROR] Empty prompt in /code/prompt.json")
        return 1

    instruction = prompt

    cmd = [
        "claude",
        "-p",
        "--dangerously-skip-permissions",
        "--model",
        os.getenv("CLAUDE_MODEL", "opus"),
    ]
    max_turns = os.getenv("CLAUDE_MAX_TURNS", "").strip()
    if max_turns:
        cmd.extend(["--max-turns", max_turns])

    if env_truthy("CLAUDE_TRAJECTORY"):
        # Emit structured event stream (JSONL) with partial chunks.
        if "--output-format" not in cmd:
            cmd.extend(["--output-format", "stream-json"])
        if "--include-partial-messages" not in cmd:
            cmd.append("--include-partial-messages")
        if "--verbose" not in cmd:
            cmd.append("--verbose")

    extra_args = os.getenv("CLAUDE_EXEC_ARGS", "").strip()
    if extra_args:
        cmd.extend(shlex.split(extra_args))
    cmd.append(instruction)

    print(f"[INFO] Running: {' '.join(cmd[:-1])} <prompt>")
    result = subprocess.run(cmd, cwd="/code", check=False)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
