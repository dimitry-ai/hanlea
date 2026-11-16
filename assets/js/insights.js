(function () {
  const feature = document.getElementById("insights-featured");
  const grid = document.getElementById("insights-grid");
  const count = document.getElementById("insights-count");
  if (!feature || !grid || !count) return;

  const root = feature.dataset.siteRoot || "../";
  const articleUrl = (path) => root + (location.protocol === "file:" ? path : path.replace(/index\.html$/, ""));
  const formatDate = (date) => new Intl.DateTimeFormat("de-DE", {
    day: "numeric", month: "long", year: "numeric", timeZone: "UTC"
  }).format(new Date(`${date}T00:00:00Z`));

  const node = (tag, className, text) => {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  };

  const isAvailable = (article) =>
    ["ready", "draft", "published"].includes(article.status) && article.path &&
    /^\d{4}-\d{2}-\d{2}$/.test(article.date || "") &&
    !Number.isNaN(Date.parse(`${article.date}T00:00:00Z`));

  const sortArticles = (articles) => articles.filter(isAvailable).sort((a, b) =>
    b.date.localeCompare(a.date) || a.id.localeCompare(b.id)
  );

  const image = (article, featured = false) => {
    const element = node("img");
    const wide = featured && article.coverImage;
    element.src = root + (wide || article.image);
    element.alt = "";
    element.width = wide ? 1440 : article.imageWidth || 960;
    element.height = wide ? 600 : article.imageHeight || 600;
    if (featured) element.fetchPriority = "high";
    else {
      element.loading = "lazy";
      element.decoding = "async";
    }
    return element;
  };

  const tags = (article) => {
    const element = node("div", "insight-tags");
    element.append(node("span", "", article.category));
    if (article.status === "draft") element.append(node("span", "draft-label", "Entwurf"));
    return element;
  };

  const date = (value, label = "") => {
    const element = node("time", "", `${label ? label + ": " : ""}${formatDate(value)}`);
    element.dateTime = value;
    return element;
  };

  const createFeature = (article) => {
    const card = node("article");
    card.dataset.insightTopic = article.id;
    const link = node("a", "insight-feature");
    link.href = articleUrl(article.path);
    const titleId = `insight-title-${article.id}`;
    const summaryId = `insight-summary-${article.id}`;
    link.setAttribute("aria-labelledby", titleId);
    link.setAttribute("aria-describedby", summaryId);
    const visual = node("div", "insight-feature-visual");
    visual.append(image(article, true));
    const copy = node("div", "insight-feature-copy");
    const title = node("h3", "", article.title);
    title.id = titleId;
    const summary = node("p", "", article.summary);
    summary.id = summaryId;
    const meta = node("div", "article-meta");
    meta.append(node("span", "", article.author || "Hanlea"));
    meta.append(node("span", "", `${article.readingMinutes} Min. Lesezeit`), date(article.date, article.dateLabel));
    const read = node("span", "insight-read-link", "Artikel lesen");
    const arrow = node("span", "", "→");
    arrow.setAttribute("aria-hidden", "true");
    read.append(arrow);
    copy.append(tags(article), title, summary, meta, read);
    link.append(visual, copy);
    card.append(link);
    return card;
  };

  const createCard = (article) => {
    const card = node("article", "insight-topic-card");
    card.dataset.insightTopic = article.id;
    if (article.wide) card.classList.add("insight-topic-card--event");
    let content = card;
    if (isAvailable(article)) {
      content = node("a", "insight-topic-link");
      content.href = articleUrl(article.path);
      content.setAttribute("aria-labelledby", `insight-title-${article.id}`);
      card.append(content);
    }
    const visual = node("div", "insight-topic-visual");
    visual.append(image(article));
    const copy = node("div", "insight-topic-copy");
    const title = node("h3", "", article.title);
    title.id = `insight-title-${article.id}`;
    const footer = node("div", "insight-topic-footer");
    if (isAvailable(article)) {
      const meta = node("span");
      meta.append(date(article.date, article.dateLabel), document.createTextNode(` · ${article.readingMinutes} Min.`));
      footer.append(meta, node("span", "insight-topic-read", "Artikel lesen →"));
    } else {
      footer.append(node("span", "", article.meta || ""), node("span", "insight-coming-label", "Artikel folgt"));
    }
    copy.append(tags(article), title, node("p", "", article.summary), footer);
    content.append(visual, copy);
    return card;
  };

  const render = () => {
    const articles = window.HANLEA_INSIGHTS;
    if (!Array.isArray(articles)) return;
    const available = sortArticles(articles);
    const planned = articles.filter((article) => article.status === "planned");
    feature.replaceChildren(...(available.length ? [createFeature(available[0])] : []));
    feature.hidden = !available.length;
    grid.replaceChildren(...[...available.slice(1), ...planned].map(createCard));
    const total = available.length + planned.length;
    count.textContent = `${String(total).padStart(2, "0")} Themen · ${String(available.length).padStart(2, "0")} Artikel`;
  };

  window.HanleaInsights = Object.freeze({ render, sortArticles });
  // Generated HTML is the initial page. Rebuild only when the fallback is needed.
  const entries = window.HANLEA_INSIGHTS;
  const expected = Array.isArray(entries)
    ? [...sortArticles(entries), ...entries.filter((article) => article.status === "planned")].map((article) => article.id)
    : [];
  const existing = [...feature.querySelectorAll("[data-insight-topic]"), ...grid.querySelectorAll("[data-insight-topic]")]
    .map((element) => element.dataset.insightTopic);
  if (expected.length && JSON.stringify(existing) !== JSON.stringify(expected)) render();
})();
