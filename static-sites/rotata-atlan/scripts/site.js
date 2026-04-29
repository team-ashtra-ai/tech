import "./shared.js";

const nodes = Array.from(document.querySelectorAll("[data-at-node]"));

const activate = (target) => {
  nodes.forEach((node) => node.classList.toggle("is-active", node === target));
};

nodes.forEach((node) => {
  node.tabIndex = 0;
  node.addEventListener("pointerenter", () => activate(node));
  node.addEventListener("focus", () => activate(node));
});

if (nodes.length) activate(nodes[0]);
