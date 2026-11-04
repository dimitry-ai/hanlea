#!/usr/bin/env python3
"""Check crawlability, article/schema consistency and local file navigation."""
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import json
import runpy
import struct
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
build = runpy.run_path(str(ROOT/'scripts/build-insights.py'))
entries = build['load_articles']()
ORIGIN = build['ORIGIN']

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.refs=[]; self.meta={}; self.h1=0
        self.canonical=None; self.json=[]; self.json_buffer=None; self.topics=[]; self.times=[]; self.labels=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag=='h1': self.h1+=1
        if tag=='meta': self.meta[a.get('name') or a.get('property')]=a.get('content')
        if tag=='link' and a.get('rel')=='canonical': self.canonical=a['href']
        if tag=='script' and a.get('type')=='application/ld+json': self.json_buffer=[]
        if 'data-insight-topic' in a: self.topics.append(a['data-insight-topic'])
        if tag=='time': self.times.append(a.get('datetime'))
        for key in ['aria-labelledby','aria-describedby']:
            self.labels.extend(a.get(key,'').split())
        for key in ['src','href']:
            if key in a: self.refs.append(a[key])
    def handle_data(self, text):
        if self.json_buffer is not None: self.json_buffer.append(text)
    def handle_endtag(self, tag):
        if tag=='script' and self.json_buffer is not None:
            self.json.append(json.loads(''.join(self.json_buffer))); self.json_buffer=None

pages={}
for file in ROOT.rglob('*.html'):
    if '.git' in file.parts or '_site' in file.parts: continue
    page=Page();page.feed(file.read_text(encoding='utf-8-sig'));pages[file.resolve()]=page

for file,page in pages.items():
    assert page.h1==1,(file,'H1 count')
    assert not [id for id,n in Counter(page.ids).items() if n>1],(file,'duplicate IDs')
    assert all(id in page.ids for id in page.labels),(file,'ARIA target')
    for ref in page.refs:
        parsed=urlsplit(ref)
        if parsed.scheme or parsed.netloc:
            if not ref.startswith(ORIGIN): continue
            target=ROOT/unquote(parsed.path).lstrip('/')
        else:
            assert not ref.startswith('/'),(file,'file-incompatible path',ref)
            parsed=urlsplit(urljoin(file.as_uri(),ref));target=Path(unquote(parsed.path))
        if target.is_dir():target=target/'index.html'
        target=target.resolve()
        assert target.is_file(),(file,'missing target',ref)
        if parsed.fragment and parsed.fragment!='datenschutzeinstellungen' and target in pages:
            assert parsed.fragment in pages[target].ids,(file,'missing anchor',ref)

ready=[a for a in entries if a['status'] in build['AVAILABLE']]
expected=sorted(ready,key=lambda a:(-date.fromisoformat(a['date']).toordinal(),a['id']))
assert pages[ROOT/'insights/index.html'].topics==[a['id'] for a in expected],'static overview ordering'
assert 'world-tour' not in {a['id'] for a in entries},'excluded event is listed'
for entry in ready:
    file=ROOT/entry['path'];page=pages[file]
    assert page.canonical==build['canonical'](entry),(file,'canonical')
    assert page.meta['description']==entry['description'],(file,'description')
    assert 80<=len(entry['description'])<=200,(file,'description length')
    assert 'assets/js/contact.js' in '\n'.join(page.refs),(file,'shared consultation script')
    if entry['status']!='draft':assert 'noindex' not in page.meta.get('robots',''),(file,'indexing blocked')
    graph=next(data['@graph'] for data in page.json if '@graph' in data)
    article=next(item for item in graph if item['@type']=='BlogPosting')
    breadcrumb=next(item for item in graph if item['@type']=='BreadcrumbList')
    assert article['headline']==entry['title'] and article['description']==entry['description'],(file,'schema text')
    assert article['dateModified']==entry['updatedAt'],(file,'revision metadata')
    assert page.times==[entry['date']],(file,'visible editorial date')
    assert article['isBasedOn'].get('dateCreated')==entry.get('sourceDate'),(file,'source-draft date')
    assert article.get('datePublished')==entry.get('publishedAt'),(file,'invented publication date')
    assert breadcrumb['itemListElement'][-1]['item']==page.canonical,(file,'breadcrumb URL')
    assert article['author']['name']=='Hanlea' and article['author']['url']==ORIGIN+'#ueber-uns',(file,'author')
    assert article['wordCount']>=450,(file,'article unexpectedly short')
    assert page.meta['og:url']==page.canonical and page.meta['og:type']=='article',(file,'sharing metadata')
    image=ROOT/entry['ogImage'];data=image.read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('!II',data[16:24])==(1200,630),(file,'sharing image')

sitemap=ET.parse(ROOT/'sitemap.xml').getroot()
urls=[item.text for item in sitemap.iter() if item.tag.endswith('}loc')]
assert len(urls)==len(set(urls)),'duplicate sitemap URL'
assert not any('musterartikel' in url or 'world-tour' in url for url in urls),'redirect or excluded event in sitemap'
for entry in ready:
    if entry['status']!='draft':assert build['canonical'](entry) in urls,entry['id']
assert 'Sitemap: '+ORIGIN+'sitemap.xml' in (ROOT/'robots.txt').read_text()
for svg in (ROOT/'assets/illustrations').glob('*.svg'):ET.parse(svg)
build['build'](check=True)
print(f'PASS {len(pages)} HTML pages, {len(ready)} complete articles, static links, dates, JSON-LD, social images and sitemap')
