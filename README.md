# Hanlea Website

Statische Website mit einem zentral gepflegten Insights-Bereich. HTML, CSS und
JavaScript funktionieren auch beim direkten Öffnen der HTML-Dateien im Browser.

## Inhalte und Pflege

- `assets/js/insights-data.js`: zentrale Metadaten für alle Artikel, als JSON-kompatibles Array.
- `insights/<slug>/index.html`: vollständiger Artikeltext, Inhaltsverzeichnis und Quellen.
- `assets/css/insights.css`: gemeinsame Artikel- und Übersichtsdarstellung.
- `assets/js/insights.js`: Sortierung und Darstellung im Browser.
- `assets/js/contact.js`: gemeinsames Beratungsformular mit Validierung und Versand.
- `scripts/build-insights.py`: erzeugt statische Karten, Artikel-Metadaten, JSON-LD und Sitemap.
- `scripts/check-site.py`: prüft Links, Daten, strukturiertes Markup und lokale Ressourcen.
- `scripts/prepare-pages.py`: vereinheitlicht interne Navigationslinks im Deployment-Artefakt.
- `docs/insights-seo-audit.md`: dokumentiert Live-Befunde und Schritte für die Search Console.

Die sechs fertigen Fachartikel behandeln AI-FinOps, Medallion-Architektur, Coding
Agents, Lakeflow, OpenJev / Unity Gateway sowie Databricks Genie. Die World Tour ist aus der
Übersicht und Sitemap herausgenommen. Bestehende Grafikdateien bleiben erhalten.

Die Website ist die zentrale fachliche Quelle. LinkedIn-Posts greifen die
Kernaussagen auf und verlinken auf den jeweiligen Artikel.

## Artikel ergänzen oder ändern

1. Einen Artikelordner als Vorlage kopieren und Inhalt, Inhaltsverzeichnis,
   Abbildungen sowie Quellen ausarbeiten. Die gemeinsame Navigation und das
   Kontakt-Skript beibehalten.
2. In `assets/js/insights-data.js` den Eintrag ergänzen: eindeutige `id`, `path`
   ab Website-Wurzel, Titel, Kurztext, `lead`, Kategorie, Beschreibung, Bilder
   und Datumsangaben. Alle Schlüssel und Texte innerhalb des Arrays müssen
   JSON-kompatibel bleiben; Kommentare nur außerhalb der Zuweisung.
3. `status: "ready"` bedeutet ausgearbeitet und indexierbar. `draft` markiert
   einen sichtbaren Entwurf mit `noindex`. `published` wird ebenfalls unterstützt.
   `planned` ist eine Themenvorschau ohne Artikel. Beim bisherigen vollständigen
   Satz sind alle sechs Artikel `ready`.
4. `date` steuert das sichtbare Artikeldatum und die Sortierung. `sourceDate`
   hält das dokumentierte Datum des ursprünglichen Beitragsentwurfs fest.
   `updatedAt` nur bei tatsächlicher fachlicher Überarbeitung ändern;
   es erscheint in den technischen Metadaten. `createdAt` beschreibt die Web-Ausarbeitung.
   `publishedAt` erst ergänzen, wenn das tatsächliche Erstveröffentlichungsdatum
   der Web-Seite feststeht. Das wird dann auch als `datePublished` ausgezeichnet.
5. Ein eigenes Social-Vorschaubild unter `ogImage` ablegen (PNG, 1200 × 630).
   Das Artikel-Headerbild verwendet das breite SVG-Format 1440 × 600. Die
   Übersicht hat eine eigene Vorschaugrafik; beide Dateipfade werden zentral gepflegt.
   Für Genie liegt die bearbeitbare Social-Bildvorlage daneben als
   `assets/og/databricks-genie.svg`; das PNG ist deren Browser-Export.
6. Generieren und prüfen:

```sh
python3 scripts/build-insights.py
python3 scripts/check-site.py
```

Der Generator aktualisiert Überschriften und Einleitungen aus den Metadaten,
Schätzungen der Lesezeit, Canonicals, Social-Metadaten, Autorenangaben,
BlogPosting- und BreadcrumbList-JSON-LD sowie verknüpfte Artikel. Die drei neuesten
indexierbaren Artikel werden zusätzlich direkt auf der Startseite verlinkt. Er schreibt
alle Übersichtskarten in das HTML; Crawler benötigen dafür kein JavaScript.
Der Browser verwendet weiterhin denselben zentralen Datensatz.

Die Sortierung erfolgt nach `date` absteigend. Der neueste verfügbare Eintrag
wird automatisch die große Karte, die übrigen Artikel stehen darunter. Neue
Einträge mit demselben Datum werden deterministisch nach ID sortiert. Titel,
Zusammenfassung und Zähler werden aus dem Datensatz erzeugt; keine Karte muss
von Hand einsortiert werden.

## Datumsverlauf der bestehenden Themen

Die sichtbaren Artikeldaten reichen von März bis November 2026.
`date` steuert diese Zeitachse in Übersicht und Artikelkopf. Dort stehen Autor,
Lesezeit und ein Datum; ein zusätzliches Aktualisierungsdatum wird nicht angezeigt.

