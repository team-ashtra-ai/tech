document.querySelectorAll("[data-language-link]").forEach((link) => {
  link.addEventListener("click", () => {
    window.rotataTrack?.("language_switch", { language: link.dataset.languageLink });
  });
});
