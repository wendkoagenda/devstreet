# Backend ASGI avec Socket.IO (messagerie temps réel).
# Remplace ``python manage.py runserver`` en développement local.
Set-Location $PSScriptRoot
.\venv\Scripts\Activate.ps1
uvicorn config.asgi:application --reload --host 127.0.0.1 --port 8000
