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
3. **Validación y Pitch Comercial con Gemini**:
   - **Verificación**: Gemini analiza si el perfil de Instagram encontrado corresponde realmente al negocio local.
   - **Redacción Persuasiva**: Redacta un mensaje directo (DM) de máximo 60 palabras, educado y persuasivo para ofrecerle la creación de su web profesional aprovechando su presencia visual en Instagram.
4. **Persistencia Deduplicada y Exportación**:
   - Almacena los leads en `data/leads.json` sin duplicar negocios ya prospectados.
   - Exportación directa a **CSV** listo para importar en CRM o Excel.

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
   PORT=8000
   HOST=127.0.0.1
   ```

4. **Iniciar el servidor**:
   ```bash
   python app.py
   ```
   O alternativamente con uvicorn:
   ```bash
   uvicorn app:app --reload --port 8000
   ```

5. **Abrir en el navegador**:
   Visita [http://127.0.0.1:8000](http://127.0.0.1:8000)

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
├── app.py                # Servidor FastAPI, endpoints /scan, /leads, agente Gemini
├── requirements.txt      # Dependencias oficiales (google-genai, fastapi, etc.)
├── .env                  # Variables de entorno locales (API Key)
├── .env.example          # Plantilla de configuración
├── README.md             # Documentación del proyecto
├── data/
│   └── leads.json        # Base de datos persistente y deduplicada
└── templates/
    └── index.html        # Frontend en Tailwind CSS interactivo
```

---

## 🌐 Endpoints de la API

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/` | Interfaz de usuario interactiva |
| `POST` | `/scan` | Ejecuta el escaneo de Código Postal y Categoría con Gemini |
| `GET` | `/leads` | Devuelve los leads almacenados en `data/leads.json` |
| `DELETE` | `/leads` | Vacía la base de datos de leads locales |
| `GET` | `/export-csv` | Descarga el CSV con todos los comercios y mensajes DM |
| `GET` | `/health` | Chequea el estado del servidor y si Gemini está configurado |
