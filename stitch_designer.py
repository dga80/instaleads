"""
Módulo de diseño inspirado en la arquitectura de Design Systems de Google Stitch.
Sintetiza tokens visuales únicos (Color Semilla, Paleta Tonal, Emparejamiento Tipográfico
y Lenguaje de Formas) para que cada web tenga una identidad exclusiva según su nicho.
"""

from typing import Dict, Any

# Catálogo de Arquetipos de Diseño estilo Stitch
DESIGN_ARCHETYPES = {
    "editorial_luxury": {
        "headline_font": "'Playfair Display', serif",
        "body_font": "'Plus Jakarta Sans', sans-serif",
        "google_fonts_url": "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
        "color_seed": "#e0a96d", # Oro suave / champán
        "primary": "#d49757",
        "primary_container": "rgba(212, 151, 87, 0.15)",
        "on_primary": "#ffffff",
        "accent": "#f3c68f",
        # Modo Oscuro
        "bg_surface": "#0c0a09", # Stone ultra dark
        "card_surface": "rgba(28, 25, 23, 0.78)",
        "border_color": "rgba(212, 151, 87, 0.22)",
        "text_primary": "#fafaf9",
        "text_secondary": "#a8a29e",
        "header_bg": "rgba(12, 10, 9, 0.88)",
        "drawer_bg": "rgba(12, 10, 9, 0.98)",
        "badge_bg": "rgba(212, 151, 87, 0.15)",
        "badge_text": "#f3c68f",
        # Modo Claro
        "light_bg_surface": "#faf7f2", # Crema / marfil cálido de lujo
        "light_card_surface": "rgba(255, 255, 255, 0.94)",
        "light_border_color": "rgba(212, 151, 87, 0.32)",
        "light_text_primary": "#1c1917",
        "light_text_secondary": "#57534e",
        "light_header_bg": "rgba(250, 247, 242, 0.92)",
        "light_drawer_bg": "rgba(255, 255, 255, 0.98)",
        "light_badge_bg": "rgba(212, 151, 87, 0.16)",
        "light_badge_text": "#9a5b1f",
        "light_pill_bg": "rgba(212, 151, 87, 0.08)",
        "light_pill_border": "rgba(212, 151, 87, 0.25)",
        # Formas
        "roundness": "1.25rem", # ROUND_TWELVE
        "roundness_button": "9999px", # ROUND_FULL
        "cta_gradient": "linear-gradient(135deg, #d49757 0%, #b8793b 100%)",
        "vibe_name": "Editorial Luxury (Refinado & Alta Gama)"
    },
    "technical_dark": {
        "headline_font": "'Space Grotesk', sans-serif",
        "body_font": "'DM Sans', sans-serif",
        "google_fonts_url": "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=DM+Sans:wght@400;500;600;700&display=swap",
        "color_seed": "#ef4444", # Rojo racing / naranja mecánico
        "primary": "#f97316",
        "primary_container": "rgba(249, 115, 22, 0.15)",
        "on_primary": "#ffffff",
        "accent": "#fb923c",
        # Modo Oscuro
        "bg_surface": "#09090b", # Zinc 950
        "card_surface": "rgba(24, 24, 27, 0.82)",
        "border_color": "rgba(249, 115, 22, 0.25)",
        "text_primary": "#f4f4f5",
        "text_secondary": "#a1a1aa",
        "header_bg": "rgba(9, 9, 11, 0.88)",
        "drawer_bg": "rgba(9, 9, 11, 0.98)",
        "badge_bg": "rgba(249, 115, 22, 0.15)",
        "badge_text": "#fdba74",
        # Modo Claro
        "light_bg_surface": "#f8fafc", # Slate ultra limpio
        "light_card_surface": "rgba(255, 255, 255, 0.96)",
        "light_border_color": "rgba(249, 115, 22, 0.28)",
        "light_text_primary": "#0f172a",
        "light_text_secondary": "#475569",
        "light_header_bg": "rgba(248, 250, 252, 0.92)",
        "light_drawer_bg": "rgba(255, 255, 255, 0.98)",
        "light_badge_bg": "rgba(249, 115, 22, 0.14)",
        "light_badge_text": "#c2410c",
        "light_pill_bg": "rgba(249, 115, 22, 0.08)",
        "light_pill_border": "rgba(249, 115, 22, 0.22)",
        # Formas
        "roundness": "0.625rem", # ROUND_EIGHT
        "roundness_button": "0.75rem",
        "cta_gradient": "linear-gradient(135deg, #f97316 0%, #ea580c 100%)",
        "vibe_name": "Technical Bold (Potencia, Precisión & Mecánica)"
    },
    "warm_artisan": {
        "headline_font": "'Bricolage Grotesque', sans-serif",
        "body_font": "'Manrope', sans-serif",
        "google_fonts_url": "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&family=Manrope:wght@400;500;600;700&display=swap",
        "color_seed": "#d97706", # Ámbar café y madera tostada
        "primary": "#eab308",
        "primary_container": "rgba(234, 179, 8, 0.15)",
        "on_primary": "#18181b",
        "accent": "#fde047",
        # Modo Oscuro
        "bg_surface": "#140f0b", # Warm dark espresso
        "card_surface": "rgba(38, 29, 23, 0.82)",
        "border_color": "rgba(234, 179, 8, 0.25)",
        "text_primary": "#fefce8",
        "text_secondary": "#d6d3d1",
        "header_bg": "rgba(20, 15, 11, 0.88)",
        "drawer_bg": "rgba(20, 15, 11, 0.98)",
        "badge_bg": "rgba(234, 179, 8, 0.15)",
        "badge_text": "#fde047",
        # Modo Claro
        "light_bg_surface": "#fefce8", # Lino artesanal cálido
        "light_card_surface": "rgba(255, 255, 255, 0.95)",
        "light_border_color": "rgba(234, 179, 8, 0.32)",
        "light_text_primary": "#1c1917",
        "light_text_secondary": "#57534e",
        "light_header_bg": "rgba(254, 252, 232, 0.92)",
        "light_drawer_bg": "rgba(255, 255, 255, 0.98)",
        "light_badge_bg": "rgba(234, 179, 8, 0.16)",
        "light_badge_text": "#a16207",
        "light_pill_bg": "rgba(234, 179, 8, 0.08)",
        "light_pill_border": "rgba(234, 179, 8, 0.25)",
        # Formas
        "roundness": "1rem", # ROUND_TWELVE
        "roundness_button": "1rem",
        "cta_gradient": "linear-gradient(135deg, #eab308 0%, #ca8a04 100%)",
        "vibe_name": "Warm Artisan (Cálido, Acogedor & Gastronómico)"
    },
    "fresh_clinical": {
        "headline_font": "'Plus Jakarta Sans', sans-serif",
        "body_font": "'Inter', sans-serif",
        "google_fonts_url": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap",
        "color_seed": "#06b6d4", # Cyan / Aqua médico
        "primary": "#0ea5e9",
        "primary_container": "rgba(14, 165, 233, 0.15)",
        "on_primary": "#ffffff",
        "accent": "#38bdf8",
        # Modo Oscuro
        "bg_surface": "#081b26", # Slate profundo médico
        "card_surface": "rgba(12, 36, 50, 0.82)",
        "border_color": "rgba(14, 165, 233, 0.25)",
        "text_primary": "#f0f9ff",
        "text_secondary": "#94a3b8",
        "header_bg": "rgba(8, 27, 38, 0.88)",
        "drawer_bg": "rgba(8, 27, 38, 0.98)",
        "badge_bg": "rgba(14, 165, 233, 0.15)",
        "badge_text": "#7dd3fc",
        # Modo Claro
        "light_bg_surface": "#f0f9ff", # Azul cielo clínico ultra higiénico
        "light_card_surface": "rgba(255, 255, 255, 0.96)",
        "light_border_color": "rgba(14, 165, 233, 0.28)",
        "light_text_primary": "#082f49",
        "light_text_secondary": "#334155",
        "light_header_bg": "rgba(240, 249, 255, 0.92)",
        "light_drawer_bg": "rgba(255, 255, 255, 0.98)",
        "light_badge_bg": "rgba(14, 165, 233, 0.14)",
        "light_badge_text": "#0284c7",
        "light_pill_bg": "rgba(14, 165, 233, 0.08)",
        "light_pill_border": "rgba(14, 165, 233, 0.24)",
        # Formas
        "roundness": "0.875rem",
        "roundness_button": "9999px",
        "cta_gradient": "linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%)",
        "vibe_name": "Fresh Clinical (Limpio, Confiable & Salud)"
    },
    "modern_lifestyle": {
        "headline_font": "'Syne', sans-serif",
        "body_font": "'Plus Jakarta Sans', sans-serif",
        "google_fonts_url": "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Syne:wght@600;700;800&display=swap",
        "color_seed": "#8b5cf6", # Púrpura eléctrico / Indigo
        "primary": "#8b5cf6",
        "primary_container": "rgba(139, 92, 246, 0.15)",
        "on_primary": "#ffffff",
        "accent": "#a78bfa",
        # Modo Oscuro
        "bg_surface": "#090514", # Deep violet
        "card_surface": "rgba(26, 16, 48, 0.8)",
        "border_color": "rgba(139, 92, 246, 0.25)",
        "text_primary": "#f5f3ff",
        "text_secondary": "#c4b5fd",
        "header_bg": "rgba(9, 5, 20, 0.88)",
        "drawer_bg": "rgba(9, 5, 20, 0.98)",
        "badge_bg": "rgba(139, 92, 246, 0.15)",
        "badge_text": "#c4b5fd",
        # Modo Claro
        "light_bg_surface": "#faf5ff", # Lila suave / blanco estudio
        "light_card_surface": "rgba(255, 255, 255, 0.96)",
        "light_border_color": "rgba(139, 92, 246, 0.28)",
        "light_text_primary": "#1e1b4b",
        "light_text_secondary": "#475569",
        "light_header_bg": "rgba(250, 245, 255, 0.92)",
        "light_drawer_bg": "rgba(255, 255, 255, 0.98)",
        "light_badge_bg": "rgba(139, 92, 246, 0.14)",
        "light_badge_text": "#7c3aed",
        "light_pill_bg": "rgba(139, 92, 246, 0.08)",
        "light_pill_border": "rgba(139, 92, 246, 0.24)",
        # Formas
        "roundness": "1rem",
        "roundness_button": "9999px",
        "cta_gradient": "linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)",
        "vibe_name": "Modern Lifestyle (Urbano, Creativo & Fitness)"
    }
}

