// Forms support validation, UTM capture, honeypot spam checks and Formspree/HubSpot-ready submission.
const params = new URLSearchParams(location.search);
const config = window.ROTATA_CONFIG || {};
const hiddenNames = ["utm_source", "utm_medium", "utm_campaign"];
const lang = document.documentElement.lang || "es";
const messages = {
  es: {
    required: "Completa los campos obligatorios.",
    connection: "Hubo un problema de conexión. Escribe a info@rotata.com.",
    success: "Solicitud recibida. Rotata revisará el contexto y responderá con los siguientes pasos.",
    locale: "es-ES",
  },
  en: {
    required: "Please complete the required fields.",
    connection: "There was a connection issue. Please email info@rotata.com.",
    success: "Request received. Rotata will review the context and respond with next steps.",
    locale: "en-GB",
  },
  fr: {
    required: "Merci de compléter les champs obligatoires.",
    connection: "Un problème de connexion est survenu. Écrivez à info@rotata.com.",
    success: "Demande reçue. Rotata va revoir le contexte et répondre avec les prochaines étapes.",
    locale: "fr-FR",
  },
}[lang.startsWith("en") ? "en" : lang.startsWith("fr") ? "fr" : "es"];

document.querySelectorAll("form[data-form]").forEach((form) => {
  hiddenNames.forEach((name) => {
    const field = form.querySelector(`[name="${name}"]`);
    if (field) field.value = params.get(name) || localStorage.getItem(`rotata-${name}`) || "";
    if (params.get(name)) localStorage.setItem(`rotata-${name}`, params.get(name));
  });
  const referrer = form.querySelector('[name="referrer"]');
  if (referrer) referrer.value = document.referrer;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const status = form.querySelector(".form-status");
    const honeypot = form.querySelector(".honeypot");
    if (honeypot && honeypot.value) return;
    let valid = true;
    form.querySelectorAll("[required]").forEach((field) => {
      const ok = field.type === "checkbox" ? field.checked : field.value.trim().length > 0 && field.checkValidity();
      field.setAttribute("aria-invalid", String(!ok));
      valid = valid && ok;
    });
    if (!valid) {
      status.textContent = messages.required;
      return;
    }
    const payload = Object.fromEntries(new FormData(form).entries());
    window.rotataTrack?.("form_submit", { form: form.dataset.form, service: payload.service_interest || "" });
    if (config.formsEndpoint) {
      try {
        await fetch(config.formsEndpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      } catch (error) {
        status.textContent = messages.connection;
        return;
      }
    }
    status.textContent = messages.success;
    form.reset();
  });
});

const calculator = document.querySelector("[data-roi-calculator]");
if (calculator) {
  const output = calculator.querySelector("[data-roi-output]");
  const update = () => {
    const leads = Number(calculator.querySelector('[name="monthly_leads"]').value || 0);
    const conversion = Number(calculator.querySelector('[name="conversion_rate"]').value || 0) / 100;
    const acv = Number(calculator.querySelector('[name="average_value"]').value || 0);
    const improvement = Number(calculator.querySelector('[name="system_improvement"]').value || 0) / 100;
    const base = leads * conversion * acv;
    const incremental = base * improvement;
    output.textContent = new Intl.NumberFormat(messages.locale, { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(incremental);
    window.rotataTrack?.("roi_interaction", { incremental_value: Math.round(incremental) });
  };
  calculator.addEventListener("input", update);
  update();
}
