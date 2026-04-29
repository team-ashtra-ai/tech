import "./shared.js";

const cards = Array.from(document.querySelectorAll(".db-card"));

cards.forEach((card) => {
  card.tabIndex = 0;
  card.addEventListener("pointerenter", () => {
    cards.forEach((item) => item.classList.toggle("is-active", item === card));
  });
  card.addEventListener("focus", () => {
    cards.forEach((item) => item.classList.toggle("is-active", item === card));
  });
});

document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  cards.forEach((card) => card.classList.remove("is-active"));
});
