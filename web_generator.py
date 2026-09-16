import os
import re
import json
import base64
import urllib.parse
import unicodedata
from pathlib import Path
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor

import requests
from jinja2 import Environment, FileSystemLoader

from instagram_extractor import obtener_datos_completos_instagram, generar_datos_instagram_mock
from stitch_designer import sintetizar_design_system

BASE_DIR = Path(__file__).resolve().parent

env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")))

def slugify(text: str) -> str:
    """Convierte texto en slug URL seguro (ej: 'Taller Dani & Hijos' -> 'taller-dani-hijos')."""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text.lower()).strip()
    return re.sub(r'[-\s]+', '-', text)

def limpiar_categoria(cat: str) -> str:
    """Elimina etiquetas OSM como (shop:tattoo), (amenity:dentist) y devuelve un nombre limpio y formal."""
    if not cat:
        return "Comercio Local"
    limpio = re.sub(r'\(.*?\)', '', cat).strip()
    limpio = re.sub(r'[:_]', ' ', limpio).strip()
    return limpio.title() if limpio else "Comercio Local"

def descargar_imagen_a_base64(url: str, timeout: int = 12) -> str:
    """
    Descarga una imagen de Instagram CDN o externa y la convierte en data URI base64.
    Esto es ESENCIAL porque los servidores CDN de Instagram envían 'cross-origin-resource-policy: same-origin',
    lo que provoca que Chrome y otros navegadores bloqueen las imágenes al abrirlas desde GitHub Pages o dominios externos.
    Además, evita que las imágenes expiren por token temporal (parámetro oe).
    """
    if not url or not isinstance(url, str):
        return ""
    if url.startswith("data:image"):
        return url
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.instagram.com/",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code == 200 and resp.content and len(resp.content) > 200:
            mime = resp.headers.get("content-type", "image/jpeg").split(";")[0].strip()
            if not mime.startswith("image/"):
                mime = "image/jpeg"
            b64_str = base64.b64encode(resp.content).decode("utf-8")
            return f"data:{mime};base64,{b64_str}"
    except Exception as e:
        print(f"[Base64 Inliner] No se pudo incrustar imagen ({e}). Se mantiene URL original.")
    
    return url

