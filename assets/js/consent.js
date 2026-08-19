(function () {
  const consentKey = "hanlea_cookie_consent";
  const measurementId = "G-LGQ37DGD7K";
  const acceptedValue = "accepted";
  const declinedValue = "declined";

  const getConsent = () => {
    try {
      return window.localStorage.getItem(consentKey);
    } catch (error) {
      return null;
    }
  };

  const setConsent = (value) => {
    try {
      window.localStorage.setItem(consentKey, value);
    } catch (error) {
      // If storage is blocked, keep the user's current page choice in memory only.
    }
  };

  const loadAnalytics = () => {
    if (window.hanleaAnalyticsLoaded) return;
    window.hanleaAnalyticsLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () {
      window.dataLayer.push(arguments);
    };
    window.gtag("js", new Date());
    window.gtag("config", measurementId, { anonymize_ip: true });

    const script = document.createElement("script");
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
    document.head.appendChild(script);
  };

  const removeBanner = () => {
    document.querySelector(".consent-banner")?.remove();
  };

  const createBanner = () => {
    removeBanner();

    const banner = document.createElement("section");
    banner.className = "consent-banner";
    banner.setAttribute("aria-label", "Datenschutzeinstellungen");
    banner.innerHTML = `
      <div class="consent-banner__copy">
        <strong>Cookies & Datenschutz</strong>
        <p>Wir nutzen optionale Cookies und ähnliche Technologien, um die Website statistisch auszuwerten und weiterzuentwickeln.</p>
      </div>
      <div class="consent-banner__actions">
        <button class="btn btn-secondary" type="button" data-consent-decline>Ablehnen</button>
        <button class="btn btn-primary" type="button" data-consent-accept>Akzeptieren</button>
      </div>
    `;

    banner.querySelector("[data-consent-accept]")?.addEventListener("click", () => {
      setConsent(acceptedValue);
      loadAnalytics();
      removeBanner();
    });

    banner.querySelector("[data-consent-decline]")?.addEventListener("click", () => {
      setConsent(declinedValue);
      removeBanner();
    });

    document.body.appendChild(banner);
  };

  const applyConsent = () => {
    const consent = getConsent();
    if (consent === acceptedValue) {
      loadAnalytics();
      return;
    }

    if (consent !== declinedValue) createBanner();
  };

  window.hanleaOpenConsentSettings = () => {
    createBanner();
  };

  document.addEventListener("click", (event) => {
    const trigger = event.target.closest("[data-consent-settings]");
    if (!trigger) return;
    event.preventDefault();
    createBanner();
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyConsent);
  } else {
    applyConsent();
  }
})();
