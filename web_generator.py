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
Actúa como Diseñador Principal UX/UI y Director Creativo de élite para comercios locales.
Tu objetivo es diseñar la identidad visual, el modo cromático y la arquitectura de contenidos de una landing page mobile-first de máxima conversión para este negocio.

Datos del negocio:
- Nombre: {nombre}
- Categoría: {categoria}
- Ciudad: {ciudad}
- Biografía de Instagram: {ig_bio}

Publicaciones recientes en Instagram:
{posts_text}

Tu misión como Director de Diseño y Copywriting es decidir y estructurar el contenido en JSON:
1. 'tema_predeterminado': Modo visual inicial ideal para este negocio. Elige estrictamente entre "light" o "dark".
   - Regla de diseño UX: Negocios de salud, clínicas dentales, centros médicos, spas, panaderías, cafeterías, boutiques de moda o belleza transmiten mucha mayor higiene, luminosidad, confianza y frescura con "light".
   - Talleres de motos/coches, estudios de tatuaje, discotecas, barberías oscuras o negocios técnicos transmiten más potencia e identidad industrial con "dark".
2. 'arquetipo_diseno': Arquetipo visual más idóneo. Elige estrictamente uno entre:
   - "fresh_clinical" (clínicas dentales, medicina, fisioterapia, estética limpia)
   - "technical_dark" (talleres de motos, coches, mecánica, diagnosis)
   - "editorial_luxury" (centros de uñas de autor, alta cosmética, joyería, moda)
   - "warm_artisan" (cafeterías de especialidad, panaderías artesanas, restaurantes)
   - "modern_lifestyle" (fitness, gimnasios, barberías urbanas, estudios)
3. 'badge_status': Una frase de estado con emoji para el header (ej. "🩺 1ª CITA & REVISIÓN DIGITAL DISPONIBLE", "⚡ BOX DE TALLER ACTIVO • CITA RÁPIDA", "✨ CITAS ABIERTAS • AGENDA ONLINE").
4. 'titular': Un título potente y persuasivo para el Hero (máx 8 palabras).
5. 'subtitulo': Una frase que explique el valor diferencial y anime a contactar (máx 20 palabras).
6. 'servicios': Lista de entre 2 y 4 servicios o especialidades clave detectadas. Para cada uno:
   - 'nombre': Nombre del servicio (ej. "Ortodoncia Invisible & Carillas", "Revisión Oficial y Neumáticos", "Manicura Rusa con Nivelación").
   - 'descripcion': Breve explicación atractiva (máx 15 palabras).
   - 'precio_o_duracion': Estimación sugerida (ej. "1ª Visita Gratuita", "Presupuesto sin compromiso", "Desde 25€", etc.).
7. 'sobre_nosotros': Párrafo cercano y profesional resumiendo su propuesta de valor (máx 40 palabras).
8. 'categoria_clean': Nombre corto y limpio de la categoría para la etiqueta (ej. "Clínica Dental", "Taller Especializado", "Studio de Uñas").

Responde ÚNICAMENTE con el objeto JSON válido:
"""
        texto, modelo_usado = generar_con_gemini_cascade(prompt, cliente=cliente_gemini, formato_json=True)
        if texto:
            texto = re.sub(r"^```(json)?", "", texto, flags=re.MULTILINE).strip("` \n")
            data = json.loads(texto)
            if "titular" in data and "servicios" in data:
                print(f"[Gemini Web Structuring] Contenido y diseño UX/UI generados con modelo {modelo_usado} (Tema: {data.get('tema_predeterminado')}, Arquetipo: {data.get('arquetipo_diseno')})")
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

    cat_low = (categoria + " " + nombre).lower()
    default_theme = "light" if any(k in cat_low for k in ["dental", "dentist", "clinic", "salud", "fisioterap", "uña", "belleza", "spa", "cafe", "panader"]) else "dark"

    return {
        "tema_predeterminado": default_theme,
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
    2. Estructura el contenido persuasivo y decisiones UX/UI con Gemini.
    3. Sintetiza el Design System estilo Stitch con tokens cromáticos y tipográficos.
    4. Compila el index.html y lo prepara para despliegue en GitHub Pages.
    """
    nombre = lead.get("nombre", "Comercio Local")
    categoria = lead.get("categoria", "Comercio")
    ciudad = lead.get("ciudad", "España")
    handle = lead.get("instagram_handle") or lead.get("instagram_url", "")
    telefono = lead.get("telefono", "")

    # 1. Extraer datos del perfil de Instagram
    ig_data = obtener_datos_completos_instagram(handle, nombre, categoria, ciudad)

    # 2. Estructurar contenidos, copy persuasivo y decisiones de diseño con Gemini
    web_content = estructurar_contenido_con_gemini(
        nombre=nombre,
        categoria=categoria,
        ciudad=ciudad,
        ig_bio=ig_data.get("biografia", ""),
        ig_posts=ig_data.get("posts", []),
        cliente_gemini=cliente_gemini
    )

    # 3. Sintetizar tokens de diseño (Google Stitch) aplicando las decisiones del Agente Diseñador
    design_tokens = sintetizar_design_system(categoria, nombre, sugerencia_gemini=web_content)

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

