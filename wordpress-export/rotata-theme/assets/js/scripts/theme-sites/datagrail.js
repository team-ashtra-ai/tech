import "./shared.js";

const button = document.querySelector("[data-dg-menu]");
const nav = document.querySelector("[data-dg-nav]");

button?.addEventListener("click", () => {
  const open = button.getAttribute("aria-expanded") !== "true";
  button.setAttribute("aria-expanded", String(open));
  nav?.classList.toggle("is-open", open);
});

document.addEventListener("click", (event) => {
  if (!button || !nav || button.contains(event.target) || nav.contains(event.target)) return;
  button.setAttribute("aria-expanded", "false");
  nav.classList.remove("is-open");
});
