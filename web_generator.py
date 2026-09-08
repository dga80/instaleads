import os
import re
import json
import unicodedata
from pathlib import Path
from typing import Dict, Any

from jinja2 import Environment, FileSystemLoader

from instagram_extractor import obtener_datos_completos_instagram
from stitch_designer import sintetizar_design_system

BASE_DIR = Path(__file__).resolve().parent


env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")))

def slugify(text: str) -> str:
    """Convierte texto en slug URL seguro (ej: 'Taller Dani & Hijos' -> 'taller-dani-hijos')."""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text.lower()).strip()
    return re.sub(r'[-\s]+', '-', text)

def estructurar_contenido_con_gemini(
    nombre: str,
    categoria: str,
    ciudad: str,
    ig_bio: str,
    ig_posts: list,
    cliente_gemini=None
) -> Dict[str, Any]:
    """
    Usa Gemini para convertir el contenido informal de Instagram en un catálogo estructurado
    de servicios, titular de alto impacto y texto de presentación para la web.
    """
    # Si tenemos cliente Gemini disponible
    try:
        from gemini_service import generar_con_gemini_cascade
        posts_text = "\n".join([f"- Post {i+1}: {p.get('caption', '')[:100]}" for i, p in enumerate(ig_posts[:6])])
        prompt = f"""
Actúa como Director Creativo y Copywriter Web de élite para comercios locales.
Vamos a convertir el perfil de Instagram de este negocio en una página web mobile-first de alta conversión.

Datos del negocio:
- Nombre: {nombre}
- Categoría: {categoria}
- Ciudad: {ciudad}
- Biografía de Instagram: {ig_bio}

Publicaciones recientes en Instagram:
{posts_text}

Tu misión es extraer y estructurar el contenido de la web en formato JSON:
1. 'titular': Un título potente y persuasivo para el Hero (máx 8 palabras).
2. 'subtitulo': Una frase que explique el valor diferencial y anime a contactar (máx 20 palabras).
3. 'servicios': Una lista de entre 2 y 4 servicios o especialidades clave detectadas en sus posts. Para cada servicio:
   - 'nombre': Nombre del servicio (ej. "Manicura Rusa con Nivelación", "Revisión Oficial y Frenos", "Desayunos Artesanos").
   - 'descripcion': Breve explicación atractiva (máx 15 palabras).
   - 'precio_o_duracion': Estimación sugerida (ej. "Desde 25€", "Cita Previa", "Consultar", etc.).
4. 'sobre_nosotros': Párrafo cercano y profesional resumiendo su pasión y trayectoria (máx 40 palabras).
5. 'categoria_clean': Nombre corto de la categoría para una etiqueta (ej. "Studio de Uñas", "Taller Especializado", "Café de Especialidad").

Responde ÚNICAMENTE con el objeto JSON válido:
"""
        texto, modelo_usado = generar_con_gemini_cascade(prompt, cliente=cliente_gemini, formato_json=True)
        if texto:
            texto = re.sub(r"^```(json)?", "", texto, flags=re.MULTILINE).strip("` \n")
            data = json.loads(texto)
            if "titular" in data and "servicios" in data:
                print(f"[Gemini Web Structuring] Contenido web generado exitosamente con modelo {modelo_usado}")
                for i, s in enumerate(data.get("servicios", [])):
                    if i < len(ig_posts):
                        s["imagen"] = ig_posts[i].get("image_url")
                return data
    except Exception as e:
        print(f"[Gemini Web Structuring Warning] {e}. Usando generador inteligente local.")

    # Fallback inteligente según categoría si no hay Gemini o hay error
    servicios_base = []
    for i, p in enumerate(ig_posts[:3]):
        caption = p.get("caption", "").strip()
        primera_linea = caption.split("\n")[0] if caption else f"Especialidad {i+1}"
        nombre_serv = primera_linea[:35] if len(primera_linea) > 5 else f"Servicio Premium {i+1}"
        servicios_base.append({
            "nombre": nombre_serv,
            "descripcion": caption[:80] if caption else f"Atención personalizada con los más altos estándares de calidad en {ciudad}.",
            "precio_o_duracion": "Cita previa",
            "imagen": p.get("image_url")
        })

    return {
        "titular": f"{nombre} en {ciudad}",
        "subtitulo": ig_bio or f"Calidad, profesionalidad y trato cercano. Descubre nuestros servicios y reserva tu cita en segundos.",
        "servicios": servicios_base,
        "sobre_nosotros": ig_bio or f"En {nombre} nos dedicamos con pasión a ofrecer la mejor experiencia a nuestros clientes en {ciudad}. Cuidamos cada detalle para garantizar los mejores resultados.",
        "categoria_clean": categoria.split(":")[0].strip().title()
    }

