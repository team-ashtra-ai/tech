#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SOURCE_DIR = SRC / "content" / "es" / "blog"
TARGET_ROOT = SRC / "content"
TARGET_CODES = {
    "en": "en",
    "fr": "fr",
}


def batched(items: list[str], size: int) -> list[list[str]]:
    return [items[index:index + size] for index in range(0, len(items), size)]


def translate_text(value: str, translator: GoogleTranslator) -> str:
    text = (value or "").strip()
    if not text:
        return value
    return translator.translate(value)


def translate_html_fragment(html: str, translator: GoogleTranslator) -> str:
    soup = BeautifulSoup(f"<div>{html}</div>", "html.parser")
    root = soup.div
    nodes = [str(child) for child in root.contents]
    translated = nodes[:]
    queue: list[tuple[int, str]] = [
        (index, node) for index, node in enumerate(nodes) if node.strip()
    ]

    for batch in batched([node for _, node in queue], 6):
        translated_batch = translator.translate_batch(batch)
        for translated_value, (index, _) in zip(translated_batch, queue[: len(batch)]):
            translated[index] = translated_value
        queue = queue[len(batch):]

    return "".join(translated)


def restore_media_attrs(source_html: str, translated_html: str) -> str:
    source_soup = BeautifulSoup(f"<div>{source_html}</div>", "html.parser")
    translated_soup = BeautifulSoup(f"<div>{translated_html}</div>", "html.parser")
    for tag_name in ("img", "iframe", "source"):
        source_tags = source_soup.find_all(tag_name)
        translated_tags = translated_soup.find_all(tag_name)
        if len(source_tags) != len(translated_tags):
            continue
        for source_tag, translated_tag in zip(source_tags, translated_tags):
            translated_alt = translated_tag.get("alt")
            translated_tag.attrs = dict(source_tag.attrs)
            if translated_alt:
                translated_tag["alt"] = translated_alt
    return translated_soup.div.decode_contents()


def translate_post(source_path: Path, lang: str) -> dict:
    translator = GoogleTranslator(source="es", target=TARGET_CODES[lang])
    source = json.loads(source_path.read_text(encoding="utf-8"))
    target = {
        "title": translate_text(source["title"], translator),
        "slug": source["slug"],
        "date": source["date"],
        "category": source["category"],
        "excerpt": translate_text(source["excerpt"], translator),
        "reading_time": source["reading_time"],
        "author": source["author"],
        "image": source["image"],
        "alt": translate_text(source["alt"], translator),
        "source_url": source["source_url"],
        "content": restore_media_attrs(source["content"], translate_html_fragment(source["content"], translator)),
    }
    return target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--langs", nargs="+", default=["en", "fr"], choices=sorted(TARGET_CODES))
    args = parser.parse_args()

    source_files = sorted(SOURCE_DIR.glob("*.json"))
    for lang in args.langs:
        target_dir = TARGET_ROOT / lang / "blog"
        target_dir.mkdir(parents=True, exist_ok=True)
        for source_path in source_files:
            translated = translate_post(source_path, lang)
            output_path = target_dir / source_path.name
            output_path.write_text(json.dumps(translated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Translated {len(source_files)} posts into {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
