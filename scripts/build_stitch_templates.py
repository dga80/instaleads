"""
Compilador y parametrizador Jinja2 para las 5 plantillas oficiales de Google Stitch.
Convierte los HTMLs descargados en plantillas de producción con inyección dinámica,
soporte para notch/Dynamic Island de iPhone (safe-area), menús de escritorio funcionales
y menús hamburguesa móviles interactivos con deslizamiento lateral suave.
"""

import os
import re

STITCH_DIR = "templates/stitch"
OUT_DIR = "templates"


def make_mobile_drawer_and_script(
    template_id: str,
    nav_items: list,  # list of tuples: (label, target_id, icon_name)
    drawer_bg_class: str,
    drawer_border_class: str,
    link_class: str,
    cta_primary_class: str,
    cta_secondary_class: str,
    icon_color_class: str,
    default_avatar: str = "https://images.unsplash.com/photo-1560750588-73207b1ef5b8?w=96&q=80"
) -> str:
    links_html = ""
    for label, target_id, icon in nav_items:
        links_html += f"""
        <a href="#{target_id}" onclick="closeMobileMenu()" class="flex items-center gap-3.5 px-3.5 py-3 rounded-xl {link_class} transition-colors group">
          <span class="material-symbols-outlined {icon_color_class} text-[20px] transition-transform group-hover:scale-110">{icon}</span>
          <span class="font-medium text-sm">{label}</span>
        </a>"""

    drawer_html = f"""
<!-- ============================================================ -->
<!-- MOBILE NAVIGATION DRAWER (ACCESIBLE & IPHONE SAFE-AREA AWARE) -->
<!-- ============================================================ -->
<div id="mobile-drawer" class="fixed inset-0 z-[100] pointer-events-none transition-opacity duration-300" aria-hidden="true">
  <!-- Backdrop desenfocado -->
  <div id="mobile-drawer-backdrop" onclick="closeMobileMenu()" class="absolute inset-0 bg-black/65 backdrop-blur-sm opacity-0 transition-opacity duration-300 pointer-events-none"></div>

  <!-- Panel lateral deslizante con padding seguro para Dynamic Island -->
  <div id="mobile-drawer-panel" class="absolute top-0 right-0 bottom-0 w-[310px] sm:w-[350px] max-w-[86vw] {drawer_bg_class} border-l {drawer_border_class} shadow-2xl flex flex-col justify-between overflow-y-auto translate-x-full transition-transform duration-300 ease-out pointer-events-auto"
       style="padding-top: max(1.25rem, calc(0.75rem + var(--sat, env(safe-area-inset-top, 0px)))); padding-bottom: max(1.25rem, calc(0.75rem + var(--sab, env(safe-area-inset-bottom, 0px)))); padding-left: 1.25rem; padding-right: 1.25rem;">
    
    <div class="space-y-6">
      <!-- Cabecera del Drawer -->
      <div class="flex items-center justify-between pb-4 border-b border-outline-variant/30">
        <div class="flex items-center gap-3 truncate">
          <img src="{{{{ ig.avatar_url or '{default_avatar}' }}}}" alt="{{{{ negocio.nombre }}}}" class="w-10 h-10 rounded-full object-cover border border-primary/30 shrink-0"/>
          <div class="flex flex-col truncate">
            <span class="font-bold text-sm text-on-surface truncate">{{{{ negocio.nombre }}}}</span>
            <span class="text-[11px] text-on-surface-variant truncate">{{{{ negocio.categoria_clean or negocio.ciudad }}}}</span>
          </div>
        </div>
        <button onclick="closeMobileMenu()" class="p-2 rounded-full hover:bg-surface-container-high transition text-on-surface flex items-center justify-center shrink-0" aria-label="Cerrar menú">
          <span class="material-symbols-outlined text-[20px]">close</span>
        </button>
      </div>

      <!-- Enlaces de navegación -->
      <nav class="flex flex-col space-y-1">
        {links_html}
      </nav>
    </div>

    <!-- Botones de Acción / Contacto al pie del Drawer -->
    <div class="space-y-3 pt-5 border-t border-outline-variant/30">
      {{% if negocio.whatsapp_url %}}
      <a href="{{{{ negocio.whatsapp_url }}}}" target="_blank" rel="noopener" class="flex items-center justify-center gap-2 w-full py-3 px-4 rounded-xl {cta_primary_class} font-bold text-xs uppercase tracking-wider shadow-md transition-all">
        <svg class="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981z"/></svg>
        <span>Escribir por WhatsApp</span>
      </a>
      {{% endif %}}

      {{% if negocio.telefono %}}
      <a href="tel:{{{{ negocio.telefono }}}}" class="flex items-center justify-center gap-2 w-full py-2.5 px-4 rounded-xl {cta_secondary_class} font-semibold text-xs transition-all">
        <span class="material-symbols-outlined text-[16px]">call</span>
        <span>Llamar {{{{ negocio.telefono }}}}</span>
      </a>
      {{% endif %}}

      <div class="text-[11px] text-center text-on-surface-variant flex items-center justify-center gap-1 pt-1">
        <span class="material-symbols-outlined text-[14px]">location_on</span>
        <span class="truncate">{{{{ negocio.direccion or negocio.ciudad }}}}</span>
      </div>
    </div>

  </div>
</div>

<script>
  function toggleMobileMenu() {{
    const panel = document.getElementById('mobile-drawer-panel');
    if (!panel) return;
    if (panel.classList.contains('translate-x-full')) {{
      openMobileMenu();
    }} else {{
      closeMobileMenu();
    }}
  }}

  function openMobileMenu() {{
    const drawer = document.getElementById('mobile-drawer');
    const backdrop = document.getElementById('mobile-drawer-backdrop');
    const panel = document.getElementById('mobile-drawer-panel');
    const btn = document.getElementById('hamburger-btn');

    if (!drawer || !backdrop || !panel) return;
    drawer.classList.remove('pointer-events-none');
    drawer.setAttribute('aria-hidden', 'false');
    backdrop.classList.remove('opacity-0', 'pointer-events-none');
    backdrop.classList.add('opacity-100');
    panel.classList.remove('translate-x-full');
    if (btn) btn.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }}

  function closeMobileMenu() {{
    const drawer = document.getElementById('mobile-drawer');
    const backdrop = document.getElementById('mobile-drawer-backdrop');
    const panel = document.getElementById('mobile-drawer-panel');
    const btn = document.getElementById('hamburger-btn');

    if (!drawer || !backdrop || !panel) return;
    backdrop.classList.remove('opacity-100');
    backdrop.classList.add('opacity-0', 'pointer-events-none');
    panel.classList.add('translate-x-full');
    drawer.classList.add('pointer-events-none');
    drawer.setAttribute('aria-hidden', 'true');
    if (btn) btn.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }}

  document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape') closeMobileMenu();
  }});
</script>
"""
    return drawer_html


def get_safe_area_script_and_css(scroll_padding_rem: float) -> str:
    return f"""<style>
  :root {{
    --sat: env(safe-area-inset-top, 0px);
    --sab: env(safe-area-inset-bottom, 0px);
  }}
  html {{
    scroll-behavior: smooth;
    scroll-padding-top: calc({scroll_padding_rem}rem + var(--sat, 0px));
  }}
</style>
<script>
  (function() {{
    try {{
      var isIframe = window.self !== window.top;
      var isSim = isIframe || /[?&]sim(=|&|$)/.test(window.location.search) || window.location.hash.indexOf('sim') !== -1;
      if (isSim) {{
        document.documentElement.style.setProperty('--sat', '54px');
        document.documentElement.style.setProperty('--sab', '20px');
      }}
    }} catch(e) {{}}
  }})();
</script>"""


