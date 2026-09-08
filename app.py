import os
import shutil
import asyncio
import json
import re
import csv
import io
import subprocess
import urllib.parse
import time
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime, timezone, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from web_generator import generar_web_comercio, DEMOS_DIR, slugify

# Cargar variables de entorno desde .env
load_dotenv()

# Inicialización segura de google-genai
try:
    from google import genai
    from google.genai import types
    HAS_GENAI_LIB = True
except ImportError:
    genai = None
    types = None
    HAS_GENAI_LIB = False

# Motor de búsqueda web DuckDuckGo (ddgs moderno / fallback legacy)
try:
    from ddgs import DDGS
    HAS_DDGS = True
except ImportError:
    try:
        from duckduckgo_search import DDGS
        HAS_DDGS = True
    except ImportError:
        HAS_DDGS = False

# Configuración del servidor y carpetas
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
LEADS_FILE = DATA_DIR / "leads.json"
import threading
leads_lock = threading.Lock()

if not LEADS_FILE.exists():
    with open(LEADS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

app = FastAPI(
    title="InstaLeads AI",
    description="Prospección de comercios locales sin web con Agente Gemini y OpenStreetMap",
    version="1.0.0"
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/demos", StaticFiles(directory=str(DEMOS_DIR), html=True), name="demos")

# Servicio centralizado de Gemini con auto-desescalado en cascada
from gemini_service import (
    generar_con_gemini_cascade,
    obtener_cliente_gemini,
    obtener_estado_gemini,
    GEMINI_MODELS_CASCADE
)

GEMINI_MODEL = GEMINI_MODELS_CASCADE[0]  # "gemini-3.8-flash"


# -------------------------------------------------------------
# CONFIGURACIÓN SMTP (GMAIL)
# -------------------------------------------------------------
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "").strip()
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "").strip().replace(" ", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
try:
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
except ValueError:
    SMTP_PORT = 587


def enviar_email_propuesta(destinatario: str, asunto: str, cuerpo_texto: str) -> dict:
    """
    Envía un email comercial o de seguimiento a través de Gmail SMTP.
    Requiere que SMTP_EMAIL y SMTP_APP_PASSWORD estén configurados en .env.
    """
    email_user = os.getenv("SMTP_EMAIL", "").strip()
    app_pwd = os.getenv("SMTP_APP_PASSWORD", "").strip().replace(" ", "")

    if not email_user or not app_pwd or "tu_correo" in email_user:
        raise ValueError(
            "Configura tu cuenta de Gmail en el archivo .env añadiendo:\n"
            "SMTP_EMAIL=tu_correo@gmail.com\n"
            "SMTP_APP_PASSWORD=tu_contraseña_de_aplicacion\n\n"
            "Puedes generar una contraseña de aplicación en https://myaccount.google.com/apppasswords"
        )

    msg = MIMEMultipart("alternative")
    msg["From"] = f"Equipo de Diseño Web <{email_user}>"
    msg["To"] = destinatario
    msg["Subject"] = asunto

    # Texto plano
    part_text = MIMEText(cuerpo_texto, "plain", "utf-8")
    msg.attach(part_text)

    # Versión HTML cuidada y legible
    cuerpo_html = f"""<!DOCTYPE html>
<html>
<body style="margin: 0; padding: 24px; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b;">
  <div style="max-width: 580px; margin: 0 auto; background: #ffffff; border-radius: 12px; padding: 28px; border: 1px solid #e2e8f0; box-shadow: 0 2px 4px rgba(0,0,0,0.04);">
    <div style="font-size: 15px; line-height: 1.6; white-space: pre-line; color: #334155;">{cuerpo_texto}</div>
    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;" />
    <p style="font-size: 12px; color: #64748b; margin: 0;">
      📍 Enviado por un equipo local de diseño web en Barcelona / Cataluña.<br>
      Este correo es una propuesta visual segura sin coste ni compromiso.
    </p>
  </div>
</body>
</html>"""
    part_html = MIMEText(cuerpo_html, "html", "utf-8")
    msg.attach(part_html)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(email_user, app_pwd)
        server.send_message(msg)

    return {"status": "ok", "enviado_a": destinatario}


# -------------------------------------------------------------
# DICCIONARIO DE RESPALDO (Fallback para categorías comunes)
# -------------------------------------------------------------
FALLBACK_OSM_CATEGORIES = {
    "taller de motos": {"key": "shop", "value": "motorcycle"},
    "motos": {"key": "shop", "value": "motorcycle"},
    "taller mecanico": {"key": "shop", "value": "car_repair"},
    "taller de coches": {"key": "shop", "value": "car_repair"},
    "centro de uñas": {"key": "shop", "value": "beauty"},
    "uñas": {"key": "shop", "value": "beauty"},
    "estetica": {"key": "shop", "value": "beauty"},
    "peluqueria": {"key": "shop", "value": "hairdresser"},
    "barberia": {"key": "shop", "value": "hairdresser"},
    "cafeteria": {"key": "amenity", "value": "cafe"},
    "bar": {"key": "amenity", "value": "bar"},
    "restaurante": {"key": "amenity", "value": "restaurant"},
    "clinica dental": {"key": "amenity", "value": "dentist"},
    "dentista": {"key": "amenity", "value": "dentist"},
    "veterinario": {"key": "amenity", "value": "veterinary"},
    "clinica veterinaria": {"key": "amenity", "value": "veterinary"},
    "farmacia": {"key": "amenity", "value": "pharmacy"},
    "panaderia": {"key": "shop", "value": "bakery"},
    "pasteleria": {"key": "shop", "value": "pastry"},
    "floristeria": {"key": "shop", "value": "florist"},
    "gimnasio": {"key": "leisure", "value": "fitness_centre"},
    "tienda de ropa": {"key": "shop", "value": "clothes"},
    "zapateria": {"key": "shop", "value": "shoes"},
    "optica": {"key": "shop", "value": "optician"},
    "tatuajes": {"key": "shop", "value": "tattoo"},
}


# -------------------------------------------------------------
# DETECTOR DE GRANDES CADENAS, FRANQUICIAS Y MULTINACIONALES
# -------------------------------------------------------------
CADENAS_Y_FRANQUICIAS = {
    # Salud y Clínicas Dentales / Estéticas
    "vitaldent", "sanitas", "adeslas", "vivanta", "dorsia", "bocadent", "cleardent",
    "dentix", "instituto dental", "institutos odontologicos", "asisa", "quironsalud",
    "quiron", "dexeus", "vithas", "clinica baviera", "baviera", "dental star", "dentisalut",
    "centros dentalplus", "i-dental", "idental", "eva fertility", "hedonai", "centros unico",
    "laserum", "no+vello", "no mas vello", "clinicas dorsia", "instituto odontologico",
    "propdental", "clínica propdental", "clinica propdental", "clíniques propdental", "cliniques propdental",
    # Restauración y Franquicias de Comida
    "mcdonald", "mcdonald's", "burger king", "telepizza", "domino's", "dominos", "kfc",
    "subway", "starbucks", "100 montaditos", "tagliatella", "la tagliatella", "vips",
    "foster's hollywood", "fosters hollywood", "tgb", "the good burger", "goiko",
    "pans & company", "pans and company", "rodilla", "dunkin", "popeyes", "taco bell",
    "five guys", "udecor", "gloria jean", "poke house", "udon", "saona", "grupo vips",
    "restalia", "pomodoro", "lizarran", "gambrinus", "cañas y tapas", "la sureña",
    # Supermercados y Grandes Superficies
    "mercadona", "carrefour", "dia", "supermercados dia", "lidl", "aldi", "eroski",
    "alcampo", "consum", "bonpreu", "el corte ingles", "hipercor", "clarel", "primor",
    "druni", "sephora", "decathlon", "leroy merlin", "ikea", "media markt", "mediamarkt",
    "brico depot", "bricomart", "bauhaus", "kiwoko", "tiendanimal", "sprinter", "fnac",
    # Fitness y Gimnasios
    "basic-fit", "basic fit", "vivagym", "altafit", "mcfit", "anytime fitness", "fitup",
    "dir", "metropolitan", "crossfit", "brooklyn fitboxing", "synergym", "forus", "duet fit",
    # Peluquerías y Salones en Cadena
    "ebanni", "jean louis david", "marco aldany", "franck provost", "spejo's", "carlos conde",
    "nails factory", "d-uñas", "d uñas", "oh my cut", "llongueras", "provost",
    # Talleres y Automoción
    "midas", "norauto", "feu vert", "euromaster", "first stop", "rodi motor", "carglass",
    "speedy", "confortauto", "bosch car service", "claxon", "driver center",
    # Moda y Textil
    "zara", "pull&bear", "pull and bear", "massimo dutti", "bershka", "stradivarius",
    "oysho", "mango", "h&m", "primark", "springfield", "cortefiel", "calzedonia",
    "intimissimi", "tezenis", "women'secret", "bimba y lola", "desigual", "parfois",
    # Bancos, Seguros e Inmobiliarias
    "caixabank", "la caixa", "santander", "banco santander", "bbva", "banco sabadell",
    "sabadell", "bankinter", "unicaja", "kutxabank", "mapfre", "mutua madrileña",
    "axa", "tecnocasa", "redpiso", "re/max", "century 21", "engel & völkers",
    # Gasolineras y Telefonía
    "repsol", "cepsa", "bp", "shell", "galp", "movistar", "vodafone", "orange", "yoigo"
}


def es_cadena_o_franquicia(nombre: str, tags: dict = None) -> bool:
    """Identifica si un comercio es una franquicia o cadena corporativa grande."""
    tags = tags or {}
    nombre_lower = (nombre or "").lower().strip()
    
    # 1. Etiquetas estándar de OSM que indican marca/franquicia con presencia en Wikidata/Wikipedia
    if tags.get("brand:wikidata") or tags.get("brand:wikipedia"):
        return True
    if tags.get("chain") in ("yes", "true", "1") or tags.get("franchise") in ("yes", "true", "1"):
        return True
        
    brand = tags.get("brand", "").lower().strip()
    operator = tags.get("operator", "").lower().strip()
    
    # 2. Comprobación contra la lista negra de grandes marcas y cadenas
    for c in CADENAS_Y_FRANQUICIAS:
        if c in nombre_lower:
            return True
        if brand and c in brand:
            return True
        if operator and c in operator:
            return True

    return False


# -------------------------------------------------------------
# 1. ROL GEMINI: MAPEAR CATEGORÍA OSM
# -------------------------------------------------------------
def mapear_categoria_osm(termino_usuario: str) -> dict:
    """
    Usa Gemini 2.5 Flash para convertir una categoría ingresada en lenguaje natural (ej. 'taller de motos')
    a la clave y valor exactos de OpenStreetMap (ej. {"key": "shop", "value": "motorcycle"}).
    """
    termino_limpio = termino_usuario.strip().lower()
    
    cliente = obtener_cliente_gemini()
    if cliente:
        prompt = f"""
Actúa como un experto en taxonomías de OpenStreetMap (OSM).
Convierte la siguiente categoría de comercio o negocio en español a la clave ('key') y valor ('value') oficiales más exactos de OSM (por ejemplo 'shop', 'amenity', 'craft', 'leisure', etc.).

Reglas:
- Devuelve EXCLUSIVAMENTE un objeto JSON válido con las propiedades 'key' y 'value'.
- No agregues explicaciones, bloques de markdown ni texto extra.

Ejemplos:
- "taller de motos" -> {{"key": "shop", "value": "motorcycle"}}
- "centro de uñas" -> {{"key": "shop", "value": "beauty"}}
- "peluqueria canina" -> {{"key": "shop", "value": "pet"}}
- "clinica dental" -> {{"key": "amenity", "value": "dentist"}}
- "gimnasio de boxeo" -> {{"key": "leisure", "value": "fitness_centre"}}

Categoría a clasificar: "{termino_usuario}"
"""
        try:
            texto, modelo_usado = generar_con_gemini_cascade(prompt, cliente=cliente, temperatura=0.1, formato_json=True)
            if texto:
                # Limpiar posible markdown en caso de que venga con comillas triples
                texto_limpio = re.sub(r"^```(json)?", "", texto, flags=re.MULTILINE).strip("` \n")
                data = json.loads(texto_limpio)
                if "key" in data and "value" in data:
                    print(f"[Gemini OSM Mapping] '{termino_usuario}' -> {data} (usando {modelo_usado})")
                    return {"key": data["key"], "value": data["value"], "modelo": modelo_usado}
        except Exception as e:
            print(f"[Error Gemini OSM Mapping] {e}. Usando fallback local...")

    # Fallback local heurístico si Gemini no está disponible o falla
    for clave, valor in FALLBACK_OSM_CATEGORIES.items():
        if clave in termino_limpio or termino_limpio in clave:
            return valor

    # Valor por defecto
    return {"key": "shop", "value": termino_limpio.replace(" ", "_")}


# -------------------------------------------------------------
# 2. ROL GEMINI: VERIFICAR PERFIL Y REDACTAR PITCH DE VENTA
# -------------------------------------------------------------
def verificar_y_redactar_pitch(nombre_negocio: str, datos_presencia: str, ciudad: str, demo_url: str = "", tiene_ig: bool = True) -> dict:
    """
    Analiza el negocio local y su presencia digital (Instagram, Doctoralia, Facebook, directorios) y genera:
    1. Mensaje de prospección comercial inicial (cercano, elogiando su trabajo/reputación, explicando que somos
       un equipo local de diseño que busca comercios en su zona para mejorar su captación móvil, con frase anti-malware).
    2. Mensaje de seguimiento (para enviar a las 48-72h por Email o WhatsApp si no han contestado).
    Utiliza gemini-3.8-flash y auto-desescalado a 3.7, 3.5 y 2.5 si hay saturación.
    """
    cliente = obtener_cliente_gemini()
    demo_texto = f"la maqueta interactiva segura que os preparé: {demo_url}" if demo_url else "la propuesta visual"

    contexto_tipo = "perfil de Instagram detectado" if tiene_ig else "huella digital y presencia en internet detectada (Doctoralia, Facebook, directorios)"
    canal_contacto = "Instagram DM" if tiene_ig else "Email / WhatsApp / Formulario"

    if cliente:
        prompt = f"""
Actúa como un estratega de prospección comercial B2B y auditor de negocios locales en España.
Analiza con rigor crítico este negocio local y los datos de su {contexto_tipo}:

Negocio local buscado:
- Nombre: {nombre_negocio}
- Localidad / Ciudad: {ciudad}

Datos de presencia encontrados en internet:
{datos_presencia}

Debes evaluar y responder:
1. 'es_gran_cadena': true si es una gran cadena corporativa, franquicia nacional/multinacional, aseguradora o gran empresa (ejemplos: Vitaldent, Sanitas, Adeslas, Vivanta, Dentix, Dorsia, McDonald's, Midas, etc.). False si es un comercio o clínica local independiente.
2. 'es_perfil_correcto': true si los datos corresponden CLARAMENTE a este negocio ({nombre_negocio} en {ciudad}). Si los datos son de una marca ajena o negocio sin relación de otra localidad lejana, devuelve false.
3. 'tiene_web_oficial': true si entre los datos/enlaces detectas que el negocio YA tiene una página web propia activa oficial (ej: clinicadentalbarcelona.com, gesclident.com). False si NO tiene web propia (solo directorios genéricos, páginas amarillas o redes sociales).
4. 'web_oficial_url': La URL de su página web oficial si 'tiene_web_oficial' es true, o cadena vacía "" si no tiene.
5. 'razon': Justificación breve y directa de tu decisión (ej: 'Coincide clínica local en {ciudad}', 'Descartado por ser gran franquicia nacional', 'Comercio local verificado sin web propia', o 'Tiene página web oficial activa').
6. 'mensaje_dm_sugerido': Si 'es_perfil_correcto' es true Y 'es_gran_cadena' es false, redacta la propuesta de primer contacto para {canal_contacto} (máximo 60 palabras, tono cercano, profesional, equipo local de diseño en su zona, enlace seguro a la maqueta {demo_url or 'https://...'} sin registros ni descargas). En caso contrario, devuelve cadena vacía "".
7. 'mensaje_seguimiento': Si 'es_perfil_correcto' es true Y 'es_gran_cadena' es false, redacta el seguimiento educado a las 48-72h. En caso contrario, devuelve cadena vacía "".

Devuelve ÚNICAMENTE un JSON con esta estructura:
{{
  "es_gran_cadena": false,
  "es_perfil_correcto": true,
  "tiene_web_oficial": false,
  "web_oficial_url": "",
  "razon": "Coincide el negocio y ubicación",
  "mensaje_dm_sugerido": "¡Hola equipo de {nombre_negocio}! Me alegra contactaros. Somos un equipo local de diseño web en {ciudad} y vemos que tenéis un gran potencial para recibir más clientes directos en Google y móvil. Os hemos preparado una maqueta interactiva adaptada a vuestro negocio: {demo_url or 'https://...'}. Es un enlace 100% seguro para verla en el navegador sin descargas. ¿Qué os parece?",
  "mensaje_seguimiento": "¡Hola de nuevo! Os escribí hace un par de días con una maqueta web interactiva para vuestro negocio: {demo_url or 'https://...'}. Os lo comparto por aquí por si os resulta cómodo revisarlo desde el móvil. ¡Un saludo cordial!"
}}
"""
        try:
            texto, modelo_usado = generar_con_gemini_cascade(prompt, cliente=cliente, temperatura=0.2, formato_json=True)
            if texto:
                texto_limpio = re.sub(r"^```(json)?", "", texto, flags=re.MULTILINE).strip("` \n")
                data = json.loads(texto_limpio)
                print(f"[Gemini Pitch] '{nombre_negocio}' evaluado con éxito (modelo: {modelo_usado})")
                return {
                    "es_gran_cadena": bool(data.get("es_gran_cadena", False)),
                    "es_perfil_correcto": bool(data.get("es_perfil_correcto", True)),
                    "tiene_web_oficial": bool(data.get("tiene_web_oficial", False)),
                    "web_oficial_url": str(data.get("web_oficial_url", "")).strip(),
                    "razon": str(data.get("razon", "Evaluación completada")),
                    "mensaje_dm_sugerido": str(data.get("mensaje_dm_sugerido", "")),
                    "mensaje_seguimiento": str(data.get("mensaje_seguimiento", "")),
                    "modelo_usado": modelo_usado
                }
        except Exception as e:
            print(f"[Error Gemini Pitch] {e}. Usando plantilla fallback...")

    # Fallback si no hay API key de Gemini
    link_texto = f" {demo_url}" if demo_url else ""
    if tiene_ig:
        pitch_dm_fallback = (
            f"¡Hola equipo de {nombre_negocio}! Me encantan vuestros trabajos en Instagram. "
            f"Somos un equipo local de diseño y estamos seleccionando comercios con gran potencial en vuestra zona de {ciudad} para ayudarles a conseguir más clientes desde Google. "
            f"Os he preparado una maqueta interactiva de cómo luciría vuestra web:{link_texto} "
            f"(El enlace es 100% seguro para navegarlo desde el móvil sin registros ni descargas). ¿Podéis echarle un ojo a ver qué os parece? ¡Un saludo!"
        )
    else:
        pitch_dm_fallback = (
            f"¡Hola equipo de {nombre_negocio}! Os contactamos desde un equipo local de diseño web en {ciudad}. "
            f"Hemos estado revisando negocios con buenas referencias en vuestra zona y os hemos preparado una maqueta interactiva móvil para vuestra clínica:{link_texto} "
            f"(Es un enlace 100% seguro sin registros para verlo en el navegador). ¿Os gustaría que conversemos 2 minutos sin compromiso? ¡Un saludo!"
        )

    seguimiento_fallback = (
        f"¡Hola de nuevo equipo de {nombre_negocio}! Os escribí hace unos días con una propuesta web interactiva para vuestro negocio:{link_texto} "
        f"Os lo comparto por aquí por si os resulta más cómodo revisarlo desde el teléfono. ¿Os gustaría que hablemos 2 minutos sin compromiso? ¡Un saludo cordial!"
    )
    return {
        "es_gran_cadena": False,
        "es_perfil_correcto": True,
        "razon": "Validación automática heurística",
        "mensaje_dm_sugerido": pitch_dm_fallback,
        "mensaje_seguimiento": seguimiento_fallback
    }


# -------------------------------------------------------------
# 3. OPENSTREETMAP: BÚSQUEDA POR CÓDIGO POSTAL Y ETIQUETA
# -------------------------------------------------------------
# Lista de espejos públicos de Overpass para garantizar alta disponibilidad
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter"
]

