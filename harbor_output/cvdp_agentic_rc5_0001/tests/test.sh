#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier
mkdir -p /code/rundir
mkdir -p /code/rundir/.cache
mkdir -p /code/rundir/harness/.cache
mkdir -p /rundir
mkdir -p /rundir/.cache
mkdir -p /rundir/harness/.cache

status=0

echo "Running service: direct"
if ! (
  set -e
  source /code/cvdp_harness_env.sh /code/src/.env
  cd /code/rundir
  sh -lc 'pytest -o cache_dir=/code/rundir/.cache /src/test_runner.py -v -s'
); then
  status=1
fi

if [ "$status" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

exit "$status"
