#!/bin/bash

# Directorio del proyecto
cd "$(dirname "$0")"

echo "=================================================="
echo "          🚀 Iniciando InstaLeads AI              "
echo "=================================================="
echo ""

# 1. Liberar puerto 8085 si quedó ocupado por un proceso previo colgado
OLD_PID=$(lsof -ti :8085 2>/dev/null)
if [ -n "$OLD_PID" ]; then
    echo "⚠️  Liberando puerto 8085 ocupado por proceso anterior (PID: $OLD_PID)..."
    kill -9 $OLD_PID 2>/dev/null || true
    sleep 1
fi

# 2. Localizar Python en el entorno virtual o en el sistema
if [ -f "./venv/bin/python" ]; then
    PY_BIN="./venv/bin/python"
elif [ -f "./.venv/bin/python" ]; then
    PY_BIN="./.venv/bin/python"
elif command -v python3 &>/dev/null; then
    PY_BIN="python3"
elif command -v python &>/dev/null; then
    PY_BIN="python"
else
    echo "❌ Error: No se encontró Python en el sistema ni en ./venv."
    echo "Por favor instala Python 3.10 o superior."
    read -p "Presiona Enter para salir..."
    exit 1
fi

echo "💻 Acceso Local: http://localhost:8085"
echo "🌐 Abriendo navegador e iniciando servidor..."
echo ""

# Abrir el navegador tras 2 segundos en segundo plano
(sleep 2 && open "http://localhost:8085") &

# Ejecutar la aplicación
$PY_BIN app.py

# Si termina por error o cierre inesperado, no cerrar la ventana inmediatamente
if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️ El servidor se detuvo."
    read -p "Presiona Enter para cerrar esta ventana..."
fi
