@echo off
rem Story 3.5a: starter demoen med uv, uten Docker. Logikken står i start\start.ps1.
chcp 65001 >nul
rem Tom PSModulePath: Windows PowerShell 5.1 bygger sine egne stier, også når fila startes fra
rem PowerShell 7 (CI 23.10, run 40027262304).
set "PSModulePath="
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start\start.ps1" -Versjon demo
