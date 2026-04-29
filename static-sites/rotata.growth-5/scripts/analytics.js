// Consent-aware analytics framework. Add IDs through build env vars.
const config = window.ROTATA_CONFIG || {};
window.dataLayer = window.dataLayer || [];
window.rotataTrack = (eventName, payload = {}) => {
  const event = { event: eventName, ...payload, page: location.pathname, ts: new Date().toISOString() };
  window.dataLayer.push(event);
  if (window.gtag) window.gtag("event", eventName, payload);
  if (window.lintrk && eventName.includes("linkedin")) window.lintrk("track", payload);
};

const loadScript = (src, attrs = {}) => {
  if (!src || document.querySelector(`script[src="${src}"]`)) return;
  const script = document.createElement("script");
  script.async = true;
  script.src = src;
  Object.entries(attrs).forEach(([key, value]) => script.setAttribute(key, value));
  document.head.appendChild(script);
};

const loadAnalytics = () => {
  if (config.gtmId) {
    window.dataLayer.push({ "gtm.start": Date.now(), event: "gtm.js" });
    loadScript(`https://www.googletagmanager.com/gtm.js?id=${config.gtmId}`);
  }
  if (config.ga4Id) {
    loadScript(`https://www.googletagmanager.com/gtag/js?id=${config.ga4Id}`);
    window.gtag = function(){ window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", config.ga4Id, { anonymize_ip: true });
  }
  if (config.clarityId) {
    window.clarity = window.clarity || function(){ (window.clarity.q = window.clarity.q || []).push(arguments); };
    loadScript(`https://www.clarity.ms/tag/${config.clarityId}`);
  }
};

const loadMarketing = () => {
  if (config.linkedinPartnerId && !window.lintrk) {
    window._linkedin_data_partner_ids = window._linkedin_data_partner_ids || [];
    window._linkedin_data_partner_ids.push(config.linkedinPartnerId);
    loadScript("https://snap.licdn.com/li.lms-analytics/insight.min.js");
  }
  if (config.hubspotPortalId) {
    loadScript(`https://js.hs-scripts.com/${config.hubspotPortalId}.js`);
  }
};

const applyConsent = (consent) => {
  if (consent.analytics) loadAnalytics();
  if (consent.marketing) loadMarketing();
};
window.addEventListener("rotata:consent", (event) => applyConsent(event.detail));
applyConsent(window.rotataConsent || {});

document.addEventListener("click", (event) => {
  const tracked = event.target.closest("[data-track]");
  if (tracked) window.rotataTrack(tracked.dataset.track, { text: tracked.textContent.trim(), href: tracked.href || "" });
});
