#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATASET_FILE="${DATASET_FILE:-$REPO_ROOT/datasets/cvdp_v1.0.2_agentic_code_generation_no_commercial.jsonl}"
DATASET_URL="https://huggingface.co/datasets/nvidia/cvdp-benchmark-dataset/resolve/main/cvdp_v1.0.2_agentic_code_generation_no_commercial.jsonl?download=true"

N_SAMPLES="${N_SAMPLES:-5}"
K_THRESHOLD="${K_THRESHOLD:-1}"
THREADS="${THREADS:-4}"
PREFIX="${PREFIX:-work_codex53_xhigh_all92_n5_k1_t4}"

CODEX_MODEL="${CODEX_MODEL:-gpt-5.3-codex}"
CODEX_REASONING_EFFORT="${CODEX_REASONING_EFFORT:-xhigh}"
CODEX_EXEC_ARGS="${CODEX_EXEC_ARGS:-}"
CODEX_TRAJECTORY="${CODEX_TRAJECTORY:-1}"

CODEX_AUTH_JSON="${CODEX_AUTH_JSON:-$HOME/.codex/auth.json}"
CODEX_CONFIG_TOML="${CODEX_CONFIG_TOML:-$HOME/.codex/config.toml}"
CODEX_VERSION_JSON="${CODEX_VERSION_JSON:-$HOME/.codex/version.json}"

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

if [[ "$CODEX_TRAJECTORY" == "1" ]] && [[ " $CODEX_EXEC_ARGS " != *" --json "* ]]; then
  if [[ -z "$CODEX_EXEC_ARGS" ]]; then
    CODEX_EXEC_ARGS="--json"
  else
    CODEX_EXEC_ARGS="$CODEX_EXEC_ARGS --json"
  fi
fi

for required_file in "$CODEX_AUTH_JSON" "$CODEX_CONFIG_TOML" "$CODEX_VERSION_JSON"; do
  if [[ ! -f "$required_file" ]]; then
    echo "[ERROR] Missing required Codex auth/config file: $required_file"
    exit 1
  fi
done

if [[ ! -f "$DATASET_FILE" ]]; then
  echo "[INFO] Dataset not found at $DATASET_FILE"
  echo "[INFO] Downloading dataset from Hugging Face..."
  mkdir -p "$(dirname "$DATASET_FILE")"
  curl -L --fail --silent --show-error "$DATASET_URL" -o "$DATASET_FILE"
fi

echo "[INFO] Building cvdp-codex-agent image..."
(
  cd "$REPO_ROOT/examples/agent_codex"
  ./build_agent.sh
)

export AGENT_EXTRA_VOLUMES="$CODEX_AUTH_JSON:/host_auth/codex-auth.json:ro,$CODEX_CONFIG_TOML:/host_auth/codex-config.toml:ro,$CODEX_VERSION_JSON:/host_auth/codex-version.json:ro"
AGENT_EXTRA_ENV_BUILT="CODEX_AUTH_FILE=/host_auth/codex-auth.json,CODEX_CONFIG_FILE=/host_auth/codex-config.toml,CODEX_VERSION_FILE=/host_auth/codex-version.json,CODEX_MODEL=$CODEX_MODEL,CODEX_REASONING_EFFORT=$CODEX_REASONING_EFFORT,CODEX_TRAJECTORY=$CODEX_TRAJECTORY"
if [[ -n "$CODEX_EXEC_ARGS" ]]; then
  append_csv AGENT_EXTRA_ENV_BUILT "CODEX_EXEC_ARGS=$CODEX_EXEC_ARGS"
fi
export AGENT_EXTRA_ENV="$AGENT_EXTRA_ENV_BUILT"

cd "$REPO_ROOT"

echo "[INFO] Running Codex benchmark samples..."
uv run python run_samples.py \
  -f "$DATASET_FILE" \
  -l -g cvdp-codex-agent \
  -n "$N_SAMPLES" -k "$K_THRESHOLD" \
  -t "$THREADS" \
  -p "$PREFIX"

echo "[INFO] Done. Results in: $REPO_ROOT/$PREFIX"
