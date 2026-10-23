@echo off
rem Story 3.5a: starter den ekte versjonen med uv, uten Docker. Logikken står i start\start.ps1.
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start\start.ps1" -Versjon ekte
