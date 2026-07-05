@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM 1. Kill old processes on port 5000 and any ssh.exe processes
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | ForEach-Object { if ($_.OwningProcess -gt 0) { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue } }"
taskkill /F /IM ssh.exe >nul 2>&1

REM 2. Start the packaged application in the foreground (hidden by VBScript)
"%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe" app.py
exit
