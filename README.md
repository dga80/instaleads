# 🚀 InstaLeads AI - Prospección Local Inteligente

Aplicación Full-Stack de prospección comercial local construida con **FastAPI**, **OpenStreetMap (Overpass API con failover + Nominatim)**, **DuckDuckGo** y un **Agente Inteligente potenciado por Google Gemini (`google-genai` SDK con modelo principal `gemini-3.8-flash` y auto-desescalado en cascada)**.

---

## 🎯 ¿Qué hace InstaLeads?

1. **Búsqueda Geográfica Flexible (Localidad / Municipio, Provincia o Código Postal)**:
   - Resuelve el área geográfica a través de OpenStreetMap / Nominatim admitiendo búsqueda por **Municipio**, **Provincia** o **Código Postal**.
   - Failover automático entre múltiples espejos públicos de Overpass (`overpass-api.de`, `kumi.systems`, `private.coffee`) para garantizar cero errores de timeout.
   - Normaliza la categoría del negocio ingresada en español a las etiquetas oficiales de OpenStreetMap mediante el Agente Gemini.
2. **Filtrado Estricto de Oportunidades Reales**:
   - **Exclusión de Cadenas y Grandes Franquicias**: Filtra automáticamente corporaciones (Vitaldent, Adeslas, Sanitas, McDonalds, etc.) tanto por etiquetas OSM (`brand`, `brand:wikidata`, `operator`) como por análisis semántico de Gemini.
   - **Descarte de Webs Propias**: Solo selecciona negocios que carecen de página web propia.
   - **Validación Estricta de Instagram**: Descarta URLs externas y verifica coincidencia de tokens entre el nombre del negocio y el perfil encontrado.
3. **Replicación de Instagram a Web Demo (Mobile-First + Stitch Design System)**:
   - Extrae el avatar, biografía y publicaciones reales de Instagram (con soporte de Apify o fallback curado).
   - Sintetiza un **Design System individualizado** (principios de Google Stitch) con paletas tonales personalizadas, fuentes de Google Fonts de impacto y lenguaje de formas exclusivo para evitar webs clónicas.
   - Genera una landing page responsive autocontenida (`demos/{slug}/index.html`) con barra fija para WhatsApp directo, galería de trabajos y mapa interactivo.
4. **Validación y Pitch Comercial con Demo Interactiva**:
   - **Verificación**: Gemini analiza la correspondencia del perfil y redacta un DM persuasivo con tranquilidad anti-malware.
   - **Pitch con Enlace a la Demo**: Mensaje de primer contacto y mensaje de seguimiento a las 48-72h listos para copiar o enviar por email.
5. **Simulador de Móvil Integrado & Exportación para GitHub Pages**:
   - Visualizador de iPhone interactivo integrado directamente en el Dashboard.
   - Estructura `demos/{slug}/index.html` lista para subir a un repositorio de **GitHub Pages**.
   - Exportación directa a **CSV** con enlaces a las demos y estados del lead.

---

## 🛠️ Requisitos Previos

