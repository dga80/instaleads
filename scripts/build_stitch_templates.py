"""
Compilador y parametrizador Jinja2 para las 5 plantillas oficiales de Google Stitch.
Convierte los HTMLs descargados en plantillas de producción con inyección dinámica.
"""

import os
import re

STITCH_DIR = "templates/stitch"
OUT_DIR = "templates"

def build_luxury_glow():
    raw_path = os.path.join(STITCH_DIR, "luxury_glow_desktop_raw.html")
    with open(raw_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Title & Meta
    html = re.sub(
        r"<title>.*?</title>",
        r"""<title>{{ negocio.nombre }} | Belleza & Cuidado Exclusivo en {{ negocio.ciudad }}</title>
  <meta name="description" content="{{ web.subtitulo or ('Sitio web oficial y reservas para ' ~ negocio.nombre ~ ' en ' ~ negocio.ciudad) }}">""",
        html,
        flags=re.DOTALL
    )

    # Favicon
    html = re.sub(
        r'<link href="https://fonts.googleapis.com"',
        r"""<link rel="icon" type="image/jpeg" href="{{ ig.avatar_url or 'https://images.unsplash.com/photo-1560750588-73207b1ef5b8?w=96&q=80' }}">
<link href="https://fonts.googleapis.com\"""",
        html,
        count=1
    )

    # Header Logo & Title
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

    # Hero badge
    html = re.sub(
        r'✨ Atención Exclusiva • Cita Previa',
        r"""{{ web.badge_status or '✨ Atención Exclusiva • Cita Previa' }}""",
        html
    )

    # Hero Headline
    html = re.sub(
        r'<h1 class="font-display-hero text-display-hero sm:text-\[60px\] sm:leading-\[68px\] text-on-surface tracking-tight">\s*Realza tu <span class="italic font-display-hero text-primary select-none drop-shadow-sm font-normal">belleza natural</span> con técnicas de autor en Madrid\s*</h1>',
        r"""<h1 class="font-display-hero text-display-hero sm:text-[60px] sm:leading-[68px] text-on-surface tracking-tight">
            {{ web.titular or ('Realza tu <span class="italic font-display-hero text-primary select-none drop-shadow-sm font-normal">belleza natural</span> en ' ~ negocio.ciudad)|safe }}
          </h1>""",
        html
    )

    # Hero Subtitle
    html = re.sub(
        r'<p class="font-body-lg text-body-lg text-on-surface-variant max-w-xl leading-relaxed">\s*Atención individualizada en cabina privada, aparatología de última generación y formulaciones botánicas bioactivas certificadas\. Sin prisas, con rigor experto en el Barrio de Salamanca\.\s*</p>',
        r"""<p class="font-body-lg text-body-lg text-on-surface-variant max-w-xl leading-relaxed">
            {{ web.subtitulo or ('Atención individualizada en cabina privada, cosmecéutica de autor y las técnicas más avanzadas de belleza en ' ~ negocio.ciudad ~ '.') }}
          </p>""",
        html
    )

    # Hero Location Stamp
    html = re.sub(
        r'<span class="font-label-caps text-label-caps uppercase text-on-surface tracking-wider">Serrano 48, Salamanca</span>',
        r"""<span class="font-label-caps text-label-caps uppercase text-on-surface tracking-wider">{{ negocio.direccion or negocio.ciudad }}</span>""",
        html
    )

    # Hero Main Image
    html = re.sub(
        r'<img class="w-full h-full object-cover" data-alt="[^"]*" src="https://lh3\.googleusercontent\.com/aida-public/AB6AXuCs-nh5VvzqIasB2CWKP9H6iZpUtFSeYkorHL7CQ43MP7CukR1o4tWwTNwqCbZDWI1jc_I0LJqoOZM8q4WmYwcpxGLN5LUPXZLp54RL50bDSE4EfwrtaAcbQqbovjxiZEa8nZGNVmXfKbzdhgCEZXjLWBLowW_RnK5b9ddQfqtn08ox3ZmP0ULY71zSvpVwtwFS-ZYBmHZq2sULjc_gGvpb1Dh4JoJuao3BwSZJ-ru50SvgaxzJryC7YQ"/>',
        r"""<img class="w-full h-full object-cover" alt="{{ negocio.nombre }}" src="{{ ig.posts[0].image_url if ig.posts and ig.posts[0].image_url else 'https://images.unsplash.com/photo-1560750588-73207b1ef5b8?auto=format&fit=crop&w=1200&q=80' }}"/>""",
        html
    )

    # Hero Secondary Overlap Image
    html = re.sub(
        r'<img alt="Detalle de piel radiante y tratamiento facial de alta cosmética en Élixir Studio" class="w-full h-full object-cover" src="https://lh3\.googleusercontent\.com/aida-public/AB6AXuC6FgXhlX5LZqPgohplJutgZ_xf-mLLI-E4aqlgheCgmhuxGOphM3EoHO3yhA82qNxg8O6sU4ZIljwQNmuQkv3rQWhzVdMPC1B728Q8gLkLHrgYVNZcOI-BhU71_LnARtqNUnryFFVy0aI6jxg1FQ7DizTMP8VQ-tVIIcQ3sSJThCOFselvmRxJmQMJxmZtSQShShlIhqnXBeDM4fO5pxth8WERyjaVCvwpobSXexJ62pnftOM3WiY4bA"/>',
        r"""<img alt="{{ negocio.nombre }} glow" class="w-full h-full object-cover" src="{{ ig.posts[1].image_url if ig.posts and ig.posts|length > 1 and ig.posts[1].image_url else 'https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=600&q=80' }}"/>""",
        html
    )

    # Services Header
    html = re.sub(
        r'Carta de Terapias <span class="italic font-display-hero text-primary font-normal">• Élixir Studio</span>',
        r"""Carta de Servicios <span class="italic font-display-hero text-primary font-normal">• {{ negocio.nombre }}</span>""",
        html
    )

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

    # Gallery Header Instagram Link
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

    # Dynamic 4-item visual gallery loop
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

    # Footer replacements
    html = re.sub(
        r'Élixir Studio &amp; Aesthetics Logo',
        r"""{{ negocio.nombre }} Logo""",
        html
    )
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

    out_file = os.path.join(OUT_DIR, "stitch_luxury_glow.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Creada plantilla {out_file}")


def build_urban_edge():
    raw_path = os.path.join(STITCH_DIR, "urban_edge_desktop_raw.html")
    with open(raw_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Title & Meta
    html = re.sub(
        r"<title>.*?</title>",
        r"""<title>{{ negocio.nombre }} | Taller & Custom Studio en {{ negocio.ciudad }}</title>
  <meta name="description" content="{{ web.subtitulo or ('Sitio web oficial y presupuestos para ' ~ negocio.nombre ~ ' en ' ~ negocio.ciudad) }}">""",
        html,
        flags=re.DOTALL
    )

    # Favicon
    html = re.sub(
        r'<link href="https://fonts.googleapis.com"',
        r"""<link rel="icon" type="image/jpeg" href="{{ ig.avatar_url or 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=96&q=80' }}">
<link href="https://fonts.googleapis.com\"""",
        html,
        count=1
    )

    # Logo & Moniker
    html = re.sub(
        r'<span class="font-headline-md text-body-md font-bold tracking-tight text-on-surface uppercase">APEX CUSTOMS</span>',
        r"""<span class="font-headline-md text-body-md font-bold tracking-tight text-on-surface uppercase">{{ negocio.nombre }}</span>""",
        html
    )
    html = re.sub(
        r'<span class="font-label-sm text-label-sm tracking-widest text-primary font-semibold -mt-1">// ATELIER</span>',
        r"""<span class="font-label-sm text-label-sm tracking-widest text-primary font-semibold -mt-1">// {{ negocio.categoria_clean|upper }}</span>""",
        html
    )

    # Status Dot
    html = re.sub(
        r'BOX ABIERTO / CITAS DISPONIBLES',
        r"""{{ web.badge_status or 'BOX ABIERTO / CITAS DISPONIBLES' }}""",
        html
    )

    # Hero Badge
    html = re.sub(
        r'ESPECIALISTAS CERTIFICADOS EN MADRID // ATELIER 01',
        r"""ESPECIALISTAS CERTIFICADOS EN {{ negocio.ciudad|upper }} // ATELIER""",
        html
    )

    # Hero Headline
    html = re.sub(
        r'<h1 class="font-headline-xl text-headline-xl text-on-surface tracking-tight uppercase leading-\[1\.05\] mt-space-xs">.*?</h1>',
        r"""<h1 class="font-headline-xl text-headline-xl text-on-surface tracking-tight uppercase leading-[1.05] mt-space-xs">
          {{ web.titular or ('Trabajo puro.<br/><span class="text-transparent bg-clip-text bg-gradient-to-r from-on-surface via-on-surface-variant to-primary">Sin rodeos.</span><br/>Calidad de máximo nivel.')|safe }}
        </h1>""",
        html,
        flags=re.DOTALL
    )

    # Hero Subtitle
    html = re.sub(
        r'<p class="font-body-lg text-body-lg text-secondary max-w-2xl mt-space-xs">.*?</p>',
        r"""<p class="font-body-lg text-body-lg text-secondary max-w-2xl mt-space-xs">
          {{ web.subtitulo or ('Precisión, actitud y acabados sin concesiones. Proyectos y servicios a medida con garantía total en ' ~ negocio.ciudad ~ '.') }}
        </p>""",
        html,
        flags=re.DOTALL
    )

    # CTAs WhatsApp & Instagram
    html = re.sub(
        r'href="#contacto"',
        r"""href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" target="_blank" rel="noopener\"""",
        html
    )
    html = re.sub(
        r'href="https://instagram\.com"',
        r"""href="{{ negocio.instagram_url }}" target="_blank" rel="noopener\"""",
        html
    )

    # Hero Right Image
    html = re.sub(
        r'<img class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" data-alt="[^"]*" src="https://lh3\.googleusercontent\.com/aida-public/AB6AXuBDs_I_ka9Zy1zK8v7eKUsioHeC7FO1Y9vnIvGkC8aQqHRIK9-oK7lZNIhnufsxEr0NNcOIDuDR0jRHOIiaMNkg3eWJkbXO8R_Za6IQZYPpYvUQ1Q4zDhd1duIVxeCJNeAREutlaP-H5dOne3iY7Iirl4hgI_dJ0Kly7di-4dfk8DBoTLjYLh0eX8TxUrgoLwfG7RRmVwH4K-N9B7R1eAhiPkxD2suEr7WEGuSjHGPhIZ_n5EFMHZYP"/>',
        r"""<img class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" alt="{{ negocio.nombre }}" src="{{ ig.posts[0].image_url if ig.posts and ig.posts[0].image_url else 'https://images.unsplash.com/photo-1558981806-ec527fa84c39?auto=format&fit=crop&w=1200&q=80' }}"/>""",
        html
    )

    # Hero Project Vanguard Tag
    html = re.sub(
        r'PROYECTO // VANGUARD',
        r"""{{ negocio.nombre|upper }}""",
        html
    )

    # Replace Portfolio Grid with dynamic loop from ig.posts
    portfolio_replacement = """<!-- Dynamic Portfolio Cards from Instagram -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-gutter">
  {% for post in ig.posts[:3] %}
  <div class="rounded-lg bg-surface-container border border-surface-container-high overflow-hidden hover:border-primary transition-all duration-300 group flex flex-col justify-between shadow-sm hover:shadow-[0_0_24px_rgba(249,115,22,0.18)]">
    <div>
      <div class="relative w-full h-72 bg-surface-container-lowest overflow-hidden">
        <img class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" src="{{ post.image_url }}" alt="{{ post.caption[:30] if post.caption else negocio.nombre }}" />
        <div class="absolute top-space-sm left-space-sm flex items-center gap-1.5">
          <span class="px-2 py-0.5 rounded bg-surface-container-lowest/90 backdrop-blur font-label-sm text-label-sm text-on-surface font-mono font-bold">PROJECT // 0{{ loop.index }}</span>
        </div>
        <div class="absolute top-space-sm right-space-sm">
          <span class="px-2 py-0.5 rounded bg-primary-container text-on-primary-container font-label-sm text-label-sm font-mono font-bold">VERIFICADO</span>
        </div>
      </div>
      <div class="p-space-lg flex flex-col gap-space-xs">
        <div class="flex items-center justify-between">
          <h3 class="font-headline-md text-headline-md uppercase text-on-surface tracking-tight">{{ post.caption.split('\\n')[0][:25] if post.caption else ('Trabajo ' ~ loop.index) }}</h3>
          <a href="{{ negocio.instagram_url }}" target="_blank" rel="noopener"><span class="material-symbols-outlined text-outline group-hover:text-primary transition-colors">arrow_outward</span></a>
        </div>
        <p class="font-body-sm text-body-sm text-secondary mt-1 line-clamp-2">
          {{ post.caption or ('Acabado profesional realizado en ' ~ negocio.ciudad ~ ' con materiales y técnicas de alta precisión.') }}
        </p>
      </div>
    </div>
    <div class="px-space-lg pb-space-lg pt-space-xs border-t border-surface-container-high/60 flex flex-wrap gap-1.5">
      <span class="px-2 py-0.5 rounded bg-surface-container-lowest text-outline font-label-sm text-[11px] font-mono">100% Custom</span>
      <span class="px-2 py-0.5 rounded bg-surface-container-lowest text-primary font-label-sm text-[11px] font-mono">Garantizado</span>
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

    # Replace Pricing Matrix with web.servicios
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

    # Footer replacements
    html = re.sub(
        r'APEX CUSTOMS HQ',
        r"""{{ negocio.nombre|upper }} HQ""",
        html
    )
    html = re.sub(
        r'Calle de la Mecánica, 14, Nave 3',
        r"""{{ negocio.direccion or negocio.ciudad }}""",
        html
    )
    html = re.sub(
        r'28022 Madrid, España',
        r"""{{ negocio.ciudad }}, España""",
        html
    )

    # Add mobile bottom sticky dock
    sticky_dock = """<!-- Fixed Mobile Bottom Action Dock -->
<div class="fixed bottom-0 inset-x-0 z-50 md:hidden p-3 bg-surface-container-lowest/95 backdrop-blur-xl border-t border-surface-container-high shadow-2xl">
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
</div>
</body>"""
    html = re.sub(r'</body>', sticky_dock, html)

    out_file = os.path.join(OUT_DIR, "stitch_urban_edge.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Creada plantilla {out_file}")


def build_warm_artisan():
    raw_path = os.path.join(STITCH_DIR, "warm_artisan_desktop_raw.html")
    with open(raw_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Title & Meta
    html = re.sub(
        r"<title>.*?</title>",
        r"""<title>{{ negocio.nombre }} | Obrador & Café de Especialidad en {{ negocio.ciudad }}</title>
  <meta name="description" content="{{ web.subtitulo or ('Sitio web oficial y carta para ' ~ negocio.nombre ~ ' en ' ~ negocio.ciudad) }}">""",
        html,
        flags=re.DOTALL
    )

    # Favicon
    html = re.sub(
        r'<link href="https://fonts.googleapis.com"',
        r"""<link rel="icon" type="image/jpeg" href="{{ ig.avatar_url or 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=96&q=80' }}">
<link href="https://fonts.googleapis.com\"""",
        html,
        count=1
    )

    # Header Logo & Title
    html = re.sub(
        r'<img alt="Origen &amp; Miga Logo"[^>]+>',
        r"""<img alt="{{ negocio.nombre }}" class="h-9 w-9 rounded-full object-cover border border-primary/30" src="{{ ig.avatar_url or 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=120&q=80' }}"/>""",
        html
    )
    html = re.sub(
        r'<span class="font-headline-sm text-headline-sm text-on-surface leading-tight">Origen &amp; Miga</span>',
        r"""<span class="font-headline-sm text-headline-sm text-on-surface leading-tight">{{ negocio.nombre }}</span>""",
        html
    )
    html = re.sub(
        r'<span class="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider">Café de Especialidad &amp; Obrador</span>',
        r"""<span class="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider">{{ negocio.categoria_clean }}</span>""",
        html
    )

    # Hero Badge
    html = re.sub(
        r'🥐 Elaborado a Diario • Café de Especialidad',
        r"""{{ web.badge_status or '🥐 Elaborado a Diario • Café de Especialidad' }}""",
        html
    )

    # Hero Headline
    html = re.sub(
        r'<h1 class="font-display-hero text-headline-xl lg:text-display-hero text-on-surface tracking-tight leading-tight">\s*Tu rincón favorito para disfrutar sin prisas en Chamberí\s*</h1>',
        r"""<h1 class="font-display-hero text-headline-xl lg:text-display-hero text-on-surface tracking-tight leading-tight">
            {{ web.titular or ('Tu rincón favorito para disfrutar sin prisas en ' ~ negocio.ciudad) }}
          </h1>""",
        html
    )

    # Hero Subtitle
    html = re.sub(
        r'<p class="font-body-lg text-body-lg text-on-surface-variant max-w-xl leading-relaxed">\s*Elaborado a diario con ingredientes reales y pasión artesana\. Masa madre de fermentación lenta de 48h y café de origen tostado en pequeños lotes semanales\.\s*</p>',
        r"""<p class="font-body-lg text-body-lg text-on-surface-variant max-w-xl leading-relaxed">
            {{ web.subtitulo or ('Elaborado a diario con ingredientes reales y pasión artesana en ' ~ negocio.ciudad ~ '. Producto de proximidad y cuidado en cada detalle.') }}
          </p>""",
        html
    )

    # Hero Action Links
    html = re.sub(
        r'href="#carta"',
        r'href="#carta-digital"',
        html
    )
    html = re.sub(
        r'href="#ubicacion"',
        r"""href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" target="_blank" rel="noopener\"""",
        html
    )

    # Hero Image
    html = re.sub(
        r'<img alt="Obrador de Origen y Miga en pleno servicio" class="w-full h-full object-cover" src="https://lh3\.googleusercontent\.com/aida-public/AB6AXuBZOZSW9Cnz5YYr2B_yvrq4q2u6nMaZziqxJ1YedYxf1Fy8eMIvEcqb0bRNx14ilQR2Lblgh4e2gVg9qVqxROWYUZNi8xG1pYaXn0ORfJKCg4oA_YWRSvvQPbN0-6lHIYYAZ-EqxgFo-p622naSu7HfxurYtn2-Xy2FY2s3_ZMaZ30KFxK-3XM9QRbsjmzWiLJYd3RXYZlTYcPtdYYlvhkWAvAENx9cxf0Js0AK6cBoik7kXitPr4CB"/>',
        r"""<img alt="{{ negocio.nombre }}" class="w-full h-full object-cover" src="{{ ig.posts[0].image_url if ig.posts and ig.posts[0].image_url else 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1200&q=80' }}"/>""",
        html
    )

    # Menu section dynamic replacement
    menu_replacement = """<!-- Dynamic Tabbed Digital Menu from Gemini & Instagram -->
<div id="carta-digital" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-gutter">
  {% for s in web.servicios %}
  <div class="bg-surface-container-lowest p-6 rounded-2xl border border-primary/20 shadow-sm hover:shadow-md transition-all flex flex-col justify-between group">
    <div>
      {% if s.imagen %}
      <div class="w-full h-44 rounded-xl overflow-hidden mb-4 border border-primary/10">
        <img class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" src="{{ s.imagen }}" alt="{{ s.nombre }}" />
      </div>
      {% endif %}
      <div class="flex items-center justify-between gap-2 mb-2">
        <span class="font-headline-sm text-lg text-on-surface font-semibold">{{ s.nombre }}</span>
        <span class="font-headline-sm text-primary font-bold">{{ s.precio_o_duracion or "Consultar" }}</span>
      </div>
      <p class="font-body-sm text-on-surface-variant leading-relaxed mb-4">
        {{ s.descripcion }}
      </p>
    </div>
    <div class="pt-4 border-t border-outline-variant/30 flex items-center justify-between">
      <span class="font-label-caps text-[11px] text-secondary uppercase tracking-wider">Elaboración Artesanal</span>
      <a class="text-primary hover:text-secondary font-label-lg text-sm font-semibold inline-flex items-center gap-1" href="{{ negocio.whatsapp_url or ('https://wa.me/' ~ negocio.telefono) }}" target="_blank" rel="noopener">
        <span>Pedir / Reservar</span>
        <span class="material-symbols-outlined text-[16px]">arrow_forward</span>
      </a>
    </div>
  </div>
  {% endfor %}
</div>"""

    html = re.sub(
        r'<!-- TABBED DIGITAL MENU -->.*?<!-- COMMUNITY & ROASTERY VISUAL MOMENTS -->',
        '<!-- TABBED DIGITAL MENU -->\n<section class="w-full py-16 bg-surface">\n<div class="max-w-[1360px] mx-auto px-margin-mobile md:px-margin-tablet lg:px-margin">\n<div class="mb-10">\n<span class="font-label-caps text-label-caps text-secondary uppercase tracking-widest block mb-1">Carta Digital &amp; Especialidades</span>\n<h2 class="font-headline-xl text-headline-xl text-on-surface">Selección Artesanal de Temporada</h2>\n</div>\n' + menu_replacement + '\n</div>\n</section>\n<!-- COMMUNITY & ROASTERY VISUAL MOMENTS -->',
        html,
        flags=re.DOTALL
    )

    # Replace visual moments with ig.posts
    visual_replacement = """<!-- Curated Moments from Instagram -->
<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
  {% for post in ig.posts[:4] %}
  <div class="rounded-2xl overflow-hidden aspect-square relative group shadow-sm">
    <img src="{{ post.image_url }}" alt="{{ post.caption[:30] if post.caption else negocio.nombre }}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
    <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity p-3 flex flex-col justify-end">
      <p class="text-white text-xs line-clamp-2">{{ post.caption or negocio.nombre }}</p>
    </div>
  </div>
  {% endfor %}
</div>"""

    html = re.sub(
        r'<!-- 4-Item Grid of Community / Atmosphere -->.*?<!-- FIND US & RESERVATIONS -->',
        visual_replacement + '\n</div>\n</section>\n<!-- FIND US & RESERVATIONS -->',
        html,
        flags=re.DOTALL
    )

    # Address & Location
    html = re.sub(
        r'Calle de Luchana, 28',
        r"""{{ negocio.direccion or negocio.ciudad }}""",
        html
    )
    html = re.sub(
        r'28010 Chamberí, Madrid',
        r"""{{ negocio.ciudad }}, España""",
        html
    )
    html = re.sub(
        r'© 2025 Origen &amp; Miga Bakery Co\. Todos los derechos reservados\.',
        r"""© 2025 {{ negocio.nombre }} • {{ negocio.ciudad }}. Todos los derechos reservados.""",
        html
    )

    # Mobile sticky bar
    sticky_bar = """<!-- Fixed Mobile Bottom Bar -->
<div class="fixed bottom-0 inset-x-0 z-50 md:hidden p-3 bg-surface/95 backdrop-blur-md border-t border-primary/20 shadow-lg">
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
</div>
</body>"""
    html = re.sub(r'</body>', sticky_bar, html)

    out_file = os.path.join(OUT_DIR, "stitch_warm_artisan.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Creada plantilla {out_file}")


def build_clinical_trust():
    raw_path = os.path.join(STITCH_DIR, "clinical_trust_desktop_raw.html")
    with open(raw_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Title & Meta
    html = re.sub(
        r"<title>.*?</title>",
        r"""<title>{{ negocio.nombre }} | Clínica & Salud en {{ negocio.ciudad }}</title>
  <meta name="description" content="{{ web.subtitulo or ('Sitio web oficial y citas para ' ~ negocio.nombre ~ ' en ' ~ negocio.ciudad) }}">""",
        html,
        flags=re.DOTALL
    )

    # Favicon
    html = re.sub(
        r'<link href="https://fonts.googleapis.com"',
        r"""<link rel="icon" type="image/jpeg" href="{{ ig.avatar_url or 'https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=96&q=80' }}">
<link href="https://fonts.googleapis.com\"""",
        html,
        count=1
    )

    # Brand Title
    html = re.sub(
        r'SannaMed',
        r"""{{ negocio.nombre }}""",
        html
    )

    # Hero Badge
    html = re.sub(
        r'🩺 1ª CITA &amp; DIAGNÓSTICO DIGITAL DISPONIBLE',
        r"""{{ web.badge_status or '🩺 1ª CITA & DIAGNÓSTICO DIGITAL DISPONIBLE' }}""",
        html
    )

    # Hero Headline
    html = re.sub(
        r'<h1 class="font-display text-display tracking-tight text-on-surface font-extrabold max-w-2xl leading-\[1\.1\]">.*?</h1>',
        r"""<h1 class="font-display text-display tracking-tight text-on-surface font-extrabold max-w-2xl leading-[1.1]">
          {{ web.titular or ('Cuidamos de tu sonrisa y salud con la tecnología más avanzada en ' ~ negocio.ciudad) }}
        </h1>""",
        html,
        flags=re.DOTALL
    )

    # Hero Subtitle
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

    # Address
    html = re.sub(
        r'Paseo de la Castellana, 120, 1º B',
        r"""{{ negocio.direccion or negocio.ciudad }}""",
        html
    )
    html = re.sub(
        r'28046 Madrid, España',
        r"""{{ negocio.ciudad }}, España""",
        html
    )
    html = re.sub(
        r'© 2025 SannaMed Dental &amp; Salud Integral S\.L\.',
        r"""© 2025 {{ negocio.nombre }} • {{ negocio.ciudad }}.""",
        html
    )

    # Sticky mobile action bar
    sticky_bar = """<!-- Sticky Mobile Bar -->
<div class="fixed bottom-0 inset-x-0 z-50 lg:hidden p-3 bg-white/95 backdrop-blur-lg border-t border-primary-container/20 shadow-lg">
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
</div>
</body>"""
    html = re.sub(r'</body>', sticky_bar, html)

    out_file = os.path.join(OUT_DIR, "stitch_clinical_trust.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Creada plantilla {out_file}")


def build_craft_build():
    raw_path = os.path.join(STITCH_DIR, "craft_build_desktop_raw.html")
    with open(raw_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Title & Meta
    html = re.sub(
        r"<title>.*?</title>",
        r"""<title>{{ negocio.nombre }} | Reformas & Construcción en {{ negocio.ciudad }}</title>
  <meta name="description" content="{{ web.subtitulo or ('Presupuesto cerrado y reformas garantizadas con ' ~ negocio.nombre ~ ' en ' ~ negocio.ciudad) }}">""",
        html,
        flags=re.DOTALL
    )

    # Favicon
    html = re.sub(
        r'<link href="https://fonts.googleapis.com"',
        r"""<link rel="icon" type="image/jpeg" href="{{ ig.avatar_url or 'https://images.unsplash.com/photo-1503387762-592deb58ef4e?w=96&q=80' }}">
<link href="https://fonts.googleapis.com\"""",
        html,
        count=1
    )

    # Brand Title
    html = re.sub(
        r'VÉRTICE',
        r"""{{ negocio.nombre|upper }}""",
        html
    )
    html = re.sub(
        r'ARQ &amp; REFORMAS',
        r"""{{ negocio.categoria_clean|upper }}""",
        html
    )

    # Hero Badge
    html = re.sub(
        r'🛡️ PRESUPUESTO CERRADO POR ESCRITO • GARANTÍA 2 AÑOS',
        r"""{{ web.badge_status or '🛡️ PRESUPUESTO CERRADO POR ESCRITO • GARANTÍA 2 AÑOS' }}""",
        html
    )

    # Hero Headline
    html = re.sub(
        r'<h1 class="font-display-hero text-display-hero tracking-tight text-on-surface font-extrabold leading-\[1\.08\]">.*?</h1>',
        r"""<h1 class="font-display-hero text-display-hero tracking-tight text-on-surface font-extrabold leading-[1.08]">
          {{ web.titular or ('Reformas e instalaciones con acabado impecable en ' ~ negocio.ciudad) }}
        </h1>""",
        html,
        flags=re.DOTALL
    )

    # Hero Subtitle
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

    # Hero Images (Before / After preview)
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

    # Dynamic Services / Work Packages
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
        r'<!-- 4 MODULAR WORK PACKAGES CARDS -->.*?<!-- POR QUÉ TRABAJAR CON NOSOTROS',
        services_replacement + '\n</div>\n</section>\n<!-- POR QUÉ TRABAJAR CON NOSOTROS',
        html,
        flags=re.DOTALL
    )

    # Address
    html = re.sub(
        r'Paseo de la Habana, 42, Chamartín',
        r"""{{ negocio.direccion or negocio.ciudad }}""",
        html
    )
    html = re.sub(
        r'28036 Madrid, España',
        r"""{{ negocio.ciudad }}, España""",
        html
    )
    html = re.sub(
        r'© 2025 Vértice Arq &amp; Reformas S\.L\.',
        r"""© 2025 {{ negocio.nombre }} • {{ negocio.ciudad }}.""",
        html
    )

    # Mobile sticky bar
    sticky_bar = """<!-- Sticky Mobile Lead Bar -->
<div class="fixed bottom-0 inset-x-0 z-50 md:hidden p-3 bg-white/95 backdrop-blur-md border-t border-slate-200 shadow-xl">
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
</div>
</body>"""
    html = re.sub(r'</body>', sticky_bar, html)

    out_file = os.path.join(OUT_DIR, "stitch_craft_build.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ Creada plantilla {out_file}")


if __name__ == "__main__":
    print("Iniciando compilación limpia de las 5 plantillas maestras...")
    build_luxury_glow()
    build_urban_edge()
    build_warm_artisan()
    build_clinical_trust()
    build_craft_build()
    print("✓ ¡Compilación finalizada con éxito!")
