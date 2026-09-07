#!/usr/bin/env bash
# ==============================================================================
# InstaLeads - Script de Despliegue de Demos a GitHub Pages
# ==============================================================================
# Este script toma los sitios estáticos generados en demos/ y los prepara
# para servirse en GitHub Pages con su propio .nojekyll.
# ==============================================================================

set -e

DEMOS_DIR="demos"

if [ ! -d "$DEMOS_DIR" ]; then
  echo "❌ Error: La carpeta '$DEMOS_DIR' no existe todavía. Genera al menos una web demo primero."
  exit 1
fi

# Crear archivo .nojekyll para asegurar que GitHub Pages sirva todas las carpetas y assets
touch "$DEMOS_DIR/.nojekyll"

echo "✅ Carpeta '$DEMOS_DIR' lista para GitHub Pages."
echo "Comando para publicar en la rama gh-pages de tu repositorio:"
echo "   git subtree push --prefix demos origin gh-pages"
