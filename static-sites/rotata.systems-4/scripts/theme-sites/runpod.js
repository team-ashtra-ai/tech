import "./shared.js";

const steps = Array.from(document.querySelectorAll(".rp-flow-step"));
let active = 0;

const update = () => {
  steps.forEach((step, index) => step.classList.toggle("is-active", index === active));
  active = (active + 1) % Math.max(steps.length, 1);
};

if (steps.length) {
  update();
  window.setInterval(update, 2200);
}
