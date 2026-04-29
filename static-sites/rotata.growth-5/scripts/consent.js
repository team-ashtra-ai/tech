// Consent manager: blocks analytics/marketing loaders until explicit consent.
const key = "rotata-consent-v1";
const banner = document.querySelector("[data-cookie-banner]");
const accept = document.querySelector("[data-cookie-accept]");
const necessary = document.querySelector("[data-cookie-necessary]");
const reject = document.querySelector("[data-cookie-reject]");

const defaults = { necessary: true, analytics: false, marketing: false, preferences: false };
const acceptAll = { necessary: true, analytics: true, marketing: true, preferences: true };
const storage = {
  get() {
    try {
      return window.localStorage.getItem(key);
    } catch {
      return null;
    }
  },
  set(value) {
    try {
      window.localStorage.setItem(key, value);
      return true;
    } catch {
      return false;
    }
  },
};
const hasStoredConsent = () => !!storage.get();
const read = () => {
  try { return { ...defaults, ...JSON.parse(storage.get() || "{}") }; }
  catch { return defaults; }
};
const apply = (consent) => {
  window.rotataConsent = consent;
  window.dispatchEvent(new CustomEvent("rotata:consent", { detail: consent }));
};
const setBannerHidden = (hidden) => {
  if (!banner) return;
  if (hidden) banner.setAttribute("hidden", "");
  else banner.removeAttribute("hidden");
};
const persist = (consent) => {
  storage.set(JSON.stringify(consent));
  apply(consent);
  setBannerHidden(true);
  banner?.style.setProperty("display", "none");
};

if (!hasStoredConsent()) setBannerHidden(false);
apply(read());
accept?.addEventListener("click", () => persist(acceptAll));
necessary?.addEventListener("click", () => persist(defaults));
reject?.addEventListener("click", () => persist(defaults));
