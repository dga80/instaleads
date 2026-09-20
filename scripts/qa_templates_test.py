#!/usr/bin/env python3
"""
Test Suite de QA Exhaustivo para Plantillas y Generador de Instaleads
Verifica resiliencia contra regresiones, valores nulos, truncamientos de texto y sintaxis.
"""

import sys
import os
import json
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

ALL_TEMPLATES = [
    "stitch_luxury_glow.html",
    "stitch_urban_edge.html",
    "stitch_clinical_trust.html",
    "stitch_warm_artisan.html",
    "stitch_craft_build.html",
]

def run_qa():
    errors = []
    print("=" * 60)
    print("INICIANDO QA EXHAUSTIVO DE INSTALEADS")
    print("=" * 60)

    # 1. VERIFICACIÓN DE SINTAXIS Y CDN EN PLANTILLAS
    print("\n[TEST 1] Verificando sintaxis de scripts y CDN en plantillas...")
    for tmpl_name in ALL_TEMPLATES:
        path = TEMPLATES_DIR / tmpl_name
        if not path.exists():
            errors.append(f"Falta la plantilla: {tmpl_name}")
            continue
        content = path.read_text(encoding="utf-8")
        if "<<script" in content:
            errors.append(f"{tmpl_name}: Contiene sintaxis corrupta '<<script'")
        if "[:18]" in content:
            errors.append(f"{tmpl_name}: Contiene truncamiento agresivo de texto [:18]")
        print(f"  ✓ {tmpl_name}: Sintaxis base limpia")

    # 2. VERIFICACIÓN DE RESILIENCIA A DATOS NULOS Y VACÍOS
    print("\n[TEST 2] Verificando resiliencia ante datos nulos / vacíos (Edge Cases)...")
    edge_cases = [
        ("Contexto totalmente vacío", {"negocio": {}, "ig": {}, "design": {}, "web": {}}),
        ("Valores None explícitos", {
            "negocio": {"nombre": None, "ciudad": None, "telefono": None, "categoria": None, "whatsapp_url": None},
            "ig": {"posts": None, "avatar_url": None, "avatar": None, "biografia": None, "username": None},
            "design": {"default_theme": None, "vibe_name": None, "badges_confianza": None},
            "web": {"servicios": None, "faqs": None, "hero_title": None, "hero_subtitle": None}
        }),
        ("Lista de posts vacía", {
            "negocio": {"nombre": "Test Negocio", "ciudad": "Madrid"},
            "ig": {"posts": []},
            "design": {"default_theme": "dark"},
            "web": {"servicios": []}
        })
    ]

    for case_name, ctx in edge_cases:
        for tmpl_name in ALL_TEMPLATES:
            try:
                t = env.get_template(tmpl_name)
                rendered = t.render(**ctx)
                if not rendered or len(rendered) < 200:
                    errors.append(f"{tmpl_name} con {case_name}: HTML generado sospechosamente corto ({len(rendered)} bytes)")
            except Exception as e:
                errors.append(f"CRASH en {tmpl_name} con {case_name}: {type(e).__name__}: {e}")
        print(f"  ✓ Probado caso: {case_name} en las 5 plantillas")

    # 3. VERIFICACIÓN DE ADAPTACIÓN POR NICHO EN STITCH URBAN EDGE
    print("\n[TEST 3] Verificando lógica y adaptación de nichos en stitch_urban_edge.html...")
    urban_t = env.get_template("stitch_urban_edge.html")
    
    # Detailing
    detailing_ctx = {
        "negocio": {"nombre": "Rentat Detailing Express", "categoria": "car detailing", "ciudad": "Barcelona", "telefono": "600000000"},
        "ig": {"posts": []},
        "design": {"default_theme": "dark"},
        "web": {"servicios": [{"nombre": "Tratamiento Cerámico 9H", "descripcion": "Protección de pintura"}]}
    }
    rendered_detailing = urban_t.render(**detailing_ctx)
    if "Cerámico 9H" not in rendered_detailing:
        errors.append("stitch_urban_edge.html: No renderiza la sección de detailing para 'car detailing'")
    if "CENTRO DE DETAILING & ESTÉTICA" not in rendered_detailing:
        errors.append("stitch_urban_edge.html: El footer no se adaptó a Detailing")
    if "cuotaCalculada" in rendered_detailing and "SIMULADOR DE FINANCIACIÓN" in rendered_detailing:
        errors.append("stitch_urban_edge.html: Detailing está mostrando erróneamente el simulador de préstamos de taller")
    print("  ✓ Detailing: Adaptación correcta (tratamientos de coating & corrección activos, sin préstamos de coches)")

    # Barbería
    barber_ctx = {
        "negocio": {"nombre": "The Barber Studio", "categoria": "barberia", "ciudad": "Valencia"},
        "ig": {"posts": []},
        "design": {},
        "web": {}
    }
    rendered_barber = urban_t.render(**barber_ctx)
    if "SELECTOR DE SERVICIO & RITUAL" not in rendered_barber:
        errors.append("stitch_urban_edge.html: No renderiza el selector de barbería")
    print("  ✓ Barbería: Selector de cortes y ritual activo")

    # Tattoo
    tattoo_ctx = {
        "negocio": {"nombre": "Black Ink Tattoo", "categoria": "estudio de tatuajes", "ciudad": "Sevilla"},
        "ig": {"posts": []},
        "design": {},
        "web": {}
    }
    rendered_tattoo = urban_t.render(**tattoo_ctx)
    if "ESTIMADOR DE TATUAJE" not in rendered_tattoo:
        errors.append("stitch_urban_edge.html: No renderiza el estimador de tatuajes")
    print("  ✓ Tattoo: Estimador de tamaño y técnica activo")

    # 4. AUDITORÍA DE TEMPLATES/INDEX.HTML (UI Y DESPLEGABLE DE CAMPAÑAS)
    print("\n[TEST 4] Verificando scripts y dropdown en templates/index.html...")
    index_path = TEMPLATES_DIR / "index.html"
    index_html = index_path.read_text(encoding="utf-8")

    # Verificar que filtrarTabla está definida exactamente UNA vez
    matches = re.findall(r"function\s+filtrarTabla\s*\(", index_html)
    if len(matches) != 1:
        errors.append(f"templates/index.html: filtrarTabla() está definida {len(matches)} veces (debe ser exactamente 1)")
    else:
        print("  ✓ filtrarTabla() definida de manera unívoca (1 sola vez)")

    # Verificar que #subnav-header tiene overflow-visible
    if 'id="subnav-header"' in index_html:
        subnav_match = re.search(r'<div[^>]*id="subnav-header"[^>]*class="([^"]*)"', index_html)
        if subnav_match:
            classes = subnav_match.group(1)
            if "overflow-x-auto" in classes:
                errors.append("templates/index.html: #subnav-header aún contiene 'overflow-x-auto' que recorta dropdowns")
            if "overflow-visible" not in classes:
                errors.append("templates/index.html: #subnav-header debería tener 'overflow-visible'")
            else:
                print("  ✓ #subnav-header tiene 'overflow-visible' para permitir la apertura de dropdowns")

    # 5. VERIFICACIÓN DE ARCHIVOS JSON DE DATOS
    print("\n[TEST 5] Verificando integridad de data/leads.json y data/campaigns.json...")
    leads_file = BASE_DIR / "data" / "leads.json"
    camps_file = BASE_DIR / "data" / "campaigns.json"
    try:
        leads_data = json.loads(leads_file.read_text(encoding="utf-8"))
        print(f"  ✓ data/leads.json es un JSON válido ({len(leads_data)} leads)")
    except Exception as e:
        errors.append(f"data/leads.json está corrupto: {e}")

    try:
        camps_data = json.loads(camps_file.read_text(encoding="utf-8"))
        print(f"  ✓ data/campaigns.json es un JSON válido ({len(camps_data)} campañas)")
    except Exception as e:
        errors.append(f"data/campaigns.json está corrupto: {e}")

    # RESULTADOS
    print("\n" + "=" * 60)
    if errors:
        print(f"❌ QA FALLIDO ({len(errors)} errores encontrados):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ TODOS LOS TESTS DE QA PASARON CON ÉXITO (0 errores)")
        print("=" * 60)
        sys.exit(0)

if __name__ == "__main__":
    run_qa()
