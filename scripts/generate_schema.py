#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCHEMA = ROOT / "schema"
site = json.loads((SRC / "data/site.json").read_text(encoding="utf-8"))
blog = json.loads((SRC / "data/blog.json").read_text(encoding="utf-8"))

SCHEMA.mkdir(exist_ok=True)
org = {"@context": "https://schema.org", "@type": "Organization", "name": site["site"]["company"], "url": site["site"]["base_url"], "logo": site["site"]["base_url"] + site["site"]["logo"], "sameAs": [site["site"]["linkedin"]]}
website = {"@context": "https://schema.org", "@type": "WebSite", "name": site["site"]["name"], "url": site["site"]["base_url"], "publisher": {"@type": "Organization", "name": site["site"]["company"]}}
services = [{"@context": "https://schema.org", "@type": "Service", "name": page["translations"]["en"]["h1"], "serviceType": page["seo_keyword"], "provider": {"@type": "Organization", "name": site["site"]["company"]}} for key, page in site["pages"].items() if key in {"solutions","hubspot","zoominfo","outbound","synapsale"}]
articles = [{"@context": "https://schema.org", "@type": "BlogPosting", "headline": item["title"], "datePublished": item["date"], "author": {"@type": "Person", "name": item["author"]}, "image": site["site"]["base_url"] + item["image"]} for item in blog]
(SCHEMA / "organization.json").write_text(json.dumps(org, ensure_ascii=False, indent=2), encoding="utf-8")
(SCHEMA / "website.json").write_text(json.dumps(website, ensure_ascii=False, indent=2), encoding="utf-8")
(SCHEMA / "service.json").write_text(json.dumps(services, ensure_ascii=False, indent=2), encoding="utf-8")
(SCHEMA / "article.json").write_text(json.dumps(articles, ensure_ascii=False, indent=2), encoding="utf-8")
print("Generated schema modules")
