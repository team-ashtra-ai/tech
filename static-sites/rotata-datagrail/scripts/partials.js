const detectLocale = () => {
  const match = window.location.pathname.match(/^\/(en|es|fr)(?=\/|$)/);
  if (match) return match[1];
  const lang = document.documentElement.lang || "en";
  return lang.startsWith("fr") ? "fr" : lang.startsWith("es") ? "es" : "en";
};

const loadPartial = async (placeholder) => {
  const name = placeholder.dataset.partial;
  const locale = placeholder.dataset.partialLocale || detectLocale();
  if (!name) return;
  try {
    const response = await fetch(`/partials/${locale}/${name}.html`, { cache: "force-cache" });
    if (!response.ok) throw new Error(`${response.status} ${name}`);
    placeholder.innerHTML = await response.text();
    placeholder.dataset.partialLoaded = "true";
  } catch (error) {
    placeholder.dataset.partialError = "true";
    console.warn("Rotata partial failed", name, error);
  }
};

const placeholders = Array.from(document.querySelectorAll("[data-partial]"));
window.RotataPartialsReady = Promise.all(placeholders.map(loadPartial)).then(() => {
  document.dispatchEvent(new CustomEvent("rotata:partials-ready"));
});

export default window.RotataPartialsReady;
