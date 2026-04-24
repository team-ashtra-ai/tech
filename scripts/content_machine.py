#!/usr/bin/env python3
"""Generate Rotata article ideas and optional draft articles.

This uses local data by default. If PIXABAY_API_KEY is present it can fetch
free imagery metadata. If OLLAMA_HOST is present it can request a local LLM
draft; otherwise it creates a structured editorial brief.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
BLOG = SRC / "content/es/blog"
TOPICS = ["HubSpot reporting", "CRM lifecycle", "ZoomInfo intent data", "LinkedIn outbound", "AI RevOps", "marketing sales ROI", "data quality", "SGE B2B SEO", "lead scoring", "pipeline governance"]

def slugify(value: str) -> str:
    value = value.lower()
    for src, dest in {"á":"a","é":"e","í":"i","ó":"o","ú":"u","ñ":"n"}.items():
        value = value.replace(src, dest)
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")

def pixabay_image(query: str) -> dict:
    key = os.getenv("PIXABAY_API_KEY")
    if not key:
        return {}
    url = "https://pixabay.com/api/?" + urllib.parse.urlencode({"key": key, "q": query, "image_type": "illustration", "safesearch": "true", "per_page": 3})
    with urllib.request.urlopen(url, timeout=20) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data.get("hits", [{}])[0] if data.get("hits") else {}

def idea(topic: str, index: int) -> dict:
    title = f"Cómo estructurar {topic} para generar pipeline B2B medible"
    return {
        "title": title,
        "slug": slugify(title),
        "category": "RevOps" if "CRM" in topic or "HubSpot" in topic else "Strategy",
        "linkedin_angle": "Abrir con un problema operativo concreto, explicar el sistema y cerrar con una pregunta para directores de marketing y ventas.",
        "outline": ["Problema de negocio", "Por qué la herramienta sola no lo resuelve", "Sistema recomendado", "Métricas para medirlo", "CTA hacia diagnóstico Rotata"],
        "image_query": f"B2B {topic} data system abstract",
    }

def create_draft(payload: dict) -> Path:
    today = dt.date.today().isoformat()
    image = pixabay_image(payload["image_query"])
    content = {
        "title": payload["title"],
        "slug": payload["slug"],
        "date": today,
        "category": payload["category"],
        "excerpt": "Un enfoque práctico para convertir herramientas, datos y procesos en un sistema de crecimiento B2B medible.",
        "reading_time": 6,
        "author": "Rotata",
        "image": image.get("webformatURL", "/assets/diagrams/rotata-growth-system-overlay.svg"),
        "alt": payload["image_query"],
        "linkedin_post": f"{payload['title']}\n\nLa clave no es añadir más herramientas. Es definir el sistema que convierte actividad en pipeline medible.\n\n¿Qué parte de tu sistema revisarías primero?",
        "content": "<p>Este borrador editorial debe revisarse antes de publicar.</p>" + "".join(f"<h2>{section}</h2><p>Desarrollar con ejemplos específicos de CRM, datos, automatización y medición.</p>" for section in payload["outline"]),
    }
    path = BLOG / f"{payload['slug']}.json"
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    return path

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ideas", type=int, default=10)
    parser.add_argument("--draft", action="store_true")
    args = parser.parse_args()
    ideas = [idea(topic, index) for index, topic in enumerate(TOPICS[: args.ideas])]
    out = SRC / "data/article-ideas.json"
    out.write_text(json.dumps(ideas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    if args.draft and ideas:
        print(f"Wrote draft {create_draft(ideas[0])}")

if __name__ == "__main__":
    main()