def generar_web_comercio(lead: Dict[str, Any], cliente_gemini=None) -> Dict[str, Any]:
    """
    Ejecuta el pipeline completo de replicación Instagram -> Web Demo:
    1. Extrae fotos, bio y datos de Instagram (Apify / Curated).
    2. Sintetiza el Design System estilo Stitch (colores, fuentes tipográficas y formas).
    3. Estructura el contenido persuasivo con Gemini.
    4. Compila el index.html y lo guarda en demos/{slug}/index.html (GitHub Pages ready).
    """
    nombre = lead.get("nombre", "Comercio Local")
    categoria = lead.get("categoria", "Comercio")
    ciudad = lead.get("ciudad", "España")
    handle = lead.get("instagram_handle") or lead.get("instagram_url", "")
    telefono = lead.get("telefono", "")

    # 1. Extraer datos del perfil de Instagram
    ig_data = obtener_datos_completos_instagram(handle, nombre, categoria, ciudad)

    # 2. Sintetizar tokens de diseño (Google Stitch)
    design_tokens = sintetizar_design_system(categoria, nombre)

    # 3. Estructurar contenidos y servicios con Gemini
    web_content = estructurar_contenido_con_gemini(
        nombre=nombre,
        categoria=categoria,
        ciudad=ciudad,
        ig_bio=ig_data.get("biografia", ""),
        ig_posts=ig_data.get("posts", []),
        cliente_gemini=cliente_gemini
    )

    # 4. Generar enlaces de acción rápida
    clean_phone = re.sub(r"[^\d]", "", telefono)
    if clean_phone and not clean_phone.startswith("34") and len(clean_phone) == 9:
        clean_phone = "34" + clean_phone
    
    whatsapp_url = ""
    if clean_phone:
        msg_prefilled = f"¡Hola equipo de {nombre}! Os contacto desde vuestra web para pedir información o cita."
        whatsapp_url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={msg_prefilled.replace(' ', '%20')}"

    slug = slugify(f"{nombre}-{ciudad}")

    # Preparar datos para la plantilla Jinja2
    template = env.get_template("landing_template.html")
    rendered_html = template.render(
        negocio={
            "nombre": nombre,
            "categoria": categoria,
            "categoria_clean": web_content.get("categoria_clean", categoria),
            "direccion": lead.get("direccion", ""),
            "ciudad": ciudad,
            "codigo_postal": lead.get("codigo_postal", ""),
            "telefono": telefono,
            "whatsapp_url": whatsapp_url,
            "instagram_url": lead.get("instagram_url", f"https://www.instagram.com/{ig_data.get('username')}"),
            "lat": float(lead.get("lat") or 41.3851), # Coordenada real del negocio o fallback Barcelona/Madrid
            "lon": float(lead.get("lon") or 2.1734)
        },
        ig=ig_data,
        design=design_tokens,
        web=web_content
    )

    print(f"[Web Generator] ✓ Demo generada en memoria para '{nombre}' (slug: {slug})")

    return {
        "slug": slug,
        "rendered_html": rendered_html,
        "design_vibe": design_tokens.get("vibe_name"),
        "servicios_count": len(web_content.get("servicios", []))
    }

