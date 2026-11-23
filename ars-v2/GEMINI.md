# Directrices de Desarrollo y Despliegue

## Regla de Despliegue Obligatoria por Defecto
Cada vez que se realice cualquier modificación, corrección o mejora en este repositorio:
1. **Comprometer y subir los cambios a `ars2.0`:**
   - Hacer `git add`, `git commit` y `git push origin main` y `git push origin main:gh-pages`.
   - Web disponible directamente en: https://dga80.github.io/ars2.0/
2. **Sincronizar y desplegar automáticamente en `instaleads`:**
   - Sincronizar siempre los archivos modificados con `/Users/danidev/Proyectos/instaleads` en la rama `gh-pages` en la carpeta `ars-preview/`.
   - Hacer `git add`, `git commit` y `git push origin gh-pages`.
   - Esperar/verificar que GitHub Pages termine de publicar la web en https://dga80.github.io/instaleads/ars-preview/.
   - Nunca dar una tarea por finalizada sin haber realizado este proceso completo de subida y despliegue por defecto.
