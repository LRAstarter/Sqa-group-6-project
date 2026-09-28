#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 1 ]; then echo "Usage: $0 /path/to/front_end_executable"; exit 2; fi
exe="$(realpath "$1")"; root="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$root/results"
while IFS=$'\t' read -r id area intent fixture; do
  [ "$id" = ID ] && continue
  out="$root/results/$id"; mkdir -p "$out"
  cp "$root/fixtures/users.txt" "$out/users.txt"
  cp "$root/fixtures/games.txt" "$out/games.txt"
  cp "$root/fixtures/collection.txt" "$out/collection.txt"
  (cd "$out" && "$exe" users.txt games.txt collection.txt daily.txt < "$root/inputs/$id.txt" > console.txt 2>&1) || echo "Nonzero exit: $id" >&2
  if [ -f "$out/daily.txt" ]; then diff -u "$root/expected_daily/$id.txt" "$out/daily.txt" > "$out/daily.diff" || true; fi
done < "$root/test_index.tsv"
