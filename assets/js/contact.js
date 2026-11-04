(function () {
  if (window.HanleaContact) return;

  const template = document.createElement("template");
  template.innerHTML = `<dialog id="contact-dialog" class="contact-dialog" aria-labelledby="contact-dialog-title" aria-describedby="contact-dialog-intro">
  <div class="contact-modal">
    <button class="modal-close" type="button" aria-label="Kontaktformular schließen">&times;</button>

    <div class="modal-heading">
      <span class="section-kicker">Anfrage</span>
      <h2 id="contact-dialog-title">Data- und AI-Vorhaben besprechen</h2>
      <p id="contact-dialog-intro">
        Teilen Sie kurz mit, wobei wir unterstützen können. Die Anfrage wird strukturiert an info@hanlea.com übermittelt.
      </p>
    </div>

    <!-- Set data-endpoint to a form backend URL, e.g. a Formspree endpoint, to send without mailto fallback. -->
    <form id="contact-form" class="contact-form" data-endpoint="https://formspree.io/f/xojygrgz">
      <label class="honeypot" aria-hidden="true">
        <span>Bitte leer lassen</span>
        <input type="text" name="website" tabindex="-1" autocomplete="off" />
      </label>

      <div class="form-grid">
        <label class="field">
          <span>Name</span>
          <input type="text" name="name" autocomplete="name" required />
        </label>

        <label class="field">
          <span>E-Mail</span>
          <input type="email" name="email" autocomplete="email" required />
        </label>

        <label class="field">
          <span>Unternehmen / Bereich</span>
          <input type="text" name="company" autocomplete="organization" required />
        </label>

        <label class="field">
          <span>Telefon</span>
          <input type="tel" name="phone" autocomplete="tel" />
        </label>
      </div>

      <fieldset class="field-group">
        <legend>Themen / Leistungen</legend>
        <div class="checkbox-grid">
          <label class="check-card">
            <input type="checkbox" name="topics" value="Data &amp; AI Strategy" />
            <span>Data &amp; AI Strategy</span>
          </label>
          <label class="check-card">
            <input type="checkbox" name="topics" value="Data Platform Review" />
            <span>Data Platform Review</span>
          </label>
          <label class="check-card">
            <input type="checkbox" name="topics" value="Platform Engineering" />
            <span>Platform Engineering</span>
          </label>
          <label class="check-card">
            <input type="checkbox" name="topics" value="BI &amp; Analytics" />
            <span>BI &amp; Analytics</span>
          </label>
          <label class="check-card">
            <input type="checkbox" name="topics" value="GenAI / AI Use Case" />
            <span>GenAI / AI Use Case</span>
          </label>
          <label class="check-card">
            <input type="checkbox" name="topics" value="Governance &amp; Data Quality" />
            <span>Governance &amp; Data Quality</span>
          </label>
        </div>
        <p id="topic-error" class="form-error" aria-live="polite"></p>
      </fieldset>

      <div class="form-grid">
        <label class="field">
          <span>Zeithorizont</span>
          <select name="timing" required>
            <option value="">Bitte auswählen</option>
            <option value="Kurzfristig">Kurzfristig</option>
            <option value="In den nächsten 1-3 Monaten">In den nächsten 1-3 Monaten</option>
            <option value="Später / Orientierung">Später / Orientierung</option>
          </select>
        </label>

        <label class="field">
          <span>Gewünschter nächster Schritt</span>
          <select name="next_step">
            <option value="Erstgespräch">Erstgespräch</option>
            <option value="Einschätzung per E-Mail">Einschätzung per E-Mail</option>
            <option value="Workshop / Review">Workshop / Review</option>
          </select>
        </label>
      </div>

      <label class="field field-full">
        <span>Kurz zur Ausgangslage</span>
        <textarea name="message" rows="5" required placeholder="Worum geht es, was ist die aktuelle Herausforderung, und was wäre ein gutes Ergebnis?"></textarea>
      </label>

      <p id="form-status" class="form-status" role="status" aria-live="polite"></p>

      <div class="form-actions">
        <p class="form-note">Die Anfrage erreicht uns strukturiert. Bei Bedarf melden wir uns mit konkreten Rückfragen.</p>
        <button class="btn btn-primary" type="submit" data-default-label="Anfrage senden">Anfrage senden</button>
      </div>
    </form>
  </div>
</dialog>`;
  document.body.appendChild(template.content);

  const siteNav = document.querySelector(".nav");
  const navToggle = document.querySelector(".nav-toggle");
  let returnFocus = null;
  let closeTimer = 0;
  let isSubmitting = false;

  const contactDialog = document.getElementById("contact-dialog");
  const contactForm = document.getElementById("contact-form");
  const contactClose = contactDialog?.querySelector(".modal-close");
  const topicError = document.getElementById("topic-error");
  const topicInputs = contactForm ? Array.from(contactForm.querySelectorAll('input[name="topics"]')) : [];
  const formStatus = document.getElementById("form-status");
  const submitButton = contactForm?.querySelector('button[type="submit"]');
  const contactRecipient = "info@hanlea.com";

  const setContactDialogState = (isOpen) => {
    document.body.classList.toggle("modal-open", isOpen);
  };

  const openContactDialog = (trigger = null) => {
    window.clearTimeout(closeTimer);
    if (trigger instanceof HTMLElement) {
      const mobileNav = trigger.closest("#primary-nav") && navToggle && getComputedStyle(navToggle).display !== "none";
      returnFocus = mobileNav ? navToggle : trigger;
    }
    if (!contactDialog) {
      window.location.href = `mailto:${contactRecipient}`;
      return;
    }

    if (contactDialog.open) {
      setContactDialogState(true);
      return;
    }

    if (typeof contactDialog.showModal === "function") {
      contactDialog.showModal();
    } else {
      contactDialog.setAttribute("open", "");
    }

    setContactDialogState(true);
    contactDialog.querySelector(".contact-modal").scrollTop = 0;
    window.requestAnimationFrame(() => {
      if (contactDialog.open) contactForm.querySelector('input[name="name"]').focus({ preventScroll: true });
    });
  };

  const closeContactDialog = () => {
    window.clearTimeout(closeTimer);
    if (!contactDialog) return;

    if (typeof contactDialog.close === "function" && contactDialog.open) {
      contactDialog.close();
    } else {
      contactDialog.removeAttribute("open");
      setContactDialogState(false);
    }
  };

  const preselectContactTopic = (topic) => {
    const selectedTopic = topic?.trim();
    if (!selectedTopic || !topicInputs.length) return;

    const matchingTopic = topicInputs.find((input) => input.value === selectedTopic);
    if (!matchingTopic) return;

    topicInputs.forEach((input) => {
      input.checked = input === matchingTopic;
    });

    if (topicError) topicError.textContent = "";
  };

  document.addEventListener("click", (event) => {
    const trigger = event.target instanceof Element ? event.target.closest("[data-contact-open]") : null;
    if (!trigger) return;
    event.preventDefault();
    if (siteNav && navToggle) {
      siteNav.removeAttribute("data-open");
      navToggle.setAttribute("aria-expanded", "false");
      navToggle.setAttribute("aria-label", "Navigation öffnen");
    }
    preselectContactTopic(trigger.dataset.contactTopic);
    openContactDialog(trigger);
  });

  contactClose?.addEventListener("click", closeContactDialog);

  contactDialog?.addEventListener("click", (event) => {
    if (event.target !== contactDialog) return;
    const modalBounds = contactDialog.querySelector(".contact-modal")?.getBoundingClientRect();
    if (!modalBounds) return;

    const isBackdropClick =
      event.clientX < modalBounds.left ||
      event.clientX > modalBounds.right ||
      event.clientY < modalBounds.top ||
      event.clientY > modalBounds.bottom;

    if (isBackdropClick) closeContactDialog();
  });

  contactDialog.addEventListener("close", () => {
    window.clearTimeout(closeTimer);
    setContactDialogState(false);
    if (returnFocus?.isConnected) returnFocus.focus({ preventScroll: true });
  });

  topicInputs.forEach((input) => {
    input.addEventListener("change", () => {
      if (topicInputs.some((topic) => topic.checked) && topicError) {
        topicError.textContent = "";
      }
    });
  });

  const setFormStatus = (message, type = "") => {
    if (!formStatus) return;
    formStatus.textContent = message;
    formStatus.dataset.type = type;
  };

  const setFormLoading = (isLoading) => {
    if (!submitButton) return;
    isSubmitting = isLoading;
    submitButton.disabled = isLoading;
    submitButton.textContent = isLoading ? "Wird gesendet..." : submitButton.dataset.defaultLabel || "Anfrage senden";
  };

  contactForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (isSubmitting || !contactForm.reportValidity()) return;

    const data = new FormData(contactForm);
    const value = (name) => String(data.get(name) || "").trim();

    if (value("website")) return;

    const selectedTopics = topicInputs.filter((input) => input.checked).map((input) => input.value);
    if (!selectedTopics.length) {
      if (topicError) topicError.textContent = "Bitte wählen Sie mindestens ein Thema aus.";
      topicInputs[0]?.focus();
      return;
    }

    if (topicError) topicError.textContent = "";

    const lines = [
      "Hallo zusammen,",
      "",
      "ich möchte ein Data- oder AI-Vorhaben besprechen.",
      "",
      "Kontaktdaten:",
      `Name: ${value("name")}`,
      `E-Mail: ${value("email")}`,
      `Unternehmen / Bereich: ${value("company")}`,
    ];

    if (value("phone")) lines.push(`Telefon: ${value("phone")}`);

    lines.push("", "Themen / Leistungen:");
    selectedTopics.forEach((topic) => lines.push(`- ${topic}`));
    lines.push(
      "",
      `Zeithorizont: ${value("timing")}`,
      `Gewünschter nächster Schritt: ${value("next_step") || "Erstgespräch"}`,
      "",
      "Kurz zur Ausgangslage:",
      value("message"),
      "",
      "Viele Grüße"
    );

    const subject = `Anfrage: ${selectedTopics.slice(0, 2).join(", ")}`;
    const messageBody = lines.join("\n");
    const contactEndpoint = contactForm.dataset.endpoint?.trim();

    if (contactEndpoint) {
      const payload = new FormData();
      payload.set("name", value("name"));
      payload.set("email", value("email"));
      payload.set("_replyto", value("email"));
      payload.set("company", value("company"));
      payload.set("phone", value("phone"));
      payload.set("topics", selectedTopics.join(", "));
      payload.set("timing", value("timing"));
      payload.set("next_step", value("next_step") || "Erstgespräch");
      payload.set("message", messageBody);
      payload.set("_subject", subject);
      payload.set("source", window.location.href);

      setFormStatus("");
      setFormLoading(true);

      try {
        const response = await fetch(contactEndpoint, {
          method: "POST",
          body: payload,
          headers: { Accept: "application/json" },
        });

        if (!response.ok) {
          throw new Error(`Form endpoint returned ${response.status}`);
        }

        contactForm.reset();
        setFormStatus("Danke, Ihre Anfrage wurde gesendet.", "success");
        closeTimer = window.setTimeout(closeContactDialog, 1800);
      } catch (error) {
        setFormStatus("Das Senden hat gerade nicht geklappt. Bitte versuchen Sie es erneut oder schreiben Sie direkt an info@hanlea.com.", "error");
      } finally {
        setFormLoading(false);
      }

      return;
    }

    setFormStatus("Es ist noch kein Formular-Endpunkt hinterlegt. Ihr E-Mail-Programm wird geöffnet.", "info");
    window.location.href = `mailto:${contactRecipient}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(messageBody)}`;
    closeTimer = window.setTimeout(closeContactDialog, 300);
  });

  document.querySelectorAll("[data-contact-open]").forEach((trigger) => {
    trigger.setAttribute("aria-haspopup", "dialog");
    trigger.setAttribute("aria-controls", "contact-dialog");
  });

  window.HanleaContact = Object.freeze({ open: openContactDialog, close: closeContactDialog });
})();