def obtener_bounding_box_ubicacion(
    localidad: str = "",
    provincia: str = "",
    codigo_postal: str = ""
) -> Optional[Dict[str, Any]]:
    """
    Consulta Nominatim para obtener el bounding box y datos geográficos
    a partir de localidad/municipio, provincia y/o código postal en España.
    """
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "InstaLeads-App/1.0 (local-prospecting-tool)"}
    
    # 1. Búsqueda estructurada
    params = {
        "country": "Spain",
        "format": "json",
        "addressdetails": 1,
        "limit": 1
    }
    if codigo_postal:
        params["postalcode"] = codigo_postal
    if localidad:
        params["city"] = localidad
    if provincia:
        params["county"] = provincia

    items = []
    try:
        r = requests.get(url, params=params, headers=headers, timeout=6)
        if r.status_code == 200 and r.json():
            items = r.json()
    except Exception as e:
        print(f"[Nominatim Structured Warning] {e}")

    # 2. Fallback no estructurado si la consulta estructurada no arrojó resultados
    if not items:
        partes = [p for p in [localidad, provincia, codigo_postal, "España"] if p]
        if partes:
            q_str = ", ".join(partes)
            try:
                r = requests.get(
                    url,
                    params={
                        "q": q_str,
                        "countrycodes": "es",
                        "format": "json",
                        "addressdetails": 1,
                        "limit": 1
                    },
                    headers=headers,
                    timeout=6
                )
                if r.status_code == 200 and r.json():
                    items = r.json()
            except Exception as e:
                print(f"[Nominatim Fallback Warning] {e}")

    if items:
        item = items[0]
        bbox = item.get("boundingbox")
        addr = item.get("address", {})
        
        ciudad = (
            addr.get("city") or
            addr.get("town") or
            addr.get("municipality") or
            addr.get("village") or
            localidad or
            "España"
        )
        prov = (
            addr.get("state_district") or
            addr.get("province") or
            addr.get("county") or
            provincia or
            ""
        )
        cp = addr.get("postcode") or codigo_postal or ""
        lat = float(item.get("lat", 0)) if item.get("lat") else None
        lon = float(item.get("lon", 0)) if item.get("lon") else None

        if bbox and len(bbox) == 4:
            return {
                "south": float(bbox[0]),
                "north": float(bbox[1]),
                "west": float(bbox[2]),
                "east": float(bbox[3]),
                "lat": lat,
                "lon": lon,
                "ciudad": ciudad,
                "provincia": prov,
                "codigo_postal": cp
            }
    return None


