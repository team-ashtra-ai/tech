const rotataPartialsReady = window.RotataPartialsReady || Promise.resolve();
rotataPartialsReady.then(() => {
const siteBasePath = window.ROTATA_SITE_BASE || new URL("../", import.meta.url).pathname;
const withSiteBase = (path) => `${siteBasePath}${String(path || "").replace(/^\/+/, "")}`;
const menuButton = document.querySelector("[data-concept-menu]");
const mobilePanel = document.querySelector("[data-concept-mobile]");
const closeButton = document.querySelector("[data-concept-menu-close]");
const lang = document.documentElement.lang.startsWith("fr")
  ? "fr"
  : document.documentElement.lang.startsWith("en")
    ? "en"
    : "es";
const localeCopy = {
  en: {
    menu: "Menu",
    close: "Close",
    langLabel: "Language",
    whatsapp: "WhatsApp",
    chatbot: "Soy Rotbot",
    chatTitle: "Soy Rotbot",
    chatLead: "B2B systems assistant for CRM, data, outbound, ROI and automation.",
    chatOpen: "Open assistant",
    chatClose: "Close assistant",
    backTop: "Back to top",
    invalid: "Please complete the required fields.",
    success: "Request received. Rotata will review the context and respond with next steps.",
    prompts: [
      ["Map CRM structure", "We start with lifecycle, stages, ownership and reporting logic before any automation layer changes."],
      ["Improve conversion", "The first review is routing, follow-up timing, qualification rules and the handoff path."],
      ["Estimate ROI", "Use the ROI framing page first, then compare conversion, speed and recovered value from less friction."],
    ],
  },
  es: {
    menu: "Menú",
    close: "Cerrar",
    langLabel: "Idioma",
    whatsapp: "WhatsApp",
    chatbot: "Soy Rotbot",
    chatTitle: "Soy Rotbot",
    chatLead: "Asistente de sistemas B2B para CRM, datos, outbound, ROI y automatizacion.",
    chatOpen: "Abrir asistente",
    chatClose: "Cerrar asistente",
    backTop: "Volver arriba",
    invalid: "Completa los campos obligatorios.",
    success: "Solicitud recibida. Rotata revisará el contexto y responderá con los siguientes pasos.",
    prompts: [
      ["Estructurar el CRM", "Empezamos por ciclo de vida, etapas, ownership y reporting antes de tocar automatización."],
      ["Mejorar conversión", "La primera revisión es routing, tiempos de seguimiento, reglas de cualificación y handoffs."],
      ["Calcular ROI", "Usa primero la página de ROI y luego comparamos conversión, velocidad y valor recuperado."],
    ],
  },
  fr: {
    menu: "Menu",
    close: "Fermer",
    langLabel: "Langue",
    whatsapp: "WhatsApp",
    chatbot: "Soy Rotbot",
    chatTitle: "Soy Rotbot",
    chatLead: "Assistant systemes B2B pour CRM, donnees, outbound, ROI et automatisation.",
    chatOpen: "Ouvrir l'assistant",
    chatClose: "Fermer l'assistant",
    backTop: "Retour en haut",
    invalid: "Merci de compléter les champs obligatoires.",
    success: "Demande reçue. Rotata va revoir le contexte et répondre avec les prochaines étapes.",
    prompts: [
      ["Structurer le CRM", "Nous commençons par le cycle de vie, les étapes, l'ownership et le reporting avant l'automatisation."],
      ["Améliorer la conversion", "La première revue couvre le routing, le suivi, les règles de qualification et les handoffs."],
      ["Calculer le ROI", "Commencez par la page ROI puis comparez conversion, vitesse et valeur récupérée."],
    ],
  },
}[lang];

const localePath = (() => {
  const relativePath = window.location.pathname.startsWith(siteBasePath)
    ? window.location.pathname.slice(siteBasePath.length - 1)
    : window.location.pathname;
  const cleaned = relativePath.replace(/^\/(en|es|fr)(?=\/|$)/, "");
  return cleaned || "/";
})();
const localeHref = (targetLang) => withSiteBase(`${targetLang}${localePath === "/" ? "/" : localePath}`);

const setMenu = (open) => {
  menuButton?.setAttribute("aria-expanded", String(open));
  if (mobilePanel) mobilePanel.hidden = !open;
  document.documentElement.classList.toggle("concept-menu-open", open);
};

menuButton?.addEventListener("click", () => {
  setMenu(menuButton.getAttribute("aria-expanded") !== "true");
});

closeButton?.addEventListener("click", () => setMenu(false));

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") setMenu(false);
});

