#!/usr/bin/env python3
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PUBLIC = ROOT / "public"
BASE_URL = "https://rotata.es"

urls = []
for html_file in sorted(DIST.rglob("*.html")):
    rel = html_file.relative_to(DIST)
    if rel.name == "404.html":
        continue
    url = "/" if str(rel) == "index.html" else "/" + str(rel.parent).replace("\\", "/").strip("/") + "/"
    urls.append(url)

body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for url in urls:
    body.append(f"  <url><loc>{BASE_URL}{url}</loc><lastmod>{date.today().isoformat()}</lastmod><changefreq>weekly</changefreq><priority>{'1.0' if url == '/' else '0.7'}</priority></url>")
body.append("</urlset>")
xml = "\n".join(body) + "\n"
PUBLIC.mkdir(exist_ok=True)
(PUBLIC / "sitemap.xml").write_text(xml, encoding="utf-8")
(DIST / "sitemap.xml").write_text(xml, encoding="utf-8")
robots = "User-agent: *\nAllow: /\nSitemap: https://rotata.es/sitemap.xml\n"
(PUBLIC / "robots.txt").write_text(robots, encoding="utf-8")
(DIST / "robots.txt").write_text(robots, encoding="utf-8")
print(f"Generated {len(urls)} sitemap URLs")
