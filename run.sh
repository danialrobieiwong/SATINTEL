#!/usr/bin/env bash
# ─────────────────────────────────────────────
#  SATINTEL — Launch script
# ─────────────────────────────────────────────

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Use venv if available
if [ -f ".venv/bin/python" ]; then
    .venv/bin/python satintel.py "$@"
elif command -v python3 &>/dev/null; then
    python3 satintel.py "$@"
else
    echo "[!] Python 3 not found. Run setup.sh first."
    exit 1
fi
