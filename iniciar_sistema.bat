@echo off
title Sistema Reporte Gerencial
echo ==========================================================
echo        SISTEMA DE REPORTE GERENCIAL - PRODUCCION
echo ==========================================================
echo.
echo 1. Iniciando Backend (FastAPI en puerto 8000)...
start "API Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn main:app --reload --port 8000"

timeout /t 2 /nobreak >nul

echo 2. Iniciando Frontend (Vite en puerto 5173)...
start "Frontend Vue" cmd /k "cd /d %~dp0frontend && npm run dev"

timeout /t 3 /nobreak >nul

echo 3. Abriendo el Dashboard en tu navegador web...
start http://localhost:5173/

echo.
echo ==========================================================
echo   El sistema esta en marcha. Puedes cerrar esta ventana.
echo ==========================================================
