# Запуск всех процессов без Docker (Windows PowerShell).
# Запустите из корня проекта: .\scripts\run-all.ps1
# Требуется: Redis уже запущен (см. ниже), Python venv активирован.

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $ProjectRoot

$env:MEDIA_ROOT = Join-Path $ProjectRoot "media"
$env:CELERY_BROKER_URL = "redis://localhost:6379/0"

Write-Host "MEDIA_ROOT = $env:MEDIA_ROOT" -ForegroundColor Cyan
Write-Host ""

# 1) API (FastAPI)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot'; `$env:MEDIA_ROOT='$env:MEDIA_ROOT'; uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000"
Start-Sleep -Seconds 1

# 2) Celery worker
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot'; `$env:MEDIA_ROOT='$env:MEDIA_ROOT'; `$env:CELERY_BROKER_URL='$env:CELERY_BROKER_URL'; celery -A backend.worker.celery_app worker --loglevel=info -P solo"
Start-Sleep -Seconds 1

# 3) Frontend (Streamlit)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot'; streamlit run frontend/ui.py --server.port 8501"
Start-Sleep -Seconds 1

Write-Host "Запущены: API (порт 8000), Worker, Frontend (порт 8501)." -ForegroundColor Green
Write-Host "Redis должен быть запущен отдельно (см. README или ниже)." -ForegroundColor Yellow
