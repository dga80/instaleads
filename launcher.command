#!/usr/bin/env bash

# Ir al directorio del script
cd "$(dirname "$0")"

echo "=========================================================="
echo "           🚀 INICIANDO INSTALEADS AI                    "
echo "  FastAPI + OpenStreetMap + Agente Google Gemini 2.5     "
echo "=========================================================="
echo ""

# 1. Liberar puerto 8085 si quedó ocupado por un proceso previo colgado
OLD_PID=$(lsof -ti :8085 2>/dev/null)
if [ -n "$OLD_PID" ]; then
    echo "⚠️  Liberando puerto 8085 ocupado por proceso anterior (PID: $OLD_PID)..."
    kill -9 $OLD_PID 2>/dev/null || true
    sleep 1
fi

# Detectar comando de Python disponible (python3 o python)
if [ -f "./venv/bin/python" ]; then
    PY_CMD="./venv/bin/python"
    source venv/bin/activate
elif [ -f "./.venv/bin/python" ]; then
    PY_CMD="./.venv/bin/python"
    source .venv/bin/activate
elif command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null; then
    PY_CMD="python"
else
    echo "❌ Error: No se encontró Python en el sistema."
    echo "Por favor instala Python 3.10 o superior desde https://www.python.org/"
    read -p "Presiona Enter para salir..."
    exit 1
fi

echo "✓ Python detectado: $($PY_CMD --version)"

# Instalar o verificar dependencias si faltan
if ! $PY_CMD -c "import fastapi, uvicorn, requests, google.genai" &>/dev/null; then
    echo "⏳ Instalando librerías requeridas..."
    $PY_CMD -m pip install -r requirements.txt
fi

# Abrir el navegador tras un retardo de 2 segundos en segundo plano
(
    sleep 2
    if command -v open &>/dev/null; then
        open "http://127.0.0.1:8085"
    elif command -v xdg-open &>/dev/null; then
        xdg-open "http://127.0.0.1:8085"
    elif command -v start &>/dev/null; then
        start "http://127.0.0.1:8085"
    fi
) &

echo "🌐 Servidor arrancando en: http://127.0.0.1:8085"
echo "Presiona CTRL+C para detener el servidor."
echo "----------------------------------------------------------"

# Iniciar la aplicación
$PY_CMD app.py

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️ El servidor se detuvo."
    read -p "Presiona Enter para salir..."
fi
