const siteBasePath = (() => {
  const scriptPath = new URL(import.meta.url).pathname;
  return scriptPath.replace(/\/scripts\/partials\.js$/, "/");
})();

window.ROTATA_SITE_BASE = siteBasePath;

const withSiteBase = (path) => {
  const clean = String(path || "").replace(/^\/+/, "");
  return `${siteBasePath}${clean}`;
};

const rebaseRootReference = (_match, attribute, target) => {
  const cleanSiteBase = siteBasePath.replace(/^\/+/, "");
  if (target.startsWith(cleanSiteBase)) {
    return `${attribute}="/${target}"`;
  }
  return `${attribute}="${siteBasePath}${target}"`;
};

const rebaseMarkup = (markup) =>
  markup
    .replace(/\b(href|src|action)=["']\/(?!\/)([^"']*)["']/g, rebaseRootReference)
    .replace(/url\(["']?\/(assets\/[^)"']+)["']?\)/g, `url('${siteBasePath}$1')`)
    .replaceAll("__ROTATA_BASE__", siteBasePath);

const detectLocale = () => {
  const relativePath = window.location.pathname.startsWith(siteBasePath)
    ? window.location.pathname.slice(siteBasePath.length - 1)
    : window.location.pathname;
  const match = relativePath.match(/^\/(en|es|fr)(?=\/|$)/);
  if (match) return match[1];
  const lang = document.documentElement.lang || "en";
  return lang.startsWith("fr") ? "fr" : lang.startsWith("es") ? "es" : "en";
};

const loadPartial = async (placeholder) => {
  const name = placeholder.dataset.partial;
  const locale = placeholder.dataset.partialLocale || detectLocale();
  if (!name) return;
  try {
    const response = await fetch(withSiteBase(`partials/${locale}/${name}.html`), { cache: "force-cache" });
    if (!response.ok) throw new Error(`${response.status} ${name}`);
    placeholder.innerHTML = rebaseMarkup(await response.text());
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
