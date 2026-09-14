"""
Módulo de diseño inspirado en la arquitectura de Design Systems de Google Stitch.
Sintetiza tokens visuales únicos (Color Semilla, Paleta Tonal, Emparejamiento Tipográfico
y Lenguaje de Formas) para que cada web tenga una identidad exclusiva según su nicho.
"""

from typing import Dict, Any

# Catálogo de Arquetipos de Diseño estilo Stitch Oficial
DESIGN_ARCHETYPES = {
    "luxury_glow": {
        "template_file": "stitch_luxury_glow.html",
        "layout_type": "editorial_luxury",
        "headline_font": "'Playfair Display', serif",
        "body_font": "'Plus Jakarta Sans', sans-serif",
        "google_fonts_url": "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;0,800;1,400;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "color_seed": "#d49757", # Oro champán
        "primary": "#855319",
        "primary_container": "#d49757",
        "on_primary": "#ffffff",
        "accent": "#fbb976",
        # Modo Oscuro
        "bg_surface": "#0c0a09",
        "card_surface": "rgba(28, 25, 23, 0.85)",
        "border_color": "rgba(212, 151, 87, 0.28)",
        "text_primary": "#fafaf9",
        "text_secondary": "#a8a29e",
        "header_bg": "rgba(12, 10, 9, 0.88)",
        "drawer_bg": "rgba(12, 10, 9, 0.98)",
        "badge_bg": "rgba(212, 151, 87, 0.18)",
        "badge_text": "#f3c68f",
        # Modo Claro
        "light_bg_surface": "#fff8f5",
        "light_card_surface": "#ffffff",
        "light_border_color": "rgba(212, 151, 87, 0.25)",
        "light_text_primary": "#1e1b19",
        "light_text_secondary": "#514439",
        "light_header_bg": "rgba(255, 248, 245, 0.92)",
        "light_drawer_bg": "rgba(255, 255, 255, 0.98)",
        "light_badge_bg": "rgba(212, 151, 87, 0.16)",
        "light_badge_text": "#855319",
        "light_pill_bg": "rgba(212, 151, 87, 0.08)",
        "light_pill_border": "rgba(212, 151, 87, 0.25)",
        # Formas y Estilo
        "roundness": "1.25rem",
        "roundness_button": "9999px",
        "default_theme": "light",
        "cta_gradient": "linear-gradient(135deg, #d49757 0%, #855319 100%)",
        "vibe_name": "Luxury Glow (Estética, Uñas, Pestañas & Alta Cosmética)",
        "status_badge": "✨ ATENCIÓN EXCLUSIVA • CITA PREVIA",
        "badges_confianza": [
            {"icono": "✨", "titulo": "Cuidado de Autor", "desc": "Técnicas exclusivas y acabados de alta fidelidad."},
            {"icono": "💎", "titulo": "Marcas Líderes", "desc": "Productos premium y máxima durabilidad garantizada."},
            {"icono": "🌿", "titulo": "Espacio Exclusivo", "desc": "Atmósfera relajante y trato 100% personalizado."}
        ]
    },
    "urban_edge": {
        "template_file": "stitch_urban_edge.html",
        "layout_type": "technical_industrial",
        "headline_font": "'Space Grotesk', sans-serif",
        "body_font": "'DM Sans', sans-serif",
        "google_fonts_url": "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700;800&family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap",
        "color_seed": "#f97316", # Blaze Orange
        "primary": "#ffb690",
        "primary_container": "#f97316",
        "on_primary": "#552100",
        "accent": "#ffdbca",
        # Modo Oscuro (Brutalist Technical Industrial)
        "bg_surface": "#131315",
        "card_surface": "#201f22",
        "border_color": "#27272a",
        "text_primary": "#e5e1e4",
        "text_secondary": "#a1a1aa",
        "header_bg": "rgba(19, 19, 21, 0.95)",
        "drawer_bg": "#131315",
        "badge_bg": "rgba(249, 115, 22, 0.18)",
        "badge_text": "#f97316",
        # Modo Claro
        "light_bg_surface": "#f4f5f7",
        "light_card_surface": "#ffffff",
        "light_border_color": "rgba(249, 115, 22, 0.35)",
        "light_text_primary": "#0f172a",
        "light_text_secondary": "#475569",
        "light_header_bg": "rgba(244, 245, 247, 0.94)",
        "light_drawer_bg": "#ffffff",
        "light_badge_bg": "rgba(249, 115, 22, 0.16)",
        "light_badge_text": "#c2410c",
        "light_pill_bg": "rgba(249, 115, 22, 0.08)",
        "light_pill_border": "rgba(249, 115, 22, 0.25)",
        # Formas
        "roundness": "0.5rem", # Ángulos rectos industriales
        "roundness_button": "0.5rem",
        "default_theme": "dark",
        "cta_gradient": "linear-gradient(135deg, #f97316 0%, #ea580c 100%)",
        "vibe_name": "Urban Edge & Dark Tech (Tatuajes, Barberías, Talleres & Fitness)",
        "status_badge": "🟢 BOX ABIERTO / CITAS DISPONIBLES",
        "badges_confianza": [
            {"icono": "⚙️", "titulo": "Técnica & Precisión", "desc": "Acabados de precisión con estándares profesionales."},
            {"icono": "🛡️", "titulo": "Garantía Total", "desc": "Piezas, tintas y componentes homologados de calidad."},
            {"icono": "⏱️", "titulo": "Transparencia & Presupuesto", "desc": "Presupuesto claro sin sorpresas antes de empezar."}
        ]
    },
    "warm_artisan": {
        "template_file": "stitch_warm_artisan.html",
        "layout_type": "warm_artisan",
        "headline_font": "'Bricolage Grotesque', sans-serif",
        "body_font": "'Manrope', sans-serif",
        "google_fonts_url": "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Manrope:wght@400;500;600;700&display=swap",
        "color_seed": "#d97706",
        "primary": "#8d4b00",
        "primary_container": "#b15f00",
        "on_primary": "#ffffff",
        "accent": "#ffdcc3",
        # Modo Oscuro
        "bg_surface": "#140f0b",
        "card_surface": "rgba(38, 29, 23, 0.88)",
        "border_color": "rgba(245, 158, 11, 0.3)",
        "text_primary": "#fefce8",
        "text_secondary": "#d6d3d1",
        "header_bg": "rgba(20, 15, 11, 0.9)",
        "drawer_bg": "rgba(20, 15, 11, 0.98)",
        "badge_bg": "rgba(245, 158, 11, 0.18)",
        "badge_text": "#fde047",
        # Modo Claro
        "light_bg_surface": "#fff8f5",
        "light_card_surface": "#ffffff",
        "light_border_color": "rgba(217, 119, 6, 0.25)",
        "light_text_primary": "#1e1b19",
        "light_text_secondary": "#554336",
        "light_header_bg": "rgba(255, 248, 245, 0.94)",
        "light_drawer_bg": "#ffffff",
        "light_badge_bg": "rgba(217, 119, 6, 0.16)",
        "light_badge_text": "#8d4b00",
        "light_pill_bg": "rgba(217, 119, 6, 0.08)",
        "light_pill_border": "rgba(217, 119, 6, 0.25)",
        # Formas
        "roundness": "1rem",
        "roundness_button": "1rem",
        "default_theme": "light",
        "cta_gradient": "linear-gradient(135deg, #d97706 0%, #ac3400 100%)",
        "vibe_name": "Warm Artisan (Cafeterías de Especialidad, Panaderías & Gastro)",
        "status_badge": "🥐 ELABORADO A DIARIO • CAFÉ DE ESPECIALIDAD",
        "badges_confianza": [
            {"icono": "🌾", "titulo": "Ingredientes Naturales", "desc": "Selección de proximidad y recetas tradicionales."},
            {"icono": "☕", "titulo": "Especialidad & Pasión", "desc": "Extracción y horneado cuidado en cada detalle."},
            {"icono": "❤️", "titulo": "Espacio Acogedor", "desc": "El mejor ambiente para disfrutar sin prisas."}
        ]
    },
    "clinical_trust": {
        "template_file": "stitch_clinical_trust.html",
        "layout_type": "clinical_trust",
        "headline_font": "'Plus Jakarta Sans', sans-serif",
        "body_font": "'Inter', sans-serif",
        "google_fonts_url": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap",
        "color_seed": "#0ea5e9",
        "primary": "#006591",
        "primary_container": "#0ea5e9",
        "on_primary": "#ffffff",
        "accent": "#89ceff",
        # Modo Oscuro
        "bg_surface": "#06131c",
        "card_surface": "rgba(10, 30, 44, 0.85)",
        "border_color": "rgba(14, 165, 233, 0.3)",
        "text_primary": "#f0f9ff",
        "text_secondary": "#94a3b8",
        "header_bg": "rgba(6, 19, 28, 0.9)",
        "drawer_bg": "rgba(6, 19, 28, 0.98)",
        "badge_bg": "rgba(14, 165, 233, 0.18)",
        "badge_text": "#7dd3fc",
        # Modo Claro
        "light_bg_surface": "#f7f9ff",
        "light_card_surface": "#ffffff",
        "light_border_color": "rgba(14, 165, 233, 0.2)",
        "light_text_primary": "#001d32",
        "light_text_secondary": "#3e4850",
        "light_header_bg": "rgba(247, 249, 255, 0.94)",
        "light_drawer_bg": "#ffffff",
        "light_badge_bg": "rgba(14, 165, 233, 0.15)",
        "light_badge_text": "#006591",
        "light_pill_bg": "rgba(14, 165, 233, 0.08)",
        "light_pill_border": "rgba(14, 165, 233, 0.25)",
        # Formas
        "roundness": "1.25rem",
        "roundness_button": "0.75rem",
        "default_theme": "light",
        "cta_gradient": "linear-gradient(135deg, #0ea5e9 0%, #006591 100%)",
        "vibe_name": "Clinical & Trust (Clínicas Dentales, Fisioterapia & Salud)",
        "status_badge": "🩺 1ª CITA & DIAGNÓSTICO DIGITAL DISPONIBLE",
        "badges_confianza": [
            {"icono": "🔬", "titulo": "Tecnología Digital 3D", "desc": "Diagnóstico digital avanzado para máxima precisión."},
            {"icono": "💳", "titulo": "Financiación Flexible", "desc": "Facilidades de pago a tu medida sin intereses."},
            {"icono": "👨‍⚕️", "titulo": "Equipo Colegiado", "desc": "Trato cercano con los más altos estándares clínicos."}
        ]
    },
    "craft_build": {
        "template_file": "stitch_craft_build.html",
        "layout_type": "craft_build",
        "headline_font": "'Outfit', sans-serif",
        "body_font": "'Plus Jakarta Sans', sans-serif",
        "google_fonts_url": "https://fonts.googleapis.com/css2?family=Outfit:wght@600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "color_seed": "#d97706",
        "primary": "#8d4b00",
        "primary_container": "#b15f00",
        "on_primary": "#ffffff",
        "accent": "#ffdcc3",
        # Modo Oscuro
        "bg_surface": "#0b1c30",
        "card_surface": "rgba(15, 23, 42, 0.9)",
        "border_color": "rgba(217, 119, 6, 0.3)",
        "text_primary": "#f8f9ff",
        "text_secondary": "#cbd5e1",
        "header_bg": "rgba(11, 28, 48, 0.92)",
        "drawer_bg": "#0b1c30",
        "badge_bg": "rgba(217, 119, 6, 0.18)",
        "badge_text": "#fbbf24",
        # Modo Claro
        "light_bg_surface": "#f8f9ff",
        "light_card_surface": "#ffffff",
        "light_border_color": "rgba(226, 232, 240, 0.9)",
        "light_text_primary": "#0b1c30",
        "light_text_secondary": "#554336",
        "light_header_bg": "rgba(248, 249, 255, 0.94)",
        "light_drawer_bg": "#ffffff",
        "light_badge_bg": "rgba(217, 119, 6, 0.15)",
        "light_badge_text": "#8d4b00",
        "light_pill_bg": "rgba(217, 119, 6, 0.08)",
        "light_pill_border": "rgba(217, 119, 6, 0.25)",
        # Formas
        "roundness": "0.625rem", # 10px redondeo arquitectónico
        "roundness_button": "0.5rem",
        "default_theme": "light",
        "cta_gradient": "linear-gradient(135deg, #d97706 0%, #0f172a 100%)",
        "vibe_name": "Craft & Build (Reformas, Interiorismo, Carpintería & Hogar)",
        "status_badge": "🛡️ PRESUPUESTO CERRADO POR ESCRITO • GARANTÍA 2 AÑOS",
        "badges_confianza": [
            {"icono": "📐", "titulo": "Precio Cerrado", "desc": "Presupuesto por escrito sin desviaciones sorpresa."},
            {"icono": "🛡️", "titulo": "Garantía & Seguro RC", "desc": "Cobertura legal completa y garantía de 2 años."},
            {"icono": "⏱️", "titulo": "Plazos Cumplidos", "desc": "Planificación rigurosa y entregas en fecha pactada."}
        ]
    }
}

