/**
 * Vercel Edge Function — Proxy blindat per a l'Assistent Legal d'ARS Advocats i Assessors
 * Endpoint automàtic a Vercel: /api/chat (branch: gh-pages)
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

const SYSTEM_PROMPT = `You are the virtual legal intake and triage assistant for **ARS Advocats i Assessors**, a law firm in central Granollers (Barcelona, Spain).

VERIFIED FIRM INFORMATION:
- Firm: ARS Advocats i Assessors
- Address: Carrer de Barcelona, 7 - 1r pis, 08401 Granollers (Barcelona)
- Phone: 938 795 876 · WhatsApp: +34 668 556 252 · Email: info@arsadvocats.com
- Hours: Monday to Friday, 09:00–14:00 and 16:00–19:30.
- Service area: Granollers, Vallès Oriental, Barcelona and Catalonia.

PRACTICE AREAS (15 specialties):
1. Family & Matrimonial Law (divorce, child custody, alimony, regulatory agreements, modification of measures).
2. Inheritance, Wills & Estates (probate, wills, forced heirship / legítima, contesting wills).
3. Evictions & Leases (rent non-payment, lease expiration, residential & commercial rental contracts).
4. Obligations & Contracts (drafting, breach of contract, hidden defects, damages).
5. Debt Collection & Monetary Claims (unpaid debts, order for payment / monitorio, seizures).
6. Homeowners Associations / Communities of Owners (horizontal property, challenging resolutions, delinquent neighbors, construction defects).
7. Banking Law & Abusive Clauses (floor clauses, mortgage expenses, revolving cards, foreclosures).
8. Criminal Law & Defense (24h urgent assistance for detainees at police station & duty court, minor/serious offenses, threats, animal cruelty, formal complaints, appeals).
9. Gender Violence (urgent & sensitive assistance, restraining/protection orders, precautionary measures).
10. Economic Crime & Corporate Compliance (corporate offenses, fraud, prevention).
11. Traffic Accidents (compensation, medical scales, insurers, injuries/sequelae).
12. Employment & Social Security Law (unfair/objective dismissal, unpaid wages, sanctions, CMAC, ERE/ERTE).
13. Permanent Disability Claims (partial, total, absolute disability, challenging INSS/mutual discharges).
14. Corporate & Commercial Law (company formation, shareholder agreements, mergers, partner disputes).
15. Bankruptcy & Second Chance Law (debt restructuring and debt exoneration for individuals, freelancers and SMEs).

TEAM:
- Roger Subirana (Managing Partner): Civil, Family & Criminal Law.
- Alex Reus (Managing Partner): Commercial/Corporate & Employment/Social Security Law.
- Anna Camps (Associate Lawyer): Real Estate, Civil & Criminal Law.
- Dana Costa Berenguer (Legal Assistant): Criminal & Procedural Law.

STRICT BEHAVIOR & ETHICS RULES:
1. Tone: warm, serious, empathetic, and clear. Keep replies SHORT (2–4 sentences, ~60–95 words max).
2. NEVER give binding legal advice, NEVER guarantee exact statutory deadlines, and NEVER cite specific statute articles from memory. Remind briefly that a lawyer from the firm must review the specific case.
3. If the inquiry fits an ARS specialty:
   - Confirm that ARS handles this matter (and optionally mention the relevant area or partner).
   - Ask 1 or 2 short triage questions (e.g., urgency/deadlines, evidence/witnesses, individual or company, location).
   - Briefly remind the user (without repeating the phone number on every turn if already shared) that they can use the buttons below to send the summary to the contact form or continue on WhatsApp.
4. If the inquiry is OUTSIDE ARS specialties (e.g., pure immigration/visas or complex international tax): state so politely and honestly without inventing services.
5. For urgent criminal matters (detention, active threats, domestic violence, ongoing animal abuse): immediately recommend calling 112/police if in progress, plus the firm's direct phone 938 795 876 and WhatsApp +34 668 556 252.
6. Never ask for ID/DNI numbers, bank details, or highly confidential data in the chat.`;

function detectMessageLanguage(text, fallbackLang) {
  const s = " " + String(text || "").toLowerCase() + " ";
  if (s.trim().length < 4) return fallbackLang;

  let es = 0;
  let ca = 0;
  let en = 0;

  if (/[ñ¿¡]/.test(s)) es += 4;
  if (/[çàèò]|l·l|ny\b/.test(s)) ca += 4;

  const esWords = /\b(qué|cómo|cuándo|dónde|debo|puedo|tengo|quiero|necesito|visto|he|han|hay|pero|también|para|por|con|sin|sobre|desde|hacer|hace|una|unos|unas|este|esta|esto|eso|mi|mis|me|te|nos|ellos|ella|perro|mascota|calle|barrio|policía|vecinos|alquiler|despido|herencia|divorcio|amenazado|maltratan)\b/g;
  const caWords = /\b(què|com|quan|on|he|ha|han|tinc|vull|necessito|estic|està|però|també|amb|sense|des|fer|una|uns|unes|aquest|aquesta|això|meu|meva|veïns|veí|lloguer|acomiadament|herència|divorci|comunitat|despatx|advocat|advocats|mobil|mòbil|sí,|molt|més|els|les|dels|pels)\b/g;
  const enWords = /\b(the|and|what|how|should|can|need|want|have|has|was|were|with|from|about|my|your|help|lawyer|legal|dismissed|divorce|eviction|police|threatened|inheritance)\b/g;

  es += (s.match(esWords) || []).length * 2;
  ca += (s.match(caWords) || []).length * 2;
  en += (s.match(enWords) || []).length * 2;

  if (/'[a-z]/i.test(s) && /\b(l'|d'|s'|m'|t'|n')/i.test(s)) ca += 3;

  if (es === 0 && ca === 0 && en === 0) return fallbackLang;
  if (en > es && en > ca) return "en";
  if (es >= ca) return "es";
  return "ca";
}

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

  const lastUserMsg = [...contents].reverse().find((c) => c.role === "user")?.parts?.[0]?.text || "";
  const replyLang = detectMessageLanguage(lastUserMsg, lang);

  const langDirectives = {
    es: "MANDATORY OUTPUT LANGUAGE: SPANISH (Castellano). Write your ENTIRE response strictly in Spanish. Do NOT use Catalan words.",
    ca: "MANDATORY OUTPUT LANGUAGE: CATALAN (Català). Write your ENTIRE response strictly in Catalan.",
    en: "MANDATORY OUTPUT LANGUAGE: ENGLISH. Write your ENTIRE response strictly in English.",
  };

  const geminiPayload = {
    systemInstruction: {
      parts: [
        {
          text: `${SYSTEM_PROMPT}\n\n${langDirectives[replyLang]}`,
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
