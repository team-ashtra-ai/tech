const modal = document.querySelector("[data-newsletter-modal]");
const articlePage = document.body.classList.contains("page-article");
const storageKey = "rotata-newsletter-state";

if (modal) {
  const dialog = modal.querySelector("[data-newsletter-dialog]");
  const closeButtons = modal.querySelectorAll("[data-newsletter-close]");
  const firstField = () => dialog?.querySelector("input, button, a");
  const state = () => sessionStorage.getItem(storageKey) || "";

  const show = (reason = "manual", force = false) => {
    if (!force && (state() === "dismissed" || state() === "subscribed")) return;
    modal.hidden = false;
    document.body.classList.add("newsletter-modal-open");
    if (!force && !state()) sessionStorage.setItem(storageKey, "shown");
    firstField()?.focus();
    window.rotataTrack?.("newsletter_modal_open", { reason });
  };

  const close = (nextState = "dismissed") => {
    modal.hidden = true;
    document.body.classList.remove("newsletter-modal-open");
    if (nextState) sessionStorage.setItem(storageKey, nextState);
  };

  closeButtons.forEach((button) => {
    button.addEventListener("click", () => close());
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !modal.hidden) close();
  });

  document.addEventListener("rotata:form-success", (event) => {
    if (event.detail?.form === "newsletter") {
      close("subscribed");
    }
  });

  if (articlePage && state() !== "dismissed" && state() !== "subscribed") {
    let shown = false;
    const onScroll = () => {
      if (shown) return;
      const maxScroll = document.documentElement.scrollHeight - window.innerHeight;
      if (maxScroll <= 0) return;
      const progress = window.scrollY / maxScroll;
      if (progress >= 0.45) {
        shown = true;
        show("scroll_depth");
        window.removeEventListener("scroll", onScroll);
      }
    };
    window.addEventListener("scroll", onScroll, { passive: true });

    const onMouseOut = (event) => {
      if (shown || window.innerWidth < 1024) return;
      if (event.relatedTarget || event.clientY > 8) return;
      shown = true;
      show("exit_intent");
      document.removeEventListener("mouseout", onMouseOut);
      window.removeEventListener("scroll", onScroll);
    };
    document.addEventListener("mouseout", onMouseOut);
  }

  dialog?.addEventListener("click", (event) => {
    event.stopPropagation();
  });
}
