import os
import re
import json
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

import urllib.parse

def extraer_sitio_web_perfil(item: Dict[str, Any]) -> str:
    """
    Extrae y normaliza el sitio web oficial enlazado en el perfil de Instagram.
    Comprueba externalUrl, externalUrlShimmed, bioLinks y regex en biography.
    Filtra redes sociales (WhatsApp, FB, TikTok, etc.) para evitar falsos positivos.
    """
    if not isinstance(item, dict):
        return ""

    candidatos = []

    # 1. externalUrl directo
    if item.get("externalUrl"):
        candidatos.append(str(item["externalUrl"]).strip())

    # 2. externalUrlShimmed (enlace de redirección seguro de Instagram: l.instagram.com/?u=...)
    if item.get("externalUrlShimmed"):
        shim = str(item["externalUrlShimmed"]).strip()
        try:
            parsed = urllib.parse.urlparse(shim)
            qs = urllib.parse.parse_qs(parsed.query)
            if "u" in qs and qs["u"]:
                candidatos.append(qs["u"][0].strip())
        except Exception:
            pass

    # 3. bioLinks (formato moderno de múltiples enlaces en bio de Instagram)
    bio_links = item.get("bioLinks")
    if isinstance(bio_links, list):
        for bl in bio_links:
            if isinstance(bl, dict) and bl.get("url"):
                candidatos.append(str(bl["url"]).strip())

    # 4. website directo
    if item.get("website"):
        candidatos.append(str(item["website"]).strip())

    # 5. URLs explícitas en el texto de la biografía
    bio_texto = item.get("biography") or item.get("bio") or ""
    if bio_texto:
        urls_bio = re.findall(r'(?:https?://|www\.)[a-zA-Z0-9_\-\.]+\.[a-zA-Z]{2,}(?:/[^\s]*)?', bio_texto)
        candidatos.extend([u.strip() for u in urls_bio])

    # Dominios de redes sociales y mensajería a excluir (NO son un sitio web propio)
    dominios_excluidos = [
        "instagram.com", "facebook.com", "fb.me", "tiktok.com", "twitter.com", "x.com",
        "threads.net", "wa.me", "whatsapp.com", "t.me", "telegram.me", "youtube.com",
        "youtu.be", "linkedin.com", "pinterest.com", "spotify.com", "twitch.tv"
    ]

    for cand in candidatos:
        if not cand:
            continue
        # Limpieza básica
        url_limpia = cand.strip().strip("'\"<>[]()").rstrip("/ .,;:")
        if not url_limpia:
            continue

        if not url_limpia.startswith("http://") and not url_limpia.startswith("https://"):
            url_limpia = "https://" + url_limpia

        try:
            parsed = urllib.parse.urlparse(url_limpia)
            netloc = parsed.netloc.lower().replace("www.", "")
            if not netloc or "." not in netloc:
                continue

            # Comprobar si pertenece a redes sociales excluidas
            if any(excl in netloc for excl in dominios_excluidos):
                continue

            # Si pasa los filtros, hemos encontrado una web válida
            return url_limpia
        except Exception:
            continue

    return ""

def normalizar_handle(handle_or_url: str) -> str:
    """Extrae el nombre de usuario limpio sin @ ni URLs."""
    if not handle_or_url:
        return ""
    limpio = handle_or_url.strip()
    match = re.search(r"instagram\.com/([a-zA-Z0-9_\.\-]+)", limpio)
    if match:
        return match.group(1).rstrip("/")
    return limpio.lstrip("@").rstrip("/")

