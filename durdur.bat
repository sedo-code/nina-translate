@echo off
chcp 65001 >nul
title Simultane Ceviri - Stop
cd /d "%~dp0"

echo.
echo  ============================================================
echo   Simultane Ceviri Sunucusu Durduruluyor...
echo  ============================================================
echo.

powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | ForEach-Object { if ($_.OwningProcess -gt 0) { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue } }"
taskkill /F /IM ssh.exe >nul 2>&1

REM Clean up the temporary desktop HTML file
if exist "%USERPROFILE%\Desktop\Mobil-Ceviri-Baglantisi.html" del /f /q "%USERPROFILE%\Desktop\Mobil-Ceviri-Baglantisi.html"

echo   Sunucu ve tunel durduruldu.
echo  ============================================================
timeout /t 2 >nul
exit
