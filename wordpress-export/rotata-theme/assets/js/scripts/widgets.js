const backToTop = document.querySelector("[data-back-to-top]");
const chatToggle = document.querySelector("[data-rotbot-toggle]");
const chatPanel = document.querySelector("[data-rotbot-panel]");
const chatClose = document.querySelector("[data-rotbot-close]");
const chatMessages = document.querySelector("[data-rotbot-messages]");

const setBackToTop = () => {
  backToTop?.classList.toggle("is-visible", window.scrollY > 520);
};

setBackToTop();
window.addEventListener("scroll", setBackToTop, { passive: true });
backToTop?.addEventListener("click", () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
  window.rotataTrack?.("back_to_top_click");
});

const openChat = () => {
  chatPanel?.removeAttribute("hidden");
  chatToggle?.setAttribute("aria-expanded", "true");
  chatPanel?.querySelector("button, a")?.focus();
  window.rotataTrack?.("rotbot_open");
};

const closeChat = () => {
  chatPanel?.setAttribute("hidden", "");
  chatToggle?.setAttribute("aria-expanded", "false");
  chatToggle?.focus();
};

chatToggle?.addEventListener("click", () => {
  if (chatPanel?.hasAttribute("hidden")) openChat();
  else closeChat();
});
chatClose?.addEventListener("click", closeChat);

document.querySelectorAll("[data-rotbot-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    const reply = button.getAttribute("data-rotbot-reply") || "";
    if (!chatMessages || !reply) return;
    const user = document.createElement("p");
    user.className = "rotbot-message user";
    user.textContent = button.textContent?.trim() || "";
    const bot = document.createElement("p");
    bot.className = "rotbot-message bot";
    bot.textContent = reply;
    chatMessages.append(user, bot);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    window.rotataTrack?.("rotbot_prompt", { prompt: user.textContent });
  });
});