def build_luxury_glow():
    raw_path = os.path.join(STITCH_DIR, "luxury_glow_desktop_raw.html")
    with open(raw_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Viewport fit cover (Dynamic Island iPhone)
    html = re.sub(
        r'<meta content="width=device-width, initial-scale=1.0" name="viewport"/>',
        r'<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover"/>',
        html
    )

    # 2. Smooth scrolling & safe-area CSS
    safe_css = get_safe_area_script_and_css(6.5)
    html = html.replace("</head>", safe_css + "\n</head>")

    # 3. Title & Meta
    html = re.sub(
        r"<title>.*?</title>",
        r"""<title>{{ negocio.nombre }} | Belleza & Cuidado Exclusivo en {{ negocio.ciudad }}</title>
  <meta name="description" content="{{ web.subtitulo or ('Sitio web oficial y reservas para ' ~ negocio.nombre ~ ' en ' ~ negocio.ciudad) }}">""",
        html,
        flags=re.DOTALL
    )

    # 4. Favicon
    html = re.sub(
        r'<link href="https://fonts.googleapis.com"',
        r"""<link rel="icon" type="image/jpeg" href="{{ ig.avatar_url or 'https://images.unsplash.com/photo-1560750588-73207b1ef5b8?w=96&q=80' }}">
<link href="https://fonts.googleapis.com\"""",
        html,
        count=1
    )

    # 5. Header Dynamic Island safe area & Logo & Brand
    html = re.sub(
        r'<header class="fixed top-0 inset-x-0 z-50 px-margin sm:px-margin-tablet lg:px-margin-desktop py-space-sm">',
        r'<header class="fixed top-0 inset-x-0 z-50 px-margin sm:px-margin-tablet lg:px-margin-desktop py-space-sm" style="padding-top: max(0.5rem, var(--sat, env(safe-area-inset-top, 0px)));">',
        html
    )

    html = re.sub(
        r'<img alt="Élixir Studio &amp; Aesthetics Logo"[^>]+>',
        r"""<img alt="{{ negocio.nombre }}" class="h-9 w-9 rounded-full object-cover border border-primary-container/40" src="{{ ig.avatar_url or 'https://images.unsplash.com/photo-1560750588-73207b1ef5b8?w=120&q=80' }}"/>""",
        html
    )
    html = re.sub(
        r'<span class="font-headline-sm text-headline-sm tracking-tight text-on-surface ml-1 hidden sm:inline-block">Élixir Studio</span>',
        r"""<span class="font-headline-sm text-headline-sm tracking-tight text-on-surface ml-1 hidden sm:inline-block">{{ negocio.nombre }}</span>""",
        html
    )
    html = re.sub(
        r'<span>@elixir\.madrid</span>',
        r"""<span>@{{ ig.username or (negocio.nombre|lower|replace(' ', '')) }}</span>""",
        html
    )
    html = re.sub(
        r'href="https://wa\.me/34600123456\?[^"]*"',
        r"""href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" target="_blank" rel="noopener\"""",
        html
    )

    # 6. Functional Desktop Navigation
    new_desktop_nav = """<nav class="hidden lg:flex items-center gap-space-xs" data-active-classes="bg-surface-container text-primary font-medium">
      <a class="px-space-md py-space-xs rounded-full font-label-md text-label-md text-on-surface-variant hover:text-primary transition-colors" href="#servicios">Servicios</a>
      <a class="px-space-md py-space-xs rounded-full font-label-md text-label-md text-on-surface-variant hover:text-primary transition-colors" href="#filosofia">Filosofía</a>
      <a class="px-space-md py-space-xs rounded-full font-label-md text-label-md text-on-surface-variant hover:text-primary transition-colors" href="#galeria">Resultados</a>
      <a class="px-space-md py-space-xs rounded-full font-label-md text-label-md text-on-surface-variant hover:text-primary transition-colors" href="#contacto">Contacto</a>
    </nav>"""
    html = re.sub(r'<nav class="hidden lg:flex items-center gap-space-xs".*?</nav>', new_desktop_nav, html, flags=re.DOTALL)

    # 7. Add Hamburger Button to Header (on the RIGHT)
    burger_btn = """<!-- Mobile Hamburger Button (On the RIGHT) -->
      <button id="hamburger-btn" onclick="toggleMobileMenu()" class="lg:hidden p-2 rounded-full hover:bg-surface-container text-on-surface transition flex items-center justify-center border border-primary-container/30 ml-1" aria-label="Abrir Menú" aria-expanded="false">
        <span class="material-symbols-outlined text-[24px]">menu</span>
      </button>"""
    html = re.sub(
        r'<div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center shadow-sm ml-1">\s*<span class="material-symbols-outlined text-on-primary text-\[18px\]">person</span>\s*</div>',
        r"""<div class="hidden sm:flex w-8 h-8 rounded-full bg-primary items-center justify-center shadow-sm ml-1"><span class="material-symbols-outlined text-on-primary text-[18px]">person</span></div>\n      """ + burger_btn,
        html
    )

    # 8. Main Safe-Area Padding
    html = re.sub(
        r'<main class="w-full pt-20 bg-surface">',
        r'<main class="w-full bg-surface" style="padding-top: calc(7.5rem + var(--sat, env(safe-area-inset-top, 0px)));">',
        html
    )

    # 9. Hero Badge & Copy
    html = re.sub(
        r'✨ Atención Exclusiva • Cita Previa',
        r"""{{ web.badge_status or '✨ Atención Exclusiva • Cita Previa' }}""",
        html
    )
    html = re.sub(
        r'<h1 class="font-display-hero text-display-hero sm:text-\[60px\] sm:leading-\[68px\] text-on-surface tracking-tight">\s*Realza tu <span class="italic font-display-hero text-primary select-none drop-shadow-sm font-normal">belleza natural</span> con técnicas de autor en Madrid\s*</h1>',
        r"""<h1 class="font-display-hero text-display-hero sm:text-[60px] sm:leading-[68px] text-on-surface tracking-tight">
            {{ web.titular or ('Realza tu <span class="italic font-display-hero text-primary select-none drop-shadow-sm font-normal">belleza natural</span> en ' ~ negocio.ciudad)|safe }}
          </h1>""",
        html
    )
    html = re.sub(
        r'<p class="font-body-lg text-body-lg text-on-surface-variant max-w-xl leading-relaxed">\s*Atención individualizada en cabina privada, aparatología de última generación y formulaciones botánicas bioactivas certificadas\. Sin prisas, con rigor experto en el Barrio de Salamanca\.\s*</p>',
        r"""<p class="font-body-lg text-body-lg text-on-surface-variant max-w-xl leading-relaxed">
            {{ web.subtitulo or ('Atención individualizada en cabina privada, cosmecéutica de autor y las técnicas más avanzadas de belleza en ' ~ negocio.ciudad ~ '.') }}
          </p>""",
        html
    )
    html = re.sub(
        r'<span class="font-label-caps text-label-caps uppercase text-on-surface tracking-wider">Serrano 48, Salamanca</span>',
        r"""<span class="font-label-caps text-label-caps uppercase text-on-surface tracking-wider">{{ negocio.direccion or negocio.ciudad }}</span>""",
        html
    )

    # Hero Images
    html = re.sub(
        r'<img class="w-full h-full object-cover" data-alt="[^"]*" src="https://lh3\.googleusercontent\.com/aida-public/AB6AXuCs-nh5VvzqIasB2CWKP9H6iZpUtFSeYkorHL7CQ43MP7CukR1o4tWwTNwqCbZDWI1jc_I0LJqoOZM8q4WmYwcpxGLN5LUPXZLp54RL50bDSE4EfwrtaAcbQqbovjxiZEa8nZGNVmXfKbzdhgCEZXjLWBLowW_RnK5b9ddQfqtn08ox3ZmP0ULY71zSvpVwtwFS-ZYBmHZq2sULjc_gGvpb1Dh4JoJuao3BwSZJ-ru50SvgaxzJryC7YQ"/>',
        r"""<img class="w-full h-full object-cover" alt="{{ negocio.nombre }}" src="{{ ig.posts[0].image_url if ig.posts and ig.posts[0].image_url else 'https://images.unsplash.com/photo-1560750588-73207b1ef5b8?auto=format&fit=crop&w=1200&q=80' }}"/>""",
        html
    )
    html = re.sub(
        r'<img alt="Detalle de piel radiante y tratamiento facial de alta cosmética en Élixir Studio" class="w-full h-full object-cover" src="https://lh3\.googleusercontent\.com/aida-public/AB6AXuC6FgXhlX5LZqPgohplJutgZ_xf-mLLI-E4aqlgheCgmhuxGOphM3EoHO3yhA82qNxg8O6sU4ZIljwQNmuQkv3rQWhzVdMPC1B728Q8gLkLHrgYVNZcOI-BhU71_LnARtqNUnryFFVy0aI6jxg1FQ7DizTMP8VQ-tVIIcQ3sSJThCOFselvmRxJmQMJxmZtSQShShlIhqnXBeDM4fO5pxth8WERyjaVCvwpobSXexJ62pnftOM3WiY4bA"/>',
        r"""<img alt="{{ negocio.nombre }} glow" class="w-full h-full object-cover" src="{{ ig.posts[1].image_url if ig.posts and ig.posts|length > 1 and ig.posts[1].image_url else 'https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=600&q=80' }}"/>""",
        html
    )

    # 10. Services Section & ID
    html = re.sub(
        r'Carta de Terapias <span class="italic font-display-hero text-primary font-normal">• Élixir Studio</span>',
        r"""Carta de Servicios <span class="italic font-display-hero text-primary font-normal">• {{ negocio.nombre }}</span>""",
        html
    )
    html = re.sub(
        r'<section class="w-full py-space-xl" id="servicios-tarifas">',
        r'<div id="servicios-tarifas" class="scroll-mt-28"></div>\n<section id="servicios" class="w-full py-space-xl scroll-mt-28">',
        html
    )
    html = html.replace('href="#servicios-tarifas"', 'href="#servicios"')

    # Replace Bento Grid with dynamic Jinja2 loop
    bento_replacement = """<!-- Dynamic Bento Grid from Instagram & Gemini -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-gutter">
  {% for s in web.servicios %}
  <div class="{% if loop.first %}lg:col-span-7{% elif loop.index == 2 %}lg:col-span-5{% elif loop.index == 3 %}lg:col-span-5{% else %}lg:col-span-7{% endif %} flex flex-col justify-between p-space-lg sm:p-space-xl rounded-[24px] bg-surface-container-lowest border border-primary-container/30 shadow-[0_12px_36px_-10px_rgba(212,151,87,0.18)] relative overflow-hidden group">
    <div>
      <div class="flex items-center justify-between gap-2 mb-space-sm">
        <span class="px-3 py-1 rounded-full bg-primary-container/20 text-primary font-label-caps text-label-caps uppercase tracking-wider font-semibold border border-primary-container/30">
          {% if loop.first %}⭐ Tratamiento Estrella{% else %}Cuidado Premium{% endif %}
        </span>
        <div class="flex items-center gap-1 text-primary">
          <span class="material-symbols-outlined text-[16px]">schedule</span>
          <span class="font-label-caps text-label-caps uppercase tracking-wider">{{ s.precio_o_duracion or "Cita Previa" }}</span>
        </div>
      </div>
      <h3 class="font-headline-sm text-headline-sm text-on-surface font-semibold mb-space-xs">
        {{ s.nombre }}
      </h3>
      <p class="font-body-md text-body-md text-on-surface-variant mb-space-md leading-relaxed">
        {{ s.descripcion }}
      </p>
      {% if s.imagen %}
      <div class="w-full h-44 rounded-xl overflow-hidden mb-space-md border border-primary-container/20">
        <img class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" src="{{ s.imagen }}" alt="{{ s.nombre }}" />
      </div>
      {% endif %}
    </div>
    <div class="pt-space-md border-t border-outline-variant/30 flex items-center justify-between gap-space-sm mt-auto">
      <div>
        <span class="font-label-caps text-[10px] uppercase text-tertiary block">Inversión Estimada</span>
        <span class="font-headline-sm text-primary font-medium">{{ s.precio_o_duracion or "Consultar" }}</span>
      </div>
      <a class="inline-flex items-center justify-center gap-2 px-space-md py-2.5 rounded-full bg-primary hover:bg-on-primary-fixed-variant text-on-primary font-label-caps text-label-caps uppercase tracking-wider transition-all duration-200 shadow-sm" href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" rel="noopener noreferrer" target="_blank">
        <span>Reservar</span>
        <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
      </a>
    </div>
  </div>
  {% endfor %}
</div>"""
    html = re.sub(
        r'<!-- Bento Grid \(4 Cards\) -->.*?<!-- 4\. GALERÍA VISUAL & INSTAGRAM FEED -->',
        bento_replacement + '\n</section>\n<!-- 4. GALERÍA VISUAL & INSTAGRAM FEED -->',
        html,
        flags=re.DOTALL
    )

    # 11. Gallery Section & ID
    html = re.sub(
        r'<!-- 4\. GALERÍA VISUAL & INSTAGRAM FEED -->\s*<section class="w-full py-space-xl">',
        r'<!-- 4. GALERÍA VISUAL & INSTAGRAM FEED -->\n<section id="galeria" class="w-full py-space-xl scroll-mt-28">',
        html
    )
    html = re.sub(
        r'href="https://instagram\.com/elixir\.madrid"',
        r"""href="{{ negocio.instagram_url }}" target="_blank" rel="noopener\"""",
        html
    )
    html = re.sub(
        r'<span>@elixir\.madrid • Síguenos en Instagram</span>',
        r"""<span>@{{ ig.username or (negocio.nombre|lower|replace(' ', '')) }} • Síguenos en Instagram</span>""",
        html
    )

    gallery_replacement = """<!-- 4-Item Curated Visual Grid -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-gutter">
  {% for post in ig.posts[:4] %}
  <div class="group relative rounded-[20px] overflow-hidden aspect-[4/5] border border-primary-container/25 shadow-sm bg-surface-container">
    <img alt="{{ post.caption[:40] if post.caption else negocio.nombre }}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out" src="{{ post.image_url }}" />
    <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-4">
      <span class="font-label-caps text-[10px] text-primary-fixed uppercase tracking-wider">Instagram Post</span>
      <p class="font-body-sm text-surface-container-lowest font-medium text-xs line-clamp-2">{{ post.caption or negocio.nombre }}</p>
    </div>
  </div>
  {% endfor %}
</div>"""
    html = re.sub(
        r'<!-- 4-Item Curated Visual Grid -->.*?<!-- 5\. TESTIMONIOS REALES',
        gallery_replacement + '\n</section>\n<!-- 5. TESTIMONIOS REALES',
        html,
        flags=re.DOTALL
    )

    # 12. Philosophy (Filosofía) Section ID
    html = re.sub(
        r'<!-- 5\. TESTIMONIOS REALES \(EDITORIAL LUXURY CARDS\) -->\s*<section class="w-full py-space-xl">',
        r'<!-- 5. TESTIMONIOS REALES (EDITORIAL LUXURY CARDS) -->\n<section id="filosofia" class="w-full py-space-xl scroll-mt-28">',
        html
    )

    # 13. Contact & Booking CTA Section ID
    html = re.sub(
        r'<!-- FINAL PRE-FOOTER CONCIERGE BANNER -->\s*<section class="w-full py-space-xl">',
        r'<!-- FINAL PRE-FOOTER CONCIERGE BANNER -->\n<section id="contacto" class="w-full py-space-xl scroll-mt-28">',
        html
    )

    # 14. Footer replacements
    html = re.sub(r'Élixir Studio &amp; Aesthetics Logo', r"""{{ negocio.nombre }} Logo""", html)
    html = re.sub(
        r'<span class="font-headline-sm text-headline-sm tracking-tight text-on-surface ml-1">Élixir Studio</span>',
        r"""<span class="font-headline-sm text-headline-sm tracking-tight text-on-surface ml-1">{{ negocio.nombre }}</span>""",
        html
    )
    html = re.sub(
        r'<p class="font-body-sm text-body-sm text-on-surface-variant max-w-sm">Medicina estética y rituales dermatológicos de autor en el corazón de Madrid\. Precisión clínica, sosiego absoluto y exclusividad artesanal\.</p>',
        r"""<p class="font-body-sm text-body-sm text-on-surface-variant max-w-sm">{{ web.sobre_nosotros or ('Servicios profesionales de alta fidelidad y cuidado de autor en ' ~ negocio.ciudad ~ '. Máxima calidad y atención 100% personalizada.') }}</p>""",
        html
    )
    html = re.sub(
        r'<p>Calle de Serrano, 48, 1º Izquierda</p>\s*<p>28001 Madrid, España</p>',
        r"""<p>{{ negocio.direccion or negocio.ciudad }}</p>\n<p>{{ negocio.ciudad }}, España</p>""",
        html
    )
    html = re.sub(
        r'© 2025 Élixir Studio • Madrid\. Todos los derechos reservados\.',
        r"""© 2025 {{ negocio.nombre }} • {{ negocio.ciudad }}. Todos los derechos reservados.""",
        html
    )

    # 15. Mobile Sticky Dock with safe-area padding
    sticky_dock = """<!-- 6. STICKY MOBILE ACTION BAR (FIXED BOTTOM DOCK ON MOBILE) -->
<div class="fixed bottom-0 inset-x-0 z-40 lg:hidden p-3 bg-surface-container-lowest/95 backdrop-blur-lg border-t border-primary-container/25 shadow-[0_-8px_20px_rgba(0,0,0,0.06)]" style="padding-bottom: max(0.75rem, env(safe-area-inset-bottom, 0px));">
  <div class="max-w-md mx-auto flex items-center justify-between gap-3">
    <div class="flex flex-col">
      <span class="font-label-caps text-[10px] text-primary uppercase font-bold tracking-wider">Cita Previa VIP</span>
      <span class="font-body-sm text-xs text-on-surface-variant truncate">Horario Hoy: Abierto</span>
    </div>
    <a class="inline-flex items-center justify-center gap-2 px-space-md py-2.5 rounded-full bg-primary-container text-on-surface font-label-caps text-label-caps uppercase tracking-wider shadow-md hover:bg-primary hover:text-on-primary transition-colors" href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" target="_blank" rel="noopener">
      <span class="material-symbols-outlined text-[18px]">chat</span>
      <span>WhatsApp</span>
    </a>
  </div>
</div>"""
    html = re.sub(r'<!-- 6\. STICKY MOBILE ACTION BAR.*?</div>\s*</div>', sticky_dock, html, flags=re.DOTALL)

    # 16. Append Mobile Drawer Component & Script
    drawer = make_mobile_drawer_and_script(
        template_id="luxury_glow",
        nav_items=[
            ("Carta de Servicios", "servicios", "spa"),
            ("Filosofía de Autor", "filosofia", "auto_awesome"),
            ("Galería de Resultados", "galeria", "photo_camera"),
            ("Contacto & Reserva", "contacto", "location_on"),
        ],
        drawer_bg_class="bg-surface-container-lowest",
        drawer_border_class="border-primary-container/30",
        link_class="hover:bg-surface-container text-on-surface hover:text-primary",
        cta_primary_class="bg-gradient-to-r from-primary to-primary-container text-on-primary",
        cta_secondary_class="bg-surface-container hover:bg-surface-container-high",
        icon_color_class="text-primary"
    )
    html = html.replace("</body>", drawer + "\n</body>")

    out_file = os.path.join(OUT_DIR, "stitch_luxury_glow.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Creada plantilla {out_file}")


def build_urban_edge():
    raw_path = os.path.join(STITCH_DIR, "urban_edge_desktop_raw.html")
    with open(raw_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Viewport fit cover (Dynamic Island iPhone)
    html = re.sub(
        r'<meta content="width=device-width, initial-scale=1.0" name="viewport"/>',
        r'<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover"/>',
        html
    )

    # 2. Smooth scrolling & safe-area CSS
    safe_css = get_safe_area_script_and_css(5.0)
    html = html.replace("</head>", safe_css + "\n</head>")

    # 3. Title & Meta
    html = re.sub(
        r"<title>.*?</title>",
        r"""<title>{{ negocio.nombre }} | Taller & Custom Studio en {{ negocio.ciudad }}</title>
  <meta name="description" content="{{ web.subtitulo or ('Sitio web oficial y presupuestos para ' ~ negocio.nombre ~ ' en ' ~ negocio.ciudad) }}">""",
        html,
        flags=re.DOTALL
    )

    # 4. Favicon
    html = re.sub(
        r'<link href="https://fonts.googleapis.com"',
        r"""<link rel="icon" type="image/jpeg" href="{{ ig.avatar_url or 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=96&q=80' }}">
<link href="https://fonts.googleapis.com\"""",
        html,
        count=1
    )

    # 5. Header Dynamic Island safe area
    html = re.sub(
        r'<header class="fixed top-0 left-0 w-full z-50 bg-surface-container-lowest/95 backdrop-blur-md border-b border-surface-container-high">',
        r'<header class="fixed top-0 left-0 w-full z-50 bg-surface-container-lowest/95 backdrop-blur-md border-b border-surface-container-high" style="padding-top: var(--sat, env(safe-area-inset-top, 0px));">',
        html
    )

    # Logo & Moniker
    html = re.sub(
        r'<span class="font-headline-md text-body-md font-bold tracking-tight text-on-surface uppercase">APEX CUSTOMS</span>',
        r"""<span class="font-headline-md text-body-md font-bold tracking-tight text-on-surface uppercase truncate max-w-[170px] sm:max-w-xs md:max-w-none">{{ negocio.nombre }}</span>""",
        html
    )
    html = re.sub(
        r'<span class="font-label-sm text-label-sm tracking-widest text-primary font-semibold -mt-1">// MADRID SPEED SHOP</span>',
        r"""<span class="font-label-sm text-label-sm tracking-widest text-primary font-semibold -mt-1">// {{ negocio.categoria_clean|upper }}</span>""",
        html
    )

    # 6. Functional Desktop Navigation
    new_desktop_nav = """<nav class="hidden md:flex items-center gap-space-md" data-active-classes="bg-primary-container text-on-primary-container font-bold rounded-lg">
      <a class="px-space-sm py-space-xs font-label-md text-label-md uppercase tracking-wider text-on-surface-variant hover:text-primary transition-colors" href="#galeria">The Works</a>
      <a class="px-space-sm py-space-xs font-label-md text-label-md uppercase tracking-wider text-on-surface-variant hover:text-primary transition-colors" href="#servicios">Servicios &amp; Tarifas</a>
      <a class="px-space-sm py-space-xs font-label-md text-label-md uppercase tracking-wider text-on-surface-variant hover:text-primary transition-colors" href="#box-hq">Box HQ</a>
      <a class="px-space-sm py-space-xs font-label-md text-label-md uppercase tracking-wider text-on-surface-variant hover:text-primary transition-colors" href="#contacto">Contacto</a>
    </nav>"""
    html = re.sub(r'<nav class="hidden md:flex items-center gap-space-md".*?</nav>', new_desktop_nav, html, flags=re.DOTALL)

    # 7. Add Hamburger Button to Header (On the RIGHT)
    burger_btn = """<!-- Mobile Hamburger Button (On the RIGHT) -->
      <button id="hamburger-btn" onclick="toggleMobileMenu()" class="md:hidden p-2 rounded-lg bg-surface-container hover:bg-surface-container-high text-on-surface transition flex items-center justify-center border border-surface-container-high shadow-sm ml-1" aria-label="Abrir Menú" aria-expanded="false">
        <span class="material-symbols-outlined text-[24px]">menu</span>
      </button>"""
    html = re.sub(
        r'<div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center">\s*<span class="material-symbols-outlined text-on-primary text-\[18px\]">person</span>\s*</div>',
        r"""<div class="hidden sm:flex w-8 h-8 rounded-full bg-primary items-center justify-center"><span class="material-symbols-outlined text-on-primary text-[18px]">person</span></div>\n      """ + burger_btn,
        html
    )

    # 8. Main Safe-Area Padding
    html = re.sub(
        r'<main class="w-full pt-16 bg-surface-container-lowest min-h-screen">',
        r'<main class="w-full bg-surface-container-lowest min-h-screen" style="padding-top: calc(6.5rem + var(--sat, env(safe-area-inset-top, 0px)));">',
        html
    )

    # 9. Hero Badge & Copy
    html = re.sub(
        r'<span class="font-label-sm text-label-sm text-secondary font-medium tracking-wider uppercase">BOX ABIERTO // 3 ELEVADORES DISPONIBLES</span>',
        r"""<span class="font-label-sm text-label-sm text-secondary font-medium tracking-wider uppercase">{{ web.badge_status or 'BOX ABIERTO // CITAS DISPONIBLES' }}</span>""",
        html
    )
    html = re.sub(
        r'<h1 class="font-display-hero text-display-hero text-on-surface tracking-tight uppercase">.*?</h1>',
        r"""<h1 class="font-display-hero text-display-hero text-on-surface tracking-tight uppercase">
          {{ web.titular or ('Mecánica de alto rendimiento y personalización en ' ~ negocio.ciudad) }}
        </h1>""",
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<p class="font-body-md text-body-md text-secondary leading-relaxed max-w-lg">.*?</p>',
        r"""<p class="font-body-md text-body-md text-secondary leading-relaxed max-w-lg">
          {{ web.subtitulo or ('Especialistas en diagnosis avanzada, mantenimiento integral y preparación custom en ' ~ negocio.ciudad ~ '.') }}
        </p>""",
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'href="#solicitar-presupuesto"',
        r"""href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" target="_blank" rel="noopener\"""",
        html
    )

    # Hero Main Image
    html = re.sub(
        r'src="https://lh3\.googleusercontent\.com/aida-public/AB6AXuAMs_K5uUuJ04X4y1C7Jd_j2iQJd8Hcx2G4"',
        r"""src="{{ ig.posts[0].image_url if ig.posts and ig.posts[0].image_url else 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=1200&q=80' }}\"""",
        html
    )

    # 10. Sections & Section IDs
    # Hero: id="inicio"
    html = re.sub(
        r'<section class="relative w-full px-gutter-mobile lg:px-margin pt-space-xl pb-space-xl overflow-hidden bg-surface-container-lowest">',
        r'<section id="inicio" class="relative w-full px-gutter-mobile lg:px-margin pt-space-xl pb-space-xl overflow-hidden bg-surface-container-lowest">',
        html
    )
    # Box HQ section (Guarantees & Standards)
    html = re.sub(
        r'<!-- 02 // KEY METRICS & TRUST BAR \(3-COLUMN BENTO GRID\) -->\s*<section class="w-full px-gutter-mobile lg:px-margin py-space-lg bg-surface-container-lowest border-y border-surface-container-high">',
        r'<!-- 02 // KEY METRICS & TRUST BAR (3-COLUMN BENTO GRID) -->\n<section id="box-hq" class="w-full px-gutter-mobile lg:px-margin py-space-lg bg-surface-container-lowest border-y border-surface-container-high scroll-mt-20">',
        html
    )
    # The Works (Gallery): id="galeria"
    html = re.sub(
        r'<!-- 03 // PORTFOLIO GRID - THE WORKS -->\s*<section class="w-full px-gutter-mobile lg:px-margin py-space-xl bg-surface-container-lowest">',
        r'<!-- 03 // PORTFOLIO GRID - THE WORKS -->\n<section id="galeria" class="w-full px-gutter-mobile lg:px-margin py-space-xl bg-surface-container-lowest scroll-mt-20">',
        html
    )
    # Services & Pricing: id="servicios"
    html = re.sub(
        r'<!-- 04 // SERVICE & PRICING BREAKDOWN \(TARIFARIO TÉCNICO MONOSPACE\) -->\s*<section class="w-full px-gutter-mobile lg:px-margin py-space-xl bg-surface-container-lowest border-t border-surface-container-high">',
        r'<!-- 04 // SERVICE & PRICING BREAKDOWN (TARIFARIO TÉCNICO MONOSPACE) -->\n<section id="servicios" class="w-full px-gutter-mobile lg:px-margin py-space-xl bg-surface-container-lowest border-t border-surface-container-high scroll-mt-20">',
        html
    )

    # Dynamic Portfolio Cards from Instagram
    portfolio_replacement = """<!-- Dynamic Portfolio Cards from Instagram -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-gutter">
  {% for post in ig.posts[:3] %}
  <div class="group relative aspect-[4/5] rounded-lg overflow-hidden bg-surface-container border border-surface-container-high">
    <img alt="{{ post.caption[:30] if post.caption else negocio.nombre }}" class="w-full h-full object-cover grayscale contrast-125 group-hover:grayscale-0 group-hover:scale-105 transition-all duration-500" src="{{ post.image_url }}" />
    <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent p-space-md flex flex-col justify-end">
      <span class="font-label-sm text-primary font-mono text-xs uppercase tracking-widest">// REEL ARCHIVE 0{{ loop.index }}</span>
      <p class="font-headline-sm text-sm text-on-surface font-bold truncate">{{ post.caption or negocio.nombre }}</p>
    </div>
  </div>
  {% endfor %}
</div>"""
    html = re.sub(
        r'<!-- 3-Column Portfolio Cards -->.*?<!-- 04 // SERVICE & PRICING BREAKDOWN',
        portfolio_replacement + '\n</div>\n</section>\n<!-- 04 // SERVICE & PRICING BREAKDOWN',
        html,
        flags=re.DOTALL
    )

    # Dynamic Pricing Matrix from Gemini
    pricing_replacement = """<!-- Dynamic Pricing Matrix from Gemini -->
<div class="grid grid-cols-1 lg:grid-cols-3 gap-gutter items-stretch">
  {% for s in web.servicios[:3] %}
  <div class="p-space-lg rounded-lg bg-surface-container {% if loop.index == 2 %}border-2 border-primary-container shadow-[0_0_32px_rgba(249,115,22,0.18)] relative transform lg:-translate-y-2{% else %}border border-surface-container-high{% endif %} flex flex-col justify-between">
    {% if loop.index == 2 %}
    <div class="absolute -top-3.5 left-1/2 -translate-x-1/2 px-space-md py-0.5 rounded bg-primary-container text-on-primary-container font-label-sm text-label-sm font-bold uppercase tracking-widest">
      POPULAR // ALTA DEMANDA
    </div>
    {% endif %}
    <div class="flex flex-col gap-space-md">
      <div class="flex items-center justify-between border-b border-surface-container-high pb-space-sm">
        <span class="font-label-sm text-label-sm text-primary font-mono font-bold uppercase">TIER 0{{ loop.index }} // {{ s.nombre[:18]|upper }}</span>
        <span class="px-2 py-0.5 rounded bg-surface-container-lowest font-label-sm text-[10px] text-secondary font-mono">STANDARDS</span>
      </div>
      <div>
        <h3 class="font-headline-md text-headline-md uppercase text-on-surface tracking-tight">{{ s.nombre }}</h3>
        <div class="font-label-lg text-[26px] font-mono font-bold text-primary mt-2">
          {{ s.precio_o_duracion or "Consultar" }}
        </div>
        <span class="font-label-sm text-label-sm text-outline font-mono">Garantía oficial por escrito</span>
      </div>
      <p class="font-body-sm text-secondary">
        {{ s.descripcion }}
      </p>
    </div>
    <div class="pt-space-lg mt-auto">
      <a class="w-full inline-flex items-center justify-center py-3 rounded {% if loop.index == 2 %}bg-primary-container text-on-primary-container font-bold shadow-lg hover:bg-primary-fixed{% else %}bg-surface-container-high hover:bg-surface-variant text-on-surface font-semibold{% endif %} font-label-md text-label-md uppercase tracking-wider transition-colors" href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" target="_blank" rel="noopener">
        Seleccionar &amp; Contactar
      </a>
    </div>
  </div>
  {% endfor %}
</div>"""
    html = re.sub(
        r'<!-- Bento 3 Columns Grid -->.*?<!-- 05 // BOX HEADQUARTERS',
        pricing_replacement + '\n</div>\n</div>\n</section>\n<!-- 05 // BOX HEADQUARTERS',
        html,
        flags=re.DOTALL
    )

    # 11. Footer replacements
    html = re.sub(r'APEX CUSTOMS HQ', r"""{{ negocio.nombre|upper }} HQ""", html)
    html = re.sub(r'Calle de la Mecánica, 14, Nave 3', r"""{{ negocio.direccion or negocio.ciudad }}""", html)
    html = re.sub(r'28022 Madrid, España', r"""{{ negocio.ciudad }}, España""", html)

    # 12. Fixed Mobile Bottom Action Dock
    sticky_dock = """<!-- Fixed Mobile Bottom Action Dock -->
<div class="fixed bottom-0 inset-x-0 z-50 md:hidden p-3 bg-surface-container-lowest/95 backdrop-blur-xl border-t border-surface-container-high shadow-2xl" style="padding-bottom: max(0.75rem, env(safe-area-inset-bottom, 0px));">
  <div class="flex items-center justify-between gap-3">
    <div class="flex flex-col">
      <span class="font-label-sm text-xs font-mono font-bold text-primary uppercase">{{ negocio.nombre }}</span>
      <span class="text-xs text-secondary">{{ negocio.ciudad }}</span>
    </div>
    <a class="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-lg bg-primary-container text-on-primary-container font-label-md font-bold text-xs uppercase tracking-wider shadow-lg" href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" target="_blank" rel="noopener">
      <span class="material-symbols-outlined text-[18px]">chat</span>
      <span>WhatsApp Directo</span>
    </a>
  </div>
</div>"""

    # 13. Mobile Drawer Component & Script
    drawer = make_mobile_drawer_and_script(
        template_id="urban_edge",
        nav_items=[
            ("The Works (Portfolio)", "galeria", "photo_camera"),
            ("Servicios & Tarifas", "servicios", "precision_manufacturing"),
            ("Box HQ / Estándares", "box-hq", "verified"),
            ("Contacto & Taller", "contacto", "location_on"),
        ],
        drawer_bg_class="bg-[#0e0f12] text-[#f2f4f8]",
        drawer_border_class="border-[#242731]",
        link_class="hover:bg-[#181a20] text-[#c5c8d4] hover:text-[#f97316]",
        cta_primary_class="bg-primary-container text-on-primary-container",
        cta_secondary_class="bg-surface-container hover:bg-surface-container-high",
        icon_color_class="text-primary"
    )
    html = html.replace("</body>", sticky_dock + "\n" + drawer + "\n</body>")

    out_file = os.path.join(OUT_DIR, "stitch_urban_edge.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Creada plantilla {out_file}")


def build_warm_artisan():
    raw_path = os.path.join(STITCH_DIR, "warm_artisan_desktop_raw.html")
    with open(raw_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Viewport fit cover (Dynamic Island iPhone)
    html = re.sub(
        r'<meta content="width=device-width, initial-scale=1.0" name="viewport"/>',
        r'<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover"/>',
        html
    )

    # 2. Smooth scrolling & safe-area CSS
    safe_css = get_safe_area_script_and_css(5.5)
    html = html.replace("</head>", safe_css + "\n</head>")

    # 3. Title & Meta
    html = re.sub(
        r"<title>.*?</title>",
        r"""<title>{{ negocio.nombre }} | Obrador & Café de Especialidad en {{ negocio.ciudad }}</title>
  <meta name="description" content="{{ web.subtitulo or ('Sitio web oficial y carta para ' ~ negocio.nombre ~ ' en ' ~ negocio.ciudad) }}">""",
        html,
        flags=re.DOTALL
    )

    # 4. Favicon
    html = re.sub(
        r'<link href="https://fonts.googleapis.com"',
        r"""<link rel="icon" type="image/jpeg" href="{{ ig.avatar_url or 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=96&q=80' }}">
<link href="https://fonts.googleapis.com\"""",
        html,
        count=1
    )

    # 5. Header Dynamic Island safe area & Brand
    html = html.replace(
        '<header class="fixed top-0 w-full z-50 bg-surface/85 backdrop-blur-xl shadow-[0_1px_8px_rgba(0,0,0,0.04)]">',
        '<header class="fixed top-0 w-full z-50 bg-surface/85 backdrop-blur-xl shadow-[0_1px_8px_rgba(0,0,0,0.04)]" style="padding-top: var(--sat, env(safe-area-inset-top, 0px));">'
    )

    html = re.sub(
        r'<span class="font-headline-sm text-headline-sm text-on-surface leading-tight">Origen &amp; Miga</span>',
        r"""<span class="font-headline-sm text-headline-sm text-on-surface leading-tight truncate max-w-[170px] sm:max-w-xs md:max-w-none">{{ negocio.nombre }}</span>""",
        html
    )
    html = re.sub(
        r'<span class="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider">Panadería Artesanal &amp; Café</span>',
        r"""<span class="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider">{{ negocio.categoria_clean }}</span>""",
        html
    )

    # 6. Functional Desktop Navigation
    new_desktop_nav = """<nav class="hidden lg:flex items-center gap-space-md" data-active-classes="bg-primary-container text-on-primary-container font-bold rounded-lg">
      <a class="font-label-lg text-label-lg px-3 py-2 text-on-surface-variant hover:text-primary transition-colors" href="#filosofia">Filosofía</a>
      <a class="font-label-lg text-label-lg px-3 py-2 text-on-surface-variant hover:text-primary transition-colors" href="#carta">Carta Digital</a>
      <a class="font-label-lg text-label-lg px-3 py-2 text-on-surface-variant hover:text-primary transition-colors" href="#comunidad">Comunidad</a>
      <a class="font-label-lg text-label-lg px-3 py-2 text-on-surface-variant hover:text-primary transition-colors" href="#ubicacion">Ubicación &amp; Reservas</a>
    </nav>"""
    html = re.sub(r'<nav class="hidden lg:flex items-center gap-space-md".*?</nav>', new_desktop_nav, html, flags=re.DOTALL)

    # 7. Add Hamburger Button to Header (On the RIGHT)
    burger_btn = """<!-- Mobile Hamburger Button (On the RIGHT) -->
      <button id="hamburger-btn" onclick="toggleMobileMenu()" class="lg:hidden p-2 rounded-lg text-on-surface hover:bg-surface-container transition flex items-center justify-center border border-outline-variant/40 ml-1" aria-label="Abrir Menú" aria-expanded="false">
        <span class="material-symbols-outlined text-[24px]">menu</span>
      </button>"""
    html = re.sub(
        r'<div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">\s*<span class="material-symbols-outlined text-on-primary text-\[18px\]">person</span>\s*</div>',
        r"""<div class="hidden sm:flex w-8 h-8 rounded-full bg-primary items-center justify-center shrink-0"><span class="material-symbols-outlined text-on-primary text-[18px]">person</span></div>\n      """ + burger_btn,
        html
    )

    # 8. Main Safe-Area Padding
    html = re.sub(
        r'<main class="w-full pt-20 bg-surface">',
        r'<main class="w-full bg-surface" style="padding-top: calc(6.5rem + var(--sat, env(safe-area-inset-top, 0px)));">',
        html
    )

    # 9. Hero Badge & Copy
    html = re.sub(
        r'🥖 Masa Madre de Cultivo Natural • Café de Finca',
        r"""{{ web.badge_status or '🥖 Elaborado a Diario • Café de Especialidad' }}""",
        html
    )
    html = re.sub(
        r'<h1 class="font-display-hero text-display-hero-mobile sm:text-display-hero font-bold tracking-tight text-on-surface mb-6">.*?</h1>',
        r"""<h1 class="font-display-hero text-display-hero-mobile sm:text-display-hero font-bold tracking-tight text-on-surface mb-6">
          {{ web.titular or ('Sabor auténtico y procesos artesanos en ' ~ negocio.ciudad) }}
        </h1>""",
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<p class="font-body-lg text-body-lg text-on-surface-variant max-w-xl mb-8 leading-relaxed">.*?</p>',
        r"""<p class="font-body-lg text-body-lg text-on-surface-variant max-w-xl mb-8 leading-relaxed">
          {{ web.subtitulo or ('Ingredientes locales seleccionados y recetas con alma en ' ~ negocio.ciudad ~ '. Ven a disfrutar de una experiencia diferente.') }}
        </p>""",
        html,
        flags=re.DOTALL
    )

    # Hero CTAs
    html = re.sub(
        r'href="#carta-digital"',
        r"""href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" target="_blank" rel="noopener\"""",
        html
    )
    html = re.sub(
        r'href="#como-llegar"',
        r"""href="#ubicacion\"""",
        html
    )

    # Hero Images
    html = re.sub(
        r'<img class="w-full h-full object-cover select-none" data-alt="[^"]*" src="https://lh3\.googleusercontent\.com/aida-public/AB6AXuCHX1Gk37C7Jd_j2iQJd8Hcx2G4cK8N2bA"/>',
        r"""<img class="w-full h-full object-cover select-none" alt="{{ negocio.nombre }}" src="{{ ig.posts[0].image_url if ig.posts and ig.posts[0].image_url else 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1200&q=80' }}"/>""",
        html
    )

    # 10. Sections & IDs
    # Section 1 (Hero): id="inicio"
    html = re.sub(
        r'<section class="relative w-full overflow-hidden bg-surface pt-6 pb-16 lg:pt-10 lg:pb-24">',
        r'<section id="inicio" class="relative w-full overflow-hidden bg-surface pt-6 pb-16 lg:pt-10 lg:pb-24">',
        html
    )
    # Section 2 (Filosofía): id="filosofia"
    html = re.sub(
        r'<section class="w-full py-16 bg-surface-container-low">',
        r'<section id="filosofia" class="w-full py-16 bg-surface-container-low scroll-mt-24">',
        html,
        count=1
    )
    # Section 3 (Carta): id="carta" already has id="carta"
    html = re.sub(
        r'<section class="w-full py-20 bg-surface" id="carta">',
        r'<section id="carta" class="w-full py-20 bg-surface scroll-mt-24">',
        html
    )
    # Section 4 (Comunidad Instagram): id="comunidad"
    html = re.sub(
        r'(<section class="w-full py-16 bg-surface-container-low">)',
        r'<section id="comunidad" class="w-full py-16 bg-surface-container-low scroll-mt-24">',
        html
    )
    # Section 5 (Ubicación): id="ubicacion"
    html = re.sub(
        r'<section class="w-full py-20 bg-surface" id="ubicacion">',
        r'<section id="ubicacion" class="w-full py-20 bg-surface scroll-mt-24">',
        html
    )

    # Dynamic Menu Cards in Tab 1
    menu_replacement = """<!-- Dynamic Services List from Gemini -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {% for s in web.servicios %}
  <div class="p-6 rounded-2xl bg-surface-container border border-outline-variant/30 flex flex-col justify-between hover:shadow-md transition-shadow">
    <div>
      <div class="flex items-start justify-between gap-2 mb-2">
        <h4 class="font-headline-sm text-lg font-bold text-on-surface">{{ s.nombre }}</h4>
        <span class="font-label-lg text-primary font-bold whitespace-nowrap">{{ s.precio_o_duracion or "Especialidad" }}</span>
      </div>
      <p class="font-body-sm text-on-surface-variant text-sm mb-4">{{ s.descripcion }}</p>
      {% if s.imagen %}
      <div class="w-full h-36 rounded-xl overflow-hidden mb-4 border border-outline-variant/20">
        <img class="w-full h-full object-cover" src="{{ s.imagen }}" alt="{{ s.nombre }}" />
      </div>
      {% endif %}
    </div>
    <a class="inline-flex items-center gap-1.5 text-xs font-bold text-primary hover:text-secondary transition-colors mt-auto" href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" target="_blank" rel="noopener">
      <span>Pedir por WhatsApp</span>
      <span class="material-symbols-outlined text-[14px]">arrow_forward</span>
    </a>
  </div>
  {% endfor %}
</div>"""
    html = re.sub(
        r'<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">.*?</div>\s*<!-- CTA Pedidos / Contacto Directo -->',
        menu_replacement + '\n<!-- CTA Pedidos / Contacto Directo -->',
        html,
        flags=re.DOTALL
    )

    # 11. Address & Footer
    html = re.sub(r'Calle de Luchana, 28', r"""{{ negocio.direccion or negocio.ciudad }}""", html)
    html = re.sub(r'28010 Chamberí, Madrid', r"""{{ negocio.ciudad }}, España""", html)
    html = re.sub(
        r'© 2025 Origen &amp; Miga Bakery Co\. Todos los derechos reservados\.',
        r"""© 2025 {{ negocio.nombre }} • {{ negocio.ciudad }}. Todos los derechos reservados.""",
        html
    )

    # 12. Mobile Bottom Bar with safe-area
    sticky_bar = """<!-- Fixed Mobile Bottom Bar -->
<div class="fixed bottom-0 inset-x-0 z-50 md:hidden p-3 bg-surface/95 backdrop-blur-md border-t border-primary/20 shadow-lg" style="padding-bottom: max(0.75rem, env(safe-area-inset-bottom, 0px));">
  <div class="flex items-center justify-between gap-3">
    <div class="flex flex-col">
      <span class="font-headline-sm text-xs font-bold text-on-surface">{{ negocio.nombre }}</span>
      <span class="text-[11px] text-on-surface-variant">{{ negocio.ciudad }}</span>
    </div>
    <a class="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-primary text-on-primary font-label-lg text-xs font-bold shadow-md" href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" target="_blank" rel="noopener">
      <span class="material-symbols-outlined text-[16px]">chat</span>
      <span>WhatsApp Carta</span>
    </a>
  </div>
</div>"""

    # 13. Mobile Drawer Component & Script
    drawer = make_mobile_drawer_and_script(
        template_id="warm_artisan",
        nav_items=[
            ("Filosofía & Origen", "filosofia", "bakery_dining"),
            ("Carta Digital", "carta", "restaurant_menu"),
            ("Comunidad & Fotos", "comunidad", "photo_camera"),
            ("Ubicación & Reservas", "ubicacion", "storefront"),
        ],
        drawer_bg_class="bg-surface",
        drawer_border_class="border-outline-variant/30",
        link_class="hover:bg-surface-container text-on-surface hover:text-primary",
        cta_primary_class="bg-primary text-on-primary",
        cta_secondary_class="bg-surface-container hover:bg-surface-container-high",
        icon_color_class="text-primary"
    )
    html = html.replace("</body>", sticky_bar + "\n" + drawer + "\n</body>")

    out_file = os.path.join(OUT_DIR, "stitch_warm_artisan.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Creada plantilla {out_file}")


def build_clinical_trust():
    raw_path = os.path.join(STITCH_DIR, "clinical_trust_desktop_raw.html")
    with open(raw_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Viewport fit cover (Dynamic Island iPhone)
    html = re.sub(
        r'<meta content="width=device-width, initial-scale=1.0" name="viewport"/>',
        r'<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover"/>',
        html
    )

    # 2. Smooth scrolling & safe-area CSS
    safe_css = get_safe_area_script_and_css(8.0)
    html = html.replace("</head>", safe_css + "\n</head>")

    # 3. Title & Meta
    html = re.sub(
        r"<title>.*?</title>",
        r"""<title>{{ negocio.nombre }} | Clínica & Salud en {{ negocio.ciudad }}</title>
  <meta name="description" content="{{ web.subtitulo or ('Sitio web oficial y citas para ' ~ negocio.nombre ~ ' en ' ~ negocio.ciudad) }}">""",
        html,
        flags=re.DOTALL
    )

    # 4. Favicon
    html = re.sub(
        r'<link href="https://fonts.googleapis.com"',
        r"""<link rel="icon" type="image/jpeg" href="{{ ig.avatar_url or 'https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=96&q=80' }}">
<link href="https://fonts.googleapis.com\"""",
        html,
        count=1
    )

    # 5. Header Dynamic Island safe area & Brand
    html = html.replace(
        '<header class="fixed top-0 left-0 w-full z-50 bg-surface/95 backdrop-blur-md shadow-[0_1px_8px_rgba(0,0,0,0.04)]">',
        '<header class="fixed top-0 left-0 w-full z-50 bg-surface/95 backdrop-blur-md shadow-[0_1px_8px_rgba(0,0,0,0.04)]" style="padding-top: var(--sat, env(safe-area-inset-top, 0px));">'
    )

    html = html.replace('alt="SannaMed Clinic Logo"', 'alt="{{ negocio.nombre }} Clinic Logo"')
    html = html.replace('<span class="font-title-lg text-title-lg text-on-surface font-bold tracking-tight">SannaMed</span>', '<span class="font-title-lg text-title-lg text-on-surface font-bold tracking-tight truncate max-w-[170px] sm:max-w-xs md:max-w-none">{{ negocio.nombre }}</span>')
    html = html.replace('SannaMed Clinic', '{{ negocio.nombre }}')
    html = html.replace('SannaMed', '{{ negocio.nombre }}')

    # 6. Functional Desktop Navigation
    new_desktop_nav = """<nav class="hidden lg:flex items-center gap-space-xs" data-active-classes="bg-surface-container text-primary font-title-md">
      <a class="px-space-md py-space-xs rounded-lg text-on-surface-variant hover:bg-surface-container hover:text-primary font-title-md text-title-md transition-colors" href="#especialidades">Especialidades</a>
      <a class="px-space-md py-space-xs rounded-lg text-on-surface-variant hover:bg-surface-container hover:text-primary font-title-md text-title-md transition-colors" href="#garantias">Garantías</a>
      <a class="px-space-md py-space-xs rounded-lg text-on-surface-variant hover:bg-surface-container hover:text-primary font-title-md text-title-md transition-colors" href="#equipo-medico">Equipo Médico</a>
      <a class="px-space-md py-space-xs rounded-lg text-on-surface-variant hover:bg-surface-container hover:text-primary font-title-md text-title-md transition-colors" href="#opiniones">Opiniones</a>
      <a class="px-space-md py-space-xs rounded-lg text-on-surface-variant hover:bg-surface-container hover:text-primary font-title-md text-title-md transition-colors" href="#tecnologia-3d">Tecnología 3D</a>
      <a class="px-space-md py-space-xs rounded-lg text-on-surface-variant hover:bg-surface-container hover:text-primary font-title-md text-title-md transition-colors" href="#cita-online">Pedir Cita</a>
    </nav>"""
    html = re.sub(r'<nav class="hidden lg:flex items-center gap-space-xs".*?</nav>', new_desktop_nav, html, flags=re.DOTALL)

    # 7. Add Hamburger Button to Header (On the RIGHT)
    burger_btn = """<!-- Mobile Hamburger Button (On the RIGHT) -->
      <button id="hamburger-btn" onclick="toggleMobileMenu()" class="lg:hidden p-2 rounded-xl text-primary hover:bg-surface-container transition flex items-center justify-center border border-outline/20 ml-1" aria-label="Abrir Menú" aria-expanded="false">
        <span class="material-symbols-outlined text-[24px]">menu</span>
      </button>"""
    html = re.sub(
        r'<div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center">\s*<span class="material-symbols-outlined text-on-primary text-\[18px\]">person</span>\s*</div>',
        r"""<div class="hidden sm:flex w-8 h-8 rounded-full bg-primary items-center justify-center"><span class="material-symbols-outlined text-on-primary text-[18px]">person</span></div>\n      """ + burger_btn,
        html
    )

    # 8. Main Safe-Area Padding
    html = re.sub(
        r'<main class="w-full pt-\[120px\] bg-background min-h-screen">',
        r'<main class="w-full bg-background min-h-screen" style="padding-top: calc(9rem + var(--sat, env(safe-area-inset-top, 0px)));">',
        html
    )

    # 9. Hero Badge & Copy
    html = re.sub(
        r'🩺 1ª CITA &amp; DIAGNÓSTICO DIGITAL DISPONIBLE',
        r"""{{ web.badge_status or '🩺 1ª CITA & DIAGNÓSTICO DIGITAL DISPONIBLE' }}""",
        html
    )
    html = re.sub(
        r'<h1 class="font-display text-display tracking-tight text-on-surface font-extrabold max-w-2xl leading-\[1\.1\]">.*?</h1>',
        r"""<h1 class="font-display text-display tracking-tight text-on-surface font-extrabold max-w-2xl leading-[1.1]">
          {{ web.titular or ('Cuidamos de tu sonrisa y salud con la tecnología más avanzada en ' ~ negocio.ciudad) }}
        </h1>""",
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<p class="font-body-lg text-body-lg text-on-surface-variant max-w-xl leading-relaxed">.*?</p>',
        r"""<p class="font-body-lg text-body-lg text-on-surface-variant max-w-xl leading-relaxed">
          {{ web.subtitulo or ('Atención médica personalizada con equipo colegiado, instalaciones de vanguardia y diagnóstico digital en ' ~ negocio.ciudad ~ '.') }}
        </p>""",
        html,
        flags=re.DOTALL
    )

    # CTAs
    html = re.sub(
        r'href="#pedir-cita"',
        r"""href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" target="_blank" rel="noopener\"""",
        html
    )
    html = re.sub(
        r'href="tel:\+34910123456"',
        r"""href="tel:{{ negocio.telefono }}\"""",
        html
    )

    # Hero Image
    html = re.sub(
        r'<img class="w-full h-full object-cover" data-alt="[^"]*" src="https://lh3\.googleusercontent\.com/aida-public/AB6AXuCTc73E84F3yE7u2W7sT3301C7Jd_j2iQJd8Hcx2G4cK8N2bA"/>',
        r"""<img class="w-full h-full object-cover" alt="{{ negocio.nombre }}" src="{{ ig.posts[0].image_url if ig.posts and ig.posts[0].image_url else 'https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=1200&q=80' }}"/>""",
        html
    )

    # 10. Ensure Section IDs have scroll-margin
    html = re.sub(
        r'<section class="w-full py-space-xl bg-surface-container-low" id="garantias">',
        r'<section class="w-full py-space-xl bg-surface-container-low scroll-mt-32" id="garantias">',
        html
    )
    html = re.sub(
        r'<section class="w-full py-space-xl bg-surface" id="especialidades">',
        r'<section class="w-full py-space-xl bg-surface scroll-mt-32" id="especialidades">',
        html
    )
    html = re.sub(
        r'<section class="w-full py-space-xl bg-surface-container-low" id="tecnologia-3d">',
        r'<section class="w-full py-space-xl bg-surface-container-low scroll-mt-32" id="tecnologia-3d">',
        html
    )
    html = re.sub(
        r'<section class="w-full py-space-xl bg-surface" id="equipo-medico">',
        r'<section class="w-full py-space-xl bg-surface scroll-mt-32" id="equipo-medico">',
        html
    )
    html = re.sub(
        r'<section class="w-full py-space-xl bg-surface-container-low" id="opiniones">',
        r'<section class="w-full py-space-xl bg-surface-container-low scroll-mt-32" id="opiniones">',
        html
    )
    html = re.sub(
        r'<section class="w-full py-space-xl bg-surface" id="cita-online">',
        r'<section class="w-full py-space-xl bg-surface scroll-mt-32" id="cita-online">',
        html
    )

    # Bento Grid for Treatments
    treatments_replacement = """<!-- Dynamic Treatments Bento Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-12 gap-gutter items-stretch">
  {% for s in web.servicios %}
  <div class="{% if loop.first %}lg:col-span-8{% elif loop.index == 2 %}lg:col-span-4{% elif loop.index == 3 %}lg:col-span-4{% else %}lg:col-span-8{% endif %} p-8 rounded-3xl bg-surface-container-lowest border border-primary-container/20 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group">
    <div>
      <div class="flex items-center justify-between mb-4">
        <span class="px-3 py-1 rounded-full bg-primary-fixed/50 text-on-primary-fixed font-label-md text-xs font-semibold">
          Especialidad 0{{ loop.index }}
        </span>
        <span class="font-label-md text-xs text-tertiary font-bold flex items-center gap-1">
          <span class="material-symbols-outlined text-[16px]">verified</span> {{ s.precio_o_duracion or "1ª Visita Incluida" }}
        </span>
      </div>
      <h3 class="font-headline-md text-headline-md text-on-surface font-bold mb-2">{{ s.nombre }}</h3>
      <p class="font-body-md text-on-surface-variant leading-relaxed mb-6">
        {{ s.descripcion }}
      </p>
      {% if s.imagen %}
      <div class="w-full h-44 rounded-2xl overflow-hidden mb-6 border border-outline-variant/30">
        <img class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" src="{{ s.imagen }}" alt="{{ s.nombre }}" />
      </div>
      {% endif %}
    </div>
    <div class="pt-4 border-t border-outline-variant/20 flex items-center justify-between mt-auto">
      <span class="text-xs text-on-surface-variant">Equipo colegiado especialista</span>
      <a class="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-primary text-on-primary text-xs font-semibold hover:bg-secondary transition-colors" href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" target="_blank" rel="noopener">
        <span>Solicitar Valoración</span>
        <span class="material-symbols-outlined text-[14px]">arrow_forward</span>
      </a>
    </div>
  </div>
  {% endfor %}
</div>"""
    html = re.sub(
        r'<!-- Bento Grid Layout -->.*?<!-- EQUIPO MÉDICO &amp; CUALIFICACIÓN -->',
        treatments_replacement + '\n</div>\n</section>\n<!-- EQUIPO MÉDICO &amp; CUALIFICACIÓN -->',
        html,
        flags=re.DOTALL
    )

    # 11. Address & Footer
    html = re.sub(r'Paseo de la Castellana, 120, 1º B', r"""{{ negocio.direccion or negocio.ciudad }}""", html)
    html = re.sub(r'28046 Madrid, España', r"""{{ negocio.ciudad }}, España""", html)
    html = re.sub(
        r'© 2025 SannaMed Dental &amp; Salud Integral S\.L\.',
        r"""© 2025 {{ negocio.nombre }} • {{ negocio.ciudad }}.""",
        html
    )

    # 12. Sticky mobile action bar with safe-area
    sticky_bar = """<!-- Sticky Mobile Bar -->
<div class="fixed bottom-0 inset-x-0 z-50 lg:hidden p-3 bg-white/95 backdrop-blur-lg border-t border-primary-container/20 shadow-lg" style="padding-bottom: max(0.75rem, env(safe-area-inset-bottom, 0px));">
  <div class="flex items-center justify-between gap-3">
    <a class="flex-1 inline-flex items-center justify-center gap-2 py-3 rounded-xl bg-surface-container text-on-surface font-semibold text-xs border border-primary-container/30" href="tel:{{ negocio.telefono }}">
      <span class="material-symbols-outlined text-[16px]">call</span>
      <span>Llamar</span>
    </a>
    <a class="flex-1 inline-flex items-center justify-center gap-2 py-3 rounded-xl bg-primary text-on-primary font-semibold text-xs shadow-md" href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" target="_blank" rel="noopener">
      <span class="material-symbols-outlined text-[16px]">chat</span>
      <span>Cita WhatsApp</span>
    </a>
  </div>
</div>"""

    # 13. Mobile Drawer Component & Script
    drawer = make_mobile_drawer_and_script(
        template_id="clinical_trust",
        nav_items=[
            ("Especialidades Médicas", "especialidades", "medical_services"),
            ("Garantías Clínicas", "garantias", "verified_user"),
            ("Equipo Colegiado", "equipo-medico", "groups"),
            ("Opiniones de Pacientes", "opiniones", "reviews"),
            ("Tecnología & Diagnóstico", "tecnologia-3d", "biotech"),
            ("Pedir Cita Online", "cita-online", "calendar_month"),
        ],
        drawer_bg_class="bg-surface",
        drawer_border_class="border-surface-container-high",
        link_class="hover:bg-surface-container text-on-surface hover:text-primary",
        cta_primary_class="bg-primary text-on-primary",
        cta_secondary_class="bg-surface-container hover:bg-surface-container-high",
        icon_color_class="text-primary"
    )
    html = html.replace("</body>", sticky_bar + "\n" + drawer + "\n</body>")

    out_file = os.path.join(OUT_DIR, "stitch_clinical_trust.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Creada plantilla {out_file}")


def build_craft_build():
    raw_path = os.path.join(STITCH_DIR, "craft_build_desktop_raw.html")
    with open(raw_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Viewport fit cover (Dynamic Island iPhone)
    html = re.sub(
        r'<meta content="width=device-width, initial-scale=1.0" name="viewport"/>',
        r'<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover"/>',
        html
    )

    # 2. Smooth scrolling & safe-area CSS
    safe_css = get_safe_area_script_and_css(7.5)
    html = html.replace("</head>", safe_css + "\n</head>")

    # 3. Title & Meta
    html = re.sub(
        r"<title>.*?</title>",
        r"""<title>{{ negocio.nombre }} | Reformas & Construcción en {{ negocio.ciudad }}</title>
  <meta name="description" content="{{ web.subtitulo or ('Presupuesto cerrado y reformas garantizadas con ' ~ negocio.nombre ~ ' en ' ~ negocio.ciudad) }}">""",
        html,
        flags=re.DOTALL
    )

    # 4. Favicon
    html = re.sub(
        r'<link href="https://fonts.googleapis.com"',
        r"""<link rel="icon" type="image/jpeg" href="{{ ig.avatar_url or 'https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=96&q=80' }}">
<link href="https://fonts.googleapis.com\"""",
        html,
        count=1
    )

    # 5. Header Dynamic Island safe area & Brand
    html = html.replace(
        '<header class="fixed top-0 left-0 w-full z-50 bg-surface/90 backdrop-blur-md shadow-[0_1px_8px_rgba(0,0,0,0.04)]">',
        '<header class="fixed top-0 left-0 w-full z-50 bg-surface/90 backdrop-blur-md shadow-[0_1px_8px_rgba(0,0,0,0.04)]" style="padding-top: var(--sat, env(safe-area-inset-top, 0px));">'
    )

    html = re.sub(r'VÉRTICE', r"""<span class="truncate max-w-[170px] sm:max-w-xs md:max-w-none">{{ negocio.nombre|upper }}</span>""", html)
    html = re.sub(r'ARQ &amp; REFORMAS', r"""{{ negocio.categoria_clean|upper }}""", html)

    # 6. Functional Desktop Navigation
    new_desktop_nav = """<nav class="hidden xl:flex items-center gap-space-lg" data-active-classes="bg-surface-container text-primary font-bold rounded-lg">
      <a class="transition-colors py-space-xs px-space-sm rounded-lg font-label-md text-label-md text-on-surface-variant hover:text-primary" href="#inicio">Inicio</a>
      <a class="transition-colors py-space-xs px-space-sm rounded-lg font-label-md text-label-md text-on-surface-variant hover:text-primary" href="#servicios">Servicios</a>
      <a class="transition-colors py-space-xs px-space-sm rounded-lg font-label-md text-label-md text-on-surface-variant hover:text-primary" href="#antes-y-despues">Antes y Después</a>
      <a class="transition-colors py-space-xs px-space-sm rounded-lg font-label-md text-label-md text-on-surface-variant hover:text-primary" href="#garantias">Garantías</a>
      <a class="transition-colors py-space-xs px-space-sm rounded-lg font-label-md text-label-md text-on-surface-variant hover:text-primary" href="#opiniones">Opiniones</a>
      <a class="transition-colors py-space-xs px-space-sm rounded-lg font-label-md text-label-md text-on-surface-variant hover:text-primary" href="#solicitar-presupuesto">Presupuesto</a>
    </nav>"""
    html = re.sub(r'<nav class="hidden xl:flex items-center gap-space-lg".*?</nav>', new_desktop_nav, html, flags=re.DOTALL)

    # 7. Add Hamburger Button to Header (On the RIGHT)
    burger_btn = """<!-- Mobile Hamburger Button (On the RIGHT) -->
      <button id="hamburger-btn" onclick="toggleMobileMenu()" class="xl:hidden p-2 rounded-lg text-on-surface hover:bg-surface-container transition flex items-center justify-center border border-outline/20 ml-1" aria-label="Abrir Menú" aria-expanded="false">
        <span class="material-symbols-outlined text-[24px]">menu</span>
      </button>"""
    html = re.sub(
        r'<div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center">\s*<span class="material-symbols-outlined text-on-primary text-\[18px\]">person</span>\s*</div>',
        r"""<div class="hidden sm:flex w-8 h-8 rounded-full bg-primary items-center justify-center"><span class="material-symbols-outlined text-on-primary text-[18px]">person</span></div>\n      """ + burger_btn,
        html
    )

    # 8. Main Safe-Area Padding
    html = html.replace(
        '<main class="w-full pt-28 pb-20 lg:pb-0 bg-surface min-h-screen">',
        '<main class="w-full pb-20 lg:pb-0 bg-surface min-h-screen" style="padding-top: calc(8.5rem + var(--sat, env(safe-area-inset-top, 0px)));">'
    )

    # 9. Hero Badge & Copy
    html = re.sub(
        r'🛡️ PRESUPUESTO CERRADO POR ESCRITO • GARANTÍA 2 AÑOS',
        r"""{{ web.badge_status or '🛡️ PRESUPUESTO CERRADO POR ESCRITO • GARANTÍA 2 AÑOS' }}""",
        html
    )
    html = re.sub(
        r'<h1 class="font-display-hero text-display-hero tracking-tight text-on-surface font-extrabold leading-\[1\.08\]">.*?</h1>',
        r"""<h1 class="font-display-hero text-display-hero tracking-tight text-on-surface font-extrabold leading-[1.08]">
          {{ web.titular or ('Reformas e instalaciones con acabado impecable en ' ~ negocio.ciudad) }}
        </h1>""",
        html,
        flags=re.DOTALL
    )
    html = re.sub(
        r'<p class="font-body-lg text-body-lg text-secondary leading-relaxed max-w-xl">.*?</p>',
        r"""<p class="font-body-lg text-body-lg text-secondary leading-relaxed max-w-xl">
          {{ web.subtitulo or ('Convertimos tus ideas en espacios reales con presupuesto cerrado, gestión integral y cumplimiento de plazos en ' ~ negocio.ciudad ~ '.') }}
        </p>""",
        html,
        flags=re.DOTALL
    )

    # CTAs
    html = re.sub(
        r'href="#presupuesto"',
        r"""href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" target="_blank" rel="noopener\"""",
        html
    )
    html = re.sub(
        r'href="#proyectos"',
        r"""href="{{ negocio.instagram_url }}" target="_blank" rel="noopener\"""",
        html
    )

    # Hero Images
    html = re.sub(
        r'src="https://lh3\.googleusercontent\.com/aida-public/AB6AXuA0yP166oI1wI7K88V2WzS1j507C7C3"',
        r"""src="{{ ig.posts[1].image_url if ig.posts and ig.posts|length > 1 and ig.posts[1].image_url else 'https://images.unsplash.com/photo-1513694203232-719a280e022f?w=600&q=80' }}\"""",
        html
    )
    html = re.sub(
        r'src="https://lh3\.googleusercontent\.com/aida-public/AB6AXuB_pL1M3J7w2c01C7Jd_j2iQJd8Hcx2G4"',
        r"""src="{{ ig.posts[0].image_url if ig.posts and ig.posts[0].image_url else 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&q=80' }}\"""",
        html
    )

    # 10. Sections & IDs
    # Section 1 (Hero): id="inicio"
    html = re.sub(
        r'<section class="relative w-full overflow-hidden bg-surface-container-low px-gutter py-space-xl lg:py-space-2xl">',
        r'<section id="inicio" class="relative w-full overflow-hidden bg-surface-container-low px-gutter py-space-xl lg:py-space-2xl">',
        html
    )
    # Section 2 (Antes y Después): id="antes-y-despues"
    html = re.sub(
        r'<!-- Interactive Before / After Showcase Section -->\s*<section class="w-full bg-surface px-gutter py-space-2xl">',
        r'<!-- Interactive Before / After Showcase Section -->\n<section id="antes-y-despues" class="w-full bg-surface px-gutter py-space-2xl scroll-mt-28">',
        html
    )
    # Section 3 (Servicios): id="servicios"
    html = re.sub(
        r'<!-- Transparent Pricing & Scope Packages \(4 Modular Bento Cards\) -->\s*<section class="w-full bg-surface-container-low px-gutter py-space-2xl">',
        r'<!-- Transparent Pricing & Scope Packages (4 Modular Bento Cards) -->\n<section id="servicios" class="w-full bg-surface-container-low px-gutter py-space-2xl scroll-mt-28">',
        html
    )
    # Section 4 (Garantías): id="garantias"
    html = re.sub(
        r'<!-- Legal Security Checklist & Warranties \(\"Por Qué Trabajar con Nosotros\"\) -->\s*<section class="w-full bg-surface px-gutter py-space-2xl">',
        r'<!-- Legal Security Checklist & Warranties ("Por Qué Trabajar con Nosotros") -->\n<section id="garantias" class="w-full bg-surface px-gutter py-space-2xl scroll-mt-28">',
        html
    )
    # Section 5 (Opiniones): id="opiniones"
    html = re.sub(
        r'<!-- Verified Testimonials \(Social Proof\) -->\s*<section class="w-full bg-surface-container-low px-gutter py-space-2xl">',
        r'<!-- Verified Testimonials (Social Proof) -->\n<section id="opiniones" class="w-full bg-surface-container-low px-gutter py-space-2xl scroll-mt-28">',
        html
    )
    # Section 6 (Calculador Presupuesto): id="solicitar-presupuesto"
    html = re.sub(
        r'<section class="w-full bg-surface px-gutter py-space-2xl" id="solicitar-presupuesto">',
        r'<section class="w-full bg-surface px-gutter py-space-2xl scroll-mt-28" id="solicitar-presupuesto">',
        html
    )

    # Dynamic Work Packages
    services_replacement = """<!-- Dynamic Work Packages from Gemini -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-gutter">
  {% for s in web.servicios %}
  <div class="p-6 rounded-xl bg-surface-container-lowest border border-outline-variant/40 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group">
    <div>
      <div class="flex items-center justify-between mb-3">
        <span class="font-label-technical text-primary font-bold uppercase tracking-wider">PAQUETE 0{{ loop.index }}</span>
        <span class="text-xs text-secondary font-semibold">{{ s.precio_o_duracion or "A medida" }}</span>
      </div>
      <h3 class="font-headline-sm text-lg text-on-surface font-bold mb-2">{{ s.nombre }}</h3>
      <p class="font-body-sm text-secondary leading-relaxed mb-4">
        {{ s.descripcion }}
      </p>
      {% if s.imagen %}
      <div class="w-full h-36 rounded-lg overflow-hidden mb-4 border border-outline-variant/30">
        <img class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" src="{{ s.imagen }}" alt="{{ s.nombre }}" />
      </div>
      {% endif %}
    </div>
    <div class="pt-4 border-t border-outline-variant/30 mt-auto">
      <a class="w-full inline-flex items-center justify-center gap-1.5 py-2.5 rounded-lg bg-surface-container hover:bg-primary hover:text-on-primary text-on-surface font-semibold text-xs transition-colors" href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" target="_blank" rel="noopener">
        <span>Pedir Presupuesto</span>
        <span class="material-symbols-outlined text-[14px]">arrow_forward</span>
      </a>
    </div>
  </div>
  {% endfor %}
</div>"""
    html = re.sub(
        r'<!-- 4 Cards Grid -->.*?<!-- Legal Security Checklist & Warranties',
        services_replacement + '\n</div>\n</div>\n</section>\n<!-- Legal Security Checklist & Warranties',
        html,
        flags=re.DOTALL
    )

    # 11. Address & Footer
    html = re.sub(r'Paseo de la Habana, 42, Chamartín', r"""{{ negocio.direccion or negocio.ciudad }}""", html)
    html = re.sub(r'28036 Madrid, España', r"""{{ negocio.ciudad }}, España""", html)
    html = re.sub(
        r'© 2025 Vértice Arq &amp; Reformas S\.L\.',
        r"""© 2025 {{ negocio.nombre }} • {{ negocio.ciudad }}.""",
        html
    )

    # 12. Sticky Mobile Lead Bar with safe-area
    sticky_bar = """<!-- Sticky Mobile Lead Bar -->
<div class="fixed bottom-0 inset-x-0 z-50 md:hidden p-3 bg-white/95 backdrop-blur-md border-t border-slate-200 shadow-xl" style="padding-bottom: max(0.75rem, env(safe-area-inset-bottom, 0px));">
  <div class="flex items-center justify-between gap-3">
    <div class="flex flex-col">
      <span class="font-headline-sm text-xs font-bold text-slate-900">{{ negocio.nombre }}</span>
      <span class="text-[10px] text-slate-500">Presupuesto en 24h</span>
    </div>
    <a class="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-lg bg-amber-600 text-white font-bold text-xs shadow-md" href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" target="_blank" rel="noopener">
      <span class="material-symbols-outlined text-[16px]">chat</span>
      <span>WhatsApp Presupuesto</span>
    </a>
  </div>
</div>"""

    # 13. Mobile Drawer Component & Script
    drawer = make_mobile_drawer_and_script(
        template_id="craft_build",
        nav_items=[
            ("Inicio", "inicio", "home"),
            ("Servicios & Reformas", "servicios", "handyman"),
            ("Antes y Después", "antes-y-despues", "compare"),
            ("Garantías & Seguro RC", "garantias", "verified"),
            ("Proyectos & Opiniones", "opiniones", "rate_review"),
            ("Calculador Presupuesto", "solicitar-presupuesto", "calculate"),
        ],
        drawer_bg_class="bg-surface",
        drawer_border_class="border-outline-variant/40",
        link_class="hover:bg-surface-container text-on-surface hover:text-primary",
        cta_primary_class="bg-primary text-on-primary",
        cta_secondary_class="bg-surface-container hover:bg-surface-container-high",
        icon_color_class="text-primary"
    )
    html = html.replace("</body>", sticky_bar + "\n" + drawer + "\n</body>")

    out_file = os.path.join(OUT_DIR, "stitch_craft_build.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Creada plantilla {out_file}")


if __name__ == "__main__":
    print("Iniciando compilación limpia de las 5 plantillas maestras con soporte Dynamic Island & Menú...")
    build_luxury_glow()
    build_urban_edge()
    build_warm_artisan()
    build_clinical_trust()
    build_craft_build()
    print("✓ ¡Compilación finalizada con éxito!")
