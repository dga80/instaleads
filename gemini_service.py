"""
Servicio centralizado de Google Gemini con soporte para la última versión (gemini-3.8-flash)
y desescalado automático (cascade fallback) entre versiones si un modelo no responde o tiene saturación.
"""

import os
import re
import json
from typing import Tuple, Optional, Any, Dict
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# Cascada de modelos por orden de prioridad (de más reciente a versiones previas)
GEMINI_MODELS_CASCADE = [
    "gemini-3.8-flash",       # Gemini 3.8 Flash (Latest)
    "gemini-3.7-flash",       # Gemini 3.7 Flash
    "gemini-3.5-flash",       # Gemini 3.5 Flash
    "gemini-2.5-flash",       # Gemini 2.5 Flash
    "gemini-flash-latest",    # Alias oficial Gemini Flash Latest
]

def obtener_cliente_gemini():
    """Obtiene una instancia del cliente oficial google-genai si la API key está configurada."""
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not HAS_GENAI or not api_key or api_key == "tu_api_key_aqui":
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"[Aviso Gemini] Error al inicializar cliente: {e}")
        return None


def generar_con_gemini_cascade(
    prompt: str,
    cliente=None,
    temperatura: float = 0.2,
    formato_json: bool = False
) -> Tuple[Optional[str], Optional[str]]:
    """
    Ejecuta una consulta contra Gemini intentando primero la versión más reciente (gemini-3.8-flash).
    Si el modelo experimenta alta demanda (503 UNAVAILABLE), límite de cuota (429) o timeout,
    desescala ordenadamente a las siguientes versiones disponibles:
    gemini-3.8-flash -> gemini-3.7-flash -> gemini-3.5-flash -> gemini-2.5-flash -> gemini-flash-latest.
    
    Retorna (texto_respuesta, modelo_utilizado). Si todos fallan o no hay conexión, retorna (None, None).
    """
    if cliente is None:
        cliente = obtener_cliente_gemini()
    if cliente is None:
        return None, None

    config = None
    if HAS_GENAI and types and hasattr(types, "GenerateContentConfig"):
        kwargs = {"temperature": temperatura}
        if formato_json:
            kwargs["response_mime_type"] = "application/json"
        config = types.GenerateContentConfig(**kwargs)

    for modelo in GEMINI_MODELS_CASCADE:
        try:
            res = cliente.models.generate_content(
                model=modelo,
                contents=prompt,
                config=config
            )
            if res and res.text:
                return res.text.strip(), modelo
        except Exception as e:
            # Capturar errores comunes: 503 UNAVAILABLE, 429 RESOURCE_EXHAUSTED, etc.
            print(f"[Gemini Desescalado] Modelo '{modelo}' no respondió ({e}). Desescalando a la siguiente versión...")
            continue

    print("[Gemini Error Crítico] Se probaron todas las versiones de la cascada y ninguna respondió.")
    return None, None


def obtener_estado_gemini() -> Dict[str, Any]:
    """Retorna información sobre la disponibilidad de Gemini y la configuración de modelos."""
    cliente = obtener_cliente_gemini()
    configurado = cliente is not None
    return {
        "configurado": configurado,
        "modelo_primario": GEMINI_MODELS_CASCADE[0],
        "cascada": GEMINI_MODELS_CASCADE,
        "sdk_instalado": HAS_GENAI
    }
