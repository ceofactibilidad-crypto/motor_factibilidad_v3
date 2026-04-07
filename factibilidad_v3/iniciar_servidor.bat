@echo off
title Factibilidad.cl - V3 Local Server
color 0b

echo.
echo ==============================================================
echo   INICIANDO FACTIBILIDAD.CL (VERSION 3)
echo ==============================================================
echo.
echo Instalando/Verificando dependencias necesarias...
pip install -r backend\requirements.txt -q

echo.
echo Levantando el servidor (FastAPI)...
echo.
echo ==============================================================
echo    Abra su navegador y visite:
echo    http://127.0.0.1:8000
echo ==============================================================
echo.

cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
pause
