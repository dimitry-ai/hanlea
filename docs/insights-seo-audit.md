# Insights: technischer SEO-/GEO-Check

Stand: 13. November 2026. Arbeit auf `feature/insights`.

## Ergebnis der Live-Prüfung

Die fünf bisherigen Fachartikel sind öffentlich mit HTTP 200 erreichbar. Sie
liefern vollständiges HTML, eine eigene kanonische URL und
`index, follow, max-image-preview:large`. Die geprüften Antworten enthalten
keinen sperrenden `X-Robots-Tag`. `robots.txt` erlaubt Crawling und verweist auf
die öffentlich erreichbare Sitemap.

| Öffentliche URL | HTTP-Status | Befund |
| --- | --- | --- |
| https://www.hanlea.com/insights/ | 200 | Übersicht mit statischen Artikellinks |
| https://www.hanlea.com/insights/ai-finops/ | 200 | Indexierung erlaubt, selbstreferenzierender Canonical |
| https://www.hanlea.com/insights/coding-agents/ | 200 | Indexierung erlaubt, selbstreferenzierender Canonical |
| https://www.hanlea.com/insights/medallion-architektur/ | 200 | Indexierung erlaubt, selbstreferenzierender Canonical |
| https://www.hanlea.com/insights/openjev-unity-gateway/ | 200 | Indexierung erlaubt, selbstreferenzierender Canonical |
| https://www.hanlea.com/insights/lakeflow-agentic-data-engineering/ | 200 | Indexierung erlaubt, selbstreferenzierender Canonical |
| https://www.hanlea.com/insights/databricks-genie/ | 404 | Neuer Artikel ist lokal vorbereitet und noch nicht veröffentlicht |
| https://www.hanlea.com/sitemap.xml | 200 | XML-Sitemap mit den fünf veröffentlichten Artikeln |
| https://www.hanlea.com/robots.txt | 200 | `Allow: /` und korrekter Sitemap-Verweis |

HTTP auf der www-Adresse sowie die HTTPS-Adresse ohne www leiten per 301 auf
https://www.hanlea.com/ weiter. Die Varianten mit `index.html` liefern ebenfalls
200 und verweisen per Canonical auf die jeweilige Verzeichnis-URL.

Die Live-Abrufe wurden per IPv4 durchgeführt. Die Prüfungsumgebung konnte
IPv6-Abrufe nicht zuverlässig abschließen; daraus folgt kein belegter
IPv6-Fehler der Website. Der gemeldete Search-Console-Status stammt vom Nutzer,
nicht aus einem direkten Zugriff auf dessen Search-Console-Konto.

## Einordnung des Search-Console-Status

Gemeldet wurde für AI-FinOps: **„Gefunden – zurzeit nicht indexiert“**.
Google kennt die URL, hat sie laut diesem Berichtsstatus jedoch noch nicht
gecrawlt. Ein vorhandener Sitemap-Eintrag ist deshalb keine Bestätigung der
Indexierung. Die Live-Prüfung hat keine eindeutige technische Crawling-Sperre
nachgewiesen. Die genaue interne Priorisierung durch Google ist von außen
nicht feststellbar.

