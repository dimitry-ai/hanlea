#!/usr/bin/env python3
"""Normalize navigation URLs in the built site; preserve file:// links in source."""
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import argparse
import re

SOURCE = Path(__file__).resolve().parents[1]
ANCHOR = re.compile(r'(<a\b[^>]*?\s+href\s*=\s*)([\"\x27])([^\"\x27]*)(\2)', re.I)

def normalize(match):
    prefix, quote, value, _ = match.groups()
    url = urlsplit(value)
    if not url.scheme and not url.netloc and url.path.endswith('index.html'):
        url = url._replace(path=url.path.removesuffix('index.html') or './')
        value = urlunsplit(url)
    return prefix+quote+value+quote

def prepare(directory):
    root = Path(directory).resolve()
    if root == SOURCE or not (root/'index.html').is_file():
        raise SystemExit('Pass a built site directory containing index.html, not the source checkout.')
    changed = 0
    for path in sorted(root.rglob('*.html')):
        original = path.read_text(encoding='utf-8')
        updated = ANCHOR.sub(normalize, original)
        if original != updated:
            path.write_text(updated, encoding='utf-8')
            changed += 1
    print(f'Prepared canonical navigation links in {changed} HTML pages')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', help='Jekyll output directory, usually _site')
    prepare(parser.parse_args().directory)
