import "./shared.js";

const guardrails = Array.from(document.querySelectorAll(".vc-guardrail"));

guardrails.forEach((guardrail, index) => {
  guardrail.style.setProperty("--delay", `${index * 90}ms`);
  guardrail.addEventListener("pointerenter", () => {
    guardrails.forEach((item) => item.classList.toggle("is-active", item === guardrail));
  });
});

if (guardrails.length) guardrails[0].classList.add("is-active");
