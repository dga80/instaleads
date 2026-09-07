import os
import json
import re
import csv
import io
from typing import List, Optional, Dict, Any
from pathlib import Path

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

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
def verificar_y_redactar_pitch(nombre_negocio: str, datos_ig: str, ciudad: str) -> dict:
    """
    Analiza el perfil de Instagram encontrado y determina si corresponde al negocio local.
    Si es afirmativo, redacta un DM persuasivo y personalizado (máximo 60 palabras).
    """
    cliente = obtener_cliente_gemini()
    if cliente:
        prompt = f"""
Actúa como un estratega de prospección comercial B2B para una agencia de diseño y desarrollo web.
Analiza la correspondencia entre este negocio local y los datos del perfil de Instagram encontrado:

Negocio local:
- Nombre: {nombre_negocio}
- Localidad / Ciudad: {ciudad}

Datos del perfil de Instagram encontrado:
{datos_ig}

Tu tarea:
1. 'es_perfil_correcto': Determina con criterio lógico si este perfil de Instagram parece corresponder a este comercio local (true o false).
2. 'razon': Una frase corta resumiendo por qué coincide o por qué hay dudas.
3. 'mensaje_dm_sugerido': Si coincide, redacta un mensaje para enviar por Direct Message (DM) de Instagram que cumpla:
   - Máximo 60 palabras.
   - Tono cercano, profesional, respetuoso y persuasivo.
   - Elogia su trabajo o presencia visual en Instagram.
   - Hazle notar con delicadeza la oportunidad que pierde al no tener una página web propia o sistema de reservas directo para convertir a sus seguidores en clientes.
   - Incluye una llamada a la acción sencilla (ej. '¿Te gustaría que te prepare una propuesta visual sin compromiso?').
   - Si no coincide el perfil, deja este campo como cadena vacía.

Devuelve ÚNICAMENTE un JSON con esta estructura exacta:
{{
  "es_perfil_correcto": true,
  "razon": "Coincide el nombre comercial y la ubicación en la biografía",
  "mensaje_dm_sugerido": "¡Hola equipo de {nombre_negocio}! Me encanta lo activo que tenéis vuestro perfil y la calidad de vuestro trabajo. Noté que aún no contáis con web propia para centralizar reservas/pedidos y destacar en Google. ¿Os interesaría ver una propuesta rápida y sin compromiso de cómo quedaría vuestra web profesional? ¡Un saludo!"
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
                "mensaje_dm_sugerido": str(data.get("mensaje_dm_sugerido", ""))
            }
        except Exception as e:
            print(f"[Error Gemini Pitch] {e}. Usando plantilla fallback...")

    # Fallback si no hay API key de Gemini
    pitch_fallback = (
        f"¡Hola equipo de {nombre_negocio}! Me encanta vuestro contenido en Instagram y lo bien que cuidáis a vuestra comunidad. "
        f"Me he fijado en que aún no tenéis una página web propia donde captar clientes en Google y automatizar citas/pedidos. "
        f"¿Os gustaría que os muestre un diseño previo sin compromiso? ¡Un saludo cordial!"
    )
    return {
        "es_perfil_correcto": True,
        "razon": "Validación automática heurística (Gemini API key no configurada)",
        "mensaje_dm_sugerido": pitch_fallback
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
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Estado del servidor y verificación de la API de Gemini."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    configurado = bool(api_key and api_key != "tu_api_key_aqui")
    return {
        "status": "ok",
        "gemini_configurado": configurado,
        "modelo": GEMINI_MODEL,
        "duckduckgo_disponible": HAS_DDGS,
        "google_genai_instalado": HAS_GENAI_LIB
    }


@app.get("/leads")
async def get_leads():
    """Devuelve todos los leads guardados en data/leads.json."""
    return leer_leads_guardados()


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
            "tiene_web": False,
            "instagram_url": ig_url,
            "instagram_handle": ig_handle,
            "gemini_verificado": analisis["es_perfil_correcto"],
            "gemini_razon": analisis["razon"],
            "mensaje_dm": analisis["mensaje_dm_sugerido"]
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