| Thema | Sichtbares Artikeldatum | Dokumentierter Themenursprung (`sourceDate`) |
| --- | --- | --- |
| Coding Agents | 18. März 2026 | 24. August 2026 |
| AI-FinOps | 12. Mai 2026 | 14. September 2026 |
| Medallion-Architektur | 9. Juli 2026 | 30. September 2026 |
| OpenJev / Unity Gateway | 3. September 2026 | 12. Oktober 2026 |
| Lakeflow | 27. Oktober 2026 | 30. Oktober 2026 |
| Databricks Genie | 13. November 2026 | 13. November 2026 |

`sourceDate` stammt bei den ersten fünf Themen aus den dokumentierten
Beitragsentwürfen im separaten LinkedIn-Repository und wird in JSON-LD unter
`isBasedOn` verwendet. Der Genie-Artikel wurde am 13. November 2026 direkt für
die Website ausgearbeitet; dieses Datum gilt auch für seinen Themenentwurf.
Die ersten fünf Web-Ausarbeitungen sind vom 4. November 2026; `dateCreated` und `dateModified`
beziehen sich auf die tatsächliche Erstellung und Überarbeitung. Ein bestätigtes
Erstveröffentlichungsdatum wird separat über `publishedAt` / `datePublished` gepflegt.

## SEO und KI-Suche

Die Artikel sind indexierbar vorbereitet, enthalten statisches HTML, direkte
Kurzantworten, klare Überschriften, sichtbare Autoren- und Artikeldatumsangaben,
Primärquellen sowie interne Links. Der Generator hält Metadaten und JSON-LD mit
dem sichtbaren Inhalt konsistent. `sitemap.xml` nennt nur kanonische Seiten,
keine Weiterleitungen; `robots.txt` verweist auf die Sitemap und blockiert die
reguläre Suche nicht. Social-Vorschauen besitzen artikelbezogene PNG-Bilder.
`lastmod` wird pro Artikel aus seiner tatsächlichen fachlichen Überarbeitung
ermittelt. Für Seiten ohne gepflegtes Änderungsdatum bleibt es weg. Artikel und
Insights-Übersicht sind im strukturierten Markup miteinander verbunden.

Der ältere Musterpfad leitet auf AI-FinOps weiter und bleibt `noindex`.

Diese technische Vorbereitung garantiert weder Indexierung noch Rankings oder
Zitate in KI-Antworten. Nach Veröffentlichung können die Sitemap in Google
Search Console und Bing Webmaster Tools eingereicht und die tatsächliche
Indexierung geprüft werden. Ein spezielles KI-Schema oder `llms.txt` ist für
Google AI Overviews und AI Mode nicht erforderlich.

- [Google: AI features and your website](https://developers.google.com/search/docs/appearance/ai-features)
- [Google: Article structured data](https://developers.google.com/search/docs/appearance/structured-data/article)
- [Google: Publication dates](https://developers.google.com/search/docs/appearance/publication-dates)
- [Bing: Webmaster Guidelines](https://www.bing.com/webmasters/help/webmaster-guidelines-30fba23a)

## Gemeinsames Beratungs-Popup

Formular, Texte, Themenauswahl, Validierung und Versandlogik liegen ausschließlich
in `assets/js/contact.js`. Dort steht der bestehende Formular-Endpunkt unter
`data-endpoint`. Ein neuer Beratungslink benötigt nur dieses Attribut:

```html
<a href="mailto:info@hanlea.com" data-contact-open>Vorhaben besprechen</a>
```

Optional wählt `data-contact-topic="Data &amp; AI Strategy"` ein Thema vor.
Mit JavaScript öffnet das Popup direkt auf der aktuellen Seite; ohne JavaScript
führt der Link zur E-Mail-Adresse. Die Mobilnavigation schließt sich dabei.
Nach dem Schließen kehrt der Fokus zum auslösenden Element zurück. Das gemeinsame
Skript muss mit einem zur HTML-Datei passenden relativen Pfad eingebunden sein.

## Vorschau und Veröffentlichung

Die `index.html` im Hauptordner direkt öffnen und **Insights** anklicken.
Optional `python3 -m http.server 8000` starten und `http://localhost:8000/` öffnen.

Der GitHub-Pages-Workflow generiert und prüft die Insights vor dem Jekyll-Build.
Nach dem Jekyll-Build normalisiert `prepare-pages.py` Links wie
`insights/ai-finops/index.html` zu `insights/ai-finops/`. Dadurch verwenden
Navigation, Canonicals und Sitemap auf der veröffentlichten Website dieselbe
URL-Form. Im Checkout bleiben explizite HTML-Dateipfade für `file://` erhalten.
Die Übersicht nutzt ihr generiertes HTML direkt; ein JavaScript-Fallback
erzeugt bei Bedarf online ebenfalls Verzeichnis-URLs.

Das fertige Artefakt wird separat geprüft:

```sh
python3 scripts/prepare-pages.py _site
python3 scripts/check-site.py --root _site --public
```

Die Prüfung erkennt auch nicht erreichbare Artikel, abweichende Sitemap- und
Canonical-URLs sowie falsche Änderungsdaten. `_config.yml` schließt interne
Dokumentation, README und Wartungsskripte aus der veröffentlichten Website aus.

Er veröffentlicht bei einem Push auf `main`. Die aktuelle Arbeit liegt lokal
auf `feature/insights`; das Generieren oder Prüfen führt keine Veröffentlichung aus.
