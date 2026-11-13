#!/usr/bin/env bash
set -e
root=$(cd -- "$(dirname -- "$0")" && pwd)
if [[ -n ${PYTHON:-} ]]; then
    exec "$PYTHON" -X utf8 "$root/src/main.py" "$@"
elif python3 -c 'import sys' >/dev/null 2>&1; then
    exec python3 -X utf8 "$root/src/main.py" "$@"
fi
exec python -X utf8 "$root/src/main.py" "$@"
