param(
  [string]$VenvDir = ".venv"
)

if (-not (Test-Path $VenvDir)) {
  python -m venv $VenvDir
}

& "$VenvDir\Scripts\python.exe" -m pip install --upgrade pip
& "$VenvDir\Scripts\python.exe" -m pip install -r requirements.txt
& "$VenvDir\Scripts\python.exe" run.py
