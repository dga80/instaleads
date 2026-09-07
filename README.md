# 🚀 InstaLeads AI - Prospección Local Inteligente

Aplicación Full-Stack de prospección comercial local construida con **FastAPI**, **OpenStreetMap (Overpass API + Nominatim)**, **DuckDuckGo** y un **Agente Inteligente potenciado por Google Gemini (`google-genai` SDK con modelo `gemini-2.5-flash`)**.

---

## 🎯 ¿Qué hace InstaLeads?

1. **Búsqueda Geográfica Precisa por Código Postal (CP)**:
   - Resuelve el Código Postal a través de OpenStreetMap / Nominatim.
   - Normaliza la categoría del negocio ingresada en español a las etiquetas oficiales de OpenStreetMap mediante el Agente Gemini.
2. **Filtrado de Oportunidades Reales**:
   - Descarta automáticamente negocios que ya cuentan con página web propia.
   - Detecta perfiles de Instagram asociados (etiquetados en OSM o investigados en DuckDuckGo).
3. **Replicación de Instagram a Web Demo (Mobile-First + Stitch Design System)**:
   - Extrae el avatar, biografía y publicaciones reales de Instagram (con soporte de Apify o fallback curado).
   - Sintetiza un **Design System individualizado** (principios de Google Stitch) con paletas tonales personalizadas, fuentes de Google Fonts de impacto y lenguaje de formas exclusivo para evitar webs clónicas.
   - Genera una landing page responsive autocontenida (`demos/{slug}/index.html`) con barra fija para WhatsApp directo, galería de trabajos y mapa interactivo.
4. **Validación y Pitch Comercial con Demo Interactiva**:
   - **Verificación**: Gemini analiza la correspondencia del perfil.
   - **Pitch con Enlace a la Demo**: Redacta un DM persuasivo que incluye el enlace a su web interactiva para que la miren desde su smartphone.
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

## 🤖 Roles del Agente Gemini en el Backend

### 1. Mapeo de Categorías OSM (`mapear_categoria_osm`)
Gemini convierte la intención del usuario a las etiquetas técnicas de OSM:
```json
// Input: "taller de motos"
// Output de Gemini:
{
  "key": "shop",
  "value": "motorcycle"
}
```

### 2. Verificación de Perfil y Pitch DM (`verificar_y_redactar_pitch`)
Analiza la correspondencia del perfil y genera el pitch:
```json
{
  "es_perfil_correcto": true,
  "razon": "Coincide el nombre comercial y la ubicación en la biografía",
  "mensaje_dm_sugerido": "¡Hola equipo de Motos Madrid! Me encanta el contenido que compartís en vuestro perfil. Noté que aún no disponéis de web propia para centralizar citas de taller y pedidos. ¿Os interesaría ver una propuesta rápida y sin compromiso de cómo quedaría vuestra web profesional? ¡Un saludo!"
}
```

---

## 📁 Estructura del Proyecto

```text
instaleads/
├── app.py                    # Servidor FastAPI, endpoints de escaneo, cadencia y emails
├── instagram_extractor.py    # Extractor Apify de Instagram + fallback fotográfico Unsplash
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
| `POST` | `/scan` | Ejecuta el escaneo de CP y Categoría con OpenStreetMap + Gemini |
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
