const menuButton = document.querySelector("[data-concept-menu]");
const mobilePanel = document.querySelector("[data-concept-mobile]");
const closeButton = document.querySelector("[data-concept-menu-close]");

const setMenu = (open) => {
  menuButton?.setAttribute("aria-expanded", String(open));
  if (mobilePanel) mobilePanel.hidden = !open;
  document.documentElement.classList.toggle("concept-menu-open", open);
};

menuButton?.addEventListener("click", () => {
  setMenu(menuButton.getAttribute("aria-expanded") !== "true");
});

closeButton?.addEventListener("click", () => setMenu(false));

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") setMenu(false);
});
