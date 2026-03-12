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

echo "Running service: sanity"
if ! (
  set -e
  source /code/cvdp_harness_env.sh /code/src/.env
  cd /code/rundir
  sh -lc 'pytest /src/test_runner_event_array.py -s -v -o cache_dir=/rundir/harness/.cache'
); then
  status=1
fi

echo "Running service: storage_sanity"
if ! (
  set -e
  source /code/cvdp_harness_env.sh /code/src/.env_event_storage
  cd /code/rundir
  sh -lc 'pytest /src/test_runner_event_storage.py -s -v -o cache_dir=/rundir/harness/.cache'
); then
  status=1
fi

if [ "$status" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

exit "$status"
