#!/usr/bin/env python3
"""Generate crawlable article metadata, overview cards and sitemap from one registry."""
from datetime import date
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import argparse
import json
import math
import os
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://www.hanlea.com/'
REGISTRY = ROOT / 'assets/js/insights-data.js'
MONTHS = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
AVAILABLE = {'ready', 'published', 'draft'}

def load_articles(root=ROOT):
    literal = (root / 'assets/js/insights-data.js').read_text().split('window.HANLEA_INSIGHTS = ', 1)[1].strip().removesuffix(';')
    entries = json.loads(literal)
    ids = [entry['id'] for entry in entries]
    if len(ids) != len(set(ids)):
        raise ValueError('Article IDs must be unique')
    for entry in entries:
        if entry['status'] in AVAILABLE:
            for key in ['date', 'createdAt', 'updatedAt']:
                date.fromisoformat(entry[key])
            path = (root / entry['path']).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                raise ValueError(f'Missing or invalid article: {entry["path"]}')
            for key in ['sourceDate', 'publishedAt']:
                if entry.get(key):
                    date.fromisoformat(entry[key])
    return entries

def german(value):
    parsed = date.fromisoformat(value)
    return f'{parsed.day}. {MONTHS[parsed.month-1]} {parsed.year}'

def display_date(entry):
    label = entry.get('dateLabel', '')
    return (escape(label)+': ' if label else '')+german(entry['date'])

def canonical(entry):
    return ORIGIN + entry['path'].removesuffix('index.html')

def relative(path, page):
    return os.path.relpath(ROOT / path, page.parent).replace(os.sep, '/')

def jsonld(value):
    return json.dumps(value, ensure_ascii=False, indent=2).replace('</', '<\\/')

def replace_block(text, name, value, initial_pattern=None):
    start, end = f'<!-- {name}:START -->', f'<!-- {name}:END -->'
    replacement = f'{start}\n{value}\n{end}'
    pattern = re.escape(start) + r'.*?' + re.escape(end)
    if start not in text:
        if initial_pattern is None:
            raise ValueError(f'Missing generation marker: {name}')
        pattern = initial_pattern
    result, count = re.subn(pattern, lambda _: replacement, text, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f'Cannot replace generation block: {name}')
    return result

class ArticleText(HTMLParser):
    def __init__(self):
        super().__init__(); self.depth = 0; self.words = []
    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            if self.depth: self.depth += 1
            elif dict(attrs).get('class') == 'article-body': self.depth = 1
    def handle_endtag(self, tag):
        if tag == 'div' and self.depth: self.depth -= 1
    def handle_data(self, text):
        if self.depth: self.words.extend(re.findall(r'\S+', text))

def article_schema(entry, words):
    url = canonical(entry)
    work = {
        '@type': 'BlogPosting', '@id': url+'#article', 'url': url,
        'mainEntityOfPage': {'@type': 'WebPage', '@id': url},
        'isPartOf': {'@type': 'CollectionPage', '@id': ORIGIN+'insights/#webpage', 'url': ORIGIN+'insights/', 'name': 'Hanlea Insights'},
        'headline': entry['title'], 'description': entry['description'],
        'abstract': entry['lead'],
        'inLanguage': 'de-DE', 'articleSection': entry['category'],
        'image': [ORIGIN+entry['ogImage']],
        'author': {'@type': 'Organization', '@id': ORIGIN+'#organization', 'name': 'Hanlea', 'url': ORIGIN+'#ueber-uns'},
        'publisher': {'@type': 'Organization', '@id': ORIGIN+'#organization', 'name': 'Hanlea', 'url': ORIGIN, 'logo': {'@type': 'ImageObject', 'url': ORIGIN+'hanlea_transparent.png'}},
        'dateCreated': entry['createdAt'], 'dateModified': entry['updatedAt'],
        'wordCount': words,
        'isBasedOn': {'@type': 'CreativeWork', 'name': 'Ursprünglicher Hanlea-Beitragsentwurf: '+entry['title']}
    }
    if entry.get('sourceDate'):
        work['isBasedOn']['dateCreated'] = entry['sourceDate']
    if entry.get('publishedAt'):
        work['datePublished'] = entry['publishedAt']
    breadcrumbs = {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Startseite', 'item': ORIGIN},
        {'@type': 'ListItem', 'position': 2, 'name': 'Insights', 'item': ORIGIN+'insights/'},
        {'@type': 'ListItem', 'position': 3, 'name': entry.get('breadcrumbTitle', entry['title']), 'item': url}
    ]}
    return {'@context': 'https://schema.org', '@graph': [work, breadcrumbs]}

