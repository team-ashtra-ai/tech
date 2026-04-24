#!/usr/bin/env python3
"""Generate non-English content from English source.

Default mode copies English text into target languages as placeholders.
If `OLLAMA_HOST` is configured, the script can ask a local model to translate.
This keeps English as the editorial source of truth while preserving a
repeatable workflow for later language generation.
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_PATH = ROOT / "src/data/site.json"


def ollama_translate(text: str, target_language: str) -> str:
    host = os.getenv("OLLAMA_HOST", "").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "llama3.1")
    if not host:
        return text

    payload = json.dumps(
        {
            "model": model,
            "stream": False,
            "prompt": (
                f"Translate the following website copy into {target_language}. "
                "Keep HTML, punctuation, CTA tone, and B2B marketing meaning intact. "
                "Return only the translated text.\n\n"
                f"{text}"
            ),
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{host}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data.get("response", text).strip() or text
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return text


def translate_value(value, target_language: str, use_ollama: bool):
    if isinstance(value, dict):
        return {key: translate_value(inner, target_language, use_ollama) for key, inner in value.items()}
    if isinstance(value, list):
        return [translate_value(item, target_language, use_ollama) for item in value]
    if isinstance(value, str):
        if use_ollama:
            return ollama_translate(value, target_language)
        return value
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-lang")
    parser.add_argument("--set-source-language", choices=["en", "es", "fr"])
    parser.add_argument("--to-langs", nargs="+", default=["es", "fr"])
    parser.add_argument("--use-ollama", action="store_true")
    args = parser.parse_args()

    site = json.loads(SITE_PATH.read_text(encoding="utf-8"))
    if args.set_source_language:
        site["source_language"] = args.set_source_language
        SITE_PATH.write_text(json.dumps(site, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Set source language to {args.set_source_language} in {SITE_PATH}")
        return 0

    source_lang = args.from_lang or site.get("source_language", "en")
    for page in site["pages"].values():
        source = deepcopy(page["translations"][source_lang])
        for lang in args.to_langs:
            if lang == source_lang:
                continue
            language_name = site["languages"][lang]["name"]
            page["translations"][lang] = translate_value(source, language_name, args.use_ollama)

    SITE_PATH.write_text(json.dumps(site, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated {SITE_PATH} from {source_lang} into {', '.join(args.to_langs)}")
    if args.use_ollama:
        print("Translation mode: local Ollama")
    else:
        print("Translation mode: English copied as placeholders")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
