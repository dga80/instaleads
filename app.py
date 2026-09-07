import os
import json
import re
import csv
import io
import subprocess
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

from web_generator import generar_web_comercio, DEMOS_DIR

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

# DuckDuckGo Search para descubrimiento de perfiles
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

# Modelo sugerido de Gemini
GEMINI_MODEL = "gemini-2.5-flash"

def obtener_cliente_gemini():
    """Obtiene una instancia del cliente oficial google-genai si la API key está configurada."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not HAS_GENAI_LIB or not api_key or api_key == "tu_api_key_aqui":
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"[Aviso Gemini] No se pudo inicializar el cliente: {e}")
        return None


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
            config = None
            if types and hasattr(types, "GenerateContentConfig"):
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            
            response = cliente.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=config
            )
            
            texto = response.text.strip()
            # Limpiar posible markdown en caso de que venga con comillas triples
            texto = re.sub(r"^```(json)?", "", texto, flags=re.MULTILINE).strip("` \n")
            data = json.loads(texto)
            if "key" in data and "value" in data:
                print(f"[Gemini OSM Mapping] '{termino_usuario}' -> {data}")
                return {"key": data["key"], "value": data["value"]}
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
def verificar_y_redactar_pitch(nombre_negocio: str, datos_ig: str, ciudad: str, demo_url: str = "") -> dict:
    """
    Analiza el perfil de Instagram encontrado y genera:
    1. Mensaje DM inicial (cercano, elogiando su trabajo, explicando que somos un equipo local de diseño
       que busca comercios en su zona para mejorar su tráfico de clientes, con frase de tranquilidad anti-malware).
    2. Mensaje de seguimiento (para enviar a las 48-72h por Email o WhatsApp si no han contestado).
    """
    cliente = obtener_cliente_gemini()
    demo_texto = f"la maqueta interactiva segura que te preparé: {demo_url}" if demo_url else "la propuesta visual"

    if cliente:
        prompt = f"""
Actúa como un estratega de prospección comercial local y copywriter de élite para un estudio de diseño web cercano y honesto.
Analiza este negocio local y los datos de su perfil de Instagram:

Negocio local:
- Nombre: {nombre_negocio}
- Localidad / Ciudad: {ciudad} (por defecto área de Barcelona / cercanías si aplica)

Datos del perfil de Instagram:
{datos_ig}

Tu tarea es redactar dos mensajes hiper-personalizados y transparentes:

1. 'mensaje_dm_sugerido' (Primer contacto por DM):
   - Máximo 70 palabras. Tono cálido, respetuoso y muy profesional.
   - Elogia un detalle real de su trabajo en Instagram según su sector específico.
   - Explica con total honestidad quiénes somos: somos un equipo local de diseño buscando negocios con potencial en su zona para ayudarles a captar más clientes directos desde Google sin depender de intermediarios.
   - Incorpora el enlace ({demo_url or 'https://...'}) con una frase de total tranquilidad y transparencia para disipar desconfianzas (ej: "Tranquilos, el enlace es una maqueta interactiva 100% segura que os he subido a la web para que podáis navegarla desde el móvil sin descargar nada ni registros").
   - Llamada a la acción suave y sin presión.

2. 'mensaje_seguimiento' (Paso 2: Seguimiento amable a las 48-72h por Email o WhatsApp):
   - Máximo 45 palabras.
   - Recuerda con simpatía que les dejaste un mensaje por Instagram con la demo de su web ({demo_url or 'la maqueta'}).
   - Pregunta con educación si tuvieron oportunidad de verla desde el móvil y si les gustaría comentar impresiones sin compromiso.

