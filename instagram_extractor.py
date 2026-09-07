import os
import re
import json
import requests
from typing import Dict, Any, List, Optional

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
    if any(k in clean_cat for k in ["moto", "taller", "mecanic", "coche", "automov"]):
        avatar = "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?w=800&auto=format&fit=crop&q=80", "caption": "Revisión completa de motor y puesta a punto. Seguridad garantizada en cada curva."},
            {"img": "https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=800&auto=format&fit=crop&q=80", "caption": "Cambio de neumáticos de alto rendimiento y equilibrado de precisión."},
            {"img": "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?w=800&auto=format&fit=crop&q=80", "caption": "Mantenimiento integral de frenos y suspensiones. Tu moto siempre lista."},
            {"img": "https://images.unsplash.com/photo-1558980394-4c7c9299fe96?w=800&auto=format&fit=crop&q=80", "caption": "Diagnóstico electrónico y resolución de averías complejas."},
            {"img": "https://images.unsplash.com/photo-1508974239320-0a029497e820?w=800&auto=format&fit=crop&q=80", "caption": "Instalación de escapes y accesorios homologados."},
            {"img": "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?w=800&auto=format&fit=crop&q=80", "caption": "Cuidamos cada detalle como si fuera nuestra propia moto."}
        ]
        bio = f"Especialistas en mecánica de precisión, mantenimiento y diagnóstico en {ciudad}. Pasión por el motor. ¡Pide tu cita sin compromiso!"
    elif any(k in clean_cat for k in ["uña", "estetica", "belleza", "nail", "lash"]):
        avatar = "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=800&auto=format&fit=crop&q=80", "caption": "Diseño exclusivo en acrílico con acabado natural y brillo duradero."},
            {"img": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=800&auto=format&fit=crop&q=80", "caption": "Manicura rusa y nivelación de uña natural. Cuidado y perfección en cada cutícula."},
            {"img": "https://images.unsplash.com/photo-1519014816548-bf5fe059798b?w=800&auto=format&fit=crop&q=80", "caption": "Nail art a mano alzada. ¡Trae tu idea y la hacemos realidad!"},
            {"img": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=800&auto=format&fit=crop&q=80", "caption": "Pedicura spa con tratamiento de hidratación profunda."},
            {"img": "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800&auto=format&fit=crop&q=80", "caption": "Esmaltado semipermanente de máxima duración con productos premium."},
            {"img": "https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?w=800&auto=format&fit=crop&q=80", "caption": "Tu momento de relax y belleza en {ciudad}. Te esperamos con cita previa."}
        ]
        bio = f"Studio de uñas y estética en {ciudad}. Manicura rusa, acrílico, gel y diseños exclusivos. Tu bienestar y belleza en las mejores manos ✨"
    elif any(k in clean_cat for k in ["peluqueria", "barber", "pelo", "hair"]):
        avatar = "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1622286342621-4bd786c2447c?w=800&auto=format&fit=crop&q=80", "caption": "Fade de precisión y arreglo de barba tradicional con toalla caliente."},
            {"img": "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800&auto=format&fit=crop&q=80", "caption": "Corte de autor y peinado adaptado a tus facciones."},
            {"img": "https://images.unsplash.com/photo-1521590832167-7bcbfaa6381f?w=800&auto=format&fit=crop&q=80", "caption": "Coloración, balayage y matices luminosos con tratamiento protector."},
            {"img": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=800&auto=format&fit=crop&q=80", "caption": "Arreglo y perfilado de barba con productos orgánicos."},
            {"img": "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=800&auto=format&fit=crop&q=80", "caption": "Ambiente auténtico y atención personalizada en cada visita."},
            {"img": "https://images.unsplash.com/photo-1599351431202-1e0f0137899a?w=800&auto=format&fit=crop&q=80", "caption": "Reserva tu turno y luce tu mejor versión."}
        ]
        bio = f"Cortes de autor, degradados limpios, color y cuidado capilar en {ciudad}. Reserva tu cita y vive la experiencia."
    elif any(k in clean_cat for k in ["cafe", "restaurante", "bar", "panaderia", "pasteleria", "gastro"]):
        avatar = "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=800&auto=format&fit=crop&q=80", "caption": "Café de especialidad recién tostado y extracción perfecta de espresso."},
            {"img": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&auto=format&fit=crop&q=80", "caption": "Ingredientes de temporada y cocina con alma para disfrutar sin prisas."},
            {"img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&auto=format&fit=crop&q=80", "caption": "Repostería y masa madre horneada cada mañana en nuestro obrador."},
            {"img": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800&auto=format&fit=crop&q=80", "caption": "Un espacio acogedor para compartir desayunos, comidas y sobremesas."},
            {"img": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=800&auto=format&fit=crop&q=80", "caption": "Tostadas artesanas, bowls saludables y bebidas naturales."},
            {"img": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&auto=format&fit=crop&q=80", "caption": "Ven a descubrir nuestro rincón en {ciudad}. ¡Te esperamos!"}
        ]
        bio = f"Sabor, producto artesano y pasión en {ciudad}. Desayunos, especialidades y momentos para disfrutar. Pasa a vernos ☕🥐"
    else:
        # Comercio general
        avatar = "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=300&auto=format&fit=crop&q=80"
        tematicas = [
            {"img": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&auto=format&fit=crop&q=80", "caption": "Calidad, cercanía y atención personalizada en cada uno de nuestros servicios."},
            {"img": "https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=800&auto=format&fit=crop&q=80", "caption": "Selección exclusiva de productos y soluciones a tu medida."},
            {"img": "https://images.unsplash.com/photo-1528698827591-e19ccd7bc23d?w=800&auto=format&fit=crop&q=80", "caption": "Comprometidos con el comercio local y la satisfacción de nuestros clientes."},
            {"img": "https://images.unsplash.com/photo-1556742049-0a67c5574f73?w=800&auto=format&fit=crop&q=80", "caption": "Te asesoramos personalmente para encontrar la mejor opción."},
            {"img": "https://images.unsplash.com/photo-1534452203293-494d7ddbf7e0?w=800&auto=format&fit=crop&q=80", "caption": "Novedades semanales y promociones exclusivas para clientes."},
            {"img": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&auto=format&fit=crop&q=80", "caption": "Tu comercio de confianza en {ciudad}."}
        ]
        bio = f"Tu comercio de proximidad en {ciudad}. Atención experta, calidad garantizada y trato cercano."

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
