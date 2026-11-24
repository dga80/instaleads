/**
 * ARS Advocats i Assessors — Assistent Legal (Client Widget)
 * Connects via secure Cloudflare Worker proxy (streaming SSE)
 */
(function () {
  const WORKER_URL = "https://ars-chat.dani-dga.workers.dev/";
  const WHATSAPP_NUMBER = "34668556252";

  const I18N = {
    ca: {
      launcher: "Assistent Legal",
      launcherAria: "Obrir l'assistent legal d'ARS Advocats",
      title: "Assistent ARS",
      subtitle: "Orientació inicial · 24/7",
      resetTitle: "Nova conversa",
      closeTitle: "Tancar xat",
      disclaimer:
        "Orientació informativa que no substitueix una consulta jurídica. Per privacitat, no incloguis DNI ni dades sensibles.",
      welcome:
        "Hola, soc l'assistent virtual d'**ARS Advocats i Assessors** (Granollers). Explica'm breument quin assumpte legal tens i t'indicaré si entra dins les nostres especialitats i com podem ajudar-te.",
      placeholder: "Escriu la teva consulta breument...",
      sendAria: "Enviar missatge",
      btnForm: "Passar al formulari",
      btnWa: "Continuar per WhatsApp",
      chips: [
        "Divorci o custòdia",
        "Acomiadament laboral",
        "Tramitació d'herència",
        "Desnonament o lloguer",
        "Urgència penal",
      ],
      errConnection:
        "Ara mateix no podem connectar amb l'assistent. Pots escriure'ns directament per WhatsApp (+34 668 556 252) o trucar al 938 795 876.",
      errNotDeployed:
        "L'assistent està pendent d'activar el codi del Worker a Cloudflare. Mentrestant, pots contactar directament amb el despatx al 938 795 876.",
      waIntro: "Hola, he fet una consulta inicial a l'assistent web d'ARS Advocats. Resum del cas:",
      formIntro: "[Resum generat des de l'Assistent Web]",
    },
    es: {
      launcher: "Asistente Legal",
      launcherAria: "Abrir el asistente legal de ARS Advocats",
      title: "Asistente ARS",
      subtitle: "Orientación inicial · 24/7",
      resetTitle: "Nueva conversación",
      closeTitle: "Cerrar chat",
      disclaimer:
        "Orientación informativa que no sustituye una consulta jurídica. Por privacidad, no incluyas DNI ni datos sensibles.",
      welcome:
        "Hola, soy el asistente virtual de **ARS Advocats i Assessors** (Granollers). Cuéntame brevemente tu consulta legal y te indicaré si entra en nuestras especialidades y cómo podemos ayudarte.",
      placeholder: "Escribe tu consulta brevemente...",
      sendAria: "Enviar mensaje",
      btnForm: "Pasar al formulario",
      btnWa: "Continuar por WhatsApp",
      chips: [
        "Divorcio o custodia",
        "Despido laboral",
        "Tramitación de herencia",
        "Desahucio o alquiler",
        "Urgencia penal",
      ],
      errConnection:
        "Ahora mismo no podemos conectar con el asistente. Puedes escribirnos por WhatsApp (+34 668 556 252) o llamar al 938 795 876.",
      errNotDeployed:
        "El asistente está pendiente de activar el código del Worker en Cloudflare. Mientras tanto, puedes contactar con el despacho en el 938 795 876.",
      waIntro: "Hola, he realizado una consulta inicial en el asistente web de ARS Advocats. Resumen del caso:",
      formIntro: "[Resumen generado desde el Asistente Web]",
    },
    en: {
      launcher: "Legal Assistant",
      launcherAria: "Open ARS Advocats legal assistant",
      title: "ARS Assistant",
      subtitle: "Initial guidance · 24/7",
      resetTitle: "New conversation",
      closeTitle: "Close chat",
      disclaimer:
        "Informational guidance only; does not replace formal legal advice. Please do not share ID numbers or sensitive data here.",
      welcome:
        "Hello, I am the virtual assistant for **ARS Advocats i Assessors** (Granollers). Briefly tell me about your legal matter and I will let you know how our team can help.",
      placeholder: "Briefly describe your legal question...",
      sendAria: "Send message",
      btnForm: "Send to contact form",
      btnWa: "Continue on WhatsApp",
      chips: [
        "Divorce or custody",
        "Unfair dismissal",
        "Inheritance / wills",
        "Eviction or rental",
        "Urgent criminal matter",
      ],
      errConnection:
        "We cannot reach the assistant right now. You can contact us directly on WhatsApp (+34 668 556 252) or call +34 938 795 876.",
      errNotDeployed:
        "The Cloudflare Worker code is pending activation. Meanwhile, you can reach the firm directly at +34 938 795 876.",
      waIntro: "Hello, I had an initial chat with the ARS Advocats web assistant. Summary of my case:",
      formIntro: "[Summary generated from Web Assistant]",
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
    if (/divorci|custòdi|custodi|aliments|alimentos|família|familia|conveni/.test(t)) return "familia";
    if (/accident|trànsit|tráfico|indemnitz|indemniz/.test(t)) return "accidents";
    if (/herènci|herenci|testament|legítima|legitima|successi/.test(t)) return "herencies";
    if (/penal|detingut|detenido|comissari|comisaría|denúnci|denunci|violènci|violenci|delict/.test(t)) return "penal";
    if (/societat|sociedad|mercantil|soci|socio|compliance|empresa/.test(t)) return "mercantil";
    if (/acomiad|despid|laboral|salari|finiquit|cmac|incapacitat|inss/.test(t)) return "laboral";
    if (/desnonament|desahuci|lloguer|alquiler|arrendament|hipotec|clàusula|clausula|comunitat/.test(t)) return "immobiliari";
    if (/segona oportunitat|segunda oportunidad|concurs|deute|deuda/.test(t)) return "segona-oportunitat";
    return "altres";
  }

  function buildCaseSummary(messages) {
    const userTurns = messages
      .filter((m) => m.role === "user")
      .map((m) => m.text.trim())
      .filter(Boolean);
    return userTurns.join(" | ").slice(0, 600);
  }

  function initChatbot() {
    let lang = getLang();
    let isOpen = false;
    let isSending = false;
    let messages = []; // { role: 'user' | 'assistant', text: string }

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
      <span class="ars-chat-launcher-label"></span>
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
            <img src="assets/images/apple-touch-icon.png" alt="ARS Advocats" class="ars-chat-avatar-img" width="24" height="24">
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
      launcherLabel: launcher.querySelector(".ars-chat-launcher-label"),
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

    function updateHandoffLinks() {
      const hasUserMsg = messages.some((m) => m.role === "user");
      els.handoff.classList.toggle("is-visible", hasUserMsg);
      if (hasUserMsg) {
        const t = I18N[lang];
        const summary = buildCaseSummary(messages);
        const waText = encodeURIComponent(`${t.waIntro} ${summary}`);
        els.toWaLink.href = `https://wa.me/${WHATSAPP_NUMBER}?text=${waText}`;
      }
    }

    function renderWelcome() {
      const t = I18N[lang];
      els.messagesBox.innerHTML = "";

      const welcomeBubble = document.createElement("div");
      welcomeBubble.className = "ars-chat-msg ars-chat-msg--assistant";
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

    function applyLanguage(newLang) {
      lang = I18N[newLang] ? newLang : "ca";
      const t = I18N[lang];
      els.launcherLabel.textContent = t.launcher;
      launcher.setAttribute("aria-label", t.launcherAria);
      els.title.textContent = t.title;
      els.subtitle.textContent = t.subtitle;
      els.resetBtn.title = t.resetTitle;
      els.resetBtn.setAttribute("aria-label", t.resetTitle);
      els.closeBtn.title = t.closeTitle;
      els.closeBtn.setAttribute("aria-label", t.closeTitle);
      els.disclaimer.textContent = t.disclaimer;
      els.input.placeholder = t.placeholder;
      els.sendBtn.setAttribute("aria-label", t.sendAria);
      els.toFormBtn.textContent = t.btnForm;
      els.toWaLink.textContent = t.btnWa;

      if (messages.length === 0) {
        renderWelcome();
      } else {
        updateHandoffLinks();
      }
    }

    function openChat() {
      isOpen = true;
      panel.classList.add("is-open");
      launcher.classList.add("is-hidden");
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
      renderWelcome();
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

      const chipsEl = els.messagesBox.querySelector("#arsChatChips");
      if (chipsEl) chipsEl.remove();

      isSending = true;
      els.sendBtn.disabled = true;
      els.input.value = "";
      els.input.style.height = "auto";

      messages.push({ role: "user", text });
      appendMessageBubble("user", formatSafeText(text));
      updateHandoffLinks();

      const assistantBubble = appendMessageBubble(
        "assistant",
        `<span class="ars-chat-typing" aria-label="..."><span></span><span></span><span></span></span>`
      );

      try {
        const response = await fetch(WORKER_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ messages, lang }),
        });

        const contentType = response.headers.get("Content-Type") || "";

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        // Detect default Cloudflare "Hello World" Worker if user hasn't pasted code yet
        if (contentType.includes("text/plain")) {
          const plain = await response.text();
          if (plain.toLowerCase().includes("hello world")) {
            assistantBubble.className = "ars-chat-msg ars-chat-msg--error";
            assistantBubble.innerHTML = formatSafeText(I18N[lang].errNotDeployed);
            return;
          }
          assistantBubble.innerHTML = formatSafeText(plain);
          messages.push({ role: "assistant", text: plain });
          return;
        }

        if (!response.body) {
          throw new Error("Empty response body");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";
        let fullText = "";

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });

          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed.startsWith("data:")) continue;
            const jsonStr = trimmed.slice(5).trim();
            if (!jsonStr || jsonStr === "[DONE]") continue;
            try {
              const parsed = JSON.parse(jsonStr);
              const parts = parsed?.candidates?.[0]?.content?.parts;
              if (Array.isArray(parts)) {
                for (const part of parts) {
                  if (typeof part.text === "string") {
                    fullText += part.text;
                  }
                }
                assistantBubble.innerHTML = formatSafeText(fullText);
                scrollToBottom();
              }
            } catch {
              // Ignore partial/malformed SSE frames
            }
          }
        }

        if (!fullText.trim()) {
          throw new Error("No text generated");
        }

        messages.push({ role: "assistant", text: fullText.trim() });
      } catch (err) {
        console.error("[ARS Chat]", err);
        assistantBubble.className = "ars-chat-msg ars-chat-msg--error";
        assistantBubble.innerHTML = formatSafeText(I18N[lang].errConnection);
      } finally {
        isSending = false;
        els.sendBtn.disabled = false;
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
      els.input.style.height = Math.min(els.input.scrollHeight, 96) + "px";
    });

    // Handoff to contact form
    els.toFormBtn.addEventListener("click", () => {
      const t = I18N[lang];
      const summary = buildCaseSummary(messages);
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
