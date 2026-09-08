"""
Módulo de diseño inspirado en la arquitectura de Design Systems de Google Stitch.
Sintetiza tokens visuales únicos (Color Semilla, Paleta Tonal, Emparejamiento Tipográfico
y Lenguaje de Formas) para que cada web tenga una identidad exclusiva según su nicho.
"""

from typing import Dict, Any

# Catálogo de Arquetipos de Diseño estilo Stitch
DESIGN_ARCHETYPES = {
    "editorial_luxury": {
        "layout_type": "editorial_luxury",
        "headline_font": "'Playfair Display', serif",
        "body_font": "'Plus Jakarta Sans', sans-serif",
        "google_fonts_url": "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;0,800;1,400;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "color_seed": "#e0a96d", # Oro suave / champán
        "primary": "#d49757",
        "primary_container": "rgba(212, 151, 87, 0.15)",
        "on_primary": "#ffffff",
        "accent": "#f3c68f",
        # Modo Oscuro
        "bg_surface": "#0c0a09", # Stone ultra dark
        "card_surface": "rgba(28, 25, 23, 0.85)",
        "border_color": "rgba(212, 151, 87, 0.28)",
        "text_primary": "#fafaf9",
        "text_secondary": "#a8a29e",
        "header_bg": "rgba(12, 10, 9, 0.88)",
        "drawer_bg": "rgba(12, 10, 9, 0.98)",
        "badge_bg": "rgba(212, 151, 87, 0.18)",
        "badge_text": "#f3c68f",
        # Modo Claro
        "light_bg_surface": "#faf7f2", # Crema / marfil cálido de lujo
        "light_card_surface": "rgba(255, 255, 255, 0.95)",
        "light_border_color": "rgba(212, 151, 87, 0.35)",
        "light_text_primary": "#1c1917",
        "light_text_secondary": "#57534e",
        "light_header_bg": "rgba(250, 247, 242, 0.92)",
        "light_drawer_bg": "rgba(255, 255, 255, 0.98)",
        "light_badge_bg": "rgba(212, 151, 87, 0.16)",
        "light_badge_text": "#9a5b1f",
        "light_pill_bg": "rgba(212, 151, 87, 0.08)",
        "light_pill_border": "rgba(212, 151, 87, 0.25)",
        # Formas y Estilo
        "roundness": "1.25rem",
        "roundness_button": "9999px",
        "default_theme": "light",
        "cta_gradient": "linear-gradient(135deg, #d49757 0%, #b8793b 100%)",
        "vibe_name": "Editorial Luxury (Refinado & Alta Gama)",
        "status_badge": "✨ ATENCIÓN EXCLUSIVA & CITA PREVIA",
        "badges_confianza": [
            {"icono": "✨", "titulo": "Cuidado de Autor", "desc": "Técnicas exclusivas y acabados de alta fidelidad."},
            {"icono": "💎", "titulo": "Marcas Líderes", "desc": "Productos premium y máxima durabilidad garantizada."},
            {"icono": "🌿", "titulo": "Espacio Exclusivo", "desc": "Atmósfera relajante y trato 100% personalizado."}
        ]
    },
    "technical_dark": {
        "layout_type": "technical_industrial",
        "headline_font": "'Space Grotesk', sans-serif",
        "body_font": "'DM Sans', sans-serif",
        "google_fonts_url": "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700;800&family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap",
        "color_seed": "#ef4444",
        "primary": "#f97316",
        "primary_container": "rgba(249, 115, 22, 0.18)",
        "on_primary": "#ffffff",
        "accent": "#fb923c",
        # Modo Oscuro (Brutalist Technical Industrial)
        "bg_surface": "#09090b",
        "card_surface": "rgba(20, 20, 24, 0.88)",
        "border_color": "rgba(249, 115, 22, 0.32)",
        "text_primary": "#f4f4f5",
        "text_secondary": "#a1a1aa",
        "header_bg": "rgba(9, 9, 11, 0.92)",
        "drawer_bg": "rgba(9, 9, 11, 0.98)",
        "badge_bg": "rgba(249, 115, 22, 0.18)",
        "badge_text": "#fdba74",
        # Modo Claro
        "light_bg_surface": "#f4f5f7",
        "light_card_surface": "rgba(255, 255, 255, 0.98)",
        "light_border_color": "rgba(249, 115, 22, 0.35)",
        "light_text_primary": "#0f172a",
        "light_text_secondary": "#475569",
        "light_header_bg": "rgba(244, 245, 247, 0.94)",
        "light_drawer_bg": "rgba(255, 255, 255, 0.98)",
        "light_badge_bg": "rgba(249, 115, 22, 0.16)",
        "light_badge_text": "#c2410c",
        "light_pill_bg": "rgba(249, 115, 22, 0.08)",
        "light_pill_border": "rgba(249, 115, 22, 0.25)",
        # Formas
        "roundness": "0.5rem", # Ángulos más rectos y técnicos
        "roundness_button": "0.5rem",
        "default_theme": "dark",
        "cta_gradient": "linear-gradient(135deg, #f97316 0%, #ea580c 100%)",
        "vibe_name": "Technical Industrial (Potencia, Precisión & Box de Taller)",
        "status_badge": "⚡ BOX DE TALLER OPERATIVO • RESPUESTA DIRECTA",
        "badges_confianza": [
            {"icono": "⚙️", "titulo": "Mecánica & Diagnosis", "desc": "Detección computerizada y puesta a punto precisa."},
            {"icono": "🛡️", "titulo": "Garantía y Recambios", "desc": "Componentes homologados con garantía oficial."},
            {"icono": "⏱️", "titulo": "Rapidez & Transparencia", "desc": "Presupuesto claro sin sorpresas antes de cada trabajo."}
        ]
    },
    "fresh_clinical": {
        "layout_type": "bento_medical",
        "headline_font": "'Plus Jakarta Sans', sans-serif",
        "body_font": "'Inter', sans-serif",
        "google_fonts_url": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap",
        "color_seed": "#06b6d4",
        "primary": "#0ea5e9",
        "primary_container": "rgba(14, 165, 233, 0.18)",
        "on_primary": "#ffffff",
        "accent": "#38bdf8",
        # Modo Oscuro (Bento Medical Dark)
        "bg_surface": "#06131c",
        "card_surface": "rgba(10, 30, 44, 0.85)",
        "border_color": "rgba(14, 165, 233, 0.3)",
        "text_primary": "#f0f9ff",
        "text_secondary": "#94a3b8",
        "header_bg": "rgba(6, 19, 28, 0.9)",
        "drawer_bg": "rgba(6, 19, 28, 0.98)",
        "badge_bg": "rgba(14, 165, 233, 0.18)",
        "badge_text": "#7dd3fc",
        # Modo Claro (Default para clínicas y salud)
        "light_bg_surface": "#f0f8ff",
        "light_card_surface": "rgba(255, 255, 255, 0.98)",
        "light_border_color": "rgba(14, 165, 233, 0.32)",
        "light_text_primary": "#082f49",
        "light_text_secondary": "#334155",
        "light_header_bg": "rgba(240, 248, 255, 0.94)",
        "light_drawer_bg": "rgba(255, 255, 255, 0.98)",
        "light_badge_bg": "rgba(14, 165, 233, 0.15)",
        "light_badge_text": "#0284c7",
        "light_pill_bg": "rgba(14, 165, 233, 0.08)",
        "light_pill_border": "rgba(14, 165, 233, 0.25)",
        # Formas
        "roundness": "1.25rem", # Bento organic corners
        "roundness_button": "9999px",
        "default_theme": "light",
        "cta_gradient": "linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)",
        "vibe_name": "Bento Medical (Tecnología Clínica, Confianza & Salud)",
        "status_badge": "🩺 1ª CITA & DIAGNÓSTICO DIGITAL DISPONIBLE",
        "badges_confianza": [
            {"icono": "🔬", "titulo": "Tecnología 3D", "desc": "Diagnóstico digital avanzado para máxima precisión."},
            {"icono": "💳", "titulo": "Financiación Flexible", "desc": "Facilidades de pago a tu medida sin intereses."},
            {"icono": "👨‍⚕️", "titulo": "Equipo Colegiado", "desc": "Trato cercano con los más altos estándares clínicos."}
        ]
    },
    "warm_artisan": {
        "layout_type": "warm_artisan",
        "headline_font": "'Bricolage Grotesque', sans-serif",
        "body_font": "'Manrope', sans-serif",
        "google_fonts_url": "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Manrope:wght@400;500;600;700&display=swap",
        "color_seed": "#d97706",
        "primary": "#f59e0b",
        "primary_container": "rgba(245, 158, 11, 0.18)",
        "on_primary": "#18181b",
        "accent": "#fcd34d",
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
        "light_bg_surface": "#fefcf6",
        "light_card_surface": "rgba(255, 255, 255, 0.98)",
        "light_border_color": "rgba(245, 158, 11, 0.35)",
        "light_text_primary": "#1c1917",
        "light_text_secondary": "#57534e",
        "light_header_bg": "rgba(254, 252, 246, 0.94)",
        "light_drawer_bg": "rgba(255, 255, 255, 0.98)",
        "light_badge_bg": "rgba(245, 158, 11, 0.16)",
        "light_badge_text": "#a16207",
        "light_pill_bg": "rgba(245, 158, 11, 0.08)",
        "light_pill_border": "rgba(245, 158, 11, 0.25)",
        # Formas
        "roundness": "1rem",
        "roundness_button": "1rem",
        "default_theme": "light",
        "cta_gradient": "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
        "vibe_name": "Warm Artisan (Cálido, Acogedor & Gastronómico)",
        "status_badge": "🥐 PRODUCTO ARTESANO ELABORADO A DIARIO",
        "badges_confianza": [
            {"icono": "🌾", "titulo": "Ingredientes Naturales", "desc": "Selección de proximidad y recetas tradicionales."},
            {"icono": "☕", "titulo": "Especialidad & Pasión", "desc": "Extracción y horneado cuidado en cada detalle."},
            {"icono": "❤️", "titulo": "Espacio Acogedor", "desc": "El mejor ambiente para disfrutar sin prisas."}
        ]
    },
    "modern_lifestyle": {
        "layout_type": "modern_lifestyle",
        "headline_font": "'Syne', sans-serif",
        "body_font": "'Plus Jakarta Sans', sans-serif",
        "google_fonts_url": "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Syne:wght@600;700;800&display=swap",
        "color_seed": "#8b5cf6",
        "primary": "#8b5cf6",
        "primary_container": "rgba(139, 92, 246, 0.18)",
        "on_primary": "#ffffff",
        "accent": "#a78bfa",
        # Modo Oscuro
        "bg_surface": "#090514",
        "card_surface": "rgba(26, 16, 48, 0.85)",
        "border_color": "rgba(139, 92, 246, 0.3)",
        "text_primary": "#f5f3ff",
        "text_secondary": "#c4b5fd",
        "header_bg": "rgba(9, 5, 20, 0.9)",
        "drawer_bg": "rgba(9, 5, 20, 0.98)",
        "badge_bg": "rgba(139, 92, 246, 0.18)",
        "badge_text": "#c4b5fd",
        # Modo Claro
        "light_bg_surface": "#faf5ff",
        "light_card_surface": "rgba(255, 255, 255, 0.98)",
        "light_border_color": "rgba(139, 92, 246, 0.32)",
        "light_text_primary": "#1e1b4b",
        "light_text_secondary": "#475569",
        "light_header_bg": "rgba(250, 245, 255, 0.94)",
        "light_drawer_bg": "rgba(255, 255, 255, 0.98)",
        "light_badge_bg": "rgba(139, 92, 246, 0.15)",
        "light_badge_text": "#7c3aed",
        "light_pill_bg": "rgba(139, 92, 246, 0.08)",
        "light_pill_border": "rgba(139, 92, 246, 0.25)",
        # Formas
        "roundness": "1rem",
        "roundness_button": "9999px",
        "default_theme": "dark",
        "cta_gradient": "linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)",
        "vibe_name": "Modern Lifestyle (Urbano, Creativo & Fitness)",
        "status_badge": "🔥 NUEVA TEMPORADA & SESIONES ABIERTAS",
        "badges_confianza": [
            {"icono": "🎯", "titulo": "Metodología Top", "desc": "Resultados visibles con acompañamiento continuo."},
            {"icono": "⚡", "titulo": "Energía & Comunidad", "desc": "Ambiente motivador diseñado para superarte."},
            {"icono": "📱", "titulo": "Reserva Flexible", "desc": "Gestiona tus citas o sesiones en segundos."}
        ]
    }
}

