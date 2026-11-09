#!/bin/sh
set -eu
cd "$(dirname "$0")"

# Prefer Python 3.12 (MacPorts, Homebrew, or PATH) when available; otherwise use python3.
if command -v python3.12 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3.12)"
elif [ -x /opt/local/bin/python3.12 ]; then
  PYTHON_BIN=/opt/local/bin/python3.12
elif [ -x /opt/homebrew/bin/python3.12 ]; then
  PYTHON_BIN=/opt/homebrew/bin/python3.12
elif [ -x /usr/local/bin/python3.12 ]; then
  PYTHON_BIN=/usr/local/bin/python3.12
elif [ -x /opt/homebrew/bin/python3 ]; then
  PYTHON_BIN=/opt/homebrew/bin/python3
else
  PYTHON_BIN="$(command -v python3)"
fi

if [ ! -d .venv ] || ! .venv/bin/python -c "import sys" >/dev/null 2>&1; then
  echo "Initializing or repairing virtual environment with $PYTHON_BIN..."
  rm -rf .venv
  "$PYTHON_BIN" -m venv .venv
fi

. .venv/bin/activate
python -m pip install -r requirements.txt

if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
    echo "Created .env from .env.example. Add your Gnani API key before using live providers."
  else
    echo "Warning: .env.example is missing; continuing with environment defaults." >&2
  fi
fi

exec uvicorn app.main:app --host "${API_HOST:-127.0.0.1}" --port "${API_PORT:-8000}" --reload
