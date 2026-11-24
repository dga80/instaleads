/**
 * Vercel Edge Function — Proxy blindat per a l'Assistent Legal d'ARS Advocats i Assessors
 * Endpoint automàtic a Vercel: /api/chat
 * Variable d'entorn requerida a Vercel: GEMINI_API_KEY
 * Variable opcional: GEMINI_MODEL
 */

export const config = {
  runtime: "edge",
};

const ALLOWED_ORIGINS = [
  "https://dga80.github.io",
  "https://www.arsadvocats.com",
  "https://arsadvocats.com",
];

const DEFAULT_MODELS = [
  "gemini-flash-lite-latest",
  "gemini-flash-latest",
  "gemini-3.8-flash-lite",
  "gemini-3.8-flash",
];

const HEADER_TIMEOUT_MS = 6500;

const SAFETY_SETTINGS = [
  { category: "HARM_CATEGORY_HARASSMENT", threshold: "BLOCK_ONLY_HIGH" },
  { category: "HARM_CATEGORY_HATE_SPEECH", threshold: "BLOCK_ONLY_HIGH" },
  { category: "HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold: "BLOCK_ONLY_HIGH" },
  { category: "HARM_CATEGORY_DANGEROUS_CONTENT", threshold: "BLOCK_ONLY_HIGH" },
];

const SYSTEM_PROMPT = `Ets l'Assistent Virtual de benvinguda i triatge d'ARS Advocats i Assessors, una firma legal situada al centre de Granollers (Barcelona).

REGLA PRIORITÀRIA D'IDIOMA (OBLIGATÒRIA):
- Detecta l'idioma de l'ÚLTIM missatge de l'usuari i respon SEMPRE 100% en aquell mateix idioma.
- Si l'usuari escriu en castellà (espanyol), respon ÍNTEGRAMENT en castellà encara que la web estigui en català.
- Si l'usuari escriu en català, respon en català.
- Si l'usuari escriu en anglès, respon en anglès.
- Només utilitza l'idioma de suport indicat al final si el missatge de l'usuari és d'1 sola paraula ambigua (p. ex. "hola" o "ok").

DADES VERIFICADES DEL DESPATX:
- Nom: ARS Advocats i Assessors
- Adreça: Carrer de Barcelona, 7 - 1r pis, 08401 Granollers (Barcelona)
- Telèfon: 938 795 876 · WhatsApp: +34 668 556 252 · Correu: info@arsadvocats.com
- Horari: Dilluns a divendres de 09:00 a 14:00 i de 16:00 a 19:30.
- Àmbit d'actuació: Granollers, Vallès Oriental, Barcelona i Catalunya.

ESPECIALITATS DEL DESPATX (15 àrees):
1. Dret Matrimonial i de Família (divorcis de mutu acord o contenciosos, custòdies, pensions d'aliments, convenis reguladors, modificació de mesures).
2. Successions, Testaments i Herències (acceptacions d'herències, declaracions d'hereus, legítima, impugnació de testaments).
3. Desnonaments i Arrendaments (impagament de rendes, expiració de contracte, contractes d'habitatge i local).
4. Obligacions i Contractes (redacció, incompliments, vicis ocults, danys i perjudicis).
5. Reclamacions de Quantitat (impagats, monitoris, execucions i embargaments).
6. Comunitats de Propietaris (propietat horitzontal, impugnació d'acords, veïns morosos, defectes constructius).
7. Dret Bancari i Clàusules Abusives (clàusula sòl, despeses hipotecàries, targetes revolving, execucions hipotecàries).
8. Dret Penal i Defensa Judicial (assistència 24h al detingut en comissaria i jutjat de guàrdia, delictes lleus, menys greus i greus, amenaces, denúncies, recursos).
9. Violència de Gènere (atenció urgent i sensible, ordres de protecció i allunyament, mesures cautelars).
10. Dret Econòmic i Compliance (delictes societaris, responsabilitat penal corporativa, estafes).
11. Accidents de Trànsit (indemnitzacions, barems mèdics, asseguradores, seqüeles).
12. Dret Laboral i Seguretat Social (acomiadaments, reclamació de salaris, sancions, CMAC, ERO/ERTO).
13. Incapacitat Laboral (incapacitat permanent parcial, total, absoluta, gran invalidesa, impugnació d'altes de l'INSS i mútues).
14. Societats Mercantils (constitució, pactes de socis, fusions, ampliacions de capital, conflictes societaris).
15. Concursos i Llei de Segona Oportunitat (exoneració de deutes per a particulars, autònoms i pimes).

EQUIP:
- Roger Subirana (Soci Director): Dret Civil, Família i Penal.
- Alex Reus (Soci Director): Dret Mercantil/Societari i Dret Laboral/Seguretat Social.
- Anna Camps (Advocada Col·laboradora): Dret Immobiliari, Civil i Penal.
- Dana Costa Berenguer (Assistent Legal): Dret Penal i Processal.

REGLES ESTRICTES DE COMPORTAMENT I DEONTOLOGIA:
1. To: proper, seriós, empàtic i clar. Respostes BREUS (màxim 2–4 frases, unes 60–95 paraules).
2. NO donis assessorament jurídic vinculant, NO calculis terminis legals exactes com a garantia ni citis articles concrets de memòria. Quan donis una orientació general, recorda breument que cal la revisió d'un advocat del despatx.
3. Si la consulta entra en una especialitat d'ARS:
   - Confirma que el despatx porta aquesta matèria (i si escau, menciona l'àrea o l'advocat responsable).
   - Fes 1 o 2 preguntes breus de triatge (per exemple: si hi ha data de judici o termini proper, si és particular o empresa, o la localitat).
   - Recorda breument (sense repetir el número a cada missatge si ja l'has donat) que pot fer servir els botons inferiors per passar el resum al formulari o continuar per WhatsApp.
4. Si la consulta NO entra dins les especialitats (p. ex. estrangeria pura, fiscalitat internacional complexa): digues-ho amb educació i honestedat, sense inventar serveis.
5. Si és una urgència penal (detenció, comissaria, violència de gènere, amenaces greus): prioritza donar el telèfon directe 938 795 876 i el WhatsApp +34 668 556 252 de seguida.
6. No demanis DNI, dades bancàries ni informació altament confidencial dins el xat.`;

function getCorsHeaders(request) {
  const origin = request.headers.get("Origin") || "";
  const isAllowed =
    !origin ||
    ALLOWED_ORIGINS.includes(origin) ||
    origin.endsWith(".vercel.app") ||
    origin.startsWith("http://localhost:") ||
    origin.startsWith("http://127.0.0.1:");

  return {
    "Access-Control-Allow-Origin": isAllowed && origin ? origin : ALLOWED_ORIGINS[0],
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Expose-Headers": "X-ARS-Model",
    "Vary": "Origin",
  };
}

function normalizeContents(rawMessages) {
  const cleaned = [];
  for (const m of rawMessages.slice(-16)) {
    const text = String(m?.text || "").trim().slice(0, 1200);
    if (!text) continue;
    const role = m?.role === "assistant" ? "model" : "user";
    if (cleaned.length === 0 && role === "model") continue;
    if (cleaned.length > 0 && cleaned[cleaned.length - 1].role === role) {
      cleaned[cleaned.length - 1].parts[0].text += "\n" + text;
    } else {
      cleaned.push({ role, parts: [{ text }] });
    }
  }
  return cleaned;
}

async function fetchWithHeaderTimeout(url, options, timeoutMs) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(timer);
    return res;
  } catch (err) {
    clearTimeout(timer);
    throw err;
  }
}

