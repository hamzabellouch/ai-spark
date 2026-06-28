#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -e

# Change directory to the script's directory
cd "$(dirname "$0")"

# Find python command (prefer python3, then python)
if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
else
  echo "ERROR: Python is not installed. Please install Python 3.11 or newer." >&2
  exit 1
fi

echo "[AI Spark] Using Python command: $PYTHON_CMD"

# Verify Python version is 3.11+
$PYTHON_CMD -c "
import sys
if sys.version_info < (3, 11):
    print('ERROR: Python version must be 3.11 or newer.')
    sys.exit(1)
"

# Set up virtual environment if it doesn't exist
if [ ! -d ".venv_macos" ]; then
  echo "[AI Spark] Creating Python virtual environment (.venv_macos) for macOS..."
  $PYTHON_CMD -m venv .venv_macos
fi

echo "[AI Spark] Activating virtual environment..."
source .venv_macos/bin/activate

echo "[AI Spark] Installing/updating requirements..."
pip install -r src/requirements.txt

# Free up port 8000 if it's already in use
if command -v lsof >/dev/null 2>&1; then
  PID=$(lsof -t -i :8000 || true)
  if [ -n "$PID" ]; then
    echo "[AI Spark] Port 8000 is occupied by process PID $PID. Terminating it to free the port..."
    kill -9 $PID 2>/dev/null || true
  fi
fi

echo ""
echo "Starting AI Spark on http://127.0.0.1:8000"
echo "Keep this window open while using the program."
echo ""
cd src
python main.py
