@echo off
title InstaLeads AI - Prospección Local Inteligente
cd /d "%~dp0"

echo ==========================================================
echo            INICIANDO INSTALEADS AI
echo   FastAPI + OpenStreetMap + Agente Google Gemini 2.5
echo ==========================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] No se ha encontrado Python instalado en el sistema.
    echo Por favor descarga e instala Python desde https://www.python.org/
    pause
    exit /b 1
)

:: Comprobar si existe entorno virtual y activarlo
if exist "venv\Scripts\activate.bat" (
    echo Activando entorno virtual venv...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo Activando entorno virtual .venv...
    call .venv\Scripts\activate.bat
)

:: Abrir el navegador automaticamente
start http://127.0.0.1:8085

:: Iniciar servidor
echo Servidor en ejecucion en http://127.0.0.1:8085
echo Presiona CTRL+C para cerrar el servidor.
echo ----------------------------------------------------------
python app.py
pause
