#!/usr/bin/env bash

set -euo pipefail

INTERVAL_SECONDS="1"
OUT_DIR=""

usage() {
  cat <<'EOF'
Usage:
  bash src/benchmark_pipeline.sh [--interval seconds] [--outdir path] -- <command> [args...]

Examples:
  bash src/benchmark_pipeline.sh -- bash src/run_all.sh
  bash src/benchmark_pipeline.sh --interval 0.5 -- bash src/run_all.sh
  bash src/benchmark_pipeline.sh --outdir data/logs/benchmarks/my_run -- bash src/run_all.sh

What this records:
  - samples.csv: timestamped CPU% and RSS (MB), sampled over the command's full process tree
  - summary.txt: peak CPU%, peak RAM, elapsed time, exit code
  - command.log: stdout/stderr from the command
  - time.txt: /usr/bin/time -l output (includes max resident set size)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --interval)
      INTERVAL_SECONDS="$2"
      shift 2
      ;;
    --outdir)
      OUT_DIR="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ $# -lt 1 ]]; then
  echo "Missing command to benchmark." >&2
  usage >&2
  exit 1
fi

if [[ -z "$OUT_DIR" ]]; then
  RUN_TS="$(date +%Y%m%d_%H%M%S)"
  OUT_DIR="data/logs/benchmarks/${RUN_TS}"
fi

mkdir -p "$OUT_DIR"

SAMPLES_CSV="${OUT_DIR}/samples.csv"
SUMMARY_TXT="${OUT_DIR}/summary.txt"
COMMAND_LOG="${OUT_DIR}/command.log"
TIME_TXT="${OUT_DIR}/time.txt"

# Header for sampled metrics (whole process tree)
echo "timestamp,pid_count,total_cpu_percent,total_rss_mb" > "$SAMPLES_CSV"

max_cpu="0"
max_rss_kb="0"

command=("$@")
start_epoch="$(date +%s)"

# Launch the command through /usr/bin/time to capture system-level stats.
/usr/bin/time -l -o "$TIME_TXT" "${command[@]}" > "$COMMAND_LOG" 2>&1 &
root_pid=$!

# Recursively collect descendant PIDs.
get_descendants() {
  local parent_pid="$1"
  local children child

  children="$(pgrep -P "$parent_pid" || true)"
  for child in $children; do
    echo "$child"
    get_descendants "$child"
  done
}

sample_once() {
  local pids_list pids_csv ps_output
  local sample_ts pid_count cpu_sum rss_sum

  pids_list="$root_pid $(get_descendants "$root_pid" | tr '\n' ' ')"
  pids_list="$(echo "$pids_list" | tr ' ' '\n' | sed '/^$/d' | sort -n | uniq | tr '\n' ' ')"

  if [[ -z "${pids_list// /}" ]]; then
    return 0
  fi

  pids_csv="$(echo "$pids_list" | tr ' ' ',' | sed 's/,$//')"
  ps_output="$(ps -o pid=,pcpu=,rss= -p "$pids_csv" 2>/dev/null || true)"

  if [[ -z "$ps_output" ]]; then
    return 0
  fi

  pid_count="$(echo "$ps_output" | awk 'NF>=3{count++} END{print count+0}')"
  cpu_sum="$(echo "$ps_output" | awk 'NF>=3{sum+=$2} END{printf "%.2f", sum+0}')"
  rss_sum="$(echo "$ps_output" | awk 'NF>=3{sum+=$3} END{printf "%.0f", sum+0}')"

  sample_ts="$(date +%Y-%m-%dT%H:%M:%S%z)"
  echo "$sample_ts,$pid_count,$cpu_sum,$(awk -v rss_kb="$rss_sum" 'BEGIN{printf "%.2f", rss_kb/1024}')" >> "$SAMPLES_CSV"

  if [[ "$(awk -v a="$cpu_sum" -v b="$max_cpu" 'BEGIN{print (a>b)?1:0}')" -eq 1 ]]; then
    max_cpu="$cpu_sum"
  fi

  if [[ "$(awk -v a="$rss_sum" -v b="$max_rss_kb" 'BEGIN{print (a>b)?1:0}')" -eq 1 ]]; then
    max_rss_kb="$rss_sum"
  fi
}

while kill -0 "$root_pid" 2>/dev/null; do
  sample_once
  sleep "$INTERVAL_SECONDS"
done

# Ensure the process is fully reaped and capture its exit code.
set +e
wait "$root_pid"
exit_code=$?
set -e

# Final sample after exit to catch any last values.
sample_once

end_epoch="$(date +%s)"
elapsed_seconds="$((end_epoch - start_epoch))"

# Pull max RSS from /usr/bin/time output if available.
time_max_rss_raw="$(awk '/maximum resident set size/ {print $1}' "$TIME_TXT" | tail -n1)"
if [[ -z "$time_max_rss_raw" ]]; then
  time_max_rss_raw="N/A"
fi

{
  echo "Benchmark run: $(date +%Y-%m-%dT%H:%M:%S%z)"
  echo "Command: ${command[*]}"
  echo "Exit code: $exit_code"
  echo "Elapsed seconds: $elapsed_seconds"
  echo "Sample interval seconds: $INTERVAL_SECONDS"
  echo "Peak CPU% (sampled, process tree): $max_cpu"
  echo "Peak RAM MB (sampled, process tree): $(awk -v rss_kb="$max_rss_kb" 'BEGIN{printf "%.2f", rss_kb/1024}')"
  echo "Peak RAM (/usr/bin/time -l max resident set size, raw units): $time_max_rss_raw"
  if [[ "$time_max_rss_raw" != "N/A" ]]; then
    echo "Peak RAM MB (/usr/bin/time -l value interpreted as bytes): $(awk -v v="$time_max_rss_raw" 'BEGIN{printf "%.2f", v/1024/1024}')"
  fi
  echo "Files:"
  echo "  - $SAMPLES_CSV"
  echo "  - $SUMMARY_TXT"
  echo "  - $COMMAND_LOG"
  echo "  - $TIME_TXT"
} > "$SUMMARY_TXT"

echo "Benchmark complete. Summary: $SUMMARY_TXT"
exit "$exit_code"
