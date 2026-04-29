const root = document.documentElement;
const themeButtons = Array.from(document.querySelectorAll("[data-design-theme-option]"));
const themeSummary = document.querySelector("[data-theme-summary]");
const themeAnnouncer = document.querySelector("[data-theme-announcer]");
const themeColorMeta = document.querySelector('meta[name="theme-color"]');
const storageKeys = {
  theme: "rotata-design-theme",
  surface: "rotata-design-surface",
  color: "rotata-design-theme-color",
};

const updateButtons = (activeId) => {
  themeButtons.forEach((button) => {
    const active = button.dataset.designThemeOption === activeId;
    button.setAttribute("aria-pressed", String(active));
  });
};

const syncThemeContent = (button, { announce = false } = {}) => {
  if (!button) return;
  if (themeSummary) themeSummary.textContent = button.dataset.themeSummary || "";
  if (themeColorMeta && button.dataset.themeColor) {
    themeColorMeta.setAttribute("content", button.dataset.themeColor);
  }
  if (announce && themeAnnouncer) {
    themeAnnouncer.textContent = button.dataset.themeAnnouncement || button.dataset.themeLabel || "";
  }
};

const applyTheme = (button, { persist = true, announce = false } = {}) => {
  if (!button) return;
  const theme = button.dataset.designThemeOption;
  const surface = button.dataset.themeSurface || "dark";
  root.dataset.designTheme = theme;
  root.dataset.themeSurface = surface;
  updateButtons(theme);
  syncThemeContent(button, { announce });
  if (persist) {
    localStorage.setItem(storageKeys.theme, theme);
    localStorage.setItem(storageKeys.surface, surface);
    if (button.dataset.themeColor) {
      localStorage.setItem(storageKeys.color, button.dataset.themeColor);
    }
  }
};

const fallbackButton =
  themeButtons.find((button) => button.dataset.themeDefault === "true") ||
  themeButtons[0];

const storedTheme = localStorage.getItem(storageKeys.theme);
const activeButton =
  themeButtons.find((button) => button.dataset.designThemeOption === storedTheme) ||
  fallbackButton;

applyTheme(activeButton, { persist: false });

themeButtons.forEach((button) => {
  button.addEventListener("click", () => {
    applyTheme(button, { announce: true });
    window.rotataTrack?.("theme_demo_switch", { theme: button.dataset.designThemeOption });
  });
});