Quelle: [Google Search Console: Bericht zur Seitenindexierung](https://support.google.com/webmasters/answer/7440203?hl=de).

## Vorbereitete Verbesserungen

1. **Direkte Artikelverlinkung auf der Startseite.** Die drei neuesten fertigen
   Artikel erscheinen als statische Links mit Titel und Zusammenfassung. Die
   Auswahl wird aus denselben Metadaten wie die Übersicht generiert.
2. **Konsistente interne URLs im Deployment.** Im gebauten Artefakt werden
   Navigationslinks zu `index.html` auf Verzeichnis-URLs vereinheitlicht.
   Navigation, Canonicals und Sitemap zeigen damit auf dieselbe URL-Form.
   Der lokale Checkout behält die bisherigen funktionierenden Dateipfade.
3. **Verlässliche Änderungsdaten in der Sitemap.** Jeder Artikel erhält sein
   eigenes `updatedAt` als `lastmod`. Ein neuer Beitrag ändert nicht länger
   pauschal die Sitemap-Daten aller Seiten. Unbekannte Datumswerte werden
   weggelassen.
4. **Zusammenhängende strukturierte Daten.** Die Artikel verweisen auf die
   Insights-Sammlung; diese nennt Website, Herausgeber und ihre indexierbaren
   Inhalte. Die Artikel-Zusammenfassung entspricht der sichtbaren Einleitung.
5. **Statische Übersicht als primäre Darstellung.** Bereits generierte Karten
   werden beim Seitenstart nicht unnötig per JavaScript ersetzt. Der Fallback
   berücksichtigt die URL-Form der veröffentlichten Website.
6. **Prüfung des fertigen Artefakts.** Der GitHub-Pages-Workflow kontrolliert
   nach dem Build noch einmal Navigation, Sitemap, Canonicals und Ressourcen.
   Dokumentation und Wartungsskripte sind von der Veröffentlichung ausgenommen.

Die URL-Vereinheitlichung ist eine Konsistenzverbesserung. Die bisherige
`index.html`-Variante mit richtigem Canonical ist kein nachgewiesener Grund
für den gemeldeten Status. Auch diese Änderungen garantieren keine Indexierung.

Grundlagen: [Google zu crawlbaren Links](https://developers.google.com/search/docs/crawling-indexing/links-crawlable),
[Canonical-URLs](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls),
[Sitemap-Änderungsdaten](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap).

## GEO / KI-Suche

Die Inhalte sind vollständig als Text verfügbar, enthalten eigene Einordnungen,
Quellen, nachvollziehbare Beispiele und klar gegliederte Überschriften.
Autor, Herausgeber und verwandte Beiträge sind erkennbar. Dafür wurde kein
zusätzliches KI-Markup erfunden und keine automatische Zitierung versprochen.

Für Google AI Overviews und AI Mode braucht eine Seite eine reguläre
Indexierung und die Möglichkeit, mit einem Snippet zu erscheinen. Google nennt
keine zusätzliche technische Voraussetzung und kein spezielles KI-Schema oder
zwingendes KI-Textdokument. Diese Aussage betrifft Google; andere Such- und
Antwortsysteme wählen ihre Quellen eigenständig.

Quelle: [Google: AI features and your website](https://developers.google.com/search/docs/appearance/ai-features).

## Veröffentlichung und Search Console

Die Strukturänderungen und der Genie-Artikel sind lokal vorbereitet. Sie wirken
auf die öffentliche Website erst nach Commit, Push und Veröffentlichung über
`main` mit erfolgreichem GitHub-Pages-Workflow.

Danach:

1. Die Property für `https://www.hanlea.com/` beziehungsweise die Domain-Property
   `hanlea.com` öffnen. Eine Property nur für die Adresse ohne www enthält die
   kanonischen www-URLs nicht automatisch.
2. Unter **Sitemaps** `https://www.hanlea.com/sitemap.xml` einreichen. Wenn die
   www-Website-Adresse im Formular schon vorgegeben ist, genügt `sitemap.xml`.
   Die Sitemap kann bereits jetzt für die fünf veröffentlichten Artikel eingereicht werden.
3. Die kanonischen Verzeichnis-URLs einzeln in der **URL-Prüfung** prüfen,
   zum Beispiel `https://www.hanlea.com/insights/ai-finops/`.
4. **Live-URL testen** und bei erfolgreichem Test **Indexierung beantragen**.
   Beim Genie-Artikel erst nach seiner Veröffentlichung, damit die URL 200 liefert.
5. Sitemap-Status und Indexierungsbericht später erneut prüfen. Eine erfolgreiche
   Einreichung oder ein bestandener Live-Test verpflichtet Google nicht zur Indexierung.

Quelle: [Google: Ask Google to recrawl your URLs](https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl).

## Validierung

- Quellseiten: `python3 scripts/check-site.py`.
- Bereitgestelltes statisches Artefakt: `python3 scripts/check-site.py --root <Artefakt> --public`.
- Browser: lokale Dateinavigation und HTTP-Vorschau, Desktop/Mobil sowie Artikelverweise.
- Der eigentliche Jekyll-/GitHub-Pages-Lauf ist erst im GitHub-Workflow geprüft;
  Jekyll ist in der lokalen Umgebung nicht installiert.