Devuelve ÚNICAMENTE un JSON con esta estructura:
{{
  "es_perfil_correcto": true,
  "razon": "Coincide el negocio y ubicación",
  "mensaje_dm_sugerido": "¡Hola equipo de {nombre_negocio}! Me encantan vuestros trabajos en Instagram. Somos un equipo local de diseño y estamos contactando con comercios de vuestra zona porque vemos que tenéis un potencial enorme para recibir citas y clientes directos en Google. Os he preparado una maqueta interactiva adaptada a vuestro negocio: {demo_url or 'https://...'}. Es un enlace 100% seguro para verla en el navegador móvil sin registros ni descargas. ¿Qué os parece la idea?",
  "mensaje_seguimiento": "¡Hola de nuevo! Os escribí hace un par de días por Instagram porque os preparé una web demo interactiva: {demo_url or 'https://...'}. Os lo dejo por aquí por si os resulta más cómodo revisarlo desde el móvil. ¡Un saludo cordial!"
}}
"""
        try:
            config = None
            if types and hasattr(types, "GenerateContentConfig"):
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            
            response = cliente.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=config
            )
            
            texto = response.text.strip()
            texto = re.sub(r"^```(json)?", "", texto, flags=re.MULTILINE).strip("` \n")
            data = json.loads(texto)
            return {
                "es_perfil_correcto": bool(data.get("es_perfil_correcto", True)),
                "razon": str(data.get("razon", "Perfil coincidente")),
                "mensaje_dm_sugerido": str(data.get("mensaje_dm_sugerido", "")),
                "mensaje_seguimiento": str(data.get("mensaje_seguimiento", ""))
            }
        except Exception as e:
            print(f"[Error Gemini Pitch] {e}. Usando plantilla fallback...")

    # Fallback si no hay API key de Gemini
    link_texto = f" {demo_url}" if demo_url else ""
    pitch_dm_fallback = (
        f"¡Hola equipo de {nombre_negocio}! Me encantan vuestros trabajos en Instagram. "
        f"Somos un equipo local de diseño y estamos seleccionando comercios con gran potencial en vuestra zona de {ciudad} para ayudarles a conseguir más clientes desde Google. "
        f"Os he preparado una maqueta interactiva de cómo luciría vuestra web:{link_texto} "
        f"(El enlace es 100% seguro para navegarlo desde el móvil sin registros ni descargas). ¿Podéis echarle un ojo a ver qué os parece? ¡Un saludo!"
    )
    seguimiento_fallback = (
        f"¡Hola de nuevo equipo de {nombre_negocio}! Os escribí hace unos días por Instagram con una propuesta web interactiva para vuestro negocio:{link_texto} "
        f"Os lo comparto por aquí por si os resulta más cómodo revisarlo desde el teléfono. ¿Os gustaría que hablemos 2 minutos sin compromiso? ¡Un saludo cordial!"
    )
    return {
        "es_perfil_correcto": True,
        "razon": "Validación automática heurística",
        "mensaje_dm_sugerido": pitch_dm_fallback,
        "mensaje_seguimiento": seguimiento_fallback
    }


# -------------------------------------------------------------
# 3. OPENSTREETMAP: BÚSQUEDA POR CÓDIGO POSTAL Y ETIQUETA
# -------------------------------------------------------------
def obtener_bounding_box_cp(codigo_postal: str) -> Optional[Dict[str, Any]]:
    """Consulta Nominatim para obtener el bounding box y localidad del Código Postal en España."""
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "InstaLeads-App/1.0 (local-prospecting-tool)"}
    params = {
        "postalcode": codigo_postal,
        "country": "Spain",
        "format": "json",
        "addressdetails": 1,
        "limit": 1
    }
    try:
        r = requests.get(url, params=params, headers=headers, timeout=6)
        if r.status_code == 200 and r.json():
            item = r.json()[0]
            bbox = item.get("boundingbox") # [south, north, west, east]
            addr = item.get("address", {})
            ciudad = (
                addr.get("city") or 
                addr.get("town") or 
                addr.get("municipality") or 
                addr.get("village") or 
                addr.get("county") or 
                addr.get("state") or 
                "España"
            )
            if bbox and len(bbox) == 4:
                return {
                    "south": float(bbox[0]),
                    "north": float(bbox[1]),
                    "west": float(bbox[2]),
                    "east": float(bbox[3]),
                    "ciudad": ciudad
                }
    except Exception as e:
        print(f"[Nominatim Error] {e}")
    return None


def consultar_overpass(codigo_postal: str, osm_key: str, osm_value: str) -> List[Dict[str, Any]]:
    """
    Ejecuta una consulta Overpass QL buscando elementos que coincidan con la clave/valor de OSM
    dentro del Código Postal especificado.
    """
    url = "https://overpass-api.de/api/interpreter"
    
    geo_data = obtener_bounding_box_cp(codigo_postal)
    ciudad_default = geo_data["ciudad"] if geo_data else "España"

    if geo_data:
        # Búsqueda rápida y precisa por Bounding Box geográfico del CP
        s, n, w, e = geo_data["south"], geo_data["north"], geo_data["west"], geo_data["east"]
        query = f"""
        [out:json][timeout:25];
        (
          node["{osm_key}"="{osm_value}"]({s},{w},{n},{e});
          way["{osm_key}"="{osm_value}"]({s},{w},{n},{e});
        );
        out center tags;
        """
    else:
        # Búsqueda por tag postal_code o addr:postcode
        query = f"""
        [out:json][timeout:25];
        (
          node["addr:postcode"="{codigo_postal}"]["{osm_key}"="{osm_value}"];
          way["addr:postcode"="{codigo_postal}"]["{osm_key}"="{osm_value}"];
          node["postal_code"="{codigo_postal}"]["{osm_key}"="{osm_value}"];
        );
        out center tags;
        """

    headers = {"User-Agent": "InstaLeads-App/1.0"}
    try:
        resp = requests.post(url, data={"data": query}, headers=headers, timeout=25)
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
                    # Si tiene un sitio web propio (ej. mipeluqueria.com), lo ignoramos
                    continue

                # Extraer dirección
                calle = tags.get("addr:street", "")
                numero = tags.get("addr:housenumber", "")
                direccion = f"{calle} {numero}".strip() if calle else tags.get("address", "")
                
                ciudad = tags.get("addr:city") or ciudad_default
                cp = tags.get("addr:postcode") or codigo_postal
                telefono = tags.get("phone") or tags.get("contact:phone") or tags.get("contact:mobile", "")
                email = tags.get("email") or tags.get("contact:email", "")
                
                # Revisar si OSM ya tenía etiquetado Instagram
                ig_osm = tags.get("contact:instagram") or tags.get("instagram", "")

                resultados.append({
                    "osm_id": str(el.get("id")),
                    "nombre": nombre.strip(),
                    "categoria": f"{osm_key}: {osm_value}",
                    "direccion": direccion,
                    "ciudad": ciudad,
                    "codigo_postal": cp,
                    "telefono": telefono,
                    "email": email,
                    "tiene_web": False,
                    "instagram_tag_osm": ig_osm,
                    "tags": tags
                })
            return resultados
    except Exception as e:
        print(f"[Overpass Error] {e}")
    
    return []


# -------------------------------------------------------------
# 4. BUSCADOR DE PERFIL DE INSTAGRAM (OSM / DuckDuckGo)
# -------------------------------------------------------------
def extraer_handle_ig(url_or_handle: str) -> tuple[str, str]:
    """Limpia y normaliza un enlace o handle de Instagram."""
    if not url_or_handle:
        return "", ""
    
    match = re.search(r"instagram\.com/([a-zA-Z0-9_\.\-]+)", url_or_handle)
    if match:
        handle = match.group(1).rstrip("/")
        if handle not in ("p", "reel", "stories", "explore", "tv"):
            return f"@{handle}", f"https://www.instagram.com/{handle}/"
            
    if url_or_handle.startswith("@"):
        handle = url_or_handle.lstrip("@").strip()
        return f"@{handle}", f"https://www.instagram.com/{handle}/"

    return url_or_handle, url_or_handle


def buscar_instagram_negocio(nombre: str, ciudad: str, ig_osm: str = "") -> dict:
    """Busca o valida el perfil de Instagram del negocio."""
    if ig_osm:
        handle, url = extraer_handle_ig(ig_osm)
        return {
            "encontrado": True,
            "handle": handle,
            "url": url,
            "datos_crudos": f"Etiquetado en OpenStreetMap: {ig_osm}"
        }

    if not HAS_DDGS:
        return {"encontrado": False, "handle": "", "url": "", "datos_crudos": "DuckDuckGo search no disponible"}

    query = f'site:instagram.com "{nombre}" "{ciudad}"'
    try:
        with DDGS() as ddgs:
            resultados = list(ddgs.text(query, max_results=3))
            for res in resultados:
                href = res.get("href", "")
                title = res.get("title", "")
                body = res.get("body", "")

                handle, url = extraer_handle_ig(href)
                if handle and handle != "@":
                    return {
                        "encontrado": True,
                        "handle": handle,
                        "url": url,
                        "datos_crudos": f"Título: {title} | Snippet: {body} | URL: {url}"
                    }
    except Exception as e:
        print(f"[DDG Error para '{nombre}'] {e}")

    return {"encontrado": False, "handle": "", "url": "", "datos_crudos": "No se localizó perfil público"}


# -------------------------------------------------------------
# 5. PERSISTENCIA DEDUPLICADA DE LEADS (data/leads.json)
# -------------------------------------------------------------
def leer_leads_guardados() -> List[Dict[str, Any]]:
    try:
        with open(LEADS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def guardar_leads_deduplicados(nuevos_leads: List[Dict[str, Any]]) -> int:
    existentes = leer_leads_guardados()
    # Claves únicas para deduplicación: (nombre normalizado, ciudad normalizada) o instagram_url
    mapa = {}
    for l in existentes:
        k = (l.get("nombre", "").lower().strip(), l.get("ciudad", "").lower().strip())
        mapa[k] = l

    agregados = 0
    for l in nuevos_leads:
        k = (l.get("nombre", "").lower().strip(), l.get("ciudad", "").lower().strip())
        if k in mapa:
            # Actualizar datos si el nuevo tiene pitch o instagram verificado
            mapa[k].update(l)
        else:
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
    codigo_postal: str
    categoria: str
    max_comercios: int = 15


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal de la aplicación."""
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/health")
async def health_check():
    """Estado del servidor y verificación de la API de Gemini y SMTP."""
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    configurado = bool(api_key and api_key != "tu_api_key_aqui")
    smtp_user = os.getenv("SMTP_EMAIL", "").strip()
    smtp_pwd = os.getenv("SMTP_APP_PASSWORD", "").strip()
    smtp_ok = bool(smtp_user and smtp_pwd and "tu_correo" not in smtp_user)
    return {
        "status": "ok",
        "gemini_configurado": configurado,
        "modelo": GEMINI_MODEL,
        "duckduckgo_disponible": HAS_DDGS,
        "google_genai_instalado": HAS_GENAI_LIB,
        "smtp_configurado": smtp_ok,
        "smtp_email": smtp_user if smtp_ok else ""
    }