def extraer_contenido_web_existente(url_web: str) -> Dict[str, Any]:
    """
    Rastrea y extrae la información clave del sitio web oficial existente del comercio:
    - Título del sitio y meta-descripción.
    - Encabezados (h1, h2, h3) con nombres de servicios y propuesta de valor.
    - Párrafos principales (sobre nosotros, historia, especialidades).
    - Imágenes destacadas y teléfonos de contacto.
    """
    if not url_web or not isinstance(url_web, str) or not url_web.startswith("http"):
        return {}
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
    }

    try:
        resp = requests.get(url_web, headers=headers, timeout=8, verify=False)
        if resp.status_code != 200 or not resp.text:
            return {}

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")

        # Eliminar scripts, estilos y elementos irrelevantes
        for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
            tag.decompose()

        titulo = soup.title.string.strip() if soup.title and soup.title.string else ""
        
        meta_desc = ""
        desc_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)}) or soup.find("meta", attrs={"property": "og:description"})
        if desc_tag and desc_tag.get("content"):
            meta_desc = desc_tag["content"].strip()

        # Encabezados
        encabezados = []
        for h in soup.find_all(["h1", "h2", "h3"]):
            txt = h.get_text(separator=" ", strip=True)
            if txt and len(txt) > 3 and len(txt) < 120 and txt not in encabezados:
                encabezados.append(txt)

        # Párrafos informativos
        parrafos = []
        for p in soup.find_all("p"):
            txt = p.get_text(separator=" ", strip=True)
            if txt and len(txt) > 25 and len(txt) < 350 and txt not in parrafos:
                parrafos.append(txt)

        # Imágenes (og:image o imágenes con alt relevante)
        imagenes = []
        og_img = soup.find("meta", attrs={"property": "og:image"})
        if og_img and og_img.get("content"):
            imagenes.append(urllib.parse.urljoin(url_web, og_img["content"]))

        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if src and not src.startswith("data:"):
                full_img = urllib.parse.urljoin(url_web, src)
                if full_img not in imagenes and any(ext in full_img.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    imagenes.append(full_img)
            if len(imagenes) >= 6:
                break

        # Teléfonos detectados en la web
        telefonos = []
        tel_links = soup.find_all("a", href=re.compile(r"^tel:", re.I))
        for t in tel_links:
            raw_tel = t["href"].replace("tel:", "").strip()
            if raw_tel and raw_tel not in telefonos:
                telefonos.append(raw_tel)

        print(f"[Web Extractor] ✓ Extraído de {url_web}: {len(encabezados)} títulos, {len(parrafos)} párrafos, {len(imagenes)} imágenes")
        return {
            "url": url_web,
            "titulo": titulo,
            "meta_descripcion": meta_desc,
            "encabezados": encabezados[:8],
            "parrafos": parrafos[:6],
            "imagenes": imagenes[:6],
            "telefonos": telefonos
        }
    except Exception as e:
        print(f"[Web Extractor Warning] No se pudo extraer datos de {url_web}: {e}")
        return {}


def descargar_imagenes_en_paralelo(urls: List[str]) -> Dict[str, str]:
    """Descarga de forma concurrente todas las imágenes necesarias en menos de un segundo."""
    unique_urls = list(dict.fromkeys([u for u in urls if u and isinstance(u, str) and not u.startswith("data:image")]))
    if not unique_urls:
        return {}

    mapping = {}
    with ThreadPoolExecutor(max_workers=min(8, len(unique_urls))) as pool:
        futures = {pool.submit(descargar_imagen_a_base64, u): u for u in unique_urls}
        for f in futures:
            orig = futures[f]
            try:
                mapping[orig] = f.result()
            except Exception:
                mapping[orig] = orig
    return mapping

def generar_servicios_inteligentes_categoria(
    categoria: str,
    nombre: str,
    ciudad: str,
    ig_bio: str,
    ig_posts: list
) -> List[Dict[str, Any]]:
    """
    Genera un catálogo comercial creíble, profesional y adaptado al nicho del negocio
    aprovechando fotos reales de Instagram y palabras clave de la biografía.
    """
    text_corpus = f"{categoria} {nombre} {ig_bio}".lower()

    if any(k in text_corpus for k in ["tattoo", "tatuaj", "piercing", "ink", "tatu"]):
        servicios = [
            {
                "nombre": "Tatuajes Personalizados & Custom",
                "descripcion": "Diseños exclusivos y asesoramiento de visagismo adaptado a tu estilo y anatomía.",
                "precio_o_duracion": "Desde 60€ / Presupuesto a medida"
            }
        ]
        if "piercing" in text_corpus or "anillad" in text_corpus or "perforac" in text_corpus:
            servicios.append({
                "nombre": "Piercing & Joyería Estéril",
                "descripcion": "Perforaciones con técnica aséptica, agujas americanas y titanio grado implante F-136.",
                "precio_o_duracion": "Desde 20€ / Cita previa"
            })
        else:
            servicios.append({
                "nombre": "Realismo, Blackwork & Fine Line",
                "descripcion": "Líneas de precisión milimétrica, degradados suaves y máxima fijación de pigmentos.",
                "precio_o_duracion": "Consultar sesión"
            })

        if "walk" in text_corpus or "walk-ins" in text_corpus:
            servicios.append({
                "nombre": "Walk-Ins & Flash Tattoos",
                "descripcion": "Atención directa sin cita previa sujeta a disponibilidad de artistas en el box.",
                "precio_o_duracion": "Atención inmediata"
            })
        else:
            servicios.append({
                "nombre": "Cover-Up & Restauración",
                "descripcion": "Transformación y cobertura experta de piezas antiguas con estudio previo.",
                "precio_o_duracion": "Valoración gratuita"
            })

    elif any(k in text_corpus for k in ["barber", "fade", "afeitad", "barba"]):
        servicios = [
            {
                "nombre": "Corte de Precisión & Skin Fade",
                "descripcion": "Degradados milimétricos a navaja y tijera con lavado y peinado con cera prémium.",
                "precio_o_duracion": "Desde 16€"
            },
            {
                "nombre": "Ritual Tradicional de Barba",
                "descripcion": "Toalla caliente aromatizada, perfilado al detalle y tratamiento de aceites orgánicos.",
                "precio_o_duracion": "Desde 12€"
            },
            {
                "nombre": "Pack Signature (Corte + Barba)",
                "descripcion": "La experiencia completa de cuidado masculino con masaje capilar y asesoramiento.",
                "precio_o_duracion": "Desde 25€"
            }
        ]

    elif any(k in text_corpus for k in ["uña", "nail", "estetic", "belleza", "beauty", "spa", "pestañ", "lash", "laser"]):
        servicios = [
            {
                "nombre": "Manicura Rusa & Nivelación",
                "descripcion": "Limpieza minuciosa de cutículas con torno y esmaltado semipermanente de alta duración.",
                "precio_o_duracion": "Desde 25€"
            },
            {
                "nombre": "Pedicura Spa & Cuidado Profundo",
                "descripcion": "Exfoliación hidratante, retirada de durezas y acabado perfecto para tus pies.",
                "precio_o_duracion": "Desde 35€"
            },
            {
                "nombre": "Lifting de Pestañas & Laminado de Cejas",
                "descripcion": "Potencia tu mirada de forma natural con curvatura definida y nutrición de queratina.",
                "precio_o_duracion": "Desde 30€"
            }
        ]

    elif any(k in text_corpus for k in ["cafe", "cafeter", "panader", "obrador", "bakery", "restauran", "bistro", "brunch", "gastro"]):
        servicios = [
            {
                "nombre": "Café de Especialidad Calibrado",
                "descripcion": "Granos seleccionados de fincas de origen único con extracción barista profesional.",
                "precio_o_duracion": "Desde 2.20€"
            },
            {
                "nombre": "Obrador & Masa Madre Diaria",
                "descripcion": "Panes de larga fermentación y bollería artesana horneada cada mañana.",
                "precio_o_duracion": "Elaboración diaria"
            },
            {
                "nombre": "Brunch & Tostas de Autor",
                "descripcion": "Combinaciones saludables con productos de proximidad, aguacate, huevos de campo y masa madre.",
                "precio_o_duracion": "Carta completa"
            }
        ]

    elif any(k in text_corpus for k in ["dent", "clinic", "odont", "fisio", "podolog", "salud", "medic", "veterinar"]):
        servicios = [
            {
                "nombre": "1ª Visita & Diagnóstico Digital 3D",
                "descripcion": "Exploración exhaustiva con escaneado digital y plan terapéutico individualizado.",
                "precio_o_duracion": "1ª Cita sin compromiso"
            },
            {
                "nombre": "Higiene Avanzada & Profilaxis",
                "descripcion": "Tratamiento preventivo con tecnología ultrasónica sin molestias para encías sanas.",
                "precio_o_duracion": "Tarifa regulada"
            },
            {
                "nombre": "Tratamientos Avanzados & Rehabilitación",
                "descripcion": "Intervenciones con mínima invasión y la tecnología clínica más puntera.",
                "precio_o_duracion": "Financiación disponible"
            }
        ]

    elif any(k in text_corpus for k in ["reforma", "construc", "interiorism", "carpinter", "fontaner", "climatiz", "electric"]):
        servicios = [
            {
                "nombre": "Reformas Integrales Llave en Mano",
                "descripcion": "Gestión integral desde el plano hasta la entrega de llaves con plazos garantizados por contrato.",
                "precio_o_duracion": "Presupuesto cerrado"
            },
            {
                "nombre": "Renovación de Cocinas y Baños",
                "descripcion": "Diseño funcional, alicatados porcelánicos y fontanería de última generación.",
                "precio_o_duracion": "Garantía oficial 2 años"
            },
            {
                "nombre": "Climatización, Suelos & Acabados",
                "descripcion": "Instalaciones certificadas de aerotermia, parquet, pintura y carpintería a medida.",
                "precio_o_duracion": "Asesoramiento gratuito"
            }
        ]

    elif any(k in text_corpus for k in ["taller", "moto", "mecanic", "coche", "automov", "chapa", "neumatic"]):
        servicios = [
            {
                "nombre": "Mantenimiento Oficial & Pre-ITV",
                "descripcion": "Diagnosis electrónica, cambio de aceite, filtros y chequeo completo de seguridad.",
                "precio_o_duracion": "Desde 65€"
            },
            {
                "nombre": "Frenos, Neumáticos & Suspensión",
                "descripcion": "Montaje y equilibrado con recambios de primeros fabricantes homologados.",
                "precio_o_duracion": "Presupuesto inmediato"
            },
            {
                "nombre": "Mecánica Rápida & Electrónica",
                "descripcion": "Reparaciones urgentes y resolución de averías complejas en banco de diagnosis.",
                "precio_o_duracion": "Cita en el día"
            }
        ]

    else:
        servicios = [
            {
                "nombre": f"Atención Personalizada en {ciudad}",
                "descripcion": "Servicio profesional diseñado a medida para cumplir con tus máximas expectativas.",
                "precio_o_duracion": "Presupuesto sin compromiso"
            },
            {
                "nombre": "Garantía de Calidad & Asesoramiento",
                "descripcion": "Equipo especializado con amplia trayectoria y materiales de primera línea.",
                "precio_o_duracion": "Cita previa"
            },
            {
                "nombre": "Servicio Rápido & Eficaz",
                "descripcion": "Compromiso de puntualidad y transparencia absoluta en cada trabajo realizado.",
                "precio_o_duracion": "Atención directa"
            }
        ]

    for i, s in enumerate(servicios):
        if i < len(ig_posts):
            s["imagen"] = ig_posts[i].get("image_url")

    return servicios

def estructurar_contenido_con_gemini(
    nombre: str,
    categoria: str,
    ciudad: str,
    ig_bio: str,
    ig_posts: list,
    cliente_gemini=None,
    web_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convierte la identidad de Instagram o la información de la web oficial existente en una arquitectura web completa y persuasiva.
    Si Gemini está saturado o sin cuota, aplica el motor semántico local por categoría.
    """
    categoria_clean = limpiar_categoria(categoria)

    # Si tenemos cliente Gemini disponible
    try:
        from gemini_service import generar_con_gemini_cascade
        posts_text = "\n".join([f"- Post {i+1}: {p.get('caption', '')[:100]}" for i, p in enumerate(ig_posts[:6])])
        
        web_context_prompt = ""
        if web_info:
            encabezados_str = ", ".join(web_info.get("encabezados", []))
            parrafos_str = "\n".join([f"  • {p}" for p in web_info.get("parrafos", [])[:4]])
            web_context_prompt = f"""
INFORMACIÓN REAL EXTRAÍDA DE SU SITIO WEB OFICIAL ACTUAL ({web_info.get('url', '')}):
- Título actual de su web: {web_info.get('titulo', '')}
- Meta-descripción actual: {web_info.get('meta_descripcion', '')}
- Secciones/Servicios reales detectados en su web: {encabezados_str}
- Contenido textual y propuesta de valor de su web:
{parrafos_str}

REGLA CRÍTICA DE REDISEÑO:
Este proyecto es una PROPUESTA DE REDISEÑO de su página web oficial actual.
Debes tomar y respetar los SERVICIOS REALES, textos y especialidades extraídas de su página web oficial para adaptarlos a la nueva arquitectura mobile-first moderna de alta conversión.
"""

        prompt = f"""
Actúa como Diseñador Principal UX/UI y Director Creativo de élite para comercios locales.
Tu objetivo es diseñar la identidad visual, el modo cromático y la arquitectura de contenidos de una landing page mobile-first de máxima conversión para este negocio.

Datos del negocio:
- Nombre: {nombre}
- Categoría: {categoria_clean}
- Ciudad: {ciudad}
- Biografía de Instagram: {ig_bio}
{web_context_prompt}

Publicaciones recientes en Instagram:
{posts_text}

Tu misión como Director de Diseño y Copywriting es decidir y estructurar el contenido en JSON:
1. 'tema_predeterminado': Modo visual inicial ideal ("light" o "dark").
2. 'arquetipo_diseno': Arquetipo visual más idóneo ("luxury_glow", "urban_edge", "warm_artisan", "clinical_trust", "craft_build").
3. 'subnicho_cultural': Identifica el concepto cultural, gastronómico o especialidad exacta (ej. "colombiano", "mexicano", "italiano", "japones", "hamburgueseria", "panaderia_artesanal", "cafeteria_especialidad", "taller_motos", "taller_coches", "clinica_dental", "barberia", "peluqueria", "estetica_unas", "tatuajes", "reformas", "general").
4. 'badge_status': Una frase de estado con emoji para el header (ej. "⚡ BOX DE TALLER ACTIVO • CITA RÁPIDA", "✨ CITAS ABIERTAS • AGENDA ONLINE").
5. 'hero_badge_pill': Frase corta para la píldora superior del Hero adaptada exactamente a la especialidad u origen del negocio (ej. "🇨🇴 SABOR AUTÉNTICO COLOMBIANO • HECHO CON AMOR", "🥖 MASA MADRE & FERMENTACIÓN LENTA").
6. 'hero_stat_number': Cifra de impacto (ej. "+10.000", "+1.200", "100%").
7. 'hero_stat_label': Etiqueta de la cifra adaptada al servicio del negocio (ej. "arepas & especialidades servidas", "sonrisas transformadas", "motos puestas a punto").
8. 'hero_stat_icon': Nombre de icono de Google Material Symbols (ej. "restaurant", "local_cafe", "verified", "star", "health_and_safety").
9. 'hero_float_tag': Etiqueta pequeña flotante (ej. "Especialidad Criolla", "Tratamiento Estrella", "Garantía Oficial").
10. 'hero_float_title': Título del elemento flotante (ej. "Arepas con Queso & Empanadas", "Diagnóstico 3D Digital").
11. 'hero_status_pill': Píldora de estado (ej. "Cocina abierta hoy", "Citas disponibles hoy").
12. 'prompt_foto_hero': Prompt fotográfico en inglés hiper-realista, descriptivo y apetitoso para la imagen principal del hero, adaptado exactamente al tipo de negocio y su propuesta cultural/gastronómica o técnica.
13. 'prompt_foto_detalle': Prompt fotográfico en inglés para la foto de detalle secundario.
14. 'titular': Un título potente y persuasivo para el Hero (máx 8 palabras).
15. 'subtitulo': Una frase que explique el valor diferencial y anime a contactar (máx 20 palabras).
16. 'servicios': Lista de 3 servicios clave detectados ('nombre', 'descripcion', 'precio_o_duracion'). Si se aportó información de su web actual, utiliza prioritariamente sus servicios reales.
17. 'sobre_nosotros': Párrafo cercano y profesional resumiendo su propuesta de valor (máx 40 palabras).
18. 'categoria_clean': Nombre corto y limpio de la categoría.

Responde ÚNICAMENTE con el objeto JSON válido:
"""
        texto, modelo_usado = generar_con_gemini_cascade(prompt, cliente=cliente_gemini, formato_json=True)
        if texto:
            match = re.search(r"\{.*\}", texto, flags=re.DOTALL)
            raw_json = match.group(0) if match else re.sub(r"^```(json)?", "", texto, flags=re.MULTILINE).strip("` \n")
            data = json.loads(raw_json)
            if "titular" in data and "servicios" in data and isinstance(data["servicios"], list) and len(data["servicios"]) > 0:
                print(f"[Gemini Web Structuring] Contenido y diseño UX/UI generados con modelo {modelo_usado} (Subnicho: {data.get('subnicho_cultural', 'general')})")
                for i, s in enumerate(data.get("servicios", [])):
                    if i < len(ig_posts):
                        s["imagen"] = ig_posts[i].get("image_url")
                data["categoria_clean"] = data.get("categoria_clean") or categoria_clean
                return data
    except Exception as e:
        print(f"[Gemini Web Structuring Warning] {e}. Usando catálogo inteligente por categoría.")

    # Motor inteligente local por nicho
    servicios_base = generar_servicios_inteligentes_categoria(categoria, nombre, ciudad, ig_bio, ig_posts)

    cat_low = (categoria + " " + nombre).lower()
    default_theme = "light" if any(k in cat_low for k in ["dental", "dentist", "clinic", "salud", "fisioterap", "uña", "belleza", "spa", "cafe", "panader"]) else "dark"

    subtitulo = ig_bio.strip() if ig_bio else f"Calidad, profesionalidad y trato cercano en {ciudad}. Descubre nuestros servicios y reserva tu cita en segundos."
    if web_info:
        if web_info.get("meta_descripcion"):
            subtitulo = web_info["meta_descripcion"]
        elif web_info.get("parrafos"):
            subtitulo = web_info["parrafos"][0][:140]
        if web_info.get("encabezados"):
            for idx, enc in enumerate(web_info["encabezados"][:3]):
                if idx < len(servicios_base):
                    servicios_base[idx]["nombre"] = enc

    subtitulo = re.sub(r'\n{3,}', '\n\n', subtitulo)
    sobre_nosotros = (web_info.get("parrafos", [""])[0] if web_info and web_info.get("parrafos") else ig_bio) or f"En {nombre} nos dedicamos con pasión a ofrecer la mejor experiencia a nuestros clientes en {ciudad}. Cuidamos cada detalle para garantizar los mejores resultados."

    badge_status = f"• {categoria_clean.upper()} EN {ciudad.upper()}"

    return {
        "tema_predeterminado": default_theme,
        "badge_status": badge_status,
        "titular": f"{nombre} en {ciudad}",
        "subtitulo": subtitulo,
        "servicios": servicios_base,
        "sobre_nosotros": sobre_nosotros,
        "categoria_clean": categoria_clean
    }

def generar_web_comercio(lead: Dict[str, Any], cliente_gemini=None, plantilla_seleccionada: str = None) -> Dict[str, Any]:
    """
    Ejecuta el pipeline completo de generación de Web Demo:
    1. Si tiene web oficial propia, extrae contenidos y fotos de su sitio web actual.
    2. Extrae fotos, bio y datos de Instagram (Apify / Curated).
    3. Estructura el contenido persuasivo y decisiones UX/UI con Gemini enfocadas a rediseño mobile-first o nueva web.
    4. Sintetiza el Design System estilo Stitch con tokens cromáticos y tipográficos (respetando plantilla elegida).
    5. Compila el index.html y lo prepara para despliegue en GitHub Pages.
    """
    nombre = lead.get("nombre", "Comercio Local")
    categoria = lead.get("categoria", "Comercio")
    ciudad = lead.get("ciudad", "España")
    handle = lead.get("instagram_handle") or lead.get("instagram_url", "")
    if not handle and lead.get("enlaces_internet"):
        for enl in lead["enlaces_internet"]:
            if enl.get("tipo") == "instagram" and enl.get("url"):
                handle = enl["url"]
                lead["instagram_url"] = enl["url"]
                break
    telefono = lead.get("telefono", "")

    # 1. Si el comercio tiene página web oficial detectada, extraer su contenido real para la propuesta de rediseño
    web_existente = lead.get("web_detectada", "")
    web_info = {}
    if web_existente:
        web_info = extraer_contenido_web_existente(web_existente)
        if not telefono and web_info.get("telefonos"):
            telefono = web_info["telefonos"][0]

    # 2. Extraer datos del perfil de Instagram
    ig_data = obtener_datos_completos_instagram(handle, nombre, categoria, ciudad)

    # Incorporar imágenes de su web existente si están disponibles para enriquecer la galería
    if web_info.get("imagenes"):
        for img_url in web_info["imagenes"]:
            if not any(p.get("image_url") == img_url for p in ig_data.get("posts", [])):
                ig_data.setdefault("posts", []).append({
                    "image_url": img_url,
                    "caption": web_info.get("titulo", "Servicio oficial")
                })

    # 3. Estructurar contenidos, copy persuasivo y decisiones de diseño con Gemini
    web_content = estructurar_contenido_con_gemini(
        nombre=nombre,
        categoria=categoria,
        ciudad=ciudad,
        ig_bio=ig_data.get("biografia", ""),
        ig_posts=ig_data.get("posts", []),
        cliente_gemini=cliente_gemini,
        web_info=web_info
    )

    if plantilla_seleccionada:
        web_content["arquetipo_diseno"] = plantilla_seleccionada

    # 3. Sintetizar tokens de diseño (Google Stitch) aplicando las decisiones del Agente Diseñador o la plantilla forzada
    design_tokens = sintetizar_design_system(
        categoria=categoria, 
        nombre_negocio=nombre, 
        sugerencia_gemini=web_content,
        arquetipo_forzado=plantilla_seleccionada
    )

    # 3.1 Detección semántica de subnicho cultural / gastronómico y sincronización fotográfica
    subnicho = web_content.get("subnicho_cultural", "")
    clean_handle = ig_data.get("username") or handle.lstrip("@").strip("/").split("/")[-1]

    # Si ig_data es un fallback curado o no tiene posts reales de Instagram,
    # re-sincronizar el catálogo temático con el subnicho cultural y gastronómico exacto detectado por Gemini
    if ig_data.get("fuente") == "curated_fallback" or not ig_data.get("exito_real") or not ig_data.get("posts"):
        mock_adaptado = generar_datos_instagram_mock(nombre, categoria, ciudad, clean_handle, subnicho=subnicho)
        ig_data["posts"] = mock_adaptado.get("posts", [])
        if not ig_data.get("avatar_url") or not ig_data.get("exito_real"):
            ig_data["avatar_url"] = mock_adaptado.get("avatar_url")
            ig_data["avatar"] = mock_adaptado.get("avatar_url")
        if not ig_data.get("biografia") or not ig_data.get("exito_real"):
            ig_data["biografia"] = mock_adaptado.get("biografia")
        # Asignar imágenes adaptadas a los servicios si venían vacías
        for i, s in enumerate(web_content.get("servicios", [])):
            if not s.get("imagen") and i < len(ig_data["posts"]):
                s["imagen"] = ig_data["posts"][i].get("image_url")

    # Asignar fotos Hero y Detalle contextuales basadas en el subnicho o publicaciones
    if not web_content.get("hero_image_url"):
        if ig_data.get("posts") and len(ig_data["posts"]) > 0:
            web_content["hero_image_url"] = ig_data["posts"][0].get("image_url", "")
    if not web_content.get("detalle_image_url"):
        if ig_data.get("posts") and len(ig_data["posts"]) > 1:
            web_content["detalle_image_url"] = ig_data["posts"][1].get("image_url", "")
        else:
            web_content["detalle_image_url"] = ig_data.get("avatar_url", "")

    # 4. Descargar e incrustar todas las imágenes en Base64 en paralelo (evita bloqueo de CORS/CORP en Chrome)
    urls_a_descargar = []
    if web_content.get("hero_image_url"):
        urls_a_descargar.append(web_content["hero_image_url"])
    if web_content.get("detalle_image_url"):
        urls_a_descargar.append(web_content["detalle_image_url"])
    if ig_data.get("avatar_url"):
        urls_a_descargar.append(ig_data["avatar_url"])
    if ig_data.get("avatar"):
        urls_a_descargar.append(ig_data["avatar"])
    for p in ig_data.get("posts", []):
        if p.get("image_url"):
            urls_a_descargar.append(p["image_url"])
    for s in web_content.get("servicios", []):
        if s.get("imagen"):
            urls_a_descargar.append(s["imagen"])

    # Descarga concurrente ultrarrápida
    b64_map = descargar_imagenes_en_paralelo(urls_a_descargar)

    if web_content.get("hero_image_url") in b64_map:
        web_content["hero_image_url"] = b64_map[web_content["hero_image_url"]]
    if web_content.get("detalle_image_url") in b64_map:
        web_content["detalle_image_url"] = b64_map[web_content["detalle_image_url"]]

    if ig_data.get("avatar_url") in b64_map:
        ig_data["avatar_url"] = b64_map[ig_data["avatar_url"]]
    if ig_data.get("avatar") in b64_map:
        ig_data["avatar"] = b64_map[ig_data["avatar"]]
    if not ig_data.get("avatar_url") and ig_data.get("avatar"):
        ig_data["avatar_url"] = ig_data["avatar"]
    elif not ig_data.get("avatar") and ig_data.get("avatar_url"):
        ig_data["avatar"] = ig_data["avatar_url"]

    for p in ig_data.get("posts", []):
        if p.get("image_url") in b64_map:
            p["image_url"] = b64_map[p["image_url"]]

    for s in web_content.get("servicios", []):
        if s.get("imagen") in b64_map:
            s["imagen"] = b64_map[s["imagen"]]

    # 4.1 Garantía absoluta contra imágenes rotas o en blanco:
    # Si alguna imagen de Instagram falló al descargarse (por DNS efímero de Meta, token expirado o timeout),
    # o si no empieza con 'data:image', recurrimos inmediatamente al catálogo temático curado y lo incrustamos en Base64.
    mock_dataset = None

    def obtener_mock():
        nonlocal mock_dataset
        if mock_dataset is None:
            mock_dataset = generar_datos_instagram_mock(nombre, categoria, ciudad, clean_handle, subnicho=subnicho)
        return mock_dataset

    # Validar avatar
    avatar_val = ig_data.get("avatar_url") or ig_data.get("avatar") or ""
    if not avatar_val.startswith("data:image"):
        fallback_avatar = obtener_mock().get("avatar_url")
        if fallback_avatar:
            b64_av = descargar_imagen_a_base64(fallback_avatar, timeout=10)
            ig_data["avatar_url"] = b64_av
            ig_data["avatar"] = b64_av

    # Validar posts
    posts_validos = []
    for i, p in enumerate(ig_data.get("posts", [])):
        img = p.get("image_url", "")
        if not img.startswith("data:image"):
            mock_posts = obtener_mock().get("posts", [])
            if mock_posts:
                fallback_post = mock_posts[i % len(mock_posts)]
                fallback_img = fallback_post.get("image_url", "")
                p["image_url"] = descargar_imagen_a_base64(fallback_img, timeout=10)
                if not p.get("caption"):
                    p["caption"] = fallback_post.get("caption", "")
        posts_validos.append(p)

    # Si hay menos de 6 publicaciones, rellenar con el catálogo temático curado
    if len(posts_validos) < 6:
        mock_posts = obtener_mock().get("posts", [])
        for i in range(len(posts_validos), min(8, len(mock_posts))):
            extra_post = dict(mock_posts[i])
            extra_post["image_url"] = descargar_imagen_a_base64(extra_post["image_url"], timeout=10)
            posts_validos.append(extra_post)

    ig_data["posts"] = posts_validos

    # Validar servicios
    for i, s in enumerate(web_content.get("servicios", [])):
        if not s.get("imagen", "").startswith("data:image"):
            mock_posts = obtener_mock().get("posts", [])
            if mock_posts:
                fallback_img = mock_posts[i % len(mock_posts)].get("image_url", "")
                s["imagen"] = descargar_imagen_a_base64(fallback_img, timeout=10)

    # 5. Generar enlaces de acción rápida (Teléfono / WhatsApp / Instagram Direct)
    clean_phone = re.sub(r"[^\d+]", "", telefono or "")
    if not clean_phone and ig_data.get("biografia"):
        # Buscar número español en la biografía de Instagram si OSM no tenía teléfono
        match_tel = re.search(r'(?:\+?34\s?)?([6-9]\d{8})', ig_data.get("biografia", ""))
        if match_tel:
            clean_phone = "34" + match_tel.group(1)
            telefono = f"+34 {match_tel.group(1)}"

    whatsapp_url = ""
    clean_handle = ig_data.get("username") or handle.lstrip("@").strip("/").split("/")[-1]
    instagram_url = lead.get("instagram_url") or (f"https://www.instagram.com/{clean_handle}/" if clean_handle else "")

    if clean_phone:
        num_wa = clean_phone.lstrip("+")
        if not num_wa.startswith("34") and len(num_wa) == 9:
            num_wa = "34" + num_wa
        msg_prefilled = f"¡Hola equipo de {nombre}! Os contacto desde vuestra web para pedir información o cita."
        whatsapp_url = f"https://api.whatsapp.com/send?phone={num_wa}&text={urllib.parse.quote(msg_prefilled)}"
    elif clean_handle:
        whatsapp_url = f"https://ig.me/m/{clean_handle}"
    else:
        whatsapp_url = "#contacto"

    slug = slugify(f"{nombre}-{ciudad}")
    categoria_clean = web_content.get("categoria_clean") or limpiar_categoria(categoria)

    # Preparar datos para la plantilla Jinja2 según el arquetipo oficial de Stitch
    template_name = design_tokens.get("template_file", "stitch_luxury_glow.html")
    try:
        template = env.get_template(template_name)
    except Exception as e:
        print(f"[Web Generator Warning] No se pudo cargar {template_name}: {e}. Usando stitch_luxury_glow.html como fallback.")
        template = env.get_template("stitch_luxury_glow.html")

    rendered_html = template.render(
        negocio={
            "nombre": nombre,
            "categoria": categoria,
            "categoria_clean": categoria_clean,
            "direccion": lead.get("direccion", ""),
            "ciudad": ciudad,
            "codigo_postal": lead.get("codigo_postal", ""),
            "telefono": telefono,
            "whatsapp_url": whatsapp_url,
            "instagram_url": instagram_url,
            "lat": float(lead.get("lat") or 41.3851),
            "lon": float(lead.get("lon") or 2.1734)
        },
        ig=ig_data,
        design=design_tokens,
        web=web_content
    )

    print(f"[Web Generator] ✓ Demo generada en memoria para '{nombre}' (slug: {slug}, plantilla: {design_tokens.get('template_file')})")

    return {
        "slug": slug,
        "rendered_html": rendered_html,
        "design_vibe": design_tokens.get("vibe_name"),
        "template_file": design_tokens.get("template_file"),
        "servicios_count": len(web_content.get("servicios", [])),
        "extraccion_fuente": ig_data.get("fuente", "curated_fallback"),
        "extraccion_aviso": ig_data.get("aviso_extraccion", ""),
        "exito_real": ig_data.get("exito_real", False),
        "sitio_web": ig_data.get("sitio_web", ""),
        "external_url": ig_data.get("external_url", "")
    }

