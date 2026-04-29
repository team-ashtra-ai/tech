const header = document.querySelector("[data-site-header]");
const toggle = document.querySelector("[data-menu-toggle]");
const panel = document.querySelector("[data-mobile-menu]");
const closeButton = document.querySelector("[data-menu-close]");
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
let closeTimer = 0;

const setScrolled = () => header?.classList.toggle("is-scrolled", window.scrollY > 12);
setScrolled();
window.addEventListener("scroll", setScrolled, { passive: true });

const resetMobileGroups = () => {
  panel?.querySelectorAll("details[open]").forEach((item) => item.removeAttribute("open"));
};

const finishClose = (restoreFocus) => {
  document.body.classList.remove("menu-open");
  panel?.setAttribute("hidden", "");
  if (restoreFocus) toggle?.focus();
  closeTimer = 0;
};

const closeMenu = ({ restoreFocus = true, resetGroups = true } = {}) => {
  if (!panel || !toggle) return;
  window.clearTimeout(closeTimer);
  toggle?.setAttribute("aria-expanded", "false");
  panel.classList.remove("is-open");
  if (resetGroups) resetMobileGroups();
  if (reducedMotion.matches) {
    finishClose(restoreFocus);
    return;
  }
  closeTimer = window.setTimeout(() => finishClose(restoreFocus), 320);
};

const openMenu = () => {
  if (!panel || !toggle) return;
  window.clearTimeout(closeTimer);
  toggle.setAttribute("aria-expanded", "true");
  document.body.classList.add("menu-open");
  panel.removeAttribute("hidden");
  requestAnimationFrame(() => panel.classList.add("is-open"));
  const firstTarget = panel.querySelector("a, button, summary");
  firstTarget?.focus();
};

const getFocusableInPanel = () =>
  panel
    ? Array.from(panel.querySelectorAll('a[href], button:not([disabled]), summary, [tabindex]:not([tabindex="-1"])'))
        .filter((element) => !element.hasAttribute("hidden"))
    : [];

toggle?.addEventListener("click", () => {
  const open = toggle.getAttribute("aria-expanded") !== "true";
  if (open) {
    openMenu();
  } else {
    closeMenu();
  }
});
closeButton?.addEventListener("click", () => closeMenu());

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && toggle?.getAttribute("aria-expanded") === "true") {
    event.preventDefault();
    closeMenu();
  }
  if (event.key === "Tab" && toggle?.getAttribute("aria-expanded") === "true") {
    const focusable = getFocusableInPanel();
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }
});
panel?.addEventListener("click", (event) => {
  if (event.target.closest("a")) closeMenu({ restoreFocus: false, resetGroups: false });
});
