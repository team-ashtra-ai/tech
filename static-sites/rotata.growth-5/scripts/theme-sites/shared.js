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
    chatbot: "Vera agent",
    chatTitle: "Vera agent",
    chatLead: "Human controls for the growth system.",
    chatOpen: "Open assistant",
    chatClose: "Close assistant",
    backTop: "Back to top",
    cookieTitle: "Cookie preferences",
    cookieBody: "We use necessary storage for the site and optional analytics or marketing scripts only after consent.",
    acceptAll: "Accept all",
    necessary: "Necessary only",
    reject: "Reject",
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
    chatbot: "Agente Vera",
    chatTitle: "Agente Vera",
    chatLead: "Controles humanos para el sistema de crecimiento.",
    chatOpen: "Abrir asistente",
    chatClose: "Cerrar asistente",
    backTop: "Volver arriba",
    cookieTitle: "Preferencias de cookies",
    cookieBody: "Usamos almacenamiento necesario y scripts opcionales de analítica o marketing solo tras consentimiento.",
    acceptAll: "Aceptar todo",
    necessary: "Solo necesarias",
    reject: "Rechazar",
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
    chatbot: "Agent Vera",
    chatTitle: "Agent Vera",
    chatLead: "Contrôles humains pour le système de croissance.",
    chatOpen: "Ouvrir l'assistant",
    chatClose: "Fermer l'assistant",
    backTop: "Retour en haut",
    cookieTitle: "Préférences cookies",
    cookieBody: "Nous utilisons le stockage nécessaire et les scripts optionnels uniquement après consentement.",
    acceptAll: "Tout accepter",
    necessary: "Nécessaires seulement",
    reject: "Refuser",
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
  const cleaned = window.location.pathname.replace(/^\/(en|es|fr)(?=\/|$)/, "");
  return cleaned || "/";
})();
const localeHref = (targetLang) => `/${targetLang}${localePath === "/" ? "/" : localePath}`;

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
  const actions = document.querySelector('[class*="header-actions"]');
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

  const floating = document.createElement("div");
  floating.className = "concept-floating";
  floating.innerHTML = `
    <button class="concept-fab concept-fab-top" type="button" data-concept-top aria-label="${localeCopy.backTop}">↑</button>
    <a class="concept-fab concept-fab-whatsapp" href="https://wa.me/34649498272?text=${encodeURIComponent(localeCopy.chatLead)}" aria-label="${localeCopy.whatsapp}">WA</a>
    <button class="concept-fab concept-fab-chat" type="button" data-concept-chat-toggle aria-expanded="false" aria-controls="concept-chat-panel" aria-label="${localeCopy.chatOpen}">${localeCopy.chatbot}</button>
  `;

  const panel = document.createElement("aside");
  panel.className = "concept-chat-panel";
  panel.id = "concept-chat-panel";
  panel.hidden = true;
  panel.innerHTML = `
    <div class="concept-chat-head">
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

  const cookie = document.createElement("section");
  cookie.className = "concept-cookie";
  cookie.hidden = true;
  cookie.innerHTML = `
    <div>
      <strong>${localeCopy.cookieTitle}</strong>
      <p>${localeCopy.cookieBody}</p>
    </div>
    <div class="concept-cookie-actions">
      <button type="button" data-concept-cookie-accept>${localeCopy.acceptAll}</button>
      <button type="button" data-concept-cookie-necessary>${localeCopy.necessary}</button>
      <button type="button" data-concept-cookie-reject>${localeCopy.reject}</button>
    </div>
  `;

  document.body.append(floating, panel, cookie);

  const topButton = floating.querySelector("[data-concept-top]");
  const chatToggle = floating.querySelector("[data-concept-chat-toggle]");
  const chatClose = panel.querySelector("[data-concept-chat-close]");
  const chatLog = panel.querySelector("[data-concept-chat-log]");
  const cookieKey = "rotata-concept-consent-v1";

  const setTop = () => topButton?.classList.toggle("is-visible", window.scrollY > 520);
  setTop();
  window.addEventListener("scroll", setTop, { passive: true });
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

  if (!localStorage.getItem(cookieKey)) cookie.hidden = false;
  cookie.querySelector("[data-concept-cookie-accept]")?.addEventListener("click", () => {
    localStorage.setItem(cookieKey, JSON.stringify({ necessary: true, analytics: true, marketing: true }));
    cookie.hidden = true;
  });
  cookie.querySelector("[data-concept-cookie-necessary]")?.addEventListener("click", () => {
    localStorage.setItem(cookieKey, JSON.stringify({ necessary: true }));
    cookie.hidden = true;
  });
  cookie.querySelector("[data-concept-cookie-reject]")?.addEventListener("click", () => {
    localStorage.setItem(cookieKey, JSON.stringify({ necessary: true, analytics: false, marketing: false }));
    cookie.hidden = true;
  });
};

const getFormsConfig = (() => {
  let promise;
  return () => {
    if (!promise) {
      promise = fetch("/content/forms.json", { cache: "no-store" })
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

injectLanguageSwitcher();
revealSections();
injectSupportLayer();
enhanceForms();
