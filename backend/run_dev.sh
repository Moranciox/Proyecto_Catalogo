#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