def extraer_con_apify(username: str, api_token: str) -> Optional[Dict[str, Any]]:
    """
    Ejecuta el actor oficial apify/instagram-scraper de forma síncrona.
    1. Primero intenta con resultsType='details', que obtiene en una sola llamada rápida:
       - Biografía real completa
       - Foto de perfil (avatar HD)
       - Contador de seguidores
       - Enlace web oficial (externalUrl, externalUrlShimmed, bioLinks)
       - Las 12 publicaciones más recientes con fotos de alta resolución y texto
    2. Si 'details' no devolviera posts, recurre a resultsType='posts' como respaldo.
    """
    if not api_token or not username:
        return None

    base_url = f"https://api.apify.com/v2/acts/apify~instagram-scraper/run-sync-get-dataset-items?token={api_token}"

    # Intento 1: Modo 'details' (Mucho más completo y rápido)
    try:
        payload_details = {
            "directUrls": [f"https://www.instagram.com/{username}/"],
            "resultsType": "details"
        }
        resp = requests.post(base_url, json=payload_details, timeout=40)
        if resp.status_code in (200, 201):
            items = resp.json()
            if items and isinstance(items, list):
                item = items[0]
                latest_posts = item.get("latestPosts") or []
                if latest_posts:
                    bio = item.get("biography") or ""
                    avatar = item.get("profilePicUrlHD") or item.get("profilePicUrl") or ""
                    full_name = item.get("fullName") or username
                    followers = item.get("followersCount") or 0
                    sitio_web = extraer_sitio_web_perfil(item)

                    posts = []
                    for p in latest_posts[:12]:
                        img_url = p.get("displayUrl") or p.get("thumbnailUrl") or (p.get("images", [None])[0])
                        caption = p.get("caption") or ""
                        likes = p.get("likesCount", 0)
                        timestamp = p.get("timestamp", "")
                        post_url = p.get("url") or (f"https://www.instagram.com/p/{p.get('shortCode')}/" if p.get("shortCode") else "")
                        if img_url:
                            posts.append({
                                "image_url": img_url,
                                "caption": caption[:250],
                                "likes": likes,
                                "date": timestamp,
                                "url": post_url
                            })

                    if posts:
                        return {
                            "username": username,
                            "nombre_completo": full_name,
                            "biografia": bio,
                            "avatar_url": avatar,
                            "seguidores": followers,
                            "sitio_web": sitio_web,
                            "external_url": item.get("externalUrl") or "",
                            "bio_links": item.get("bioLinks") or [],
                            "posts": posts,
                            "fuente": "apify",
                            "exito_real": True,
                            "aviso_extraccion": ""
                        }
    except Exception as e:
        print(f"[Apify Details Error] {e}")

    # Intento 2: Modo 'posts' de respaldo
    try:
        payload_posts = {
            "directUrls": [f"https://www.instagram.com/{username}/"],
            "resultsType": "posts",
            "resultsLimit": 8,
            "addParentData": True
        }
        resp = requests.post(base_url, json=payload_posts, timeout=40)
        if resp.status_code in (200, 201):
            items = resp.json()
            if items and isinstance(items, list):
                primer_item = items[0]
                owner = primer_item.get("owner", {}) or {}
                bio = primer_item.get("ownerBio") or owner.get("biography", "")
                avatar = primer_item.get("ownerProfilePicUrl") or owner.get("profilePicUrl", "")
                full_name = primer_item.get("ownerFullName") or owner.get("fullName", username)
                sitio_web = extraer_sitio_web_perfil(primer_item) or extraer_sitio_web_perfil(owner)
                
                posts = []
                for it in items:
                    img_url = it.get("displayUrl") or it.get("thumbnailUrl") or (it.get("images", [None])[0])
                    caption = it.get("caption") or ""
                    likes = it.get("likesCount", 0)
                    timestamp = it.get("timestamp", "")
                    post_url = it.get("url", "")
                    if img_url:
                        posts.append({
                            "image_url": img_url,
                            "caption": caption[:250],
                            "likes": likes,
                            "date": timestamp,
                            "url": post_url
                        })

                if posts:
                    return {
                        "username": username,
                        "nombre_completo": full_name or username,
                        "biografia": bio,
                        "avatar_url": avatar,
                        "seguidores": primer_item.get("ownerFollowersCount", 0),
                        "sitio_web": sitio_web,
                        "external_url": primer_item.get("externalUrl") or owner.get("externalUrl") or "",
                        "bio_links": primer_item.get("bioLinks") or owner.get("bioLinks") or [],
                        "posts": posts,
                        "fuente": "apify",
                        "exito_real": True,
                        "aviso_extraccion": ""
                    }
    except Exception as e:
        print(f"[Apify Posts Error] {e}")
    return None

