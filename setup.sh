#!/usr/bin/env bash
# ─────────────────────────────────────────────
#  SATINTEL — One-click setup
# ─────────────────────────────────────────────
set -e

echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║        SATINTEL SETUP                ║"
echo "  ╚══════════════════════════════════════╝"
echo ""

# Check Python 3
if ! command -v python3 &>/dev/null; then
    echo "  [!] Python 3 is not installed."
    echo ""
    echo "  Install it from: https://www.python.org/downloads/"
    echo "  Then re-run this script."
    exit 1
fi

PYTHON=$(command -v python3)
echo "  [✓] Python found: $($PYTHON --version)"

# Create virtual environment if not exists
if [ ! -d ".venv" ]; then
    echo "  [*] Creating virtual environment..."
    $PYTHON -m venv .venv
    echo "  [✓] Virtual environment created."
fi

# Activate and install
echo "  [*] Installing Python packages..."
source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "  [✓] Packages installed."

echo ""
echo "  ─────────────────────────────────────────"
echo "  Setup complete! To run SATINTEL:"
echo ""
echo "    python3 satintel.py"
echo ""
echo "  Or use the launcher:"
echo ""
echo "    ./run.sh"
echo "  ─────────────────────────────────────────"
echo ""
