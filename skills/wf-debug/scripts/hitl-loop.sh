#!/usr/bin/env bash
# Structured human-in-the-loop repro: the person performs each step, the script records the verdict.
#   hitl-loop.sh <log file> "<step 1>" "<step 2>" ... "<what the bug looks like>"
# Prints each step, waits for Enter, then asks whether the symptom appeared. Appends one line per run
# (timestamp, verdict, note) to the log file so the agent can read the failure rate back.
set -euo pipefail

[ $# -ge 3 ] || { echo "usage: hitl-loop.sh <log file> <step>... <symptom>" >&2; exit 2; }
log="$1"; shift
symptom="${*: -1}"
steps=("${@:1:$#-1}")

run=1
while :; do
  echo "== run $run"
  for step in "${steps[@]}"; do
    read -r -p "  $step  [Enter when done] " _
  done
  read -r -p "  Did you see: $symptom ? [y/n/q] " answer
  case "$answer" in
    q) break ;;
    y) verdict="red" ;;
    *) verdict="green" ;;
  esac
  read -r -p "  Note (optional): " note
  printf '%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$verdict" "$note" >> "$log"
  run=$((run + 1))
done
echo "results in $log"