def generar_datos_instagram_mock(nombre_negocio: str, categoria: str, ciudad: str, handle: str) -> Dict[str, Any]:
    """
    Genera un conjunto de datos enriquecidos representativos basados en el negocio,
    utilizando imágenes temáticas profesionales de Unsplash para garantizar que la demo
    sea visualmente impactante y única de inmediato.
    """
    clean_cat = categoria.lower()
    
    # Selección de imágenes de stock curadas y temáticas por nicho
    if any(k in clean_cat for k in ["dental", "dentist", "odontol", "dientes", "sonrisa"]):
        avatar = "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=1000&auto=format&fit=crop&q=80", "caption": "Tecnología de diagnóstico 3D y odontología mínimamente invasiva. Tu salud dental en las mejores manos."},
            {"img": "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=800&auto=format&fit=crop&q=80", "caption": "Diseño de sonrisas y blanqueamiento dental avanzado con resultados inmediatos y naturales."},
            {"img": "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=800&auto=format&fit=crop&q=80", "caption": "Ortodoncia invisible (alineadores transparentes) y tratamientos personalizados para adultos y niños."},
            {"img": "https://images.unsplash.com/photo-1598256989800-fe5f95da9787?w=800&auto=format&fit=crop&q=80", "caption": "Implantología guiada por ordenador y rehabilitación oral de máxima durabilidad."},
            {"img": "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=800&auto=format&fit=crop&q=80", "caption": "Instalaciones de máxima higiene y confort para que tu visita sea relajante y segura."},
            {"img": "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=800&auto=format&fit=crop&q=80", "caption": "Equipo médico cercano y profesional. Pide tu primera revisión y diagnóstico sin compromiso."}
        ]
        bio = f"Clínica odontológica de referencia en {ciudad}. Implantes, estética dental, ortodoncia invisible y prevención. Cuidamos de tu sonrisa y salud con la última tecnología."
    elif any(k in clean_cat for k in ["clinic", "salud", "fisioterap", "osteopat", "podol", "medico", "psicol"]):
        avatar = "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=1000&auto=format&fit=crop&q=80", "caption": "Tratamientos especializados de recuperación funcional y terapia manual avanzada."},
            {"img": "https://images.unsplash.com/photo-1584515979956-d9f6e5d09982?w=800&auto=format&fit=crop&q=80", "caption": "Diagnóstico individualizado y planes de salud integrales adaptados a tu ritmo de vida."},
            {"img": "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=800&auto=format&fit=crop&q=80", "caption": "Especialistas en bienestar corporal, rehabilitación deportiva y prevención de lesiones."},
            {"img": "https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=800&auto=format&fit=crop&q=80", "caption": "Espacio clínico moderno y relajante para garantizar tu máxima recuperación."},
            {"img": "https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=800&auto=format&fit=crop&q=80", "caption": "Tecnología clínica de vanguardia y aparatología médica certificada."},
            {"img": "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=800&auto=format&fit=crop&q=80", "caption": "Atención humana, cercana y de confianza en {ciudad}."}
        ]
        bio = f"Centro de salud y bienestar en {ciudad}. Terapias avanzadas, atención personalizada y profesionales cualificados para cuidar de ti."
    elif any(k in clean_cat for k in ["gimnasio", "fitness", "crossfit", "gym", "entrenam", "yoga", "pilates"]):
        avatar = "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=1000&auto=format&fit=crop&q=80", "caption": "Entrenamiento funcional y fuerza con equipamiento de alta gama para alcanzar tus metas."},
            {"img": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=800&auto=format&fit=crop&q=80", "caption": "Clases grupales dinámicas dirigidas por entrenadores certificados."},
            {"img": "https://images.unsplash.com/photo-1540497077202-7c8a3999166f?w=800&auto=format&fit=crop&q=80", "caption": "Espacios amplios, zonas de peso libre y área de cardio de última generación."},
            {"img": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=800&auto=format&fit=crop&q=80", "caption": "Planes de entrenamiento y nutrición deportiva totalmente personalizados."},
            {"img": "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800&auto=format&fit=crop&q=80", "caption": "Comunidad activa, motivación y ambiente inmejorable cada día."},
            {"img": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?w=800&auto=format&fit=crop&q=80", "caption": "¡Únete hoy y prueba tu primera sesión gratuita en {ciudad}!"}
        ]
        bio = f"Tu club de fitness y entrenamiento en {ciudad}. Instalaciones premium, entrenadores personales y clases dirigidas. Transforma tu energía 💪"
    elif any(k in clean_cat for k in ["moto", "taller", "mecanic", "coche", "automov", "neumat"]):
        avatar = "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?w=1000&auto=format&fit=crop&q=80", "caption": "Revisión completa de motor y puesta a punto. Seguridad y potencia en cada trayecto."},
            {"img": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=800&auto=format&fit=crop&q=80", "caption": "Cambio de neumáticos de alto rendimiento y equilibrado con tecnología láser."},
            {"img": "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?w=800&auto=format&fit=crop&q=80", "caption": "Mantenimiento integral de frenos, suspensiones y electrónica oficial."},
            {"img": "https://images.unsplash.com/photo-1558980394-4c7c9299fe96?w=800&auto=format&fit=crop&q=80", "caption": "Diagnóstico computerizado y resolución de averías complejas."},
            {"img": "https://images.unsplash.com/photo-1508974239320-0a029497e820?w=800&auto=format&fit=crop&q=80", "caption": "Instalación de accesorios homologados y recambios originales."},
            {"img": "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?w=800&auto=format&fit=crop&q=80", "caption": "Cuidamos de tu vehículo con la máxima garantía y rapidez en {ciudad}."}
        ]
        bio = f"Especialistas en mecánica de precisión, mantenimiento y diagnosis en {ciudad}. Pasión por el motor y servicio de confianza. ¡Pide tu cita!"
    elif any(k in clean_cat for k in ["uña", "estetica", "belleza", "nail", "lash", "spa"]):
        avatar = "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=1000&auto=format&fit=crop&q=80", "caption": "Diseño exclusivo en acrílico y gel con acabado natural y brillo duradero."},
            {"img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=800&auto=format&fit=crop&q=80", "caption": "Manicura rusa y nivelación de uña natural. Cuidado y perfección en cutículas."},
            {"img": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b?w=800&auto=format&fit=crop&q=80", "caption": "Nail art a mano alzada y extensiones de pestañas pelo a pelo."},
            {"img": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800&auto=format&fit=crop&q=80", "caption": "Tratamientos faciales y pedicura spa con hidratación profunda."},
            {"img": "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800&auto=format&fit=crop&q=80", "caption": "Esmaltado semipermanente premium con marcas líderes internacionales."},
            {"img": "https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=800&auto=format&fit=crop&q=80", "caption": "Tu momento de relax y belleza en {ciudad}. Te esperamos con cita previa ✨"}
        ]
        bio = f"Studio de uñas y estética en {ciudad}. Manicura rusa, acrílico, pestañas y tratamientos exclusivos. Tu bienestar y belleza en las mejores manos ✨"
    elif any(k in clean_cat for k in ["peluqueria", "barber", "pelo", "hair"]):
        avatar = "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?w=1000&auto=format&fit=crop&q=80", "caption": "Fade de precisión y arreglo de barba tradicional con ritual de toalla caliente."},
            {"img": "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800&auto=format&fit=crop&q=80", "caption": "Cortes de autor, peinados de tendencia y asesoría de imagen personalizada."},
            {"img": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f?w=800&auto=format&fit=crop&q=80", "caption": "Coloración premium, balayage luminoso y tratamientos de hidratación capilar."},
            {"img": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=800&auto=format&fit=crop&q=80", "caption": "Arreglo y perfilado de barba con productos orgánicos de primera calidad."},
            {"img": "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=800&auto=format&fit=crop&q=80", "caption": "Ambiente auténtico y atención cuidada al detalle en cada servicio."},
            {"img": "https://images.unsplash.com/photo-1599351431202-1e0f0137899a?w=800&auto=format&fit=crop&q=80", "caption": "Reserva tu turno y luce tu mejor versión en {ciudad}."}
        ]
        bio = f"Cortes de autor, degradados limpios, color y cuidado capilar en {ciudad}. Reserva tu cita y vive la experiencia."
    elif any(k in clean_cat for k in ["cafe", "restaurante", "bar", "panaderia", "pasteleria", "gastro"]):
        avatar = "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=1000&auto=format&fit=crop&q=80", "caption": "Café de especialidad recién tostado y extracción de autor para los más exigentes."},
            {"img": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80", "caption": "Ingredientes frescos de temporada y cocina con alma para saborear sin prisas."},
            {"img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&auto=format&fit=crop&q=80", "caption": "Repostería artesanal y panes de masa madre horneados a diario en nuestro obrador."},
            {"img": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&auto=format&fit=crop&q=80", "caption": "Espacio acogedor y atmósfera única para tus desayunos, comidas y sobremesas."},
            {"img": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=800&auto=format&fit=crop&q=80", "caption": "Tostadas gourmet, platos saludables y bebidas naturales de autor."},
            {"img": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&auto=format&fit=crop&q=80", "caption": "Ven a descubrir nuestro rincón favorito en {ciudad}. ¡Te esperamos! ☕🥐"}
        ]
        bio = f"Sabor, producto artesano y pasión en {ciudad}. Desayunos, especialidades y momentos para disfrutar. Pasa a vernos ☕🥐"
    elif any(k in clean_cat for k in ["tattoo", "tatuaj", "piercing", "ink", "body art"]):
        avatar = "https://images.unsplash.com/photo-1598371839696-5c5bb00bdc28?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1598371839696-5c5bb00bdc28?w=1000&auto=format&fit=crop&q=80", "caption": "Diseños exclusivos, líneas finas y realismo blackwork. Arte único plasmado en tu piel."},
            {"img": "https://images.unsplash.com/photo-1562962230-16e4623d36e6?w=800&auto=format&fit=crop&q=80", "caption": "Sesiones de realismo en sombras y piezas de gran formato con acabado de máxima precisión."},
            {"img": "https://images.unsplash.com/photo-1611501275019-9b5cda994e8d?w=800&auto=format&fit=crop&q=80", "caption": "Material esterilizado 100% desechable, tintas homologadas UE y máxima higiene sanitaria."},
            {"img": "https://images.unsplash.com/photo-1568515045052-f9a854d70bfd?w=800&auto=format&fit=crop&q=80", "caption": "Piercings de precisión y anillado profesional con joyería de titanio grado implante."},
            {"img": "https://images.unsplash.com/photo-1550537687-c91072c4792d?w=800&auto=format&fit=crop&q=80", "caption": "Cover-up y restauración de tatuajes con técnicas avanzadas de contraste."},
            {"img": "https://images.unsplash.com/photo-1560707303-4e980ce876ad?w=800&auto=format&fit=crop&q=80", "caption": "Asesoramiento personalizado en diseño antes de cada sesión en {ciudad}."}
        ]
        bio = f"Estudio de tatuajes y piercing en {ciudad}. Diseños de autor, realismo, fine line y máxima higiene. ¡Reserva tu sesión! 🖤"
    else:
        # Comercio y servicios profesionales de proximidad
        avatar = "https://images.unsplash.com/photo-1497366216548-37526070297c?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1000&auto=format&fit=crop&q=80", "caption": "Excelencia, cercanía y asesoramiento profesional en cada uno de nuestros servicios."},
            {"img": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&auto=format&fit=crop&q=80", "caption": "Soluciones a medida con los más altos estándares de calidad y garantía."},
            {"img": "https://images.unsplash.com/photo-1556742049-0a67c5574f73?w=800&auto=format&fit=crop&q=80", "caption": "Compromiso absoluto con nuestros clientes y con el tejido local de {ciudad}."},
            {"img": "https://images.unsplash.com/photo-1497215728101-856f4ea42174?w=800&auto=format&fit=crop&q=80", "caption": "Atención personalizada y respuesta ágil a todas tus consultas."},
            {"img": "https://images.unsplash.com/photo-1521791136064-7986c2920216?w=800&auto=format&fit=crop&q=80", "caption": "Confianza, transparencia y resultados comprobados."},
            {"img": "https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=800&auto=format&fit=crop&q=80", "caption": "Tu elección de confianza en {ciudad}. Contáctanos hoy mismo."}
        ]
        bio = f"Servicio profesional y cercano en {ciudad}. Calidad, experiencia y dedicación en cada proyecto."

    posts = [
        {
            "image_url": t["img"],
            "caption": t["caption"].replace("{ciudad}", ciudad),
            "likes": 42 + (i * 18),
            "date": "Reciente",
            "url": f"https://www.instagram.com/{handle}/"
        }
        for i, t in enumerate(tematicas)
    ]

    return {
        "username": handle or "comercio_local",
        "nombre_completo": nombre_negocio,
        "biografia": bio,
        "avatar_url": avatar,
        "seguidores": 1420,
        "sitio_web": "",
        "external_url": "",
        "bio_links": [],
        "posts": posts,
        "fuente": "curated_fallback",
        "exito_real": False,
        "aviso_extraccion": f"No se pudieron extraer fotos reales de Instagram (@{handle or nombre_negocio}). Se ha generado la web con fotos de catálogo temáticas adaptadas a {categoria}."
    }

def obtener_datos_completos_instagram(
    handle_or_url: str,
    nombre_negocio: str,
    categoria: str,
    ciudad: str
) -> Dict[str, Any]:
    """
    Intenta extraer datos reales mediante Apify si hay token configurado.
    Si no hay token o la extracción falla, recurre a datos curados de alta calidad
    adaptados al nicho y notifica con un aviso transparente.
    """
    handle = normalizar_handle(handle_or_url)
    apify_token = os.getenv("APIFY_TOKEN") or os.getenv("APIFY_API_KEY", "").strip()

    if apify_token and handle:
        print(f"[Instagram Extractor] Consultando Apify para @{handle}...")
        datos = extraer_con_apify(handle, apify_token)
        if datos and datos.get("posts"):
            print(f"[Instagram Extractor] ✓ Obtenidos {len(datos['posts'])} posts y perfil real vía Apify.")
            return datos
        else:
            print(f"[Instagram Extractor] ⚠️ Apify no devolvió publicaciones para @{handle}. Activando fallback curado.")

    # Fallback visual de alta fidelidad
    print(f"[Instagram Extractor] Generando feed curado adaptado a '{categoria}' para @{handle}...")
    return generar_datos_instagram_mock(nombre_negocio, categoria, ciudad, handle)