def obtener_bounding_box_cp(codigo_postal: str) -> Optional[Dict[str, Any]]:
    """Función de compatibilidad que redirige a obtener_bounding_box_ubicacion."""
    return obtener_bounding_box_ubicacion(codigo_postal=codigo_postal)


def consultar_overpass(
    codigo_postal: str = "",
    osm_key: str = "",
    osm_value: str = "",
    localidad: str = "",
    provincia: str = "",
    max_resultados: int = 50
) -> List[Dict[str, Any]]:
    """
    Ejecuta una consulta Overpass QL buscando elementos que coincidan con la clave/valor de OSM
    dentro de la localidad, provincia o código postal especificados.
    Dispone de failover automático entre múltiples espejos públicos de Overpass.
    """
    geo_data = obtener_bounding_box_ubicacion(
        localidad=localidad,
        provincia=provincia,
        codigo_postal=codigo_postal
    )
    
    ciudad_default = (geo_data["ciudad"] if geo_data else None) or localidad or "España"
    provincia_default = (geo_data["provincia"] if geo_data else None) or provincia or ""
    cp_default = (geo_data["codigo_postal"] if geo_data else None) or codigo_postal or ""

    if geo_data:
        lat = geo_data.get("lat")
        lon = geo_data.get("lon")
        if codigo_postal and lat and lon:
            # Para Código Postal, utilizamos un radio focalizado de 1400m para no capturar municipios vecinos
            query = f"""
            [out:json][timeout:30];
            (
              node["{osm_key}"="{osm_value}"](around:1400, {lat}, {lon});
              way["{osm_key}"="{osm_value}"](around:1400, {lat}, {lon});
            );
            out center tags {max_resultados};
            """
        else:
            s, n, w, e = geo_data["south"], geo_data["north"], geo_data["west"], geo_data["east"]
            query = f"""
            [out:json][timeout:30];
            (
              node["{osm_key}"="{osm_value}"]({s},{w},{n},{e});
              way["{osm_key}"="{osm_value}"]({s},{w},{n},{e});
            );
            out center tags {max_resultados};
            """
    else:
        # Fallback de búsqueda directa por atributos en OSM
        condiciones = []
        if codigo_postal:
            condiciones.extend([
                f'node["addr:postcode"="{codigo_postal}"]["{osm_key}"="{osm_value}"];',
                f'way["addr:postcode"="{codigo_postal}"]["{osm_key}"="{osm_value}"];',
                f'node["postal_code"="{codigo_postal}"]["{osm_key}"="{osm_value}"];'
            ])
        if localidad:
            condiciones.extend([
                f'node["addr:city"~"^{localidad}$",i]["{osm_key}"="{osm_value}"];',
                f'way["addr:city"~"^{localidad}$",i]["{osm_key}"="{osm_value}"];'
            ])
        if not condiciones:
            condiciones = [
                f'node["{osm_key}"="{osm_value}"];',
                f'way["{osm_key}"="{osm_value}"];'
            ]
        
        bloque_query = "\n  ".join(condiciones)
        query = f"""
        [out:json][timeout:30];
        (
          {bloque_query}
        );
        out center tags {max_resultados};
        """

    headers = {"User-Agent": "InstaLeads-App/1.0 (local-prospecting-tool)"}
    
    # Intento secuencial entre espejos Overpass
    for endpoint in OVERPASS_ENDPOINTS:
        try:
            resp = requests.post(endpoint, data={"data": query}, headers=headers, timeout=25)
            if resp.status_code == 200:
                elementos = resp.json().get("elements", [])
                resultados = []
                for el in elementos:
                    tags = el.get("tags", {})
                    nombre = tags.get("name") or tags.get("brand") or tags.get("operator")
                    if not nombre:
                        continue  # Si no tiene nombre comercial público no es útil para prospección

                    # FILTRAR: Excluir si ya tiene página web propia
                    website = tags.get("website") or tags.get("contact:website") or tags.get("url")
                    if website and ("instagram.com" not in website.lower()):
                        continue

                    # FILTRAR: Excluir grandes cadenas, franquicias o corporaciones
                    if es_cadena_o_franquicia(nombre, tags):
                        print(f"      [Filtro Cadena] Ignorado '{nombre}' por ser gran cadena o franquicia.")
                        continue

                    # FILTRAR: Si se buscó un CP específico, descartar nodos cuyo código postal o ciudad difiera claramente
                    if codigo_postal:
                        node_cp = tags.get("addr:postcode", "").strip()
                        if node_cp and node_cp != codigo_postal:
                            continue
                        node_city = tags.get("addr:city", "").strip().lower()
                        if node_city and ciudad_default and node_city != ciudad_default.lower() and ciudad_default.lower() not in node_city:
                            continue

                    calle = tags.get("addr:street", "")
                    numero = tags.get("addr:housenumber", "")
                    direccion = f"{calle} {numero}".strip() if calle else tags.get("address", "")
                    
                    ciudad = tags.get("addr:city") or ciudad_default
                    prov_res = tags.get("addr:province") or provincia_default
                    cp_res = tags.get("addr:postcode") or cp_default
                    telefono = tags.get("phone") or tags.get("contact:phone") or tags.get("contact:mobile", "")
                    email = tags.get("email") or tags.get("contact:email", "")
                    
                    ig_osm = tags.get("contact:instagram") or tags.get("instagram", "")

                    resultados.append({
                        "osm_id": str(el.get("id")),
                        "nombre": nombre.strip(),
                        "categoria": f"{osm_key}: {osm_value}",
                        "direccion": direccion,
                        "ciudad": ciudad,
                        "provincia": prov_res,
                        "codigo_postal": cp_res,
                        "telefono": telefono,
                        "email": email,
                        "tiene_web": False,
                        "instagram_tag_osm": ig_osm,
                        "tags": tags
                    })
                return resultados
            else:
                print(f"[Overpass Warning] Servidor {endpoint} respondió con status {resp.status_code}. Probando siguiente espejo...")
        except Exception as e:
            print(f"[Overpass Error] Fallo al consultar {endpoint}: {e}. Probando siguiente espejo...")

    return []


# -------------------------------------------------------------
# 4. BUSCADOR DE PERFIL DE INSTAGRAM (OSM / DuckDuckGo)
# -------------------------------------------------------------
def extraer_handle_ig(url_or_handle: str) -> tuple[str, str]:
    """
    Limpia y normaliza un enlace o handle de Instagram.
    NUNCA devuelve enlaces ajenos (como sitios web propios, revistas o blogs).
    """
    if not url_or_handle:
        return "", ""
    
    url_or_handle = url_or_handle.strip()
    
    rutas_prohibidas = {
        "p", "reel", "reels", "stories", "explore", "tv", "accounts",
        "developer", "about", "legal", "directory", "graphql", "channel",
        "tags", "location", "share", "direct", "privacy", "help"
    }

    # 1. Si contiene instagram.com
    if "instagram.com" in url_or_handle.lower():
        match = re.search(r"instagram\.com/([a-zA-Z0-9_\.\-]+)", url_or_handle, re.IGNORECASE)
        if match:
            handle = match.group(1).rstrip("/").lower()
            if handle not in rutas_prohibidas and re.match(r"^[a-zA-Z0-9_\.]{2,35}$", handle):
                return f"@{handle}", f"https://www.instagram.com/{handle}/"
        return "", ""

    # 2. Si viene precedido por @ (ej. @clinica_dental)
    if url_or_handle.startswith("@"):
        handle = url_or_handle.lstrip("@").strip().lower()
        if re.match(r"^[a-zA-Z0-9_\.]{2,35}$", handle) and handle not in rutas_prohibidas:
            return f"@{handle}", f"https://www.instagram.com/{handle}/"
        return "", ""

    # 3. Si viene solo un handle alfanumérico limpio (desde etiqueta OSM contact:instagram)
    if not url_or_handle.startswith("http") and "/" not in url_or_handle and "." not in url_or_handle:
        handle = url_or_handle.lower().strip()
        if re.match(r"^[a-zA-Z0-9_\.]{2,35}$", handle) and handle not in rutas_prohibidas:
            return f"@{handle}", f"https://www.instagram.com/{handle}/"

    # En cualquier otro caso (enlace externo, web corporativa, etc.), NO es Instagram
    return "", ""


