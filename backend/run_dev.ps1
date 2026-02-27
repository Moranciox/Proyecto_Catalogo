$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

if (-not (Test-Path ".venv")) {
  py -m venv .venv
}

# Activate venv
. .\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