async function discoverFlashModel(apiKey) {
  try {
    const res = await fetchWithHeaderTimeout(
      "https://generativelanguage.googleapis.com/v1beta/models",
      { headers: { "x-goog-api-key": apiKey } },
      4500
    );
    if (!res.ok) return null;
    const data = await res.json();
    const candidates = (data.models || [])
      .filter(
        (m) =>
          m.name?.includes("flash") &&
          !m.name?.includes("tts") &&
          !m.name?.includes("image") &&
          Array.isArray(m.supportedGenerationMethods) &&
          m.supportedGenerationMethods.includes("generateContent")
      )
      .map((m) => m.name.replace(/^models\//, ""))
      .sort()
      .reverse();
    return candidates[0] || null;
  } catch {
    return null;
  }
}

export default async function handler(request) {
  const cors = getCorsHeaders(request);
  const apiKey = process.env.GEMINI_API_KEY;
  const preferredModel = process.env.GEMINI_MODEL;

  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: cors });
  }

  if (request.method === "GET") {
    return new Response(
      JSON.stringify({
        ok: true,
        service: "ars-advocats-chat-vercel",
        configured: Boolean(apiKey),
      }),
      {
        status: 200,
        headers: { ...cors, "Content-Type": "application/json; charset=utf-8" },
      }
    );
  }

  if (request.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { ...cors, "Content-Type": "application/json" },
    });
  }

  if (!apiKey) {
    return new Response(
      JSON.stringify({ error: "GEMINI_API_KEY no configurada a Vercel Environment Variables" }),
      {
        status: 500,
        headers: { ...cors, "Content-Type": "application/json" },
      }
    );
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: "JSON invàlid" }), {
      status: 400,
      headers: { ...cors, "Content-Type": "application/json" },
    });
  }

  const rawMessages = Array.isArray(body.messages) ? body.messages : [];
  const lang = ["ca", "es", "en"].includes(body.lang) ? body.lang : "ca";
  const contents = normalizeContents(rawMessages);

  if (contents.length === 0) {
    return new Response(JSON.stringify({ error: "Falten missatges vàlids" }), {
      status: 400,
      headers: { ...cors, "Content-Type": "application/json" },
    });
  }

  const langNames = { ca: "Català", es: "Castellano", en: "English" };

  const geminiPayload = {
    systemInstruction: {
      parts: [
        {
          text: `${SYSTEM_PROMPT}\n\nIdioma de suport (NOMÉS si el missatge de l'usuari és ambigu d'1 sola paraula): ${langNames[lang]}.`,
        },
      ],
    },
    contents,
    safetySettings: SAFETY_SETTINGS,
    generationConfig: {
      temperature: 0.35,
      maxOutputTokens: 700,
    },
  };

  const modelsToTry = preferredModel
    ? [preferredModel, ...DEFAULT_MODELS.filter((m) => m !== preferredModel)]
    : [...DEFAULT_MODELS];

  let upstream = null;
  let usedModel = "";
  let lastErrorText = "";

  const tryModel = async (model) => {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:streamGenerateContent?alt=sse`;
    return fetchWithHeaderTimeout(
      url,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-goog-api-key": apiKey,
        },
        body: JSON.stringify(geminiPayload),
      },
      HEADER_TIMEOUT_MS
    );
  };

  for (const model of modelsToTry) {
    let res;
    try {
      res = await tryModel(model);
    } catch (err) {
      lastErrorText = `Timeout/xarxa en ${model}: ${err?.message || err}`;
      continue;
    }
    if (res.ok && res.body) {
      upstream = res;
      usedModel = model;
      break;
    }
    lastErrorText = await res.text();
    if (![404, 429, 500, 502, 503, 504].includes(res.status)) {
      return new Response(
        JSON.stringify({
          error: "Error del servei d'IA",
          status: res.status,
          detail: lastErrorText.slice(0, 300),
        }),
        {
          status: res.status,
          headers: { ...cors, "Content-Type": "application/json" },
        }
      );
    }
  }

  if (!upstream) {
    const discovered = await discoverFlashModel(apiKey);
    if (discovered && !modelsToTry.includes(discovered)) {
      try {
        const res = await tryModel(discovered);
        if (res.ok && res.body) {
          upstream = res;
          usedModel = discovered;
        } else {
          lastErrorText = await res.text();
        }
      } catch (err) {
        lastErrorText = `Timeout/xarxa en ${discovered}: ${err?.message || err}`;
      }
    }
  }

  if (!upstream) {
    return new Response(
      JSON.stringify({
        error: "Cap model Gemini disponible",
        detail: lastErrorText.slice(0, 300),
      }),
      {
        status: 502,
        headers: { ...cors, "Content-Type": "application/json" },
      }
    );
  }

  return new Response(upstream.body, {
    status: 200,
    headers: {
      ...cors,
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache",
      "X-ARS-Model": usedModel,
    },
  });
}
