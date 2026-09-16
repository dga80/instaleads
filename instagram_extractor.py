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

    # Dominios de redes sociales, mensajería, agregadores y directorios a excluir (NO son un sitio web propio)
    dominios_excluidos = [
        "instagram.com", "facebook.com", "fb.me", "tiktok.com", "twitter.com", "x.com",
        "threads.net", "wa.me", "whatsapp.com", "api.whatsapp.com", "t.me", "telegram.me",
        "youtube.com", "youtu.be", "linkedin.com", "pinterest.com", "spotify.com", "twitch.tv",
        # Agregadores de enlaces y mini-bios
        "linktr.ee", "linktree.com", "beacons.ai", "beacons.page", "bio.site", "campsite.bio",
        "taplink.cc", "taplink.at", "carrd.co", "solo.to", "snipfeed.co", "linkin.bio",
        "lnk.bio", "instabio.cc", "hoo.be", "urlbio.com", "direct.me", "msha.ke",
        "allmylinks.com", "contactinbio.com", "bento.me", "link.me",
        # Motores de búsqueda, mapas y directorios
        "google.com", "maps.google.com", "goo.gl", "maps.app.goo.gl", "tripadvisor.com",
        "tripadvisor.es", "yelp.com", "yelp.es", "tattooswizard.com", "tattoolove.es",
        "culturetattoo.com", "downundercafe.com"
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

def generar_datos_instagram_mock(nombre_negocio: str, categoria: str, ciudad: str, handle: str, subnicho: str = "") -> Dict[str, Any]:
    """
    Genera un conjunto de datos enriquecidos representativos basados en el negocio y su nicho cultural/gastronómico,
    utilizando imágenes temáticas profesionales adaptadas específicamente para garantizar que la demo
    sea visualmente consecuente con la identidad real del local.
    """
    clean_cat = categoria.lower()
    text_corpus = f"{clean_cat} {nombre_negocio.lower()} {handle.lower()} {subnicho.lower()}"
    
    # Selección de imágenes de stock curadas y temáticas por nicho
    if any(k in clean_cat for k in ["detail", "pulido", "car detailing", "coating", "detailing"]):
        avatar = "https://images.unsplash.com/photo-1601362840469-51e4d8d58785?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1601362840469-51e4d8d58785?w=1000&auto=format&fit=crop&q=80", "caption": "Corrección de pintura en varias etapas y sellado cerámico de máxima dureza y brillo espejo."},
            {"img": "https://images.unsplash.com/photo-1520340356584-f9917d1eea6f?w=800&auto=format&fit=crop&q=80", "caption": "Limpieza técnica de interiores, nutrición de cuero e higienización profesional con ozono."},
            {"img": "https://images.unsplash.com/photo-1607860108855-64acf2078ed9?w=800&auto=format&fit=crop&q=80", "caption": "Tratamiento hidrofóbico en cristales y protección PPF contra impactos y microarañazos."},
            {"img": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=800&auto=format&fit=crop&q=80", "caption": "Detallado de llantas y pasos de rueda con coating resistente a altas temperaturas."},
            {"img": "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?w=800&auto=format&fit=crop&q=80", "caption": "Lavado artesanal a mano sin fricción con champú de pH neutro y secado por aire caliente."},
            {"img": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800&auto=format&fit=crop&q=80", "caption": "El acabado showroom que tu vehículo merece en {ciudad}. Pide tu valoración sin compromiso."}
        ]
        bio = f"Especialistas en Car Detailing y tratamiento cerámico en {ciudad}. Corrección de pintura, protección PPF y cuidado artesanal de alta gama."
    elif any(k in clean_cat for k in ["canin", "perr", "mascot", "grooming"]):
        avatar = "https://images.unsplash.com/photo-1516734212186-a967f81ad0d7?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1516734212186-a967f81ad0d7?w=1000&auto=format&fit=crop&q=80", "caption": "Corte a tijera según estándar de raza y estilismo personalizado con mimo y calma."},
            {"img": "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=800&auto=format&fit=crop&q=80", "caption": "Baños relajantes con cosmética natural vegana adaptada al tipo de piel y manto."},
            {"img": "https://images.unsplash.com/photo-1541599540903-216a46ca1dc0?w=800&auto=format&fit=crop&q=80", "caption": "Deslanado profesional y eliminación de pelo muerto para mantener un manto sano y ligero."},
            {"img": "https://images.unsplash.com/photo-1537151625747-768eb6cf92b2?w=800&auto=format&fit=crop&q=80", "caption": "Cuidado e higiene de almohadillas, corte de uñas y limpieza auricular respetuosa."},
            {"img": "https://images.unsplash.com/photo-1548767797-d8c844163c4c?w=800&auto=format&fit=crop&q=80", "caption": "Ambiente tranquilo y libre de jaulas para que su visita sea una experiencia positiva."},
            {"img": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?w=800&auto=format&fit=crop&q=80", "caption": "Tu peluquería canina de confianza en {ciudad}. ¡Pide tu cita previa!"}
        ]
        bio = f"Peluquería y estilismo canino respetuoso en {ciudad}. Baños terapéuticos, corte a tijera y trato con amor sin jaulas 🐶✂️"
    elif any(k in clean_cat for k in ["tarta", "reposteria", "pastel", "cake", "dulce"]):
        avatar = "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=1000&auto=format&fit=crop&q=80", "caption": "Tartas de autor personalizadas para bodas, cumpleaños y celebraciones únicas."},
            {"img": "https://images.unsplash.com/photo-1535141192574-5d4897c13136?w=800&auto=format&fit=crop&q=80", "caption": "Diseños temáticos con flores naturales, detalles en pan de oro y texturas modernas."},
            {"img": "https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?w=800&auto=format&fit=crop&q=80", "caption": "Bizcochos esponjosos y rellenos gourmet con ingredientes 100% naturales."},
            {"img": "https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=800&auto=format&fit=crop&q=80", "caption": "Cupcakes, galletas decoradas y mesas dulces que deslumbran en cualquier evento."},
            {"img": "https://images.unsplash.com/photo-1588195538326-c5b1e9f80a1b?w=800&auto=format&fit=crop&q=80", "caption": "Modelado artesanal y acabados limpios pensados para sorprender al primer vistazo."},
            {"img": "https://images.unsplash.com/photo-1557925923-cd4648e211a0?w=800&auto=format&fit=crop&q=80", "caption": "Creamos la tarta de tus sueños en {ciudad}. Encarga tu diseño con antelación 🎂✨"}
        ]
        bio = f"Obrador de tartas personalizadas y repostería creativa en {ciudad}. Diseños exclusivos y sabor inolvidable para momentos especiales 🎂"
    elif any(k in clean_cat for k in ["microblading", "micropigmentacion", "pmu", "brow"]):
        avatar = "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=1000&auto=format&fit=crop&q=80", "caption": "Microblading pelo a pelo de máxima naturalidad y diseño morfológico según tus facciones."},
            {"img": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800&auto=format&fit=crop&q=80", "caption": "Micropigmentación efecto polvo (Powder Brows) para unas cejas tupidas y elegantes."},
            {"img": "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800&auto=format&fit=crop&q=80", "caption": "Micropigmentación labial (Aquarelle Lips) para dar color, definición y volumen sutil."},
            {"img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=800&auto=format&fit=crop&q=80", "caption": "Pigmentos orgánicos certificados por Sanidad UE y material estéril 100% desechable."},
            {"img": "https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=800&auto=format&fit=crop&q=80", "caption": "Lifting de pestañas y laminado de cejas para potenciar tu mirada sin necesidad de maquillaje."},
            {"img": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b?w=800&auto=format&fit=crop&q=80", "caption": "Especialista certificada en belleza de la mirada en {ciudad}. Pide tu diagnóstico previo ✨"}
        ]
        bio = f"Especialista en Microblading, Powder Brows y Micropigmentación en {ciudad}. Realza tu belleza natural con técnica hiperrealista ✨"
    elif any(k in clean_cat for k in ["microcemento", "pavimento continuo", "resina epoxi", "suelo continuo"]):
        avatar = "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=1000&auto=format&fit=crop&q=80", "caption": "Pavimentos continuos de microcemento sin juntas para un diseño contemporáneo y luminoso."},
            {"img": "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800&auto=format&fit=crop&q=80", "caption": "Reformas de baños integrales en microcemento impermeable y antideslizante de fácil limpieza."},
            {"img": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&auto=format&fit=crop&q=80", "caption": "Encimeras de cocina y mobiliario revestido con acabados satinados y ultra resistentes."},
            {"img": "https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=800&auto=format&fit=crop&q=80", "caption": "Revestimiento de paredes interiores y exteriores con texturas rústicas o pulidas."},
            {"img": "https://images.unsplash.com/photo-1507089947368-19c1da9775ae?w=800&auto=format&fit=crop&q=80", "caption": "Amplia carta de colores minerales y barnices selladores de poliuretano de alta resistencia."},
            {"img": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop&q=80", "caption": "Aplicación artesanal con máxima garantía en {ciudad}. Solicita presupuesto sin compromiso."}
        ]
        bio = f"Aplicación profesional de microcemento en {ciudad}. Pavimentos continuos sin juntas, baños y reformas de alta gama con máxima resistencia."
    elif any(k in clean_cat for k in ["dental", "dentist", "odontol", "dientes", "sonrisa"]):
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
    # Detección y fotos temáticas específicas por gastronomía / cultura internacional
    elif any(k in text_corpus for k in ["colomb", "arepa", "empanada", "latino", "paisa", "bogota", "medellin"]):
        avatar = "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=400&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=1000&auto=format&fit=crop&q=80", "caption": "Nuestras auténticas arepas de maíz doradas con queso fundido y carnes tradicionales en {ciudad}."},
            {"img": "https://images.unsplash.com/photo-1541544741938-0af808871cc0?w=800&auto=format&fit=crop&q=80", "caption": "Empanadas criollas crocantes con relleno jugoso y ají casero recién preparado."},
            {"img": "https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=800&auto=format&fit=crop&q=80", "caption": "Café 100% colombiano de origen, aroma intenso y cuerpo balanceado."},
            {"img": "https://images.unsplash.com/photo-1615870216519-2f9fa575fa5c?w=800&auto=format&fit=crop&q=80", "caption": "Platos criollos completos y generosos: frijoles, arroz, plátano maduro y sazón tradicional."},
            {"img": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80", "caption": "Tu rincón acogedor en {ciudad} para disfrutar de los auténticos sabores de nuestra tierra."},
            {"img": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&auto=format&fit=crop&q=80", "caption": "Desayunos típicos, perritos criollos y sopas del día. ¡Ven a vernos o pide a domicilio!"}
        ]
        bio = f"El auténtico sabor de Colombia en {ciudad}. Arepas caseras, empanadas criollas, platos típicos y café de origen. ¡Pasa a vernos o pide a domicilio! 🇨🇴✨"
    elif any(k in text_corpus for k in ["mexic", "taco", "taquer"]):
        avatar = "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=400&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=1000&auto=format&fit=crop&q=80", "caption": "Tacos al pastor tradicionales con piña asada, cilantro y cebolla fresca en {ciudad}."},
            {"img": "https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?w=800&auto=format&fit=crop&q=80", "caption": "Quesadillas artesanales con queso fundido y salsas caseras de chiles tatemados."},
            {"img": "https://images.unsplash.com/photo-1599974579688-8dbdd335c77f?w=800&auto=format&fit=crop&q=80", "caption": "Guacamole fresco preparado al momento con totopos crujientes de maíz."},
            {"img": "https://images.unsplash.com/photo-1541544741938-0af808871cc0?w=800&auto=format&fit=crop&q=80", "caption": "Especialidades mexicanas al plato con tortillas de maíz recién hechas."},
            {"img": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80", "caption": "Ambiente festivo y la mejor música para compartir con amigos en {ciudad}."},
            {"img": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&auto=format&fit=crop&q=80", "caption": "Margaritas y aguas frescas de sabores naturales para acompañar tus tacos."}
        ]
        bio = f"Auténtica taquería mexicana en {ciudad}. Tacos al pastor, quesadillas, guacamole y sabor tradicional. ¡Viva México! 🌮🇲🇽"
    elif any(k in text_corpus for k in ["pizz", "trattoria", "pasta", "italian"]):
        avatar = "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=1000&auto=format&fit=crop&q=80", "caption": "Pizza napolitana auténtica en horno de leña, masa fermentada 48h e ingredientes DOP en {ciudad}."},
            {"img": "https://images.unsplash.com/photo-1621996346565-e3d5d6281691?w=800&auto=format&fit=crop&q=80", "caption": "Pasta fresca artesana elaborada cada mañana con sémola de trigo duro."},
            {"img": "https://images.unsplash.com/photo-1579684947550-22e945225d9a?w=800&auto=format&fit=crop&q=80", "caption": "Burrata cremosa con tomates cherry maduros y albahaca fresca."},
            {"img": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80", "caption": "Atmósfera de trattoria italiana con selección de vinos y trato familiar."},
            {"img": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=800&auto=format&fit=crop&q=80", "caption": "Antipasti para compartir y postres tradicionales como el clásico tiramisú."},
            {"img": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800&auto=format&fit=crop&q=80", "caption": "Reserva tu mesa y disfruta de la verdadera cocina de Italia en {ciudad}."}
        ]
        bio = f"Auténtica cucina italiana en {ciudad}. Pizza napolitana al horno de leña, pasta fresca artesanal y postres caseros. Buon appetito! 🍕🇮🇹"
    elif any(k in text_corpus for k in ["sushi", "ramen", "japones", "nikkei", "asian"]):
        avatar = "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=400&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=1000&auto=format&fit=crop&q=80", "caption": "Nigiris y uramakis de autor con pescado fresco de lonja y arroz calibrado en {ciudad}."},
            {"img": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=800&auto=format&fit=crop&q=80", "caption": "Ramen artesanal con caldo tonkotsu cocinado a fuego lento durante 12 horas."},
            {"img": "https://images.unsplash.com/photo-1611143669185-af224c5e3252?w=800&auto=format&fit=crop&q=80", "caption": "Gyozas crujientes a la plancha y entrantes asiáticos tradicionales."},
            {"img": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80", "caption": "Espacio zen contemporáneo diseñado para una experiencia culinaria inmersiva."},
            {"img": "https://images.unsplash.com/photo-1553621042-f6e147245754?w=800&auto=format&fit=crop&q=80", "caption": "Sashimi de corte limpio con salmón y atún rojo de primera calidad."},
            {"img": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&auto=format&fit=crop&q=80", "caption": "Reserva tu mesa o pide para llevar y vive Japón en {ciudad}."}
        ]
        bio = f"Gastronomía japonesa de autor en {ciudad}. Sushi fresco, ramen artesanal y bocados de alta cocina nipona. 🍣🥢"
    elif any(k in text_corpus for k in ["burger", "hamburgues"]):
        avatar = "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=1000&auto=format&fit=crop&q=80", "caption": "Smash burgers gourmet con costra perfecta, queso fundido y pan brioche artesano en {ciudad}."},
            {"img": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=800&auto=format&fit=crop&q=80", "caption": "Patatas rústicas sazonadas, bacon crujiente y salsas caseras secretas."},
            {"img": "https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=800&auto=format&fit=crop&q=80", "caption": "Carne 100% vacuno seleccionada y madurada para el máximo sabor y jugosidad."},
            {"img": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80", "caption": "Ambiente desenfadado, buena música y cerveza fría para disfrutar."},
            {"img": "https://images.unsplash.com/photo-1550317138-10000687a72b?w=800&auto=format&fit=crop&q=80", "caption": "Opciones de pollo crujiente con rebozado especiado y dips caseros."},
            {"img": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&auto=format&fit=crop&q=80", "caption": "Ven a probar la hamburguesa de la que todos hablan en {ciudad}."}
        ]
        bio = f"Smash burgers artesanales en {ciudad}. Carne madurada, pan brioche tierno y salsas caseras. ¡Pide la tuya! 🍔🍟"
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