def sintetizar_design_system(
    categoria: str, 
    nombre_negocio: str = "",
    sugerencia_gemini: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Sintetiza un Design System individualizado en base a la categoría, tono del negocio
    y decisiones creativas del Agente Diseñador UX/UI de Gemini.
    """
    cat = (categoria + " " + nombre_negocio).lower()
    
    # 1. Selección de Arquetipo Base
    if sugerencia_gemini and sugerencia_gemini.get("arquetipo_diseno") in DESIGN_ARCHETYPES:
        tokens = dict(DESIGN_ARCHETYPES[sugerencia_gemini["arquetipo_diseno"]])
    elif any(k in cat for k in ["moto", "taller", "mecanic", "coche", "automov", "neumatico"]):
        tokens = dict(DESIGN_ARCHETYPES["technical_dark"])
    elif any(k in cat for k in ["uña", "estetica", "belleza", "nail", "lash", "spa", "joyer", "moda"]):
        tokens = dict(DESIGN_ARCHETYPES["editorial_luxury"])
    elif any(k in cat for k in ["cafe", "panaderia", "pasteleria", "restaurante", "bar", "tapas", "gastro"]):
        tokens = dict(DESIGN_ARCHETYPES["warm_artisan"])
    elif any(k in cat for k in ["dental", "dentist", "clinic", "salud", "fisioterap", "optica", "farmacia", "veterinar"]):
        tokens = dict(DESIGN_ARCHETYPES["fresh_clinical"])
    elif any(k in cat for k in ["peluqueria", "barber", "gimnasio", "fitness", "crossfit", "tatuaje", "tattoo"]):
        tokens = dict(DESIGN_ARCHETYPES["modern_lifestyle"])
    else:
        tokens = dict(DESIGN_ARCHETYPES["editorial_luxury"])

    # 2. Aplicar decisión de tema (Light vs Dark) sugerida por el Agente de IA
    if sugerencia_gemini and sugerencia_gemini.get("tema_predeterminado") in ["light", "dark"]:
        tokens["default_theme"] = sugerencia_gemini["tema_predeterminado"]

    # 3. Aplicar badge de estado dinámico si Gemini lo generó
    if sugerencia_gemini and sugerencia_gemini.get("badge_status"):
        tokens["status_badge"] = sugerencia_gemini["badge_status"]

    return tokens