const injectLanguageSwitcher = () => {
  const actions = document.querySelector('[class*="header-actions"], [class*="actions-top"], [class*="top-actions"], .dg-header-note');
  if (actions && !actions.querySelector(".concept-lang-switch")) {
    const switcher = document.createElement("nav");
    switcher.className = "concept-lang-switch";
    switcher.setAttribute("aria-label", localeCopy.langLabel);
    ["en", "es", "fr"].forEach((code) => {
      const link = document.createElement("a");
      link.href = localeHref(code);
      link.textContent = code.toUpperCase();
      if (code === lang) link.setAttribute("aria-current", "page");
      switcher.appendChild(link);
    });
    actions.insertBefore(switcher, actions.firstChild);
  }

  if (mobilePanel && !mobilePanel.querySelector(".concept-mobile-languages")) {
    const switcher = document.createElement("nav");
    switcher.className = "concept-mobile-languages";
    switcher.setAttribute("aria-label", localeCopy.langLabel);
    ["en", "es", "fr"].forEach((code) => {
      const link = document.createElement("a");
      link.href = localeHref(code);
      link.textContent = code.toUpperCase();
      if (code === lang) link.setAttribute("aria-current", "page");
      switcher.appendChild(link);
    });
    mobilePanel.appendChild(switcher);
  }
};

const revealSections = () => {
  const items = Array.from(
    document.querySelectorAll(".concept-page-hero, .concept-section, .concept-special, .concept-final-cta"),
  );
  items.forEach((item) => item.classList.add("concept-reveal"));
  if (!("IntersectionObserver" in window) || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    items.forEach((item) => item.classList.add("is-visible"));
    return;
  }
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.14 });
  items.forEach((item) => observer.observe(item));
};