def sintetizar_design_system(categoria: str, nombre_negocio: str = "") -> Dict[str, Any]:
    """
    Sintetiza un Design System individualizado en base a la categoría y tono del negocio.
    """
    cat = (categoria + " " + nombre_negocio).lower()

    if any(k in cat for k in ["moto", "taller", "mecanic", "coche", "automov", "neumatico"]):
        return DESIGN_ARCHETYPES["technical_dark"]
    elif any(k in cat for k in ["uña", "estetica", "belleza", "nail", "lash", "spa", "joyer", "moda"]):
        return DESIGN_ARCHETYPES["editorial_luxury"]
    elif any(k in cat for k in ["cafe", "panaderia", "pasteleria", "restaurante", "bar", "tapas", "gastro"]):
        return DESIGN_ARCHETYPES["warm_artisan"]
    elif any(k in cat for k in ["dental", "dentist", "clinic", "salud", "fisioterap", "optica", "farmacia", "veterinar"]):
        return DESIGN_ARCHETYPES["fresh_clinical"]
    elif any(k in cat for k in ["peluqueria", "barber", "gimnasio", "fitness", "crossfit", "tatuaje", "tattoo"]):
        return DESIGN_ARCHETYPES["modern_lifestyle"]
    else:
        # Alternativa refinada por defecto
        return DESIGN_ARCHETYPES["editorial_luxury"]
