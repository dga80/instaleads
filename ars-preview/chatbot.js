/**
 * ARS Advocats i Assessors — Assistent Legal (Client Widget)
 * Connects via secure Vercel Edge proxy (streaming SSE)
 */
(function () {
  const WORKER_URL =
    window.location.hostname === "ars20.vercel.app" ||
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
      ? "/api/chat"
      : "https://ars20.vercel.app/api/chat";
  const WHATSAPP_NUMBER = "34668556252";
  const MAX_USER_TURNS = 12;

  const I18N = {
    ca: {
      launcher: "Assistent Legal",
      launcherShort: "Assistent",
      launcherAria: "Obrir l'assistent legal d'ARS Advocats",
      title: "Assistent ARS",
      subtitle: "Orientació inicial · 24/7",
      resetTitle: "Nova conversa",
      closeTitle: "Tancar xat",
      disclaimer:
        "Orientació informativa que no substitueix una consulta jurídica. Per privacitat, no inclogui DNI ni dades sensibles.",
      welcome:
        "Benvingut a l'assistent virtual d'**ARS Advocats i Assessors** (Granollers). Indiqui'ns breument el seu assumpte legal i li informarem si entra dins les nostres especialitats i com el podem ajudar.",
      placeholder: "Escrigui la seva consulta...",
      sendAria: "Enviar missatge",
      btnForm: "Passar al formulari",
      btnWa: "Continuar per WhatsApp",
      retryBtn: "Tornar a provar",
      areaLabel: "Àrea estimada",
      turnLimitPlaceholder: "Contacti amb un advocat pels botons superiors",
      turnLimitMsg:
        "Hem assolit el límit de consultes orientatives d'aquesta sessió. Per continuar amb el seu cas de manera personalitzada, pot enviar el resum al formulari, continuar per WhatsApp o trucar al 938 795 876.",
      chips: [
        "Divorci o custòdia",
        "Acomiadament laboral",
        "Tramitació d'herència",
        "Desnonament o lloguer",
        "Urgència penal",
      ],
      errConnection:
        "En aquest moment no podem connectar amb l'assistent. Pot tornar-ho a provar, escriure'ns per WhatsApp (+34 668 556 252) o trucar al 938 795 876.",
      errNotDeployed:
        "L'assistent es troba temporalment en manteniment. Mentrestant, pot contactar directament amb el despatx al 938 795 876.",
      waIntro: "Hola, he fet una consulta inicial a l'assistent web d'ARS Advocats.",
      formIntro: "[Resum generat des de l'Assistent Web]",
    },
    es: {
      launcher: "Asistente Legal",
      launcherShort: "Asistente",
      launcherAria: "Abrir el asistente legal de ARS Advocats",
      title: "Asistente ARS",
      subtitle: "Orientación inicial · 24/7",
      resetTitle: "Nueva conversación",
      closeTitle: "Cerrar chat",
      disclaimer:
        "Orientación informativa que no sustituye una consulta jurídica. Por privacidad, no incluya DNI ni datos sensibles.",
      welcome:
        "Bienvenido al asistente virtual de **ARS Advocats i Assessors** (Granollers). Indíquenos brevemente su consulta legal y le informaremos si entra en nuestras especialidades y cómo podemos ayudarle.",
      placeholder: "Escriba su consulta...",
      sendAria: "Enviar mensaje",
      btnForm: "Pasar al formulario",
      btnWa: "Continuar por WhatsApp",
      retryBtn: "Reintentar",
      areaLabel: "Área estimada",
      turnLimitPlaceholder: "Contacte con un abogado mediante los botones superiores",
      turnLimitMsg:
        "Hemos alcanzado el límite de consultas orientativas de esta sesión. Para continuar con su caso de forma personalizada, puede enviar el resumen al formulario, continuar por WhatsApp o llamar al 938 795 876.",
      chips: [
        "Divorcio o custodia",
        "Despido laboral",
        "Tramitación de herencia",
        "Desahucio o alquiler",
        "Urgencia penal",
      ],
      errConnection:
        "En este momento no podemos conectar con el asistente. Puede reintentarlo, escribirnos por WhatsApp (+34 668 556 252) o llamar al 938 795 876.",
      errNotDeployed:
        "El asistente se encuentra temporalmente en mantenimiento. Mientras tanto, puede contactar con el despacho en el 938 795 876.",
      waIntro: "Hola, he realizado una consulta inicial en el asistente web de ARS Advocats.",
      formIntro: "[Resumen generado desde el Asistente Web]",
    },
    en: {
      launcher: "Legal Assistant",
      launcherShort: "Assistant",
      launcherAria: "Open ARS Advocats legal assistant",
      title: "ARS Assistant",
      subtitle: "Initial guidance · 24/7",
      resetTitle: "New conversation",
      closeTitle: "Close chat",
      disclaimer:
        "Informational guidance only; does not replace formal legal advice. Please do not share ID numbers or sensitive data here.",
      welcome:
        "Hello, I am the virtual assistant for **ARS Advocats i Assessors** (Granollers). Briefly tell me about your legal matter and I will let you know how our team can help.",
      placeholder: "Write your legal question...",
      sendAria: "Send message",
      btnForm: "Send to contact form",
      btnWa: "Continue on WhatsApp",
      retryBtn: "Retry",
      areaLabel: "Estimated area",
      turnLimitPlaceholder: "Please use the buttons above to contact a lawyer",
      turnLimitMsg:
        "We have reached the guidance limit for this session. To continue with a specialist lawyer, please use the contact form or WhatsApp buttons below, or call +34 938 795 876.",
      chips: [
        "Divorce or custody",
        "Unfair dismissal",
        "Inheritance / wills",
        "Eviction or rental",
        "Urgent criminal matter",
      ],
      errConnection:
        "We cannot reach the assistant right now. You can retry, contact us on WhatsApp (+34 668 556 252), or call +34 938 795 876.",
      errNotDeployed:
        "The assistant is temporarily under maintenance. Meanwhile, you can reach the firm directly at +34 938 795 876.",
      waIntro: "Hello, I had an initial chat with the ARS Advocats web assistant.",
      formIntro: "[Summary generated from Web Assistant]",
    },
  };

  const AREA_LABELS = {
    ca: {
      familia: "Dret de família i matrimonial",
      herencies: "Successions, testaments i herències",
      immobiliari: "Immobiliari, arrendaments i desnonaments",
      contractes: "Obligacions i contractes",
      quantitat: "Reclamacions de quantitat",
      comunitats: "Comunitats de propietaris",
      bancari: "Dret bancari i clàusules abusives",
      penal: "Dret penal i litigació",
      violencia: "Violència masclista i de gènere",
      compliance: "Dret econòmic i compliance",
      accidents: "Accidents de trànsit i indemnitzacions",
      laboral: "Dret laboral i Seguretat Social",
      incapacitats: "Incapacitats laborals i invalidesa",
      mercantil: "Dret mercantil i societari",
      "segona-oportunitat": "Dret concursal i segona oportunitat",
      altres: "Consulta jurídica general",
    },
    es: {
      familia: "Derecho de familia y matrimonial",
      herencies: "Sucesiones, testamentos y herencias",
      immobiliari: "Inmobiliario, alquileres y desahucios",
      contractes: "Obligaciones y contratos",
      quantitat: "Reclamaciones de cantidad",
      comunitats: "Comunidades de propietarios",
      bancari: "Derecho bancario y cláusulas abusivas",
      penal: "Derecho penal y litigación",
      violencia: "Violencia de género",
      compliance: "Derecho económico y compliance",
      accidents: "Accidentes de tráfico e indemnizaciones",
      laboral: "Derecho laboral y Seguridad Social",
      incapacitats: "Incapacidades laborales e invalidez",
      mercantil: "Derecho mercantil y societario",
      "segona-oportunitat": "Derecho concursal y segunda oportunidad",
      altres: "Consulta jurídica general",
    },
    en: {
      familia: "Family & Matrimonial Law",
      herencies: "Inheritance, Wills & Estates",
      immobiliari: "Real Estate, Leases & Evictions",
      contractes: "Obligations & Contracts",
      quantitat: "Debt Collection & Claims",
      comunitats: "Homeowners Associations",
      bancari: "Banking Law & Abusive Clauses",
      penal: "Criminal Law & Defense",
      violencia: "Gender & Domestic Violence",
      compliance: "Economic Crime & Compliance",
      accidents: "Traffic Accidents & Compensation",
      laboral: "Employment & Social Security Law",
      incapacitats: "Permanent Disability Claims",
      mercantil: "Corporate & Commercial Law",
      "segona-oportunitat": "Bankruptcy & Second Chance Law",
      altres: "General Legal Inquiry",
    },
  };

  function getLang() {
    const bodyLang = document.body.getAttribute("data-lang");
    const saved = localStorage.getItem("ars_lang");
    const lang = bodyLang || saved || "ca";
    return I18N[lang] ? lang : "ca";
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function formatSafeText(text) {
    const escaped = escapeHtml(text);
    return escaped
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n/g, "<br>");
  }

  function detectArea(conversationText) {
    const t = conversationText.toLowerCase();
    if (/violènci|violenci|violence|allunyament|alejamiento|restraining|masclist|machist/.test(t)) return "violencia";
    if (/divorci|divorce|custòdi|custodi|custody|aliments|alimentos|alimony|família|familia|family|conveni/.test(t)) return "familia";
    if (/accident|trànsit|tráfico|traffic|indemnitz|indemniz|compensation|crash/.test(t)) return "accidents";
    if (/herènci|herenci|inheritance|testament|wills?\b|probate|legítima|legitima|successi|estate/.test(t)) return "herencies";
    if (/incapacitat|incapacidad|invalidesa|invalidez|disability|inss|mútu|mutu/.test(t)) return "incapacitats";
    if (/comunitat|comunidad|veïns|vecin|propietat horitzontal|propiedad horizontal|homeowner|neighbor/.test(t)) return "comunitats";
    if (/bancari|bancario|hipotec|mortgage|clàusula|clausula|revolving/.test(t)) return "bancari";
    if (/compliance|delictes societaris|delitos societarios|estaf|fraud/.test(t)) return "compliance";
    if (/desnonament|desahuci|evict|lloguer|alquiler|rent|tenant|lease|arrendament/.test(t)) return "immobiliari";
    if (/monitori|impagat|impagad|reclamaci[óo] de quantitat|reclamaci[óo]n de cantidad|embarg/.test(t)) return "quantitat";
    if (/contract|contrat|vici|incompliment|incumplimient|breach/.test(t)) return "contractes";
    if (/penal|criminal|detingut|detenido|detained|arrest|comissari|comisaría|police|denúnci|denunci|delict|threat|amenaz|maltrat/.test(t)) return "penal";
    if (/segona oportunitat|segunda oportunidad|second chance|concurs|bankrupt|insolvenc|deute|deuda|debt/.test(t)) return "segona-oportunitat";
    if (/societat|sociedad|mercantil|corporate|commercial|company|shareholder|soci|socio|empresa/.test(t)) return "mercantil";
    if (/acomiad|despid|dismiss|fired|unfair|laboral|employment|salari|wages|severance|finiquit|cmac/.test(t)) return "laboral";
    return "altres";
  }

  function buildCaseSummary(messages, activeLang, maxLen) {
    const langKey = AREA_LABELS[activeLang] ? activeLang : "ca";
    const t = I18N[langKey];
    const fullText = messages.map((m) => m.text).join(" ");
    const areaCode = detectArea(fullText);
    const areaName = AREA_LABELS[langKey][areaCode] || AREA_LABELS[langKey].altres;

    const seen = new Set();
    const userPoints = [];
    for (const m of messages) {
      if (m.role !== "user") continue;
      const clean = m.text.replace(/\s+/g, " ").trim();
      if (!clean) continue;
      const norm = clean.toLowerCase();
      if (seen.has(norm)) continue;
      seen.add(norm);
      userPoints.push(clean.length > 220 ? clean.slice(0, 217) + "..." : clean);
    }

    const lines = [`${t.areaLabel}: ${areaName}`];
    userPoints.slice(-5).forEach((pt) => {
      lines.push(`• ${pt}`);
    });
    return lines.join("\n").slice(0, maxLen || 650);
  }

  const STORAGE_KEY = "ars_chat_session_v1";
  const STORAGE_LANG_KEY = "ars_chat_lang_v1";
  const STORAGE_FROM_CHAT_KEY = "ars_from_chat_v1";

  function loadSessionLang(fallback) {
    try {
      const saved = sessionStorage.getItem(STORAGE_LANG_KEY);
      return saved && I18N[saved] ? saved : fallback;
    } catch {
      return fallback;
    }
  }

  function saveSessionLang(l) {
    try {
      if (!l) sessionStorage.removeItem(STORAGE_LANG_KEY);
      else sessionStorage.setItem(STORAGE_LANG_KEY, l);
    } catch {
      // Ignore storage restrictions
    }
  }

  function loadSessionMessages() {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      if (!raw) return [];
      const parsed = JSON.parse(raw);
      if (!Array.isArray(parsed)) return [];
      return parsed
        .filter(
          (m) =>
            m &&
            (m.role === "user" || m.role === "assistant") &&
            typeof m.text === "string" &&
            m.text.trim()
        )
        .slice(-16);
    } catch {
      return [];
    }
  }

  function saveSessionMessages(msgs) {
    try {
      if (!msgs || msgs.length === 0) {
        sessionStorage.removeItem(STORAGE_KEY);
      } else {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(msgs.slice(-16)));
      }
    } catch {
      // Ignore storage quota or private-mode restrictions
    }
  }

  function initChatbot() {
    let lang = getLang();
    let isOpen = false;
    let isSending = false;
    let messages = loadSessionMessages(); // { role: 'user' | 'assistant', text: string }
    let chatLang = messages.length > 0 ? loadSessionLang(lang) : lang;

    // Create Launcher Button
    const launcher = document.createElement("button");
    launcher.type = "button";
    launcher.className = "ars-chat-launcher";
    launcher.id = "arsChatLauncher";
    launcher.innerHTML = `
      <span class="ars-chat-launcher-icon" aria-hidden="true">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
        <span class="ars-chat-live-dot"></span>
      </span>
      <span class="ars-chat-launcher-label-full"></span>
      <span class="ars-chat-launcher-label-short"></span>
    `;

    // Create Chat Panel
    const panel = document.createElement("section");
    panel.className = "ars-chat-panel";
    panel.id = "arsChatPanel";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-modal", "false");
    panel.setAttribute("aria-labelledby", "arsChatTitle");
    panel.innerHTML = `
      <header class="ars-chat-header">
        <div class="ars-chat-header-info">
          <div class="ars-chat-avatar" aria-hidden="true">
            <img src="data:image/png;base64,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" alt="ARS Advocats" class="ars-chat-avatar-img" width="24" height="24">
          </div>
          <div class="ars-chat-title-wrap">
            <h3 class="ars-chat-title" id="arsChatTitle"></h3>
            <p class="ars-chat-subtitle" id="arsChatSubtitle"></p>
          </div>
        </div>
        <div class="ars-chat-header-actions">
          <button type="button" class="ars-chat-icon-btn" id="arsChatReset">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="1 4 1 10 7 10"></polyline><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path></svg>
          </button>
          <button type="button" class="ars-chat-icon-btn" id="arsChatClose">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>
      </header>
      <div class="ars-chat-disclaimer" id="arsChatDisclaimer"></div>
      <div class="ars-chat-messages" id="arsChatMessages" role="log" aria-live="polite"></div>
      <div class="ars-chat-handoff" id="arsChatHandoff">
        <button type="button" class="ars-chat-handoff-btn ars-chat-handoff-btn--form" id="arsChatToForm"></button>
        <a href="#" target="_blank" rel="noopener" class="ars-chat-handoff-btn ars-chat-handoff-btn--wa" id="arsChatToWa"></a>
      </div>
      <form class="ars-chat-form" id="arsChatForm">
        <textarea class="ars-chat-input" id="arsChatInput" rows="1" maxlength="1000"></textarea>
        <button type="submit" class="ars-chat-send" id="arsChatSend">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        </button>
      </form>
    `;

    document.body.appendChild(launcher);
    document.body.appendChild(panel);

    const els = {
      launcherLabelFull: launcher.querySelector(".ars-chat-launcher-label-full"),
      launcherLabelShort: launcher.querySelector(".ars-chat-launcher-label-short"),
      title: panel.querySelector("#arsChatTitle"),
      subtitle: panel.querySelector("#arsChatSubtitle"),
      resetBtn: panel.querySelector("#arsChatReset"),
      closeBtn: panel.querySelector("#arsChatClose"),
      disclaimer: panel.querySelector("#arsChatDisclaimer"),
      messagesBox: panel.querySelector("#arsChatMessages"),
      handoff: panel.querySelector("#arsChatHandoff"),
      toFormBtn: panel.querySelector("#arsChatToForm"),
      toWaLink: panel.querySelector("#arsChatToWa"),
      form: panel.querySelector("#arsChatForm"),
      input: panel.querySelector("#arsChatInput"),
      sendBtn: panel.querySelector("#arsChatSend"),
    };

    function scrollToBottom() {
      els.messagesBox.scrollTop = els.messagesBox.scrollHeight;
    }

    function getUserTurnCount() {
      return messages.filter((m) => m.role === "user").length;
    }

    function updateComposerLimitState(forceReached) {
      const activeLang = I18N[chatLang] ? chatLang : lang;
      const t = I18N[activeLang];
      const limitReached = Boolean(forceReached) || getUserTurnCount() >= MAX_USER_TURNS;
      els.input.disabled = limitReached;
      els.sendBtn.disabled = limitReached || isSending;
      els.input.placeholder = limitReached ? t.turnLimitPlaceholder : t.placeholder;
      els.handoff.classList.toggle("ars-chat-handoff--highlight", limitReached);
    }

    function updateHandoffLinks() {
      const activeLang = I18N[chatLang] ? chatLang : lang;
      const t = I18N[activeLang];
      els.toFormBtn.textContent = t.btnForm;
      els.toWaLink.textContent = t.btnWa;
      els.disclaimer.textContent = t.disclaimer;
      els.sendBtn.setAttribute("aria-label", t.sendAria);
      updateComposerLimitState();

      const hasUserMsg = messages.some((m) => m.role === "user");
      if (hasUserMsg) {
        const summary = buildCaseSummary(messages, activeLang, 520);
        const waText = encodeURIComponent(`${t.waIntro}\n${summary}`);
        els.toWaLink.href = `https://wa.me/${WHATSAPP_NUMBER}?text=${waText}`;
      } else {
        const waDefault = encodeURIComponent(
          activeLang === "es"
            ? "Hola, quería solicitar información sobre una consulta jurídica en ARS Advocats."
            : activeLang === "en"
            ? "Hello, I would like to request information about a legal consultation at ARS Advocats."
            : "Hola, volia sol·licitar informació sobre una consulta jurídica a ARS Advocats."
        );
        els.toWaLink.href = `https://wa.me/${WHATSAPP_NUMBER}?text=${waDefault}`;
      }
    }

    function applyDialogLanguage(detectedLang) {
      if (!I18N[detectedLang] || detectedLang === chatLang) return;
      chatLang = detectedLang;
      saveSessionLang(chatLang);
      const t = I18N[chatLang];
      els.title.textContent = t.title;
      els.subtitle.textContent = t.subtitle;
      els.resetBtn.title = t.resetTitle;
      els.resetBtn.setAttribute("aria-label", t.resetTitle);
      els.closeBtn.title = t.closeTitle;
      els.closeBtn.setAttribute("aria-label", t.closeTitle);
      updateHandoffLinks();
    }

    function renderWelcome() {
      const t = I18N[lang];
      els.messagesBox.innerHTML = "";

      const welcomeBubble = document.createElement("div");
      welcomeBubble.className = "ars-chat-msg ars-chat-msg--assistant";
      welcomeBubble.setAttribute("data-welcome", "true");
      welcomeBubble.innerHTML = formatSafeText(t.welcome);
      els.messagesBox.appendChild(welcomeBubble);

      const chipsWrap = document.createElement("div");
      chipsWrap.className = "ars-chat-chips";
      chipsWrap.id = "arsChatChips";
      t.chips.forEach((label) => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "ars-chat-chip";
        chip.textContent = label;
        chip.addEventListener("click", () => {
          sendMessage(label);
        });
        chipsWrap.appendChild(chip);
      });
      els.messagesBox.appendChild(chipsWrap);
      updateHandoffLinks();
    }

    function renderRestoredConversation() {
      const t = I18N[lang];
      els.messagesBox.innerHTML = "";

      const welcomeBubble = document.createElement("div");
      welcomeBubble.className = "ars-chat-msg ars-chat-msg--assistant";
      welcomeBubble.setAttribute("data-welcome", "true");
      welcomeBubble.innerHTML = formatSafeText(t.welcome);
      els.messagesBox.appendChild(welcomeBubble);

      messages.forEach((m) => {
        appendMessageBubble(m.role, formatSafeText(m.text));
      });
      updateHandoffLinks();
    }

    function applyLanguage(newLang) {
      lang = I18N[newLang] ? newLang : "ca";
      const t = I18N[lang];
      els.launcherLabelFull.textContent = t.launcher;
      els.launcherLabelShort.textContent = t.launcherShort;
      launcher.setAttribute("aria-label", t.launcherAria);

      if (messages.length === 0) {
        chatLang = lang;
        saveSessionLang(null);
        els.title.textContent = t.title;
        els.subtitle.textContent = t.subtitle;
        els.resetBtn.title = t.resetTitle;
        els.resetBtn.setAttribute("aria-label", t.resetTitle);
        els.closeBtn.title = t.closeTitle;
        els.closeBtn.setAttribute("aria-label", t.closeTitle);
        renderWelcome();
      } else {
        const ct = I18N[chatLang] || t;
        els.title.textContent = ct.title;
        els.subtitle.textContent = ct.subtitle;
        els.resetBtn.title = ct.resetTitle;
        els.resetBtn.setAttribute("aria-label", ct.resetTitle);
        els.closeBtn.title = ct.closeTitle;
        els.closeBtn.setAttribute("aria-label", ct.closeTitle);
        const welcomeEl = els.messagesBox.querySelector('[data-welcome="true"]');
        if (welcomeEl) {
          welcomeEl.innerHTML = formatSafeText(t.welcome);
        } else {
          renderRestoredConversation();
        }
        updateHandoffLinks();
      }
    }

    function openChat() {
      isOpen = true;
      panel.classList.add("is-open");
      launcher.classList.add("is-hidden");
      scrollToBottom();
      if (typeof window.arsTrack === "function") {
        window.arsTrack("chat_open");
      }
      setTimeout(() => els.input.focus(), 180);
    }

    function closeChat() {
      isOpen = false;
      panel.classList.remove("is-open");
      launcher.classList.remove("is-hidden");
      launcher.focus();
    }

    function resetChat() {
      if (isSending) return;
      messages = [];
      chatLang = lang;
      saveSessionMessages(messages);
      saveSessionLang(null);
      applyLanguage(lang);
      els.input.focus();
    }

    function appendMessageBubble(role, htmlContent, extraClass) {
      const el = document.createElement("div");
      el.className = `ars-chat-msg ars-chat-msg--${role}${extraClass ? " " + extraClass : ""}`;
      el.innerHTML = htmlContent;
      els.messagesBox.appendChild(el);
      scrollToBottom();
      return el;
    }

    async function sendMessage(rawText) {
      const text = rawText.trim();
      if (!text || isSending) return;

      const activeLang = I18N[chatLang] ? chatLang : lang;
      if (getUserTurnCount() >= MAX_USER_TURNS) {
        updateComposerLimitState(true);
        appendMessageBubble("assistant", formatSafeText(I18N[activeLang].turnLimitMsg));
        return;
      }

      const chipsEl = els.messagesBox.querySelector("#arsChatChips");
      if (chipsEl) chipsEl.remove();

      isSending = true;
      els.sendBtn.disabled = true;
      els.input.value = "";
      els.input.style.height = "auto";
      els.input.style.overflowY = "hidden";

      messages.push({ role: "user", text });
      const userBubble = appendMessageBubble("user", formatSafeText(text));
      updateHandoffLinks();
      // Production chat_message/chat_session are tracked server-side in /api/chat (immune to adblockers);
      // keep client-side tracking only on localhost for local development.
      if (
        (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") &&
        typeof window.arsTrack === "function"
      ) {
        const devEvents = ["chat_message"];
        if (getUserTurnCount() === 1) devEvents.push("chat_session");
        window.arsTrack(devEvents);
      }

      const assistantBubble = appendMessageBubble(
        "assistant",
        `<span class="ars-chat-typing" aria-label="..."><span></span><span></span><span></span></span>`
      );

      const fetchOnce = async () => {
        const controller = new AbortController();
        const tid = setTimeout(() => controller.abort(), 16000);
        try {
          const res = await fetch(WORKER_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ messages, lang }),
            signal: controller.signal,
          });
          clearTimeout(tid);
          return res;
        } catch (e) {
          clearTimeout(tid);
          throw e;
        }
      };

      let hitServerLimit = false;

      try {
        let response;
        try {
          response = await fetchOnce();
        } catch {
          await new Promise((r) => setTimeout(r, 450));
          response = await fetchOnce();
        }

        const contentType = response.headers.get("Content-Type") || "";
        const detectedLang = response.headers.get("X-ARS-Lang");
        if (detectedLang) {
          applyDialogLanguage(detectedLang);
        }
        if (response.headers.get("X-ARS-Limit") === "1") {
          hitServerLimit = true;
        }

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        if (contentType.includes("text/plain")) {
          const plain = await response.text();
          if (plain.toLowerCase().includes("hello world")) {
            assistantBubble.className = "ars-chat-msg ars-chat-msg--error";
            assistantBubble.innerHTML = formatSafeText(I18N[chatLang || lang].errNotDeployed);
            return;
          }
          assistantBubble.innerHTML = formatSafeText(plain);
          messages.push({ role: "assistant", text: plain });
          saveSessionMessages(messages);
          return;
        }

        if (!response.body) {
          throw new Error("Empty response body");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";
        let fullText = "";

        const parseSseLine = (line) => {
          const trimmed = line.trim();
          if (!trimmed.startsWith("data:")) return;
          const jsonStr = trimmed.slice(5).trim();
          if (!jsonStr || jsonStr === "[DONE]") return;
          try {
            const parsed = JSON.parse(jsonStr);
            const parts = parsed?.candidates?.[0]?.content?.parts;
            if (Array.isArray(parts)) {
              for (const part of parts) {
                if (typeof part.text === "string" && !part.thought) {
                  fullText += part.text;
                }
              }
              if (fullText) {
                assistantBubble.innerHTML = formatSafeText(fullText);
                scrollToBottom();
              }
            }
          } catch {
            // Ignore partial/malformed SSE frames
          }
        };

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });

          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            parseSseLine(line);
          }
        }

        if (buffer.trim()) {
          parseSseLine(buffer);
        }

        if (!fullText.trim()) {
          throw new Error("No text generated");
        }

        messages.push({ role: "assistant", text: fullText.trim() });
        saveSessionMessages(messages);
      } catch (err) {
        console.error("[ARS Chat]", err);
        if (messages.length > 0 && messages[messages.length - 1].role === "user") {
          messages.pop();
        }
        saveSessionMessages(messages);
        const errT = I18N[chatLang] || I18N[lang];
        assistantBubble.className = "ars-chat-msg ars-chat-msg--error";
        assistantBubble.innerHTML = `<div>${formatSafeText(errT.errConnection)}</div>`;
        const retryBtn = document.createElement("button");
        retryBtn.type = "button";
        retryBtn.className = "ars-chat-retry-btn";
        retryBtn.textContent = `↻ ${errT.retryBtn}`;
        retryBtn.addEventListener("click", () => {
          if (isSending) return;
          assistantBubble.remove();
          if (userBubble && userBubble.parentNode) {
            userBubble.remove();
          }
          sendMessage(text);
        });
        assistantBubble.appendChild(retryBtn);
      } finally {
        isSending = false;
        updateComposerLimitState(hitServerLimit);
        scrollToBottom();
      }
    }

    // Events
    launcher.addEventListener("click", openChat);
    els.closeBtn.addEventListener("click", closeChat);
    els.resetBtn.addEventListener("click", resetChat);

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && isOpen) {
        closeChat();
      }
    });

    els.form.addEventListener("submit", (e) => {
      e.preventDefault();
      sendMessage(els.input.value);
    });

    els.input.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage(els.input.value);
      }
    });

    els.input.addEventListener("input", () => {
      els.input.style.height = "auto";
      const nextHeight = Math.min(els.input.scrollHeight, 96);
      els.input.style.height = nextHeight + "px";
      els.input.style.overflowY = els.input.scrollHeight > 96 ? "auto" : "hidden";
    });

    // Track WhatsApp handoff from chatbot
    els.toWaLink.addEventListener("click", () => {
      if (typeof window.arsTrack === "function") {
        window.arsTrack("chat_to_wa");
      }
    });

    // Handoff to contact form
    els.toFormBtn.addEventListener("click", () => {
      window.__arsFromChat = true;
      try {
        sessionStorage.setItem(STORAGE_FROM_CHAT_KEY, "1");
      } catch {
        // Ignore storage restrictions
      }
      if (typeof window.arsTrack === "function") {
        window.arsTrack("chat_to_form");
      }
      const activeLang = I18N[chatLang] ? chatLang : lang;
      const t = I18N[activeLang];
      const hasUserMsg = messages.some((m) => m.role === "user");
      const summary = hasUserMsg ? buildCaseSummary(messages, activeLang, 750) : "";
      const fullConversation = messages.map((m) => m.text).join(" ");
      const detectedArea = detectArea(fullConversation);

      const areaSelect = document.getElementById("formArea");
      const msgField = document.getElementById("formMessage");
      const contactSection = document.getElementById("contacte");

      if (areaSelect && detectedArea) {
        areaSelect.value = detectedArea;
      }
      if (msgField && summary) {
        msgField.value = `${t.formIntro}\n${summary}`;
      }

      closeChat();
      if (contactSection) {
        contactSection.scrollIntoView({ behavior: "smooth", block: "start" });
        setTimeout(() => {
          const nameInput = document.getElementById("formName");
          if (nameInput) nameInput.focus();
        }, 550);
      }
    });

    // Sync with ARS topbar language switcher
    const langObserver = new MutationObserver(() => {
      const current = getLang();
      if (current !== lang) {
        applyLanguage(current);
      }
    });
    langObserver.observe(document.body, {
      attributes: true,
      attributeFilter: ["data-lang"],
    });

    applyLanguage(lang);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initChatbot);
  } else {
    initChatbot();
  }
})();
