#!/usr/bin/env python3
"""
QA Backend & API Test Suite para InstaLeads
Verifica exhaustivamente que todos los endpoints de app.py respondan correctamente.
"""

import sys
import os
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app import app, leer_leads_guardados, leer_campanas

client = TestClient(app)

def run_backend_qa():
    errors = []
    print("=" * 60)
    print("INICIANDO QA DEL BACKEND & API (FastAPI)")
    print("=" * 60)

    # 1. Healthcheck
    print("\n[TEST 1] GET /health")
    try:
        res = client.get("/health")
        assert res.status_code == 200, f"Status code: {res.status_code}"
        data = res.json()
        assert data.get("status") == "ok", f"Health status no es 'ok': {data}"
        print(f"  ✓ /health responde 200 OK (total_leads: {data.get('total_leads', 0)})")
    except Exception as e:
        errors.append(f"GET /health: {e}")

    # 2. Main Dashboard Page
    print("\n[TEST 2] GET / (Dashboard HTML)")
    try:
        res = client.get("/")
        assert res.status_code == 200, f"Status code: {res.status_code}"
        html = res.text
        assert "InstaLeads" in html, "Título InstaLeads no encontrado en HTML"
        assert 'id="btn-campaign-select"' in html, "Botón de dropdown de campañas no encontrado"
        assert 'id="campaign-dropdown-menu"' in html, "Menú de dropdown de campañas no encontrado"
        assert "filtrarTabla" in html, "Función filtrarTabla no encontrada"
        print(f"  ✓ GET / responde 200 OK ({len(html)} bytes renderizados)")
    except Exception as e:
        print(f"  ✗ GET / falló: {e}")
        errors.append(f"GET /: {e}")

    # 3. GET /leads
    print("\n[TEST 3] GET /leads")
    try:
        res = client.get("/leads")
        assert res.status_code == 200, f"Status code: {res.status_code}"
        leads = res.json()
        assert isinstance(leads, list), f"Se esperaba lista de leads, recibido: {type(leads)}"
        print(f"  ✓ GET /leads responde 200 OK ({len(leads)} leads en memoria)")
    except Exception as e:
        errors.append(f"GET /leads: {e}")

    # 4. GET /campaigns
    print("\n[TEST 4] GET /campaigns")
    try:
        res = client.get("/campaigns")
        assert res.status_code == 200, f"Status code: {res.status_code}"
        camps = res.json()
        assert isinstance(camps, list), f"Se esperaba lista de campañas, recibido: {type(camps)}"
        print(f"  ✓ GET /campaigns responde 200 OK ({len(camps)} campañas registradas)")
    except Exception as e:
        errors.append(f"GET /campaigns: {e}")

    # 5. GET /export-csv
    print("\n[TEST 5] GET /export-csv")
    try:
        res = client.get("/export-csv")
        assert res.status_code == 200, f"Status code: {res.status_code}"
        assert "text/csv" in res.headers.get("content-type", ""), f"Content-Type incorrecto: {res.headers.get('content-type')}"
        csv_text = res.text
        assert len(csv_text.splitlines()) > 1, "CSV vacío o sin filas"
        print(f"  ✓ GET /export-csv responde 200 OK con Content-Type text/csv ({len(csv_text.splitlines())} filas)")
    except Exception as e:
        errors.append(f"GET /export-csv: {e}")

    # 6. GET /campaigns/{id}/export-csv (si hay campañas)
    camps = leer_campanas()
    if camps:
        first_camp_id = camps[0].get("id")
        print(f"\n[TEST 6] GET /campaigns/{first_camp_id}/export-csv")
        try:
            res = client.get(f"/campaigns/{first_camp_id}/export-csv")
            assert res.status_code == 200, f"Status code: {res.status_code}"
            assert "text/csv" in res.headers.get("content-type", ""), "Content-Type no es text/csv"
            print(f"  ✓ Export de campaña {first_camp_id} responde 200 OK ({len(res.text.splitlines())} filas)")
        except Exception as e:
            errors.append(f"GET /campaigns/{first_camp_id}/export-csv: {e}")

    # 7. Agent Endpoints
    print("\n[TEST 7] GET /agent/suggest-outliers & /agent/memory")
    try:
        res_out = client.get("/agent/suggest-outliers")
        assert res_out.status_code == 200, f"suggest-outliers code: {res_out.status_code}"
        print("  ✓ GET /agent/suggest-outliers responde 200 OK")

        res_mem = client.get("/agent/memory")
        assert res_mem.status_code == 200, f"memory code: {res_mem.status_code}"
        print("  ✓ GET /agent/memory responde 200 OK")
    except Exception as e:
        errors.append(f"Agent endpoints: {e}")

    # 8. Lead Status & Pitch approach mutation tests
    leads = leer_leads_guardados()
    if leads:
        test_lead = leads[0]
        osm_id = test_lead.get("osm_id")
        estado_original = test_lead.get("estado", "Sin Web")
        print(f"\n[TEST 8] POST /leads/{osm_id}/status y /cambiar-enfoque-pitch")
        try:
            # Test status update
            res_st = client.post(f"/leads/{osm_id}/status", json={"estado": "Contactado"})
            assert res_st.status_code == 200, f"status update code: {res_st.status_code}"
            data_st = res_st.json()
            assert data_st.get("lead", {}).get("estado") == "Contactado", f"Estado no actualizado: {data_st}"

            # Restore original status
            client.post(f"/leads/{osm_id}/status", json={"estado": estado_original})
            print(f"  ✓ POST /leads/{osm_id}/status funciona y restaura estado correctamente")

            # Test pitch approach
            res_pitch = client.post(f"/leads/{osm_id}/cambiar-enfoque-pitch", json={"enfoque": "dolor"})
            assert res_pitch.status_code == 200, f"pitch approach code: {res_pitch.status_code}"
            assert res_pitch.json().get("status") == "ok", "Respuesta pitch no es ok"
            print(f"  ✓ POST /leads/{osm_id}/cambiar-enfoque-pitch responde 200 OK")
        except Exception as e:
            errors.append(f"Lead mutation endpoints: {e}")

    # 9. GET /demo/{osm_id} y GET /demos/{slug}
    lead_con_demo = next((l for l in leads if l.get("demo_slug")), None)
    if lead_con_demo:
        demo_osm = lead_con_demo.get("osm_id")
        demo_slug = lead_con_demo.get("demo_slug")
        print(f"\n[TEST 9] GET /demo/{demo_osm} y GET /demos/{demo_slug}")
        try:
            # 9.1 Redirección /demo/{osm_id}
            res_demo_redir = client.get(f"/demo/{demo_osm}")
            assert res_demo_redir.status_code == 200, f"GET /demo/{demo_osm} code: {res_demo_redir.status_code}"
            assert "window.location.href" in res_demo_redir.text, "Redirección JS no encontrada"
            print(f"  ✓ GET /demo/{demo_osm} devuelve script de redirección a demo")

            # 9.2 Servido directo /demos/{slug}
            res_demo_file = client.get(f"/demos/{demo_slug}")
            assert res_demo_file.status_code == 200, f"GET /demos/{demo_slug} code: {res_demo_file.status_code}"
            assert "<!DOCTYPE html>" in res_demo_file.text or "<html" in res_demo_file.text, "HTML de demo no encontrado"
            assert len(res_demo_file.text) > 1000, "Contenido de demo sospechosamente corto"
            print(f"  ✓ GET /demos/{demo_slug} sirve la web demo completa ({len(res_demo_file.text)} bytes)")
        except Exception as e:
            errors.append(f"Demo serving endpoints: {e}")

    print("\n" + "=" * 60)
    if errors:
        print(f"❌ QA BACKEND FALLIDO ({len(errors)} errores encontrados):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ TODOS LOS TESTS DE BACKEND PASARON CON ÉXITO (0 errores)")
        print("=" * 60)
        sys.exit(0)

if __name__ == "__main__":
    run_backend_qa()