# Alias de compatibilidad hacia atrás
DESIGN_ARCHETYPES["editorial_luxury"] = DESIGN_ARCHETYPES["luxury_glow"]
DESIGN_ARCHETYPES["technical_dark"] = DESIGN_ARCHETYPES["urban_edge"]
DESIGN_ARCHETYPES["modern_lifestyle"] = DESIGN_ARCHETYPES["urban_edge"]
DESIGN_ARCHETYPES["fresh_clinical"] = DESIGN_ARCHETYPES["clinical_trust"]


def sintetizar_design_system(
    categoria: str, 
    nombre_negocio: str = "",
    sugerencia_gemini: Dict[str, Any] = None,
    arquetipo_forzado: str = None
) -> Dict[str, Any]:
    """
    Sintetiza un Design System individualizado en base a la categoría, tono del negocio
    y decisiones creativas del Agente Diseñador UX/UI de Gemini, o respetando la plantilla forzada.
    """
    cat = (categoria + " " + nombre_negocio).lower()
    
    # 1. Selección de Arquetipo Base (Prioridad máxima: elección manual del usuario)
    if arquetipo_forzado and arquetipo_forzado in DESIGN_ARCHETYPES:
        tokens = dict(DESIGN_ARCHETYPES[arquetipo_forzado])
    elif sugerencia_gemini and sugerencia_gemini.get("arquetipo_diseno") in DESIGN_ARCHETYPES:
        tokens = dict(DESIGN_ARCHETYPES[sugerencia_gemini["arquetipo_diseno"]])
    elif any(k in cat for k in ["reforma", "obra", "construc", "carpinter", "fontaner", "electric", "pladur", "climatiz", "pintor", "albanil", "cristal", "persiana", "mueble"]):
        tokens = dict(DESIGN_ARCHETYPES["craft_build"])
    elif any(k in cat for k in ["moto", "taller", "mecanic", "coche", "automov", "neumatico", "tattoo", "tatuaje", "piercing", "barber", "fitness", "gimnasio", "crossfit", "detailing"]):
        tokens = dict(DESIGN_ARCHETYPES["urban_edge"])
    elif any(k in cat for k in ["dental", "dentist", "clinic", "salud", "fisioterap", "osteopat", "podolog", "optica", "farmacia", "veterinar", "psicolog", "medico"]):
        tokens = dict(DESIGN_ARCHETYPES["clinical_trust"])
    elif any(k in cat for k in ["cafe", "panaderia", "pasteleria", "restaurante", "bar", "tapas", "gastro", "bistro", "brunch", "bakery", "pizzeria", "hamburgues"]):
        tokens = dict(DESIGN_ARCHETYPES["warm_artisan"])
    elif any(k in cat for k in ["uña", "estetica", "belleza", "nail", "lash", "pestaña", "spa", "joyer", "moda", "peluqueria"]):
        tokens = dict(DESIGN_ARCHETYPES["luxury_glow"])
    else:
        tokens = dict(DESIGN_ARCHETYPES["luxury_glow"])

    # 2. Aplicar decisión de tema (Light vs Dark) sugerida por el Agente de IA
    if sugerencia_gemini and sugerencia_gemini.get("tema_predeterminado") in ["light", "dark"]:
        tokens["default_theme"] = sugerencia_gemini["tema_predeterminado"]

    # 3. Aplicar badge de estado dinámico si Gemini lo generó
    if sugerencia_gemini and sugerencia_gemini.get("badge_status"):
        tokens["status_badge"] = sugerencia_gemini["badge_status"]

    return tokens
