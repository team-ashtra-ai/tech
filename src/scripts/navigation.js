const header = document.querySelector("[data-site-header]");
const toggle = document.querySelector("[data-menu-toggle]");
const panel = document.querySelector("[data-mobile-menu]");
const closeButton = document.querySelector("[data-menu-close]");
const themeToggle = document.querySelector("[data-theme-toggle]");
const themeLabel = document.querySelector("[data-theme-label]");

const setScrolled = () => header?.classList.toggle("is-scrolled", window.scrollY > 12);
setScrolled();
window.addEventListener("scroll", setScrolled, { passive: true });

const closeMenu = () => {
  document.body.classList.remove("menu-open");
  panel?.setAttribute("hidden", "");
  panel?.classList.remove("is-open");
  toggle?.setAttribute("aria-expanded", "false");
};

toggle?.addEventListener("click", () => {
  const open = toggle.getAttribute("aria-expanded") !== "true";
  toggle.setAttribute("aria-expanded", String(open));
  document.body.classList.toggle("menu-open", open);
  if (open) {
    panel?.removeAttribute("hidden");
    panel?.classList.add("is-open");
    panel?.querySelector("a")?.focus();
  } else {
    closeMenu();
  }
});
closeButton?.addEventListener("click", closeMenu);

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeMenu();
});
panel?.addEventListener("click", (event) => {
  if (event.target.closest("a")) closeMenu();
});

const storedTheme = localStorage.getItem("rotata-theme");
if (storedTheme) document.documentElement.dataset.theme = storedTheme;
const syncThemeLabel = () => {
  if (!themeLabel) return;
  const lightLabel = themeToggle?.dataset.themeLightLabel || "Light";
  const darkLabel = themeToggle?.dataset.themeDarkLabel || "Dark";
  themeLabel.textContent = document.documentElement.dataset.theme === "light" ? lightLabel : darkLabel;
};
syncThemeLabel();
themeToggle?.addEventListener("click", () => {
  const next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
  document.documentElement.dataset.theme = next;
  localStorage.setItem("rotata-theme", next);
  syncThemeLabel();
  window.rotataTrack?.("theme_toggle", { theme: next });
});
