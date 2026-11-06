(function () {
  const year = document.getElementById("y");
  if (year) year.textContent = new Date().getFullYear();

  const nav = document.querySelector(".nav");
  const toggle = document.querySelector(".nav-toggle");
  if (!nav || !toggle) return;

  const close = (restoreFocus = false) => {
    const wasOpen = nav.getAttribute("data-open") === "true";
    nav.removeAttribute("data-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Navigation öffnen");
    if (wasOpen && restoreFocus) toggle.focus();
  };

  toggle.addEventListener("click", () => {
    if (nav.getAttribute("data-open") === "true") {
      close();
      return;
    }
    nav.setAttribute("data-open", "true");
    toggle.setAttribute("aria-expanded", "true");
    toggle.setAttribute("aria-label", "Navigation schließen");
  });

  nav.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => close()));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") close(true);
  });
  document.addEventListener("click", (event) => {
    if (!nav.contains(event.target)) close();
  });
  nav.addEventListener("focusout", (event) => {
    if (!nav.contains(event.relatedTarget)) close();
  });

  const desktop = window.matchMedia("(min-width: 1101px)");
  const onResize = (event) => {
    if (event.matches) close();
  };
  if (desktop.addEventListener) desktop.addEventListener("change", onResize);
  else desktop.addListener(onResize);
})();
