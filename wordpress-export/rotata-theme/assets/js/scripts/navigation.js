const header = document.querySelector("[data-site-header]");
const toggle = document.querySelector("[data-menu-toggle]");
const panel = document.querySelector("[data-mobile-menu]");
const themeToggle = document.querySelector("[data-theme-toggle]");

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

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeMenu();
});
panel?.addEventListener("click", (event) => {
  if (event.target.closest("a")) closeMenu();
});

const storedTheme = localStorage.getItem("rotata-theme");
if (storedTheme) document.documentElement.dataset.theme = storedTheme;
themeToggle?.addEventListener("click", () => {
  const next = document.documentElement.dataset.theme === "light" ? "dark" : "light";
  document.documentElement.dataset.theme = next;
  localStorage.setItem("rotata-theme", next);
  window.rotataTrack?.("theme_toggle", { theme: next });
});
