#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATASET_FILE="${DATASET_FILE:-$REPO_ROOT/datasets/cvdp_v1.0.2_agentic_code_generation_no_commercial.jsonl}"
DATASET_URL="https://huggingface.co/datasets/nvidia/cvdp-benchmark-dataset/resolve/main/cvdp_v1.0.2_agentic_code_generation_no_commercial.jsonl?download=true"

N_SAMPLES="${N_SAMPLES:-5}"
K_THRESHOLD="${K_THRESHOLD:-1}"
THREADS="${THREADS:-4}"
PREFIX="${PREFIX:-work_claude_opus46_all92_n5_k1_t4}"

# Override if your Claude CLI uses a different model alias.
# `opus` maps to the latest available Opus tier in Claude Code.
CLAUDE_MODEL="${CLAUDE_MODEL:-opus}"
CLAUDE_MAX_TURNS="${CLAUDE_MAX_TURNS:-}"
CLAUDE_EXEC_ARGS="${CLAUDE_EXEC_ARGS:---output-format stream-json --verbose}"
CLAUDE_TRAJECTORY="${CLAUDE_TRAJECTORY:-0}"
CLAUDE_CODE_EFFORT_LEVEL="${CLAUDE_CODE_EFFORT_LEVEL:-high}"
CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING="${CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING:-}"

KEYCHAIN_SERVICE="${KEYCHAIN_SERVICE:-Claude Code-credentials}"
CLAUDE_AUTH_JSON="${CLAUDE_AUTH_JSON:-$HOME/.claude.json}"
CLAUDE_SETTINGS_JSON="${CLAUDE_SETTINGS_JSON:-$HOME/.claude/settings.json}"

append_csv() {
  local var_name="$1"
  local entry="$2"
  local current="${!var_name:-}"
  if [[ -z "$entry" ]]; then
    return
  fi
  if [[ -z "$current" ]]; then
    printf -v "$var_name" '%s' "$entry"
  else
    printf -v "$var_name" '%s,%s' "$current" "$entry"
  fi
}

CLAUDE_TOKEN="${CLAUDE_CODE_OAUTH_TOKEN:-}"
AUTH_MODE="oauth-token"
if [[ -z "$CLAUDE_TOKEN" && "$(uname -s)" == "Darwin" ]] && command -v security >/dev/null 2>&1 && command -v jq >/dev/null 2>&1; then
  if keychain_payload="$(security find-generic-password -s "$KEYCHAIN_SERVICE" -w 2>/dev/null)"; then
    CLAUDE_TOKEN="$(printf '%s' "$keychain_payload" | jq -r '.claudeAiOauth.accessToken // empty')"
  fi
fi

if [[ -z "$CLAUDE_TOKEN" ]]; then
  AUTH_MODE="file-mount"
  if [[ ! -f "$CLAUDE_AUTH_JSON" ]]; then
    echo "[ERROR] No Claude OAuth token found and missing fallback auth file: $CLAUDE_AUTH_JSON"
    echo "[ERROR] Either set CLAUDE_CODE_OAUTH_TOKEN or make sure Claude CLI is logged in and keychain is accessible."
    exit 1
  fi
fi

if [[ ! -f "$DATASET_FILE" ]]; then
  echo "[INFO] Dataset not found at $DATASET_FILE"
  echo "[INFO] Downloading dataset from Hugging Face..."
  mkdir -p "$(dirname "$DATASET_FILE")"
  curl -L --fail --silent --show-error "$DATASET_URL" -o "$DATASET_FILE"
fi

echo "[INFO] Building cvdp-claude-agent image..."
(
  cd "$REPO_ROOT/examples/agent_claude"
  ./build_agent.sh
)

AGENT_EXTRA_VOLUMES_BUILT=""
AGENT_EXTRA_ENV_BUILT="CLAUDE_MODEL=$CLAUDE_MODEL"
append_csv AGENT_EXTRA_ENV_BUILT "CLAUDE_TRAJECTORY=$CLAUDE_TRAJECTORY"
append_csv AGENT_EXTRA_ENV_BUILT "CLAUDE_CODE_EFFORT_LEVEL=$CLAUDE_CODE_EFFORT_LEVEL"
if [[ -n "$CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING" ]]; then
  append_csv AGENT_EXTRA_ENV_BUILT "CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING=$CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING"
fi

if [[ -n "$CLAUDE_MAX_TURNS" ]]; then
  append_csv AGENT_EXTRA_ENV_BUILT "CLAUDE_MAX_TURNS=$CLAUDE_MAX_TURNS"
fi
if [[ -n "$CLAUDE_EXEC_ARGS" ]]; then
  append_csv AGENT_EXTRA_ENV_BUILT "CLAUDE_EXEC_ARGS=$CLAUDE_EXEC_ARGS"
fi

if [[ -n "$CLAUDE_TOKEN" ]]; then
  append_csv AGENT_EXTRA_ENV_BUILT "CLAUDE_CODE_OAUTH_TOKEN=$CLAUDE_TOKEN"
else
  append_csv AGENT_EXTRA_VOLUMES_BUILT "$CLAUDE_AUTH_JSON:/host_auth/claude-auth.json:ro"
  append_csv AGENT_EXTRA_ENV_BUILT "CLAUDE_AUTH_FILE=/host_auth/claude-auth.json"
  if [[ -f "$CLAUDE_SETTINGS_JSON" ]]; then
    append_csv AGENT_EXTRA_VOLUMES_BUILT "$CLAUDE_SETTINGS_JSON:/host_auth/claude-settings.json:ro"
    append_csv AGENT_EXTRA_ENV_BUILT "CLAUDE_SETTINGS_FILE=/host_auth/claude-settings.json"
  fi
fi

export AGENT_EXTRA_VOLUMES="$AGENT_EXTRA_VOLUMES_BUILT"
export AGENT_EXTRA_ENV="$AGENT_EXTRA_ENV_BUILT"

echo "[INFO] Claude auth mode: $AUTH_MODE"

cd "$REPO_ROOT"

echo "[INFO] Running Claude benchmark samples..."
uv run python run_samples.py \
  -f "$DATASET_FILE" \
  -l -g cvdp-claude-agent \
  -n "$N_SAMPLES" -k "$K_THRESHOLD" \
  -t "$THREADS" \
  -p "$PREFIX"

echo "[INFO] Done. Results in: $REPO_ROOT/$PREFIX"