def article_head(entry, words):
    title, description = escape(entry['seoTitle'], quote=True), escape(entry['description'], quote=True)
    url, image = canonical(entry), ORIGIN+entry['ogImage']
    robots = 'noindex, follow' if entry['status'] == 'draft' else 'index, follow, max-image-preview:large'
    return f'''  <title>{title}</title>
  <meta name="description" content="{description}" />
  <meta name="robots" content="{robots}" />
  <meta name="theme-color" content="#070814" />
  <link rel="canonical" href="{url}" />
  <meta property="og:title" content="{escape(entry['title'], quote=True)} | Hanlea Insights" />
  <meta property="og:description" content="{description}" />
  <meta property="og:type" content="article" />
  <meta property="og:url" content="{url}" />
  <meta property="og:site_name" content="Hanlea" />
  <meta property="og:locale" content="de_DE" />
  <meta property="og:image" content="{image}" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="{escape(entry['title'], quote=True)}" />
  <meta property="article:modified_time" content="{entry['updatedAt']}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{title}" />
  <meta name="twitter:description" content="{description}" />
  <meta name="twitter:image" content="{image}" />
  <script type="application/ld+json">
{jsonld(article_schema(entry, words))}
  </script>'''

def article_header(entry, page):
    home, index = relative('index.html', page), relative('insights/index.html', page)
    badge = '<span class="draft-label">Entwurf</span>' if entry['status'] == 'draft' else ''
    return f'''      <header class="article-header">
        <nav class="article-breadcrumb" aria-label="Brotkrumennavigation">
          <ol><li><a href="{home}">Startseite</a></li><li><a href="{index}">Insights</a></li><li><span aria-current="page">{escape(entry.get('breadcrumbTitle', entry['title']))}</span></li></ol>
        </nav>
        <div class="insight-tags"><span>{escape(entry['category'])}</span>{badge}</div>
        <h1 id="article-title">{escape(entry['title'])}</h1>
        <p class="article-lead">{escape(entry['lead'])}</p>
        <div class="article-meta"><span>Von <a href="{home}#ueber-uns" rel="author">Hanlea</a></span><span>{entry['readingMinutes']} Min. Lesezeit</span><time datetime="{entry['date']}">{display_date(entry)}</time></div>
      </header>'''

def related(entry, entries, page):
    by_id = {item['id']: item for item in entries}
    items = [by_id[id] for id in entry.get('related', []) if id in by_id and by_id[id]['status'] in AVAILABLE]
    links = '\n'.join(f'  <li><a href="{relative(item["path"], page)}">{escape(item["title"])}</a></li>' for item in items)
    return f'<section class="article-related" aria-labelledby="related-title"><h2 id="related-title">Weiterlesen</h2><ul>\n{links}\n</ul></section>'

def card(entry, page, featured=False):
    id, title = entry['id'], escape(entry['title'])
    badge = '<span class="draft-label">Entwurf</span>' if entry['status'] == 'draft' else ''
    wide = featured and entry.get('coverImage')
    image = f'<img src="{relative(wide or entry["image"], page)}" alt="" width="{1440 if wide else entry["imageWidth"]}" height="{600 if wide else entry["imageHeight"]}" '+('fetchpriority="high"' if featured else 'loading="lazy" decoding="async"')+' />'
    tags = f'<div class="insight-tags"><span>{escape(entry["category"])}</span>{badge}</div>'
    date_label = display_date(entry)
    if featured:
        return f'''<article data-insight-topic="{id}"><a class="insight-feature" href="{relative(entry['path'], page)}" aria-labelledby="insight-title-{id}" aria-describedby="insight-summary-{id}">
  <div class="insight-feature-visual">{image}</div>
  <div class="insight-feature-copy">{tags}<h3 id="insight-title-{id}">{title}</h3><p id="insight-summary-{id}">{escape(entry['summary'])}</p>
    <div class="article-meta"><span>Hanlea</span><span>{entry['readingMinutes']} Min. Lesezeit</span><time datetime="{entry['date']}">{date_label}</time></div>
    <span class="insight-read-link">Artikel lesen <span aria-hidden="true">→</span></span>
  </div></a></article>'''
    return f'''<article class="insight-topic-card" data-insight-topic="{id}"><a class="insight-topic-link" href="{relative(entry['path'], page)}" aria-labelledby="insight-title-{id}">
  <div class="insight-topic-visual">{image}</div><div class="insight-topic-copy">{tags}<h3 id="insight-title-{id}">{title}</h3><p>{escape(entry['summary'])}</p>
    <div class="insight-topic-footer"><span><time datetime="{entry['date']}">{date_label}</time> · {entry['readingMinutes']} Min.</span><span class="insight-topic-read">Artikel lesen →</span></div>
  </div></a></article>'''

