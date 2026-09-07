#!/bin/bash

# Directorio del proyecto
cd "/Users/danidev/Desktop/instaleads"

echo "=================================================="
echo "          🚀 Iniciando InstaLeads AI              "
echo "=================================================="
echo ""
echo "💻 Acceso Local: http://localhost:8085"
echo ""
echo "Abriendo navegador e iniciando servidor..."

# Abrir el navegador tras 2 segundos
(sleep 2 && open "http://localhost:8085") &

# Ejecutar con el entorno virtual del proyecto
./venv/bin/python app.py