- **Python 3.10+** (Probado en Python 3.14).
- Una clave de API de **Google Gemini** (gratuita en [Google AI Studio](https://aistudio.google.com/)).

---

## ⚡ Instalación Rápida

1. **Clonar o ubicarse en el directorio del proyecto**:
   ```bash
   cd c:\Users\34616\Desktop\AppsDani_\instaleads
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar la API Key de Gemini**:
   Copia el archivo `.env.example` a `.env` (o edita el `.env` existente):
   ```env
   GEMINI_API_KEY=tu_clave_de_google_ai_studio_aqui
   PORT=8085
   HOST=127.0.0.1
   ```

4. **Iniciar el servidor**:
   ```bash
   python app.py
   ```
   O alternativamente con uvicorn:
   ```bash
   uvicorn app:app --reload --port 8085
   ```

5. **Abrir en el navegador**:
   Visita [http://127.0.0.1:8085](http://127.0.0.1:8085)

---

## 🤖 Cascada de Modelos y Roles de Google Gemini

InstaLeads implementa un servicio inteligente de alta disponibilidad (`gemini_service.py`) con auto-desescalado en cascada:
```text
gemini-3.8-flash (Latest) ──(si 503/429)──> gemini-3.7-flash ──> gemini-3.5-flash ──> gemini-2.5-flash ──> gemini-flash-latest
```

### 1. Mapeo de Categorías OSM (`mapear_categoria_osm`)
Gemini convierte la intención en lenguaje natural a etiquetas técnicas oficiales de OSM:
```json
// Input: "taller de motos"
// Output de Gemini 3.8:
{
  "key": "shop",
  "value": "motorcycle"
}
```

### 2. Verificación de Perfil, Filtro Anti-Cadenas y Pitch DM (`verificar_y_redactar_pitch`)
Analiza la correspondencia del perfil, descarta franquicias multinacionales y redacta pitches personalizados:
```json
{
  "es_gran_cadena": false,
  "es_perfil_correcto": true,
  "razon": "Coincide el nombre comercial y la ubicación en Badalona",
  "mensaje_dm_sugerido": "¡Hola equipo de Dra. Laguna! Me encantan vuestros trabajos en Instagram...",
  "mensaje_seguimiento": "¡Hola de nuevo! Os escribí hace un par de días por Instagram..."
}
```

---

## 📁 Estructura del Proyecto

```text
instaleads/
├── app.py                    # Servidor FastAPI, endpoints de escaneo, cadencia y emails
├── gemini_service.py         # Cliente Gemini 3.8 Flash con auto-desescalado en cascada
├── instagram_extractor.py    # Extractor de Instagram (Apify / DuckDuckGo con validación estricta)
├── stitch_designer.py        # Sintetizador de Design System estilo Stitch (tokens, fuentes, paleta)
├── web_generator.py          # Compilador de landings mobile-first en demos/{slug}/index.html
├── deploy_github_pages.sh    # Script de publicación a GitHub Pages
├── requirements.txt          # Dependencias (google-genai, fastapi, uvicorn, etc.)
├── .env                      # Variables de entorno locales (API Keys y Gmail SMTP)
├── .env.example              # Plantilla con ejemplos de configuración
├── README.md                 # Documentación completa
├── data/
│   └── leads.json            # Base de datos persistente de leads y estados CRM
├── demos/                    # Webs estáticas individuales generadas (GitHub Pages ready)
└── templates/
    ├── index.html            # Dashboard dual (Tabla + Tablero Kanban + Simulador iPhone)
    └── landing_template.html # Plantilla mobile-first con barra WhatsApp fija y mapa
```

---

## 🌐 Endpoints de la API

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/` | Dashboard interactivo (Tabla + Kanban CRM + Simulador móvil) |
| `POST` | `/scan` | Escaneo por Localidad, Provincia o CP con OpenStreetMap + Gemini 3.8 |
| `GET` | `/leads` | Devuelve leads calculando horas transcurridas y alertas >48h |
| `DELETE` | `/leads` | Vacía la base de datos de leads locales |
| `POST` | `/leads/{id}/generate-web` | Extrae Instagram, diseña con Stitch y genera demo en `/demos/{slug}` |
| `POST` | `/leads/{id}/status` | Actualiza estado CRM (*Sin Web, Web Lista, DM Enviado, Respondido, Cerrado*) |
| `POST` | `/leads/{id}/pitch` | Guarda ediciones manuales de los mensajes del Paso 1 y Paso 2 |
| `POST` | `/leads/{id}/send-email` | Envía la propuesta comercial directamente usando Gmail SMTP |
| `POST` | `/leads/{id}/simulate-time` | Simula +50h transcurridas para probar la alerta de seguimiento |
| `GET` | `/demo/{id}` | Redirección directa a la demo del comercio |
| `GET` | `/demos/{slug}` | Servidor de webs demo individuales generadas |
| `GET` | `/export-csv` | Descarga el CSV con leads, enlaces de demo y estados |
| `GET` | `/health` | Chequea el estado del servidor, Gemini y credenciales SMTP |
