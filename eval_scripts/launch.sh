#!/usr/bin/env bash
#
# Launch CVDP Harbor benchmark for multiple models in parallel.
# Staggers launches by 15 seconds to avoid thundering-herd Docker builds.
#
# Usage:
#   # Run default models (edit MODELS array below)
#   ./eval_scripts/launch.sh
#
#   # Pass extra flags through to run_harbor_terminus2.py
#   ./eval_scripts/launch.sh --dry-run
#   ./eval_scripts/launch.sh --n-tasks 5
#
#   # Override concurrency, stagger, or agent
#   N_CONCURRENT=4 STAGGER=30 ./eval_scripts/launch.sh
#   AGENT=terminus-3 ./eval_scripts/launch.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGS_DIR="$REPO_ROOT/logs"
TIMESTAMP="$(date +%Y-%m-%d__%H-%M-%S)"
STAGGER="${STAGGER:-15}"
N_CONCURRENT="${N_CONCURRENT:-8}"
AGENT="${AGENT:-terminus-2}"

# ── Models to evaluate ──────────────────────────────────────────────
# Edit this list for each eval run.
MODELS=(
    "openrouter/openai/gpt-5.4"
    "openrouter/anthropic/claude-opus-4.6"
    "openrouter/google/gemini-3.1-pro-preview"
)
# ────────────────────────────────────────────────────────────────────

# Pass through extra args (e.g. --dry-run, --n-tasks 5)
EXTRA_ARGS=("$@")

mkdir -p "$LOGS_DIR"

PIDS=()
MODEL_NAMES=()

cleanup() {
    echo ""
    echo "Caught signal — killing all background jobs..."
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
        fi
    done
    wait
    echo "All jobs terminated."
    exit 1
}

trap cleanup SIGINT SIGTERM

echo "========================================"
echo "CVDP Harbor Benchmark — Multi-Model Launch"
echo "========================================"
echo "  Agent:        $AGENT"
echo "  Models:       ${#MODELS[@]}"
echo "  Timestamp:    $TIMESTAMP"
echo "  Concurrency:  $N_CONCURRENT per model"
echo "  Stagger:      ${STAGGER}s between launches"
echo "  Extra args:   ${EXTRA_ARGS[*]:-none}"
echo ""

for i in "${!MODELS[@]}"; do
    model="${MODELS[$i]}"
    short_name="${model##*/}"
    log_file="$LOGS_DIR/${short_name}_${TIMESTAMP}.log"

    echo "[$((i+1))/${#MODELS[@]}] Launching: $model"
    echo "    Log: $log_file"

    python3 "$REPO_ROOT/run_harbor_terminus2.py" \
        --agent "$AGENT" \
        --model "$model" \
        --n-concurrent "$N_CONCURRENT" \
        "${EXTRA_ARGS[@]}" \
        > >(tee "$log_file") 2>&1 &

    PIDS+=($!)
    MODEL_NAMES+=("$short_name")

    # Stagger launches (skip delay after last model)
    if [[ $i -lt $(( ${#MODELS[@]} - 1 )) ]]; then
        echo "    Waiting ${STAGGER}s before next launch..."
        sleep "$STAGGER"
    fi
done

echo ""
echo "All models launched. PIDs: ${PIDS[*]}"
echo ""
echo "Monitor progress with:"
echo "  python3 eval_scripts/monitor.py --agent $AGENT"
echo ""
echo "Waiting for all jobs to finish..."
echo ""

EXIT_CODE=0
for i in "${!PIDS[@]}"; do
    pid="${PIDS[$i]}"
    name="${MODEL_NAMES[$i]}"
    if wait "$pid"; then
        echo "[DONE] $name (PID $pid) — exit code 0"
    else
        code=$?
        echo "[FAIL] $name (PID $pid) — exit code $code"
        EXIT_CODE=1
    fi
done

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "All jobs completed successfully."
else
    echo "Some jobs failed. Check logs in $LOGS_DIR"
fi

exit $EXIT_CODE
