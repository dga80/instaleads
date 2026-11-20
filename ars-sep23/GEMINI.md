# Directrices de Desarrollo y Despliegue

## Regla de Despliegue Obligatoria por Defecto
Cada vez que se realice cualquier modificación, corrección o mejora en este repositorio:
1. **Comprometer y subir los cambios a `ars2.0`:**
   - Hacer `git add`, `git commit` y `git push origin main` y `git push origin main:gh-pages`.
2. **Sincronizar y desplegar automáticamente en `instaleads`:**
   - Sincronizar siempre los archivos modificados con `/Users/danidev/Desktop/instaleads` en la rama `gh-pages` en las carpetas `ars-advocats/` y `arsadvocats/`.
   - Hacer `git add`, `git commit` y `git push origin gh-pages`.
   - Esperar/verificar que GitHub Pages termine de publicar la web en https://dga80.github.io/instaleads/ars-advocats/.
   - Nunca dar una tarea por finalizada sin haber realizado este proceso completo de subida y despliegue por defecto.