def clasificar_fuente_web(url: str, titulo: str = "") -> dict:
    url_lower = url.lower()

    if "instagram.com" in url_lower:
        return {"tipo": "instagram", "label": "Instagram", "icono": "📸", "url": url, "titulo": titulo}
    elif "facebook.com" in url_lower:
        return {"tipo": "facebook", "label": "Facebook", "icono": "👥", "url": url, "titulo": titulo}
    elif "doctoralia.es" in url_lower or "doctoralia.com" in url_lower:
        return {"tipo": "doctoralia", "label": "Doctoralia", "icono": "🩺", "url": url, "titulo": titulo}
    elif any(x in url_lower for x in ["topdoctors.es", "topdentistas", "dentalia"]):
        return {"tipo": "topdoctors", "label": "Top Doctors / Dentistas", "icono": "👨‍⚕️", "url": url, "titulo": titulo}
    elif "linkedin.com" in url_lower:
        return {"tipo": "linkedin", "label": "LinkedIn", "icono": "💼", "url": url, "titulo": titulo}
    elif any(x in url_lower for x in ["setmore.com", "treatwell", "reservas", "booking"]):
        return {"tipo": "reserva", "label": "Citas Online", "icono": "📅", "url": url, "titulo": titulo}
    elif any(x in url_lower for x in [
        "paginasamarillas.es", "qdq.com", "empresite", "einforma.com", "axesor.es",
        "mejoresclinicas.com", "espainfo.com", "geodruid.com", "mapaclinicas.com",
        "citacentrodesalud.com", "centreodontologic", "cylex", "infocif", "vulka",
        "metropoliabierta", "guias.es", "dentavacation", "medicaltourismco", "eixsagradafamilia"
    ]):
        return {"tipo": "directorio", "label": "Directorio Local", "icono": "📁", "url": url, "titulo": titulo}
    else:
        return {"tipo": "web", "label": "Sitio Web", "icono": "🌐", "url": url, "titulo": titulo}


def investigar_presencia_negocio(nombre: str, ciudad: str, ig_osm: str = "") -> dict:
    """
    Investiga a fondo la presencia digital de un negocio:
    1. Perfil de Instagram (vía OSM o DuckDuckGo con matching por tokens)
    2. Fuentes de internet alternativas (Facebook, Doctoralia, directorios, etc.)
    3. Enlaces directos 1-click a Google Search y Google Maps
    4. Detección de posibles webs existentes en internet
    """
    nom_limpio = nombre.strip()
    ciu_limpia = ciudad.strip()
    q_encoded = urllib.parse.quote_plus(f"{nom_limpio} {ciu_limpia}")
    google_search_url = f"https://www.google.com/search?q={q_encoded}"
    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={q_encoded}"

    res_ig = {"encontrado": False, "handle": "", "url": "", "datos_crudos": ""}
    enlaces_internet = []
    web_detectada = ""

    # 1. Si viene en etiqueta OSM
    if ig_osm:
        handle, url = extraer_handle_ig(ig_osm)
        if handle and url:
            res_ig = {
                "encontrado": True,
                "handle": handle,
                "url": url,
                "datos_crudos": f"Etiquetado en OpenStreetMap: {ig_osm}"
            }
            enlaces_internet.append({
                "tipo": "instagram",
                "label": "Instagram (OSM)",
                "icono": "📸",
                "url": url,
                "titulo": f"Instagram @{handle}",
                "snippet": "Perfil oficial enlazado en OpenStreetMap"
            })

    if not HAS_DDGS:
        return {
            "instagram": res_ig,
            "enlaces_internet": enlaces_internet,
            "web_detectada": web_detectada,
            "google_search_url": google_search_url,
            "google_maps_url": google_maps_url
        }

    # Tokens clave del negocio para validación
    todos_tokens = [t for t in re.sub(r"[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ]", " ", nom_limpio.lower()).split() if len(t) >= 3]
    stopwords = {
        "dr", "dra", "carrer", "calle", "avenida", "avda", "del", "los", "las", "les", "dels",
        "taller", "peluqueria", "bar", "restaurant", "restaurante", "centro", "centre"
    }
    tokens_negocio = [t for t in todos_tokens if t not in stopwords]
    if not tokens_negocio:
        tokens_negocio = todos_tokens

    try:
        with DDGS() as ddgs:
            # A) Si aún no tenemos Instagram, buscar con DDG
            if not res_ig["encontrado"]:
                query_ig = f"site:instagram.com {nom_limpio} {ciu_limpia}"
                try:
                    resultados_ig = ddgs.text(query_ig, region="es-es", max_results=4)
                    for r in resultados_ig:
                        href = r.get("href", "")
                        title = r.get("title", "")
                        body = r.get("body", "")

                        if "instagram.com" not in href.lower():
                            continue

                        handle, url = extraer_handle_ig(href)
                        if handle and url:
                            texto_busqueda = (handle + " " + title + " " + body).lower()
                            coincide = False
                            if not tokens_negocio:
                                if ciu_limpia.lower() in texto_busqueda:
                                    coincide = True
                            else:
                                for tok in tokens_negocio:
                                    if tok in texto_busqueda:
                                        coincide = True
                                        break

                            if coincide:
                                res_ig = {
                                    "encontrado": True,
                                    "handle": handle,
                                    "url": url,
                                    "datos_crudos": f"Título: {title} | Snippet: {body} | URL: {url}"
                                }
                                enlaces_internet.append({
                                    "tipo": "instagram",
                                    "label": f"Instagram ({handle})",
                                    "icono": "📸",
                                    "url": url,
                                    "titulo": title or f"Perfil {handle}",
                                    "snippet": body[:120] if body else ""
                                })
                                break
                except Exception as e_ig:
                    print(f"[DDG IG Search Error para '{nombre}'] {e_ig}")

            time.sleep(0.3)

            # B) Buscar presencia general en internet (Doctoralia, Facebook, directorios, etc.)
            query_general = f"{nom_limpio} {ciu_limpia}"
            try:
                resultados_gen = ddgs.text(query_general, region="es-es", max_results=6)
                vistos_urls = {res_ig["url"].rstrip("/")} if res_ig["url"] else set()

                for r in resultados_gen:
                    href = r.get("href", "")
                    title = r.get("title", "")
                    body = r.get("body", "")
                    clean_href = href.rstrip("/")

                    if not clean_href or clean_href in vistos_urls:
                        continue
                    vistos_urls.add(clean_href)

                    # Si es Instagram y no lo teníamos
                    if "instagram.com" in href.lower() and not res_ig["encontrado"]:
                        handle, url = extraer_handle_ig(href)
                        if handle and url:
                            res_ig = {
                                "encontrado": True,
                                "handle": handle,
                                "url": url,
                                "datos_crudos": f"Título: {title} | Snippet: {body} | URL: {url}"
                            }
                            enlaces_internet.append({
                                "tipo": "instagram",
                                "label": f"Instagram ({handle})",
                                "icono": "📸",
                                "url": url,
                                "titulo": title or f"Perfil {handle}",
                                "snippet": body[:120] if body else ""
                            })
                            continue

                    fuente = clasificar_fuente_web(href, title)
                    fuente["snippet"] = body[:120] if body else ""

                    # Si parece ser su propia web oficial (ej. www.clinicadentalbarcelona.com)
                    if fuente["tipo"] == "web" and not web_detectada:
                        domain = urllib.parse.urlparse(href).netloc.lower().replace("www.", "")
                        nom_compacto = re.sub(r"[^a-z0-9]", "", nom_limpio.lower())
                        if any(tok in domain for tok in tokens_negocio if len(tok) >= 3) or (nom_compacto and nom_compacto in domain):
                            web_detectada = href
                            fuente["label"] = "Sitio Web Detectado"

                    enlaces_internet.append(fuente)
            except Exception as e_gen:
                print(f"[DDG General Search Error para '{nombre}'] {e_gen}")

    except Exception as e:
        print(f"[DDG Global Error para '{nombre}'] {e}")

    return {
        "instagram": res_ig,
        "enlaces_internet": enlaces_internet[:6],
        "web_detectada": web_detectada,
        "google_search_url": google_search_url,
        "google_maps_url": google_maps_url
    }


def buscar_instagram_negocio(nombre: str, ciudad: str, ig_osm: str = "") -> dict:
    """Función de compatibilidad que redirige a investigar_presencia_negocio."""
    presencia = investigar_presencia_negocio(nombre, ciudad, ig_osm)
    return presencia["instagram"]