@app.get("/leads")
async def get_leads():
    """Devuelve todos los leads calculando el tiempo transcurrido y alertas de seguimiento temporal."""
    leads = leer_leads_guardados()
    now = datetime.now(timezone.utc)
    for l in leads:
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
    return leads


@app.delete("/leads")
async def clear_leads():
    """Vacía la lista de leads guardados."""
    with open(LEADS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)
    return {"status": "ok", "mensaje": "Base de datos de leads reiniciada."}


@app.post("/scan")
async def scan_local_leads(req: ScanRequest):
    """
    Orquesta el pipeline completo de prospección:
    1. Normaliza la categoría a etiquetas OSM con Gemini.
    2. Consulta OpenStreetMap filtrando negocios sin web.
    3. Descubre o extrae el perfil de Instagram.
    4. Verifica con Gemini y redacta el pitch comercial DM.
    5. Deduplica y persiste en data/leads.json.
    """
    cp = req.codigo_postal.strip()
    cat_usuario = req.categoria.strip()

    if not cp or not cat_usuario:
        raise HTTPException(status_code=400, detail="El código postal y la categoría son obligatorios.")

    print(f"\n[1/4] Mapeando categoría '{cat_usuario}' con Gemini...")
    osm_tag = mapear_categoria_osm(cat_usuario)
    osm_key = osm_tag["key"]
    osm_value = osm_tag["value"]

    print(f"[2/4] Buscando comercios en OSM (CP: {cp}, {osm_key}={osm_value})...")
    comercios = consultar_overpass(cp, osm_key, osm_value)
    print(f"      Encontrados {len(comercios)} comercios sin web propia.")

    if not comercios:
        return {
            "status": "ok",
            "categoria_osm": osm_tag,
            "nuevos_leads_encontrados": 0,
            "mensaje": f"No se encontraron comercios sin página web con la etiqueta OSM '{osm_key}={osm_value}' en el CP {cp}."
        }

    # Limitar para respetar cuotas de búsqueda y generación
    comercios_a_procesar = comercios[:req.max_comercios]
    prospectos_procesados = []

    print(f"[3/4 y 4/4] Buscando Instagram, verificando y generando pitch con Gemini...")
    for com in comercios_a_procesar:
        nombre = com["nombre"]
        ciudad = com["ciudad"]
        ig_osm = com.get("instagram_tag_osm", "")

        # Buscar perfil en Instagram
        ig_info = buscar_instagram_negocio(nombre, ciudad, ig_osm)
        
        datos_ig_texto = ig_info["datos_crudos"]
        ig_url = ig_info["url"]
        ig_handle = ig_info["handle"]

        # Si encontramos perfil o datos de Instagram, consultamos a Gemini
        if ig_info["encontrado"]:
            analisis = verificar_y_redactar_pitch(nombre, datos_ig_texto, ciudad)
        else:
            analisis = {
                "es_perfil_correcto": False,
                "razon": "No se detectó perfil de Instagram público",
                "mensaje_dm_sugerido": ""
            }

        lead = {
            "osm_id": com["osm_id"],
            "nombre": nombre,
            "categoria": f"{cat_usuario} ({osm_key}:{osm_value})",
            "direccion": com["direccion"],
            "ciudad": ciudad,
            "codigo_postal": com["codigo_postal"],
            "telefono": com["telefono"],
            "email": com.get("email", ""),
            "tiene_web": False,
            "instagram_url": ig_url,
            "instagram_handle": ig_handle,
            "gemini_verificado": analisis["es_perfil_correcto"],
            "gemini_razon": analisis["razon"],
            "mensaje_dm": analisis["mensaje_dm_sugerido"],
            "estado": "Sin Web",
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


class StatusUpdateRequest(BaseModel):
    estado: str


@app.post("/leads/{osm_id}/generate-web")
async def generate_lead_web(osm_id: str, request: Request):
    """
    Genera la web demo individualizada para un lead usando:
    1. Extracción de datos de Instagram (Apify o fallback adaptado).
    2. Design System estilo Stitch (colores, fuentes y formas).
    3. Estructuración con Gemini.
    4. Guardado en demos/{slug}/index.html (GitHub Pages ready).
    5. Actualización del pitch de prospección con el enlace de la demo.
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

    cliente_gemini = obtener_cliente_gemini()
    res = generar_web_comercio(target_lead, cliente_gemini=cliente_gemini)

    base_url = str(request.base_url).rstrip("/")
    demo_url_absoluta = f"{base_url}/demos/{res['slug']}"

    # Actualizar lead
    target_lead["demo_slug"] = res["slug"]
    target_lead["demo_url"] = res["demo_url_local"]
    target_lead["demo_url_absoluta"] = demo_url_absoluta
    target_lead["demo_vibe"] = res["design_vibe"]
    target_lead["estado"] = "Web Generada"

    # Regenerar el pitch comercial incorporando la URL de la demo
    nuevo_pitch = verificar_y_redactar_pitch(
        nombre_negocio=target_lead.get("nombre", ""),
        datos_ig=f"Instagram: {target_lead.get('instagram_url', '')} | Categoría: {target_lead.get('categoria', '')}",
        ciudad=target_lead.get("ciudad", ""),
        demo_url=demo_url_absoluta
    )
    target_lead["mensaje_dm"] = nuevo_pitch.get("mensaje_dm_sugerido", target_lead.get("mensaje_dm", ""))
    target_lead["mensaje_seguimiento"] = nuevo_pitch.get("mensaje_seguimiento", target_lead.get("mensaje_seguimiento", ""))

    leads[target_idx] = target_lead
    with open(LEADS_FILE, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)

    return {
        "status": "ok",
        "lead": target_lead,
        "demo": res
    }


class PitchSaveRequest(BaseModel):
    mensaje_dm: str
    mensaje_seguimiento: Optional[str] = ""


@app.post("/leads/{osm_id}/pitch")
async def save_lead_pitch(osm_id: str, req: PitchSaveRequest):
    """Guarda las ediciones personalizadas que el usuario realiza sobre el DM o seguimiento."""
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
async def update_lead_status(osm_id: str, req: StatusUpdateRequest):
    """Actualiza el estado de prospección del lead y registra la fecha de contacto."""
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
async def simulate_lead_time(osm_id: str):
    """Simula que han transcurrido 50 horas desde el contacto para comprobar la alerta de seguimiento."""
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
async def send_lead_email(osm_id: str, req: EmailSendRequest):
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
async def deploy_github_pages_endpoint():
    """Endpoint llamado desde el botón de la UI para publicar las demos en GitHub Pages."""
    return ejecutar_despliegue_github_pages()


@app.get("/demo/{osm_id}")
async def redirect_to_demo(osm_id: str):
    """Redirige directamente a la demo del lead si existe."""
    leads = leer_leads_guardados()
    for l in leads:
        if str(l.get("osm_id")) == str(osm_id) and l.get("demo_slug"):
            return HTMLResponse(content=f'<script>window.location.href="/demos/{l["demo_slug"]}";</script>')
    raise HTTPException(status_code=404, detail="Demo aún no generada para este lead.")


@app.get("/export-csv")
async def export_leads_csv():
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
    host = os.getenv("HOST", "127.0.0.1")
    print(f"Iniciando InstaLeads AI en http://{host}:{port}")
    uvicorn.run("app:app", host=host, port=port, reload=True)
