import os
import re
import json
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

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
    Ejecuta el actor oficial apify/instagram-scraper de forma síncrona
    para obtener el perfil y las últimas publicaciones.
    """
    if not api_token or not username:
        return None

    url = f"https://api.apify.com/v2/acts/apify~instagram-scraper/run-sync-get-dataset-items?token={api_token}"
    payload = {
        "directUrls": [f"https://www.instagram.com/{username}/"],
        "resultsType": "posts",
        "resultsLimit": 8,
        "addParentData": True
    }

    try:
        resp = requests.post(url, json=payload, timeout=40)
        if resp.status_code in (200, 201):
            items = resp.json()
            if items and isinstance(items, list):
                primer_item = items[0]
                # Extraer info del perfil del parent o del primer item
                owner = primer_item.get("owner", {}) or {}
                bio = primer_item.get("ownerBio") or owner.get("biography", "")
                avatar = primer_item.get("ownerProfilePicUrl") or owner.get("profilePicUrl", "")
                full_name = primer_item.get("ownerFullName") or owner.get("fullName", username)
                
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

                return {
                    "username": username,
                    "nombre_completo": full_name or username,
                    "biografia": bio,
                    "avatar_url": avatar,
                    "seguidores": primer_item.get("ownerFollowersCount", 0),
                    "posts": posts,
                    "fuente": "apify"
                }
    except Exception as e:
        print(f"[Apify Scraper Error] {e}")
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
            "caption": t["caption"],
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
        "posts": posts,
        "fuente": "curated_fallback"
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
    adaptados al nicho para que la demo quede perfecta de forma instantánea.
    """
    handle = normalizar_handle(handle_or_url)
    apify_token = os.getenv("APIFY_TOKEN") or os.getenv("APIFY_API_KEY", "").strip()

    if apify_token and handle:
        print(f"[Instagram Extractor] Consultando Apify para @{handle}...")
        datos = extraer_con_apify(handle, apify_token)
        if datos and datos.get("posts"):
            print(f"[Instagram Extractor] ✓ Obtenidos {len(datos['posts'])} posts reales vía Apify.")
            return datos

    # Fallback visual de alta fidelidad
    print(f"[Instagram Extractor] Generando feed curado adaptado a '{categoria}' para @{handle}...")
    return generar_datos_instagram_mock(nombre_negocio, categoria, ciudad, handle)