# -------------------------------------------------------------
# 5. PERSISTENCIA DEDUPLICADA DE LEADS (data/leads.json)
# -------------------------------------------------------------
def leer_leads_guardados() -> List[Dict[str, Any]]:
    try:
        with open(LEADS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def detectar_demo_existente(nombre: str, ciudad: str = "") -> Optional[str]:
    """Comprueba si ya existe una demo compilada previamente en disco demos/{slug}/index.html"""
    slugs = []
    nom_limpio = (nombre or "").strip()
    ciu_limpia = (ciudad or "").strip()
    if nom_limpio and ciu_limpia:
        slugs.append(slugify(f"{nom_limpio}-{ciu_limpia}"))
    if nom_limpio:
        slugs.append(slugify(nom_limpio))

    for s in slugs:
        if s and (DEMOS_DIR / s / "index.html").exists():
            return s
    return None


def guardar_leads_deduplicados(nuevos_leads: List[Dict[str, Any]]) -> int:
    with leads_lock:
        existentes = leer_leads_guardados()
        # Claves únicas para deduplicación: (nombre normalizado, ciudad normalizada)
        mapa = {}
        for l in existentes:
            k = (l.get("nombre", "").lower().strip(), l.get("ciudad", "").lower().strip())
            mapa[k] = l

        agregados = 0
        for l in nuevos_leads:
            k = (l.get("nombre", "").lower().strip(), l.get("ciudad", "").lower().strip())
            if k in mapa:
                existente = mapa[k]
                # Preservar demo previa y estado avanzado si ya existían
                if existente.get("demo_slug"):
                    l["demo_slug"] = existente.get("demo_slug")
                    l["demo_url"] = existente.get("demo_url", "")
                    l["demo_url_absoluta"] = existente.get("demo_url_absoluta", "")
                    l["demo_vibe"] = existente.get("demo_vibe", "")
                    if existente.get("estado") in ["Web Generada", "DM Enviado", "Respuesta Recibida", "Cerrado"]:
                        l["estado"] = existente.get("estado")
                else:
                    # Comprobar si existe demo en disco
                    slug_existente = detectar_demo_existente(l.get("nombre", ""), l.get("ciudad", ""))
                    if slug_existente:
                        l["demo_slug"] = slug_existente
                        l["demo_url"] = f"/demos/{slug_existente}"
                        if l.get("estado") in ["Sin Web", "Tiene Web"]:
                            l["estado"] = "Web Generada"

                mapa[k].update(l)
            else:
                # Comprobar si existe demo en disco para nuevo lead
                slug_existente = detectar_demo_existente(l.get("nombre", ""), l.get("ciudad", ""))
                if slug_existente:
                    l["demo_slug"] = slug_existente
                    l["demo_url"] = f"/demos/{slug_existente}"
                    if l.get("estado") in ["Sin Web", "Tiene Web"]:
                        l["estado"] = "Web Generada"

                mapa[k] = l
                agregados += 1

        lista_final = list(mapa.values())
        with open(LEADS_FILE, "w", encoding="utf-8") as f:
            json.dump(lista_final, f, ensure_ascii=False, indent=2)

        return agregados


# -------------------------------------------------------------
# 6. MODELOS PYDANTIC Y ENDPOINTS FASTAPI
# -------------------------------------------------------------
class ScanRequest(BaseModel):
    codigo_postal: Optional[str] = ""
    localidad: Optional[str] = ""
    provincia: Optional[str] = ""
    categoria: str
    max_comercios: int = 20


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal de la aplicación."""
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/health")
async def health_check():
    """Estado del servidor y verificación de la API de Gemini y SMTP."""
    load_dotenv(override=True)
    estado_gemini = obtener_estado_gemini()
    smtp_user = os.getenv("SMTP_EMAIL", "").strip()
    smtp_pwd = os.getenv("SMTP_APP_PASSWORD", "").strip()
    smtp_ok = bool(smtp_user and smtp_pwd and "tu_correo" not in smtp_user)
    return {
        "status": "ok",
        "gemini_configurado": estado_gemini["configurado"],
        "modelo": estado_gemini["modelo_primario"],
        "cascada": estado_gemini["cascada"],
        "duckduckgo_disponible": HAS_DDGS,
        "google_genai_instalado": estado_gemini["sdk_instalado"],
        "smtp_configurado": smtp_ok,
        "smtp_email": smtp_user if smtp_ok else ""
    }


def calcular_prioridad_lead(lead: dict) -> tuple:
    tiene_web = bool(lead.get("tiene_web") or lead.get("web_detectada") or lead.get("estado") == "Tiene Web")
    tiene_ig = bool(lead.get("instagram_url") or lead.get("instagram_handle"))
    tiene_enlaces = bool(lead.get("enlaces_internet") and len(lead["enlaces_internet"]) > 0)
    
    if tiene_ig and not tiene_web:
        return (100, "🔥 Alta Prioridad")
    elif not tiene_web and tiene_enlaces:
        return (60, "⚡ Prioridad Media")
    elif not tiene_web:
        return (30, "⚪ Sin Web")
    else:
        return (10, "🌐 Ya Tiene Web")


@app.get("/leads")
def get_leads():
    """Devuelve todos los leads calculando el tiempo transcurrido, alertas de seguimiento temporal y ordenados por prioridad de prospección."""
    leads = leer_leads_guardados()
    now = datetime.now(timezone.utc)
    for l in leads:
        score, label = calcular_prioridad_lead(l)
        l["prioridad_score"] = score
        l["prioridad_label"] = label

        fc_str = l.get("fecha_contacto")
        horas_transcurridas = 0
        alerta_seguimiento = False
        if fc_str:
            try:
                fc = datetime.fromisoformat(fc_str.replace("Z", "+00:00"))
                if fc.tzinfo is None:
                    fc = fc.replace(tzinfo=timezone.utc)
                horas_transcurridas = round((now - fc).total_seconds() / 3600, 1)
                # Si el estado es 'DM Enviado' y han pasado 48h o más sin respuesta
                if l.get("estado") == "DM Enviado" and horas_transcurridas >= 48:
                    alerta_seguimiento = True
            except Exception:
                pass
        l["horas_transcurridas"] = horas_transcurridas
        l["alerta_seguimiento"] = alerta_seguimiento

        # Auto-detectar demo previamente existente en disco
        if not l.get("demo_slug"):
            slug_existente = detectar_demo_existente(l.get("nombre", ""), l.get("ciudad", ""))
            if slug_existente:
                l["demo_slug"] = slug_existente
                l["demo_url"] = f"/demos/{slug_existente}"
                if l.get("estado") in ["Sin Web", "Tiene Web"]:
                    l["estado"] = "Web Generada"

        # Compatibilidad: asegurar URLs de búsqueda directa y enlaces_internet
        if not l.get("google_search_url") and l.get("nombre"):
            q_enc = urllib.parse.quote_plus(f"{l['nombre']} {l.get('ciudad', '')}")
            l["google_search_url"] = f"https://www.google.com/search?q={q_enc}"
        if not l.get("google_maps_url") and l.get("nombre"):
            q_enc = urllib.parse.quote_plus(f"{l['nombre']} {l.get('ciudad', '')}")
            l["google_maps_url"] = f"https://www.google.com/maps/search/?api=1&query={q_enc}"
        if "enlaces_internet" not in l:
            l["enlaces_internet"] = []

    # Ordenar por prioridad descendente: Con IG y Sin Web primero (100 -> 60 -> 30 -> 10)
    leads.sort(key=lambda x: x.get("prioridad_score", 0), reverse=True)
    return leads


@app.delete("/leads")
def clear_leads():
    """Vacía la lista de leads guardados."""
    with leads_lock:
        with open(LEADS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    return {"status": "ok", "mensaje": "Base de datos de leads reiniciada."}


@app.post("/scan")
def scan_local_leads(req: ScanRequest):
    """
    Orquesta el pipeline completo de prospección:
    1. Normaliza la categoría a etiquetas OSM con Gemini (con auto-desescalado desde gemini-3.8-flash).
    2. Consulta OpenStreetMap (por localidad, provincia y/o código postal) filtrando negocios sin web.
    3. Descubre o extrae el perfil de Instagram y huella en internet (Doctoralia, Facebook, etc.).
    4. Verifica con Gemini y redacta el pitch comercial adaptado (DM o Email/WhatsApp).
    5. Deduplica y persiste en data/leads.json.
    """
    cp = (req.codigo_postal or "").strip()
    loc = (req.localidad or "").strip()
    prov = (req.provincia or "").strip()
    cat_usuario = req.categoria.strip()

    if not cat_usuario:
        raise HTTPException(status_code=400, detail="La categoría de negocio es obligatoria.")

    if not cp and not loc and not prov:
        raise HTTPException(
            status_code=400,
            detail="Debes especificar al menos un dato de ubicación: Localidad / Municipio, Provincia o Código Postal."
        )

    ubicacion_texto = ", ".join([p for p in [loc, prov, f"CP {cp}" if cp else ""] if p])

    print(f"\n[1/4] Mapeando categoría '{cat_usuario}' con Gemini...")
    osm_tag = mapear_categoria_osm(cat_usuario)
    osm_key = osm_tag["key"]
    osm_value = osm_tag["value"]

    print(f"[2/4] Buscando comercios en OSM ({ubicacion_texto}, {osm_key}={osm_value})...")
    comercios = consultar_overpass(
        codigo_postal=cp,
        osm_key=osm_key,
        osm_value=osm_value,
        localidad=loc,
        provincia=prov,
        max_resultados=50
    )
    print(f"      Encontrados {len(comercios)} comercios sin web propia.")

    if not comercios:
        return {
            "status": "ok",
            "categoria_osm": osm_tag,
            "nuevos_leads_encontrados": 0,
            "mensaje": f"No se encontraron comercios sin página web con la etiqueta OSM '{osm_key}={osm_value}' en {ubicacion_texto}."
        }

    # Limitar para respetar cuotas de búsqueda y generación
    comercios_a_procesar = comercios[:req.max_comercios]
    prospectos_procesados = []

    print(f"[3/4 y 4/4] Investigando presencia online, verificando y generando pitch con Gemini...")
    for com in comercios_a_procesar:
        time.sleep(0.5)
        nombre = com["nombre"]
        ciudad = com.get("ciudad") or loc or "Local"
        prov_lead = com.get("provincia") or prov or ""
        ig_osm = com.get("instagram_tag_osm", "")
        calle = com.get("direccion", "")

        nombre_para_buscar = f"{nombre} {calle}".strip() if nombre.lower().strip() in ["clínica dental", "clinica dental", "dentista", "peluqueria", "taller"] and calle else nombre

        # Investigar huella en internet (Instagram, Facebook, Doctoralia, directorios, etc.)
        presencia = investigar_presencia_negocio(nombre_para_buscar, ciudad, ig_osm)
        ig_info = presencia["instagram"]
        enlaces_internet = presencia["enlaces_internet"]
        web_detectada = presencia["web_detectada"]
        google_search_url = presencia["google_search_url"]
        google_maps_url = presencia["google_maps_url"]

        # Si encontramos perfil de Instagram, consultamos a Gemini para evaluar IG
        if ig_info["encontrado"]:
            analisis = verificar_y_redactar_pitch(nombre, ig_info["datos_crudos"], ciudad, tiene_ig=True)
        elif enlaces_internet:
            # Si no tiene Instagram pero encontramos huella digital en internet
            resumen_enlaces = "\n".join([f"- {e['label']}: {e['url']} | {e.get('titulo', '')} {e.get('snippet', '')}" for e in enlaces_internet])
            analisis = verificar_y_redactar_pitch(nombre, resumen_enlaces, ciudad, tiene_ig=False)
        else:
            analisis = {
                "es_gran_cadena": False,
                "es_perfil_correcto": False,
                "razon": "No se detectó perfil de Instagram ni presencia web directa en el rastreo inicial",
                "mensaje_dm_sugerido": "",
                "mensaje_seguimiento": ""
            }

        # 1. Filtro estricto: Descartar si es gran cadena / franquicia detectada por Gemini o por nombre/tags
        if analisis.get("es_gran_cadena") or es_cadena_o_franquicia(nombre, com.get("tags")):
            print(f"      [Descarte Cadena] Omitido '{nombre}' por ser gran cadena o franquicia.")
            continue

        # 2. Configurar perfil y pitch según si tiene Instagram o presencia web alternativa
        if ig_info["encontrado"] and not analisis.get("es_perfil_correcto"):
            ig_url = ""
            ig_handle = ""
            mensaje_dm = ""
            mensaje_seguimiento = ""
            razon = analisis.get("razon", "Perfil de Instagram no coincidente")
        elif ig_info["encontrado"] and analisis.get("es_perfil_correcto"):
            ig_url = ig_info["url"]
            ig_handle = ig_info["handle"]
            mensaje_dm = analisis.get("mensaje_dm_sugerido", "")
            mensaje_seguimiento = analisis.get("mensaje_seguimiento", "")
            razon = analisis.get("razon", "Perfil de Instagram verificado y coincidente")
        elif enlaces_internet:
            ig_url = ""
            ig_handle = ""
            mensaje_dm = analisis.get("mensaje_dm_sugerido", "")
            mensaje_seguimiento = analisis.get("mensaje_seguimiento", "")
            nombres_fuentes = ", ".join(list(dict.fromkeys([e['label'] for e in enlaces_internet])))
            razon = f"Sin Instagram. Presencia online detectada ({len(enlaces_internet)} fuentes: {nombres_fuentes})"
        else:
            ig_url = ""
            ig_handle = ""
            mensaje_dm = ""
            mensaje_seguimiento = ""
            razon = "Sin Instagram ni presencia web detectada"

        # Si Gemini o DuckDuckGo detectaron una web oficial
        if analisis.get("tiene_web_oficial") and analisis.get("web_oficial_url"):
            web_detectada = analisis["web_oficial_url"]

        tiene_web_real = bool(web_detectada or analisis.get("tiene_web_oficial"))

        lead = {
            "osm_id": com["osm_id"],
            "nombre": nombre,
            "categoria": f"{cat_usuario} ({osm_key}:{osm_value})",
            "direccion": com["direccion"],
            "ciudad": ciudad,
            "provincia": prov_lead,
            "codigo_postal": com["codigo_postal"],
            "telefono": com["telefono"],
            "email": com.get("email", ""),
            "tiene_web": tiene_web_real,
            "instagram_url": ig_url,
            "instagram_handle": ig_handle,
            "enlaces_internet": enlaces_internet,
            "web_detectada": web_detectada,
            "google_search_url": google_search_url,
            "google_maps_url": google_maps_url,
            "gemini_verificado": bool(analisis.get("es_perfil_correcto")),
            "gemini_razon": razon,
            "mensaje_dm": mensaje_dm,
            "mensaje_seguimiento": mensaje_seguimiento,
            "estado": "Tiene Web" if tiene_web_real else "Sin Web",
            "demo_slug": "",
            "demo_url": "",
            "demo_vibe": ""
        }
        prospectos_procesados.append(lead)

    # Persistir deduplicando
    agregados = guardar_leads_deduplicados(prospectos_procesados)
    print(f"      Pipeline completado. {agregados} leads nuevos agregados a data/leads.json.")

    return {
        "status": "ok",
        "categoria_osm": osm_tag,
        "total_procesados": len(prospectos_procesados),
        "nuevos_leads_encontrados": agregados,
        "leads": prospectos_procesados
    }


@app.post("/scan-stream")
async def scan_local_leads_stream(req: ScanRequest):
    """
    Streaming en tiempo real vía Server-Sent Events (SSE) del pipeline de prospección:
    Emite eventos conforme se mapea la categoría, se descubren comercios en OSM y
    se evalúa / persiste cada lead de forma incremental sin esperar al lote completo.
    """
    cp = (req.codigo_postal or "").strip()
    loc = (req.localidad or "").strip()
    prov = (req.provincia or "").strip()
    cat_usuario = req.categoria.strip()

    if not cat_usuario:
        raise HTTPException(status_code=400, detail="La categoría de negocio es obligatoria.")

    if not cp and not loc and not prov:
        raise HTTPException(
            status_code=400,
            detail="Debes especificar al menos un dato de ubicación: Localidad / Municipio, Provincia o Código Postal."
        )

    ubicacion_texto = ", ".join([p for p in [loc, prov, f"CP {cp}" if cp else ""] if p])

    async def stream_events():
        def sse(payload: dict) -> str:
            return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

        yield sse({
            "type": "step",
            "step": 1,
            "total_steps": 4,
            "message": f"Mapeando categoría '{cat_usuario}' con Gemini..."
        })

        try:
            osm_tag = await asyncio.to_thread(mapear_categoria_osm, cat_usuario)
        except Exception as e:
            osm_tag = {"key": "amenity", "value": "restaurant", "label": cat_usuario}

        osm_key = osm_tag.get("key", "amenity")
        osm_value = osm_tag.get("value", "restaurant")

        yield sse({
            "type": "step",
            "step": 2,
            "total_steps": 4,
            "categoria_osm": osm_tag,
            "message": f"Buscando comercios en OpenStreetMap ({ubicacion_texto}, {osm_key}={osm_value})..."
        })

        try:
            comercios = await asyncio.to_thread(
                consultar_overpass,
                codigo_postal=cp,
                osm_key=osm_key,
                osm_value=osm_value,
                localidad=loc,
                provincia=prov,
                max_resultados=50
            )
        except Exception as e:
            yield sse({
                "type": "error",
                "message": f"Error al consultar OpenStreetMap: {str(e)}"
            })
            return

        if not comercios:
            yield sse({
                "type": "complete",
                "status": "ok",
                "categoria_osm": osm_tag,
                "nuevos_leads_encontrados": 0,
                "total_procesados": 0,
                "message": f"No se encontraron comercios sin página web con la etiqueta OSM '{osm_key}={osm_value}' en {ubicacion_texto}."
            })
            return

        comercios_a_procesar = comercios[:req.max_comercios]
        total_a_procesar = len(comercios_a_procesar)

        yield sse({
            "type": "step",
            "step": 3,
            "total_steps": 4,
            "total_encontrados_osm": len(comercios),
            "total_a_procesar": total_a_procesar,
            "message": f"Encontrados {len(comercios)} comercios en OSM. Analizando presencia digital ({total_a_procesar} a evaluar)..."
        })

        total_agregados = 0
        prospectos_procesados = []

        for idx, com in enumerate(comercios_a_procesar, start=1):
            nombre = com["nombre"]
            ciudad = com.get("ciudad") or loc or "Local"
            prov_lead = com.get("provincia") or prov or ""
            ig_osm = com.get("instagram_tag_osm", "")
            calle = com.get("direccion", "")

            yield sse({
                "type": "progress",
                "step": 4,
                "index": idx,
                "total": total_a_procesar,
                "nombre": nombre,
                "ciudad": ciudad,
                "message": f"[{idx}/{total_a_procesar}] Analizando presencia online de '{nombre}'..."
            })

            def procesar_un_comercio():
                nombre_para_buscar = f"{nombre} {calle}".strip() if nombre.lower().strip() in ["clínica dental", "clinica dental", "dentista", "peluqueria", "taller"] and calle else nombre
                presencia = investigar_presencia_negocio(nombre_para_buscar, ciudad, ig_osm)
                ig_info = presencia["instagram"]
                enlaces_internet = presencia["enlaces_internet"]
                web_detectada = presencia["web_detectada"]
                google_search_url = presencia["google_search_url"]
                google_maps_url = presencia["google_maps_url"]

                if ig_info["encontrado"]:
                    analisis = verificar_y_redactar_pitch(nombre, ig_info["datos_crudos"], ciudad, tiene_ig=True)
                elif enlaces_internet:
                    resumen_enlaces = "\n".join([f"- {e['label']}: {e['url']} | {e.get('titulo', '')} {e.get('snippet', '')}" for e in enlaces_internet])
                    analisis = verificar_y_redactar_pitch(nombre, resumen_enlaces, ciudad, tiene_ig=False)
                else:
                    analisis = {
                        "es_gran_cadena": False,
                        "es_perfil_correcto": False,
                        "razon": "No se detectó perfil de Instagram ni presencia web directa en el rastreo inicial",
                        "mensaje_dm_sugerido": "",
                        "mensaje_seguimiento": ""
                    }

                if analisis.get("es_gran_cadena") or es_cadena_o_franquicia(nombre, com.get("tags")):
                    return None, "Gran cadena o franquicia detectada"

                if ig_info["encontrado"] and not analisis.get("es_perfil_correcto"):
                    ig_url = ""
                    ig_handle = ""
                    mensaje_dm = ""
                    mensaje_seguimiento = ""
                    razon = analisis.get("razon", "Perfil de Instagram no coincidente")
                elif ig_info["encontrado"] and analisis.get("es_perfil_correcto"):
                    ig_url = ig_info["url"]
                    ig_handle = ig_info["handle"]
                    mensaje_dm = analisis.get("mensaje_dm_sugerido", "")
                    mensaje_seguimiento = analisis.get("mensaje_seguimiento", "")
                    razon = analisis.get("razon", "Perfil de Instagram verificado y coincidente")
                elif enlaces_internet:
                    ig_url = ""
                    ig_handle = ""
                    mensaje_dm = analisis.get("mensaje_dm_sugerido", "")
                    mensaje_seguimiento = analisis.get("mensaje_seguimiento", "")
                    nombres_fuentes = ", ".join(list(dict.fromkeys([e['label'] for e in enlaces_internet])))
                    razon = f"Sin Instagram. Presencia online detectada ({len(enlaces_internet)} fuentes: {nombres_fuentes})"
                else:
                    ig_url = ""
                    ig_handle = ""
                    mensaje_dm = ""
                    mensaje_seguimiento = ""
                    razon = "Sin Instagram ni presencia web detectada"

                if analisis.get("tiene_web_oficial") and analisis.get("web_oficial_url"):
                    web_detectada = analisis["web_oficial_url"]

                tiene_web_real = bool(web_detectada or analisis.get("tiene_web_oficial"))

                lead = {
                    "osm_id": com["osm_id"],
                    "nombre": nombre,
                    "categoria": f"{cat_usuario} ({osm_key}:{osm_value})",
                    "direccion": com["direccion"],
                    "ciudad": ciudad,
                    "provincia": prov_lead,
                    "codigo_postal": com["codigo_postal"],
                    "telefono": com["telefono"],
                    "email": com.get("email", ""),
                    "tiene_web": tiene_web_real,
                    "instagram_url": ig_url,
                    "instagram_handle": ig_handle,
                    "enlaces_internet": enlaces_internet,
                    "web_detectada": web_detectada,
                    "google_search_url": google_search_url,
                    "google_maps_url": google_maps_url,
                    "gemini_verificado": bool(analisis.get("es_perfil_correcto")),
                    "gemini_razon": razon,
                    "mensaje_dm": mensaje_dm,
                    "mensaje_seguimiento": mensaje_seguimiento,
                    "estado": "Tiene Web" if tiene_web_real else "Sin Web",
                    "demo_slug": "",
                    "demo_url": "",
                    "demo_vibe": ""
                }
                return lead, None

            lead_res, motivo_descarte = await asyncio.to_thread(procesar_un_comercio)

            if lead_res is None:
                yield sse({
                    "type": "skipped",
                    "index": idx,
                    "total": total_a_procesar,
                    "nombre": nombre,
                    "razon": motivo_descarte or "Omitido"
                })
            else:
                agregado = await asyncio.to_thread(guardar_leads_deduplicados, [lead_res])
                total_agregados += agregado
                prospectos_procesados.append(lead_res)

                # Leer lead con datos persistidos
                yield sse({
                    "type": "lead",
                    "index": idx,
                    "total": total_a_procesar,
                    "lead": lead_res,
                    "agregado_nuevo": bool(agregado > 0),
                    "message": f"Lead procesado: {nombre}"
                })

            await asyncio.sleep(0.05)

        yield sse({
            "type": "complete",
            "status": "ok",
            "categoria_osm": osm_tag,
            "total_procesados": len(prospectos_procesados),
            "nuevos_leads_encontrados": total_agregados,
            "message": f"¡Escaneo finalizado con éxito! {total_agregados} nuevas oportunidades agregadas."
        })

    return StreamingResponse(
        stream_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


class StatusUpdateRequest(BaseModel):
    estado: str


@app.post("/leads/{osm_id}/generate-web")
def generate_lead_web(osm_id: str, request: Request):
    """
    Genera la web demo individualizada para un lead usando:
    1. Extracción de datos de Instagram (Apify o fallback adaptado).
    2. Design System estilo Stitch (colores, fuentes y formas).
    3. Estructuración con Gemini.
    4. Guardado en demos/{slug}/index.html (GitHub Pages ready).
    5. Actualización del pitch de prospección con el enlace de la demo.
    """
    leads = leer_leads_guardados()
    target_lead = None
    for l in leads:
        if str(l.get("osm_id")) == str(osm_id):
            target_lead = dict(l)
            break

    if target_lead is None:
        raise HTTPException(status_code=404, detail="Lead no encontrado.")

    # Comprobar si la demo ya existía previamente
    slug_existente = target_lead.get("demo_slug") or detectar_demo_existente(target_lead.get("nombre", ""), target_lead.get("ciudad", ""))
    ya_existia = bool(slug_existente and (DEMOS_DIR / slug_existente / "index.html").exists())

    cliente_gemini = obtener_cliente_gemini()
    res = generar_web_comercio(target_lead, cliente_gemini=cliente_gemini)

    base_url = str(request.base_url).rstrip("/")
    demo_url_absoluta = f"{base_url}/demos/{res['slug']}/"

    # Actualizar lead
    target_lead["demo_slug"] = res["slug"]
    target_lead["demo_url"] = res["demo_url_local"]
    target_lead["demo_url_absoluta"] = demo_url_absoluta
    target_lead["demo_vibe"] = res["design_vibe"]
    if target_lead.get("estado") in ["Sin Web", "Tiene Web"]:
        target_lead["estado"] = "Web Generada"

    # Regenerar el pitch comercial incorporando la URL de la demo
    nuevo_pitch = verificar_y_redactar_pitch(
        nombre_negocio=target_lead.get("nombre", ""),
        datos_presencia=f"Instagram: {target_lead.get('instagram_url', '')} | Categoría: {target_lead.get('categoria', '')}",
        ciudad=target_lead.get("ciudad", ""),
        demo_url=demo_url_absoluta
    )
    target_lead["mensaje_dm"] = nuevo_pitch.get("mensaje_dm_sugerido", target_lead.get("mensaje_dm", ""))
    target_lead["mensaje_seguimiento"] = nuevo_pitch.get("mensaje_seguimiento", target_lead.get("mensaje_seguimiento", ""))

    with leads_lock:
        fresh_leads = leer_leads_guardados()
        target_idx = None
        for idx, l in enumerate(fresh_leads):
            if str(l.get("osm_id")) == str(osm_id):
                target_idx = idx
                break
        if target_idx is not None:
            fresh_leads[target_idx] = target_lead
        else:
            fresh_leads.append(target_lead)
        with open(LEADS_FILE, "w", encoding="utf-8") as f:
            json.dump(fresh_leads, f, ensure_ascii=False, indent=2)

    return {
        "status": "ok",
        "ya_existia": ya_existia,
        "lead": target_lead,
        "demo": res
    }


@app.delete("/leads/{osm_id}/demo")
@app.post("/leads/{osm_id}/delete-demo")
def delete_lead_demo(osm_id: str):
    """
    Elimina la web demo generada para un lead:
    1. Borra la carpeta física en demos/{slug} si existe en disco.
    2. Resetea los metadatos de demo en el lead (demo_slug, demo_url, demo_vibe, estado).
    3. Regenera el pitch de prospección sin el enlace de la demo.
    4. Guarda los cambios de forma concurrente y atómica.
    """
    with leads_lock:
        leads = leer_leads_guardados()
        target_idx = None
        target_lead = None
        for idx, l in enumerate(leads):
            if str(l.get("osm_id")) == str(osm_id):
                target_idx = idx
                target_lead = l
                break

        if target_lead is None:
            raise HTTPException(status_code=404, detail="Lead no encontrado.")

        slug = target_lead.get("demo_slug") or detectar_demo_existente(target_lead.get("nombre", ""), target_lead.get("ciudad", ""))
        
        # Eliminar carpeta física en disco si existe
        if slug:
            demo_folder = DEMOS_DIR / slug
            if demo_folder.exists() and demo_folder.is_dir():
                try:
                    shutil.rmtree(demo_folder)
                    print(f"[Demo Cleaner] ✓ Carpeta eliminada: {demo_folder}")
                except Exception as e:
                    print(f"[Demo Cleaner Error] al borrar {slug}: {e}")

        # Resetear estado y metadatos de demo
        target_lead["demo_slug"] = ""
        target_lead["demo_url"] = ""
        target_lead["demo_url_absoluta"] = ""
        target_lead["demo_vibe"] = ""
        if target_lead.get("estado") == "Web Generada":
            target_lead["estado"] = "Tiene Web" if target_lead.get("tiene_web") else "Sin Web"

        # Limpiar URLs de la demo en los mensajes existentes de forma instantánea
        if target_lead.get("mensaje_dm"):
            target_lead["mensaje_dm"] = re.sub(r"https?://[^\s]+/demos/[^\s]+", "", target_lead["mensaje_dm"]).replace("  ", " ").strip()
        if target_lead.get("mensaje_seguimiento"):
            target_lead["mensaje_seguimiento"] = re.sub(r"https?://[^\s]+/demos/[^\s]+", "", target_lead["mensaje_seguimiento"]).replace("  ", " ").strip()

        leads[target_idx] = target_lead
        with open(LEADS_FILE, "w", encoding="utf-8") as f:
            json.dump(leads, f, ensure_ascii=False, indent=2)

        return {
            "status": "ok",
            "message": f"Web demo de '{target_lead.get('nombre')}' eliminada correctamente.",
            "lead": target_lead
        }


@app.post("/demos/cleanup-all")
def cleanup_all_demos():
    """Elimina todas las carpetas de demos en disco y resetea las referencias en los leads."""
    with leads_lock:
        leads = leer_leads_guardados()
        # Eliminar carpetas físicas en demos/ (excepto ocultas o index de galería)
        eliminadas = 0
        if DEMOS_DIR.exists():
            for item in DEMOS_DIR.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    try:
                        shutil.rmtree(item)
                        eliminadas += 1
                    except Exception as e:
                        print(f"Error borrando {item}: {e}")
        
        # Resetear leads
        for l in leads:
            l["demo_slug"] = ""
            l["demo_url"] = ""
            l["demo_url_absoluta"] = ""
            l["demo_vibe"] = ""
            if l.get("estado") == "Web Generada":
                l["estado"] = "Tiene Web" if l.get("tiene_web") else "Sin Web"
            if l.get("mensaje_dm"):
                l["mensaje_dm"] = re.sub(r"https?://[^\s]+/demos/[^\s]+", "", l["mensaje_dm"]).replace("  ", " ").strip()
            if l.get("mensaje_seguimiento"):
                l["mensaje_seguimiento"] = re.sub(r"https?://[^\s]+/demos/[^\s]+", "", l["mensaje_seguimiento"]).replace("  ", " ").strip()

        with open(LEADS_FILE, "w", encoding="utf-8") as f:
            json.dump(leads, f, ensure_ascii=False, indent=2)

        return {"status": "ok", "message": f"Se han eliminado {eliminadas} demos correctamente."}


class PitchSaveRequest(BaseModel):
    mensaje_dm: str
    mensaje_seguimiento: Optional[str] = ""


@app.post("/leads/{osm_id}/pitch")
def save_lead_pitch(osm_id: str, req: PitchSaveRequest):
    """Guarda las ediciones personalizadas que el usuario realiza sobre el DM o seguimiento."""
    with leads_lock:
        leads = leer_leads_guardados()
        for l in leads:
            if str(l.get("osm_id")) == str(osm_id):
                l["mensaje_dm"] = req.mensaje_dm.strip()
                if req.mensaje_seguimiento:
                    l["mensaje_seguimiento"] = req.mensaje_seguimiento.strip()
                with open(LEADS_FILE, "w", encoding="utf-8") as f:
                    json.dump(leads, f, ensure_ascii=False, indent=2)
                return {"status": "ok", "lead": l}
    raise HTTPException(status_code=404, detail="Lead no encontrado.")


@app.post("/leads/{osm_id}/status")
def update_lead_status(osm_id: str, req: StatusUpdateRequest):
    """Actualiza el estado de prospección del lead y registra la fecha de contacto."""
    with leads_lock:
        leads = leer_leads_guardados()
        for l in leads:
            if str(l.get("osm_id")) == str(osm_id):
                l["estado"] = req.estado
                if req.estado in ("DM Enviado", "Email Enviado") and not l.get("fecha_contacto"):
                    l["fecha_contacto"] = datetime.now(timezone.utc).isoformat()
                    l["canal_contacto"] = "Instagram DM" if "DM" in req.estado else "Email"
                with open(LEADS_FILE, "w", encoding="utf-8") as f:
                    json.dump(leads, f, ensure_ascii=False, indent=2)
                return {"status": "ok", "lead": l}
    raise HTTPException(status_code=404, detail="Lead no encontrado.")


@app.post("/leads/{osm_id}/simulate-time")
def simulate_lead_time(osm_id: str):
    """Simula que han transcurrido 50 horas desde el contacto para comprobar la alerta de seguimiento."""
    with leads_lock:
        leads = leer_leads_guardados()
        for l in leads:
            if str(l.get("osm_id")) == str(osm_id):
                hace_50h = datetime.now(timezone.utc) - timedelta(hours=50)
                l["fecha_contacto"] = hace_50h.isoformat()
                l["estado"] = "DM Enviado"
                with open(LEADS_FILE, "w", encoding="utf-8") as f:
                    json.dump(leads, f, ensure_ascii=False, indent=2)
                return {"status": "ok", "mensaje": "Simuladas 50 horas para el lead.", "lead": l}
    raise HTTPException(status_code=404, detail="Lead no encontrado.")


class EmailSendRequest(BaseModel):
    email_destino: str
    asunto: Optional[str] = ""
    mensaje: str


@app.post("/leads/{osm_id}/send-email")
def send_lead_email(osm_id: str, req: EmailSendRequest):
    """
    Envía la propuesta comercial o seguimiento directamente al correo del negocio
    usando la cuenta Gmail configurada por el usuario.
    """
    leads = leer_leads_guardados()
    target_idx = None
    target_lead = None
    for idx, l in enumerate(leads):
        if str(l.get("osm_id")) == str(osm_id):
            target_idx = idx
            target_lead = l
            break

    if target_lead is None:
        raise HTTPException(status_code=404, detail="Lead no encontrado.")

    email_limpio = req.email_destino.strip()
    if not email_limpio or "@" not in email_limpio:
        raise HTTPException(status_code=400, detail="Debes proporcionar una dirección de email válida.")

    asunto = req.asunto.strip() if req.asunto else f"Propuesta web interactiva para {target_lead.get('nombre', 'vuestro negocio')}"

    try:
        enviar_email_propuesta(
            destinatario=email_limpio,
            asunto=asunto,
            cuerpo_texto=req.mensaje.strip()
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar correo por Gmail SMTP: {str(e)}")

    # Actualizar estado y fecha en el CRM
    target_lead["email"] = email_limpio
    target_lead["estado"] = "Email Enviado"
    if not target_lead.get("fecha_contacto"):
        target_lead["fecha_contacto"] = datetime.now(timezone.utc).isoformat()
    target_lead["canal_contacto"] = "Email"

    leads[target_idx] = target_lead
    with open(LEADS_FILE, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)

    return {
        "status": "ok",
        "mensaje": f"Correo enviado exitosamente a {email_limpio}",
        "lead": target_lead
    }


def ejecutar_despliegue_github_pages() -> dict:
    """
    Sincroniza y despliega la carpeta demos/ en la rama 'gh-pages' de GitHub.
    Calcula la URL pública de GitHub Pages y actualiza las demos y pitches.
    """
    demos_path = BASE_DIR / "demos"
    if not demos_path.exists() or not any(demos_path.iterdir()):
        raise HTTPException(
            status_code=400,
            detail="No hay demos generadas en la carpeta 'demos/'. Genera al menos una web demo primero."
        )

    # 1. Crear archivo .nojekyll en demos/
    nojekyll = demos_path / ".nojekyll"
    if not nojekyll.exists():
        nojekyll.touch()

    # 2. Generar index.html centralizado en demos/ para que la raíz de GitHub Pages no dé 404
    leads = leer_leads_guardados()
    demos_leads = [l for l in leads if l.get("demo_slug")]

    items_html = ""
    for dl in demos_leads:
        items_html += f"""
        <li style="margin-bottom: 12px; padding: 16px; background: #1e293b; border-radius: 12px; border: 1px solid #334155; display: flex; justify-content: space-between; align-items: center;">
          <div>
            <div style="font-weight: bold; font-size: 16px; color: #f8fafc;">{dl.get('nombre', 'Comercio')}</div>
            <div style="color: #94a3b8; font-size: 13px; margin-top: 2px;">{dl.get('categoria', '')} · {dl.get('ciudad', '')}</div>
          </div>
          <a href="./{dl['demo_slug']}/" style="background: linear-gradient(135deg, #ec4899, #8b5cf6); color: #ffffff; text-decoration: none; padding: 8px 16px; border-radius: 8px; font-weight: 600; font-size: 13px;">Ver Demo &rarr;</a>
        </li>"""

    index_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>InstaLeads Demos Showcase</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0b0f19; color: #f8fafc; padding: 40px 16px; margin: 0; }}
    .container {{ max-width: 620px; margin: 0 auto; }}
    ul {{ list-style: none; padding: 0; margin-top: 24px; }}
  </style>
</head>
<body>
  <div class="container">
    <h1 style="font-size: 26px; margin-bottom: 6px; font-weight: 800;">🚀 Portafolio de Webs Demo</h1>
    <p style="color: #94a3b8; font-size: 14px; margin-top: 0;">Sitios web interactivos diseñados para comercios locales por nuestro equipo.</p>
    <ul>{items_html or '<li style="color: #64748b; padding: 16px;">No hay comercios generados aún.</li>'}</ul>
  </div>
</body>
</html>"""
    with open(demos_path / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    # 3. Detectar remote URL de origin
    try:
        remote_proc = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=str(BASE_DIR),
            check=True,
            capture_output=True,
            text=True
        )
        remote_url = remote_proc.stdout.strip()
    except Exception:
        remote_url = "https://github.com/dga80/instaleads.git"

    # Calcular base pública de GitHub Pages
    gh_pages_base = ""
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?", remote_url)
    if m:
        user = m.group(1)
        repo = m.group(2)
        gh_pages_base = f"https://{user}.github.io/{repo}"
    else:
        gh_pages_base = os.getenv("GITHUB_PAGES_BASE_URL", "https://dga80.github.io/instaleads")
    
    gh_pages_base = gh_pages_base.rstrip("/")

    # 4. Git add & commit de demos/
    try:
        subprocess.run(["git", "add", "demos/"], cwd=str(BASE_DIR), check=True, capture_output=True, text=True)
        diff_proc = subprocess.run(["git", "diff-index", "--quiet", "HEAD", "--", "demos"], cwd=str(BASE_DIR))
        if diff_proc.returncode != 0:
            subprocess.run(
                ["git", "commit", "-m", "chore(demos): actualizar webs demo para GitHub Pages"],
                cwd=str(BASE_DIR),
                check=True,
                capture_output=True,
                text=True
            )

        # 5. Obtener hash del commit de demos/ con git subtree split
        split_proc = subprocess.run(
            ["git", "subtree", "split", "--prefix", "demos", "HEAD"],
            cwd=str(BASE_DIR),
            check=True,
            capture_output=True,
            text=True
        )
        commit_hash = split_proc.stdout.strip().splitlines()[-1]

        # 6. Push a la rama gh-pages de origin
        push_proc = subprocess.run(
            ["git", "push", "origin", f"{commit_hash}:refs/heads/gh-pages", "--force"],
            cwd=str(BASE_DIR),
            check=True,
            capture_output=True,
            text=True
        )

        # 7. Actualizar leads en data/leads.json con la URL pública activa
        leads_actualizados = 0
        for l in leads:
            slug = l.get("demo_slug")
            if slug:
                public_demo_url = f"{gh_pages_base}/{slug}/"
                old_demo_url = l.get("demo_url_absoluta", "")
                l["demo_url_absoluta"] = public_demo_url
                l["demo_url_publica"] = public_demo_url

                # Actualizar DM y Seguimiento sustituyendo la URL local por la URL pública
                if old_demo_url and old_demo_url in l.get("mensaje_dm", ""):
                    l["mensaje_dm"] = l["mensaje_dm"].replace(old_demo_url, public_demo_url)
                else:
                    l["mensaje_dm"] = re.sub(r"http://[^/]+/demos/[a-zA-Z0-9_-]+", public_demo_url, l.get("mensaje_dm", ""))

                if old_demo_url and old_demo_url in l.get("mensaje_seguimiento", ""):
                    l["mensaje_seguimiento"] = l["mensaje_seguimiento"].replace(old_demo_url, public_demo_url)
                else:
                    l["mensaje_seguimiento"] = re.sub(r"http://[^/]+/demos/[a-zA-Z0-9_-]+", public_demo_url, l.get("mensaje_seguimiento", ""))

                leads_actualizados += 1

        with open(LEADS_FILE, "w", encoding="utf-8") as f:
            json.dump(leads, f, ensure_ascii=False, indent=2)

        return {
            "status": "ok",
            "mensaje": "¡Demos publicadas con éxito en GitHub Pages!",
            "github_pages_url": gh_pages_base,
            "demos_actualizadas": leads_actualizados,
            "commit": commit_hash[:7]
        }

    except subprocess.CalledProcessError as err:
        err_msg = err.stderr or err.stdout or str(err)
        print(f"[Error Deploy GitHub Pages] {err_msg}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al desplegar en GitHub Pages: {err_msg.strip()}"
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Error inesperado durante el despliegue: {str(ex)}")


@app.post("/deploy-github-pages")
def deploy_github_pages_endpoint():
    """Endpoint llamado desde el botón de la UI para publicar las demos en GitHub Pages."""
    return ejecutar_despliegue_github_pages()


@app.get("/demo/{osm_id}")
def redirect_to_demo(osm_id: str):
    """Redirige directamente a la demo del lead si existe."""
    leads = leer_leads_guardados()
    for l in leads:
        if str(l.get("osm_id")) == str(osm_id) and l.get("demo_slug"):
            return HTMLResponse(content=f'<script>window.location.href="/demos/{l["demo_slug"]}";</script>')
    raise HTTPException(status_code=404, detail="Demo aún no generada para este lead.")


@app.get("/export-csv")
def export_leads_csv():
    """Genera y descarga un archivo CSV con todos los leads registrados."""
    leads = leer_leads_guardados()
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

    # Cabeceras del CSV
    writer.writerow([
        "Nombre del Negocio",
        "Categoría",
        "Dirección",
        "Ciudad",
        "Código Postal",
        "Teléfono",
        "Instagram Handle",
        "Instagram URL",
        "Verificado por Gemini",
        "Razón de Validación",
        "Estado",
        "Web Demo URL",
        "Vibe de Diseño",
        "Mensaje de Venta DM"
    ])

    for l in leads:
        writer.writerow([
            l.get("nombre", ""),
            l.get("categoria", ""),
            l.get("direccion", ""),
            l.get("ciudad", ""),
            l.get("codigo_postal", ""),
            l.get("telefono", ""),
            l.get("instagram_handle", ""),
            l.get("instagram_url", ""),
            "Sí" if l.get("gemini_verificado") else "No",
            l.get("gemini_razon", ""),
            l.get("estado", "Sin Web"),
            l.get("demo_url_absoluta", l.get("demo_url", "")),
            l.get("demo_vibe", ""),
            l.get("mensaje_dm", "")
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leads_instagram.csv"}
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8085))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Iniciando InstaLeads AI en http://{host}:{port}")
    uvicorn.run("app:app", host=host, port=port, reload=True)
