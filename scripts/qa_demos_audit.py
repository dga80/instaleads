#!/usr/bin/env python3
"""
Auditoría y Migración Automática de Demos
Inspecciona todas las carpetas en demos/ y asegura que el 100% utilicen
el sistema oficial de diseño Google Stitch, sin ninguna plantilla antigua.
"""

import sys
import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from web_generator import generar_web_comercio
from app import sincronizar_gh_pages, leer_leads_guardados

DEMOS_DIR = BASE_DIR / "demos"

def run_demos_audit(regenerate_legacy: bool = True):
    print("=" * 60)
    print("INICIANDO AUDITORÍA DE TODAS LAS DEMOS EN demos/")
    print("=" * 60)

    leads = leer_leads_guardados()
    leads_by_slug = {l.get("demo_slug"): l for l in leads if l.get("demo_slug")}

    legacy_demos = []
    modern_demos = []
    broken_demos = []

    for demo_folder in sorted(DEMOS_DIR.iterdir()):
        if not demo_folder.is_dir() or demo_folder.name.startswith("."):
            continue
        index_file = demo_folder / "index.html"
        if not index_file.exists():
            continue

        content = index_file.read_text(encoding="utf-8", errors="ignore")
        has_tailwind_config = "<script id=\"tailwind-config\">" in content
        has_corrupt_tag = "<<script" in content
        is_legacy = "landing_template" in content or ("cdn.tailwindcss.com" in content and not has_tailwind_config)

        if has_corrupt_tag:
            broken_demos.append(demo_folder.name)
        elif is_legacy:
            legacy_demos.append(demo_folder.name)
        else:
            modern_demos.append(demo_folder.name)

    print(f"\nTotal Demos Encontradas: {len(legacy_demos) + len(modern_demos) + len(broken_demos)}")
    print(f"  ✓ Demos Stitch Modernas: {len(modern_demos)}")
    print(f"  ⚠️  Demos con Plantilla Antigua (Legacy): {len(legacy_demos)}")
    print(f"  ❌ Demos con Sintaxis Rota: {len(broken_demos)}")

    if legacy_demos:
        print("\nDemos obsoletas detectadas:")
        for s in legacy_demos:
            print(f"  - {s}")

    if regenerate_legacy and (legacy_demos or broken_demos):
        to_regenerate = list(set(legacy_demos + broken_demos))
        print(f"\n[MIGRACIÓN] Regenerando {len(to_regenerate)} demos con arquitectura Stitch oficial...")
        for slug in to_regenerate:
            lead = leads_by_slug.get(slug)
            if not lead:
                # Buscar por coincidencia parcial de slug
                lead = next((l for l in leads if slug in (l.get("demo_slug") or "") or l.get("nombre", "").lower().replace(" ", "-") in slug), None)
            
            if not lead:
                # Reconstruir lead mínimo a partir del slug
                partes = slug.split("-")
                ciudad = partes[-1].capitalize() if len(partes) > 1 else "España"
                nombre = " ".join(partes[:-1]).title()
                cat = "comercio"
                if any(k in slug for k in ["moto", "motorrad", "bike", "racing"]):
                    cat = "taller de custom motos (shop:motorcycle)"
                elif any(k in slug for k in ["nail", "estetica", "glamour"]):
                    cat = "estetica y uñas"
                elif any(k in slug for k in ["tattoo", "tatuaje", "ink"]):
                    cat = "estudio de tatuajes (shop:tattoo)"
                elif any(k in slug for k in ["dental", "dentist"]):
                    cat = "clinica dental (amenity:dentist)"
                
                lead = {
                    "osm_id": f"synth_{slug}",
                    "nombre": nombre,
                    "categoria": cat,
                    "ciudad": ciudad,
                    "telefono": "",
                    "demo_slug": slug
                }

            print(f"  -> Regenerando: {slug} ({lead.get('nombre')}, {lead.get('categoria')})...")
            try:
                res = generar_web_comercio(lead)
                html = res["rendered_html"]
                dest_file = DEMOS_DIR / slug / "index.html"
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                dest_file.write_text(html, encoding="utf-8")
                sync_res = sincronizar_gh_pages(slug=slug, html_content=html, accion="guardar")
                print(f"     ✓ Regenerada con {res.get('template_file')} ({len(html)} bytes) y sincronizada en gh-pages")
            except Exception as e:
                print(f"     ✗ Error regenerando {slug}: {e}")

    # Re-auditar
    final_legacy = 0
    for demo_folder in DEMOS_DIR.iterdir():
        if not demo_folder.is_dir() or demo_folder.name.startswith("."):
            continue
        idx = demo_folder / "index.html"
        if idx.exists():
            c = idx.read_text(encoding="utf-8", errors="ignore")
            if "<script id=\"tailwind-config\">" not in c or "<<script" in c:
                final_legacy += 1

    print("\n" + "=" * 60)
    if final_legacy > 0:
        print(f"❌ AUDITORÍA FALLIDA: Aún quedan {final_legacy} demos con plantilla antigua o rota.")
        sys.exit(1)
    else:
        print("✅ AUDITORÍA DE DEMOS EXITOSA: El 100% de las demos usan el nuevo motor Google Stitch.")
        print("=" * 60)
        sys.exit(0)

if __name__ == "__main__":
    run_demos_audit(regenerate_legacy=True)