const injectSupportLayer = () => {
  if (document.querySelector(".concept-floating")) return;

  const rotbotSrc = withSiteBase("assets/images/rotata-rotbot-ai-assistant.png");
  const whatsappIcon = `
    <svg aria-hidden="true" viewBox="0 0 32 32" focusable="false">
      <path d="M16.03 3.2A12.72 12.72 0 0 0 3.3 15.91c0 2.24.59 4.42 1.71 6.34L3.2 28.8l6.71-1.76a12.7 12.7 0 0 0 6.11 1.56h.01A12.72 12.72 0 0 0 28.8 15.89 12.74 12.74 0 0 0 16.03 3.2Zm0 23.23h-.01a10.55 10.55 0 0 1-5.38-1.47l-.39-.23-3.98 1.04 1.06-3.88-.25-.4a10.5 10.5 0 1 1 8.95 4.94Zm5.77-7.87c-.32-.16-1.87-.92-2.16-1.03-.29-.1-.5-.16-.71.16-.21.32-.81 1.03-1 1.24-.18.21-.37.24-.69.08-.32-.16-1.34-.49-2.55-1.57-.94-.84-1.58-1.88-1.76-2.2-.18-.32-.02-.49.14-.65.14-.14.32-.37.47-.55.16-.18.21-.32.32-.53.1-.21.05-.4-.03-.55-.08-.16-.71-1.72-.98-2.36-.26-.62-.52-.54-.71-.55h-.61c-.21 0-.55.08-.84.4-.29.32-1.1 1.07-1.1 2.61 0 1.54 1.13 3.03 1.29 3.24.16.21 2.22 3.39 5.38 4.75.75.32 1.34.51 1.8.65.76.24 1.45.2 1.99.12.61-.09 1.87-.76 2.13-1.5.26-.74.26-1.37.18-1.5-.08-.13-.29-.21-.61-.37Z"/>
    </svg>`;
  const floating = document.createElement("div");
  floating.className = "concept-floating";
  floating.innerHTML = `
    <button class="concept-fab concept-fab-chat" type="button" data-concept-chat-toggle aria-expanded="false" aria-controls="concept-chat-panel" aria-label="${localeCopy.chatOpen}">
      <img src="${rotbotSrc}" alt="" width="46" height="46">
    </button>
    <button class="concept-fab concept-fab-top" type="button" data-concept-top aria-label="${localeCopy.backTop}">
      <svg aria-hidden="true" viewBox="0 0 24 24" focusable="false"><path d="M12 5 5.5 11.5l1.4 1.4L11 8.82V20h2V8.82l4.1 4.08 1.4-1.4L12 5Z"/></svg>
    </button>
    <a class="concept-fab concept-fab-whatsapp" href="https://wa.me/34649498272?text=${encodeURIComponent(localeCopy.chatLead)}" aria-label="${localeCopy.whatsapp}">${whatsappIcon}</a>
  `;

  const panel = document.createElement("aside");
  panel.className = "concept-chat-panel";
  panel.id = "concept-chat-panel";
  panel.hidden = true;
  panel.innerHTML = `
    <div class="concept-chat-head">
      <img src="${rotbotSrc}" alt="" width="46" height="46">
      <div>
        <strong>${localeCopy.chatTitle}</strong>
        <p>${localeCopy.chatLead}</p>
      </div>
      <button type="button" data-concept-chat-close aria-label="${localeCopy.chatClose}">×</button>
    </div>
    <div class="concept-chat-log" data-concept-chat-log>
      <p class="concept-chat-message is-bot">${localeCopy.chatLead}</p>
    </div>
    <div class="concept-chat-prompts">
      ${localeCopy.prompts
        .map(
          ([prompt, reply]) =>
            `<button type="button" data-concept-chat-prompt data-concept-chat-reply="${reply.replace(/"/g, "&quot;")}">${prompt}</button>`,
        )
        .join("")}
    </div>
  `;

  document.body.append(floating, panel);

  const topButton = floating.querySelector("[data-concept-top]");
  const chatToggle = floating.querySelector("[data-concept-chat-toggle]");
  const chatClose = panel.querySelector("[data-concept-chat-close]");
  const chatLog = panel.querySelector("[data-concept-chat-log]");

  topButton?.classList.add("is-visible");
  topButton?.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

  const setChat = (open) => {
    panel.hidden = !open;
    chatToggle?.setAttribute("aria-expanded", String(open));
  };
  chatToggle?.addEventListener("click", () => setChat(panel.hidden));
  chatClose?.addEventListener("click", () => setChat(false));

  panel.querySelectorAll("[data-concept-chat-prompt]").forEach((button) => {
    button.addEventListener("click", () => {
      const user = document.createElement("p");
      user.className = "concept-chat-message is-user";
      user.textContent = button.textContent?.trim() || "";
      const bot = document.createElement("p");
      bot.className = "concept-chat-message is-bot";
      bot.textContent = button.getAttribute("data-concept-chat-reply") || "";
      chatLog?.append(user, bot);
      chatLog?.scrollTo({ top: chatLog.scrollHeight, behavior: "smooth" });
    });
  });

};

const getFormsConfig = (() => {
  let promise;
  return () => {
    if (!promise) {
      promise = fetch(withSiteBase("content/forms.json"), { cache: "no-store" })
        .then((response) => (response.ok ? response.json() : {}))
        .catch(() => ({}));
    }
    return promise;
  };
})();

const enhanceForms = async () => {
  const config = await getFormsConfig();
  document.querySelectorAll(".concept-form").forEach((form) => {
    if (form.dataset.enhanced === "true") return;
    form.dataset.enhanced = "true";
    form.setAttribute("novalidate", "");
    let status = form.querySelector(".concept-form-status");
    if (!status) {
      status = document.createElement("p");
      status.className = "concept-form-status";
      status.setAttribute("role", "status");
      status.setAttribute("aria-live", "polite");
      form.appendChild(status);
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      let valid = true;
      form.querySelectorAll("[required]").forEach((field) => {
        const ok = field.value.trim() && field.checkValidity();
        field.setAttribute("aria-invalid", String(!ok));
        valid = valid && ok;
      });
      if (!valid) {
        status.textContent = localeCopy.invalid;
        return;
      }

      const endpoint = config.contact_endpoint || "";
      if (!endpoint || endpoint.includes("REPLACE_WITH_FORM_ID")) {
        window.location.href = `${form.action}?${new URLSearchParams(new FormData(form)).toString()}`;
        return;
      }

      try {
        const response = await fetch(endpoint, {
          method: "POST",
          headers: { Accept: "application/json" },
          body: new FormData(form),
        });
        if (!response.ok) throw new Error("submit");
        form.reset();
        status.textContent = localeCopy.success;
      } catch {
        status.textContent = localeCopy.invalid;
      }
    });
  });
};


const markActiveNavigation = () => {
  const path = window.location.pathname.replace(/\/+$/, "/") || "/";
  document.querySelectorAll("header a[href], .concept-mobile-panel a[href]").forEach((link) => {
    const href = new URL(link.getAttribute("href"), window.location.href).pathname.replace(/\/+$/, "/") || "/";
    if (href === path) link.setAttribute("aria-current", "page");
  });
};

markActiveNavigation();
injectLanguageSwitcher();
revealSections();
injectSupportLayer();
enhanceForms();

});
