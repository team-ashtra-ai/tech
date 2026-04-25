#!/usr/bin/env python3
import json
from pathlib import Path

import build_site

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCHEMA = ROOT / "schema"
site = json.loads((SRC / "data/site.json").read_text(encoding="utf-8"))
blog = json.loads((SRC / "data/blog.json").read_text(encoding="utf-8"))

SCHEMA.mkdir(exist_ok=True)
org = {"@context": "https://schema.org", "@type": "Organization", "name": site["site"]["company"], "url": site["site"]["base_url"], "logo": site["site"]["base_url"] + site["site"]["logo"], "sameAs": [site["site"]["linkedin"]]}
website = {"@context": "https://schema.org", "@type": "WebSite", "name": site["site"]["name"], "url": site["site"]["base_url"], "publisher": {"@type": "Organization", "name": site["site"]["company"]}}
services = []
for key, meta in build_site.PAGE_DEFS.items():
    if not meta.get("schema_service"):
        continue
    payload = build_site.page_payload(key, "en")
    services.append({
        "@context": "https://schema.org",
        "@type": "Service",
        "name": payload["translation"]["h1"],
        "serviceType": payload["seo_keyword"] or payload["translation"]["h1"],
        "provider": {"@type": "Organization", "name": site["site"]["company"]},
    })
articles = [{"@context": "https://schema.org", "@type": "BlogPosting", "headline": item["title"], "datePublished": item["date"], "author": {"@type": "Person", "name": item["author"]}, "image": site["site"]["base_url"] + item["image"]} for item in blog]
(SCHEMA / "organization.json").write_text(json.dumps(org, ensure_ascii=False, indent=2), encoding="utf-8")
(SCHEMA / "website.json").write_text(json.dumps(website, ensure_ascii=False, indent=2), encoding="utf-8")
(SCHEMA / "service.json").write_text(json.dumps(services, ensure_ascii=False, indent=2), encoding="utf-8")
(SCHEMA / "article.json").write_text(json.dumps(articles, ensure_ascii=False, indent=2), encoding="utf-8")
print("Generated schema modules")
