// Consent manager: blocks analytics/marketing loaders until explicit consent.
const key = "rotata-consent-v1";
const banner = document.querySelector("[data-cookie-banner]");
const options = document.querySelector("[data-cookie-options]");
const accept = document.querySelector("[data-cookie-accept]");
const reject = document.querySelector("[data-cookie-reject]");
const manage = document.querySelector("[data-cookie-manage]");
const save = document.querySelector("[data-cookie-save]");

const defaults = { necessary: true, analytics: false, marketing: false, preferences: false };
const acceptAll = { necessary: true, analytics: true, marketing: true, preferences: true };
const read = () => {
  try { return { ...defaults, ...JSON.parse(localStorage.getItem(key) || "{}") }; }
  catch { return defaults; }
};
const apply = (consent) => {
  window.rotataConsent = consent;
  window.dispatchEvent(new CustomEvent("rotata:consent", { detail: consent }));
};
const persist = (consent) => {
  localStorage.setItem(key, JSON.stringify(consent));
  banner?.setAttribute("hidden", "");
  apply(consent);
};

if (!localStorage.getItem(key)) banner?.removeAttribute("hidden");
apply(read());
accept?.addEventListener("click", () => persist(acceptAll));
reject?.addEventListener("click", () => persist(defaults));
manage?.addEventListener("click", () => {
  options?.removeAttribute("hidden");
  save?.removeAttribute("hidden");
  manage.setAttribute("hidden", "");
});
save?.addEventListener("click", () => {
  const next = { necessary: true, analytics: false, marketing: false, preferences: false };
  document.querySelectorAll("[data-cookie-category]").forEach((input) => {
    next[input.value] = input.checked;
  });
  persist(next);
});

const autoAcceptOnScroll = () => {
  if (localStorage.getItem(key)) return;
  if (window.scrollY < Math.max(140, window.innerHeight * 0.35)) return;
  persist(acceptAll);
  window.removeEventListener("scroll", autoAcceptOnScroll);
};

window.addEventListener("scroll", autoAcceptOnScroll, { passive: true });
