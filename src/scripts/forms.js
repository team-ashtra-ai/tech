// Forms support validation, UTM capture, honeypot spam checks and Formspree/HubSpot-ready submission.
const params = new URLSearchParams(location.search);
const config = window.ROTATA_CONFIG || {};
const hiddenNames = ["utm_source", "utm_medium", "utm_campaign"];

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
      status.textContent = "Please complete the required fields.";
      return;
    }
    const payload = Object.fromEntries(new FormData(form).entries());
    window.rotataTrack?.("form_submit", { form: form.dataset.form, service: payload.service_interest || "" });
    if (config.formsEndpoint) {
      try {
        await fetch(config.formsEndpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      } catch (error) {
        status.textContent = "There was a connection issue. Please email info@rotata.com.";
        return;
      }
    }
    status.textContent = "Request received. Rotata will review the context and respond with next steps.";
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
    output.textContent = new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR", maximumFractionDigits: 0 }).format(incremental);
    window.rotataTrack?.("roi_interaction", { incremental_value: Math.round(incremental) });
  };
  calculator.addEventListener("input", update);
  update();
}