def home_card(entry):
    id = entry['id']
    return f'''          <a class="card home-insight-card" href="{escape(entry['path'], quote=True)}" data-home-insight="{id}" aria-labelledby="home-insight-{id}">
            <span class="section-kicker">{escape(entry['category'])}</span>
            <h3 id="home-insight-{id}">{escape(entry['title'])}</h3>
            <p>{escape(entry['summary'])}</p>
            <span class="home-insight-meta">{display_date(entry)} · {entry['readingMinutes']} Min. Lesezeit</span>
            <span class="home-insight-read">Artikel lesen <span aria-hidden="true">→</span></span>
          </a>'''

def build(check=False):
    entries = load_articles()
    output = {}
    for entry in entries:
        if entry['status'] not in AVAILABLE: continue
        page = ROOT / entry['path']
        text = page.read_text()
        # Exclude generated related links from the reading-time calculation.
        content = re.sub(r'<!-- RELATED:START -->.*?<!-- RELATED:END -->', '', text, flags=re.S)
        parser = ArticleText(); parser.feed(content)
        entry['readingMinutes'] = max(1, math.ceil(len(parser.words)/200))
        text = replace_block(text, 'ARTICLE_SEO', article_head(entry, len(parser.words)), r'  <title>.*?(?=  <link rel="icon")')
        text = replace_block(text, 'ARTICLE_HEADER', article_header(entry, page), r'      <header class="article-header">.*?</header>')
        if '<!-- RELATED:START -->' not in text:
            text = text.replace('          <div class="article-end">', '<!-- RELATED:START --><!-- RELATED:END -->\n          <div class="article-end">', 1)
        text = replace_block(text, 'RELATED', related(entry, entries, page))
        output[page] = text

    header = '/* Central metadata. Edit this JSON-compatible array, then run python3 scripts/build-insights.py.\n   date controls the editorial timeline; sourceDate records the original draft;\n   updatedAt records the actual article revision. */\n'
    output[REGISTRY] = header+'window.HANLEA_INSIGHTS = '+json.dumps(entries, ensure_ascii=False, indent=2)+';\n'
    available = sorted((a for a in entries if a['status'] in AVAILABLE), key=lambda a: (-date.fromisoformat(a['date']).toordinal(), a['id']))
    indexable = [a for a in available if a['status'] != 'draft']
    home = ROOT/'index.html'
    home_text = home.read_text()
    home_section = '''    <section id="insights" class="section-pad" aria-labelledby="home-insights-title">
      <div class="container">
        <div class="section-heading compact">
          <span class="section-kicker">Insights</span>
          <h2 id="home-insights-title">Wissen für Ihre Data- und AI-Entscheidungen.</h2>
          <p>Unsere aktuellen Fachartikel zu Datenplattformen, KI und produktivem Betrieb.</p>
        </div>
        <div class="home-insights-grid">
'''+ '\n'.join(home_card(a) for a in indexable[:3])+'''
        </div>
        <a class="btn btn-secondary home-insights-all" href="insights/index.html">Alle Insights ansehen <span aria-hidden="true">→</span></a>
      </div>
    </section>'''
    if '<!-- HOME_INSIGHTS:START -->' not in home_text:
        home_text = home_text.replace('    <section id="qa"', '<!-- HOME_INSIGHTS:START --><!-- HOME_INSIGHTS:END -->\n\n    <section id="qa"', 1)
    output[home] = replace_block(home_text, 'HOME_INSIGHTS', home_section)
    page = ROOT/'insights/index.html'
    text = page.read_text()
    if '<!-- INSIGHTS_FEATURE:START -->' not in text:
        start = text.index('<div id="insights-featured"'); start = text.index('>', start)+1
        end = text.index('\n        <div class="insights-topics-heading">', start)
        closing = text.rfind('</div>', start, end)
        text = text[:start]+'\n<!-- INSIGHTS_FEATURE:START --><!-- INSIGHTS_FEATURE:END -->\n'+text[closing:]
    text = replace_block(text, 'INSIGHTS_FEATURE', card(available[0], page, True) if available else '')
    if '<!-- INSIGHTS_GRID:START -->' not in text:
        start = text.index('<div id="insights-grid"'); start = text.index('>', start)+1
        end = text.index('\n      </div>\n    </section>', start)
        closing = text.rfind('</div>', start, end)
        text = text[:start]+'\n<!-- INSIGHTS_GRID:START --><!-- INSIGHTS_GRID:END -->\n'+text[closing:]
    text = replace_block(text, 'INSIGHTS_GRID', '\n'.join(card(a, page) for a in available[1:]))
    text = re.sub(r'(<span id="insights-count">).*?(</span>)', lambda m: m[1]+f'{len(entries):02d} Themen · {len(available):02d} Artikel'+m[2], text)
    collection = {'@context': 'https://schema.org', '@type': 'CollectionPage', '@id': ORIGIN+'insights/#webpage',
      'url': ORIGIN+'insights/', 'name': 'Hanlea Insights', 'inLanguage': 'de-DE',
      'description': 'Fachartikel von Hanlea zu Datenplattformen, Enterprise AI, Strategie und Governance.',
      'isPartOf': {'@type': 'WebSite', '@id': ORIGIN+'#website', 'url': ORIGIN, 'name': 'Hanlea'},
      'publisher': {'@type': 'Organization', '@id': ORIGIN+'#organization', 'name': 'Hanlea', 'url': ORIGIN},
      'breadcrumb': {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Startseite', 'item': ORIGIN},
        {'@type': 'ListItem', 'position': 2, 'name': 'Insights', 'item': ORIGIN+'insights/'}]},
      'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(indexable),
        'itemListElement': [{'@type': 'ListItem', 'position': n+1, 'url': canonical(a), 'name': a['title']} for n,a in enumerate(indexable)]}}
    value = '<script type="application/ld+json">\n'+jsonld(collection)+'\n  </script>'
    if '<!-- COLLECTION_SEO:START -->' not in text:
        text = text.replace('</head>', '<!-- COLLECTION_SEO:START --><!-- COLLECTION_SEO:END -->\n</head>', 1)
    text = replace_block(text, 'COLLECTION_SEO', value)
    output[page] = text

    ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
    ns = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
    sitemap = ET.Element(ns+'urlset')
    # Unknown revision dates stay omitted; one new article must not refresh every URL.
    urls = [(ORIGIN, None), (ORIGIN+'insights/', max((a['updatedAt'] for a in indexable), default=None)),
            (ORIGIN+'impressum.html', None), (ORIGIN+'datenschutz.html', None)]
    urls += [(canonical(a), a['updatedAt']) for a in indexable]
    for url, lastmod in urls:
        item = ET.SubElement(sitemap, ns+'url')
        ET.SubElement(item, ns+'loc').text = url
        if lastmod:
            ET.SubElement(item, ns+'lastmod').text = lastmod
    ET.indent(sitemap, space='  ')
    output[ROOT/'sitemap.xml'] = '<?xml version="1.0" encoding="UTF-8"?>\n'+ET.tostring(sitemap, encoding='unicode')+'\n'
    output[ROOT/'robots.txt'] = 'User-agent: *\nAllow: /\n\nSitemap: '+ORIGIN+'sitemap.xml\n'
    stale = [str(path.relative_to(ROOT)) for path, value in output.items() if not path.exists() or path.read_text() != value]
    if check and stale:
        raise SystemExit('Generated files are stale: '+', '.join(stale))
    if not check:
        for path, value in output.items(): path.write_text(value)
    print(f'{"Checked" if check else "Built"} {len(available)} articles, static overview, structured data, sitemap and robots.txt')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    build(parser.parse_args().check)
