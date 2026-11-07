#!/usr/bin/env bash
# Run all indexed tests and validate daily and terminal output using Python 3.
set -euo pipefail
if [ "$#" -ne 1 ]; then
    echo "Usage: bash scripts/run_all.sh /path/to/frontend" >&2
    exit 2
fi
script_dir="$(cd "$(dirname "$0")" && pwd)"
exec python3 "$script_dir/run_tests.py" "$1"
