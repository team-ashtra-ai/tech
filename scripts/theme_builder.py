#!/usr/bin/env python3
"""Analyze a reference site and write a replaceable theme slot override.

This script is intentionally heuristic. It extracts common colors and font
families from a URL, then updates `src/data/themes.json` and
`src/styles/generated/theme-overrides.css` for a chosen theme id.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
THEMES_PATH = ROOT / "src/data/themes.json"
OVERRIDES_PATH = ROOT / "src/styles/generated/theme-overrides.css"
USER_AGENT = "Mozilla/5.0 (compatible; RotataThemeBuilder/1.0; +https://rotata.es/)"
HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}")
FONT_RE = re.compile(r"font-family\s*:\s*([^;}{]+)", re.I)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_hex(value: str) -> str | None:
    value = value.strip().lower()
    if not value.startswith("#"):
        return None
    raw = value[1:]
    if len(raw) == 3:
        raw = "".join(channel * 2 for channel in raw)
    elif len(raw) == 4:
        raw = "".join(channel * 2 for channel in raw[:3])
    elif len(raw) == 8:
        raw = raw[:6]
    if len(raw) != 6:
        return None
    return f"#{raw}"


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = normalize_hex(value) or "#000000"
    return tuple(int(value[index:index + 2], 16) for index in (1, 3, 5))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def rgba(value: str, alpha: float) -> str:
    r, g, b = hex_to_rgb(value)
    alpha = max(0.0, min(1.0, alpha))
    return f"rgba({r}, {g}, {b}, {alpha:.2f})"


def mix(a: str, b: str, ratio: float) -> str:
    ar, ag, ab = hex_to_rgb(a)
    br, bg, bb = hex_to_rgb(b)
    ratio = max(0.0, min(1.0, ratio))
    rgb = (
        round(ar * (1 - ratio) + br * ratio),
        round(ag * (1 - ratio) + bg * ratio),
        round(ab * (1 - ratio) + bb * ratio),
    )
    return rgb_to_hex(rgb)


def lighten(color: str, amount: float) -> str:
    return mix(color, "#ffffff", amount)


def darken(color: str, amount: float) -> str:
    return mix(color, "#000000", amount)


def luminance(color: str) -> float:
    channels = []
    for channel in hex_to_rgb(color):
        normalized = channel / 255
        if normalized <= 0.03928:
            channels.append(normalized / 12.92)
        else:
            channels.append(((normalized + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def saturation(color: str) -> float:
    r, g, b = [channel / 255 for channel in hex_to_rgb(color)]
    maximum = max(r, g, b)
    minimum = min(r, g, b)
    if maximum == minimum:
        return 0.0
    lightness = (maximum + minimum) / 2
    delta = maximum - minimum
    divisor = 1 - abs(2 * lightness - 1)
    return delta / divisor if divisor else 0.0


def unique_preserving_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def fetch_reference(url: str) -> tuple[str, list[str], list[str], str | None, str | None]:
    response = requests.get(url, timeout=20, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else None
    description_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
    description = description_tag.get("content", "").strip() if description_tag else None

    css_sources: list[str] = []
    for link in soup.find_all("link", rel=lambda value: value and "stylesheet" in value):
        href = link.get("href")
        if href:
            css_sources.append(urljoin(url, href))

    css_chunks: list[str] = []
    for source in css_sources[:8]:
        try:
            sheet = requests.get(source, timeout=20, headers={"User-Agent": USER_AGENT})
            if sheet.ok:
                css_chunks.append(sheet.text)
        except requests.RequestException:
            continue

    for style in soup.find_all("style"):
        text = style.get_text(" ", strip=True)
        if text:
            css_chunks.append(text)

    colors = [normalized for normalized in (normalize_hex(match) for match in HEX_RE.findall("\n".join(css_chunks))) if normalized]
    fonts = []
    for family in FONT_RE.findall("\n".join(css_chunks)):
        fonts.extend(part.strip(" '\"\t") for part in family.split(","))
    fonts = [font for font in fonts if font and not font.startswith("var(")]
    return html, colors, unique_preserving_order(fonts), title, description


def choose_surface(colors: list[str], explicit: str) -> str:
    if explicit in {"light", "dark"}:
        return explicit
    if not colors:
        return "dark"
    weighted = []
    counts = Counter(colors)
    for color, count in counts.most_common(20):
        weighted.extend([luminance(color)] * count)
    score = sum(weighted) / len(weighted)
    return "dark" if score < 0.45 else "light"


def pick_palette(colors: list[str], surface: str) -> dict[str, str]:
    counts = Counter(colors)
    popular = [color for color, _ in counts.most_common(80)]
    if not popular:
        popular = ["#07131f", "#7fdaf6", "#ff6d70"] if surface == "dark" else ["#f6f8fb", "#2563eb", "#0f766e"]

    if surface == "dark":
        backgrounds = sorted(popular, key=luminance)
        texts = sorted(popular, key=luminance, reverse=True)
    else:
        backgrounds = sorted(popular, key=luminance, reverse=True)
        texts = sorted(popular, key=luminance)

    background = backgrounds[0]
    text = texts[0]
    accent_candidates = [
        color for color in popular
        if abs(luminance(color) - luminance(background)) > 0.14 and saturation(color) > 0.18
    ]
    accent = accent_candidates[0] if accent_candidates else ("#7a4cff" if surface == "dark" else "#2563eb")
    accent_2 = accent_candidates[1] if len(accent_candidates) > 1 else (lighten(accent, 0.2) if surface == "dark" else darken(accent, 0.25))
    signal = accent_candidates[2] if len(accent_candidates) > 2 else accent_2
    muted = mix(text, background, 0.48 if surface == "dark" else 0.56)

    if surface == "dark":
        return {
            "background": darken(background, 0.06),
            "surface": lighten(background, 0.04),
            "surface_2": lighten(background, 0.07),
            "surface_3": lighten(background, 0.12),
            "text": lighten(text, 0.04),
            "muted": muted,
            "accent": accent,
            "accent_2": accent_2,
            "signal": signal,
        }
    return {
        "background": lighten(background, 0.02),
        "surface": "#ffffff" if luminance(background) > 0.85 else lighten(background, 0.08),
        "surface_2": darken(background, 0.02),
        "surface_3": darken(background, 0.06),
        "text": darken(text, 0.08),
        "muted": muted,
        "accent": accent,
        "accent_2": accent_2,
        "signal": signal,
    }


def pick_fonts(fonts: list[str], surface: str) -> tuple[str, str]:
    fallbacks = {
        "heading_dark": '"Space Grotesk", "Aptos Display", sans-serif',
        "body_dark": '"Manrope", "Aptos", sans-serif',
        "heading_light": '"Aptos Display", "Segoe UI", sans-serif',
        "body_light": '"Manrope", "Aptos", sans-serif',
    }
    custom = [font for font in fonts if font.lower() not in {"serif", "sans-serif", "monospace", "arial", "helvetica", "verdana"}]
    heading = custom[0] if custom else None
    body = custom[1] if len(custom) > 1 else heading
    if heading:
        heading_stack = f'"{heading}", {fallbacks["heading_dark" if surface == "dark" else "heading_light"]}'
    else:
        heading_stack = fallbacks["heading_dark" if surface == "dark" else "heading_light"]
    if body:
        body_stack = f'"{body}", {fallbacks["body_dark" if surface == "dark" else "body_light"]}'
    else:
        body_stack = fallbacks["body_dark" if surface == "dark" else "body_light"]
    return heading_stack, body_stack


def build_theme_metadata(theme_id: str, label: str, url: str, surface: str, palette: dict[str, str]) -> dict:
    host = urlparse(url).netloc.replace("www.", "")
    short_label = label.split()[0][:12]
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    summary = {
        "es": f"Tema generado desde {host} el {generated_at} a partir de paleta y tipografia detectadas automaticamente.",
        "en": f"Theme generated from {host} on {generated_at} using automatically detected palette and typography cues.",
        "fr": f"Theme genere depuis {host} le {generated_at} a partir d'indices automatiques de palette et de typographie.",
    }
    return {
        "id": theme_id,
        "surface": surface,
        "replaceable": True,
        "theme_color": palette["background"],
        "reference_url": url,
        "label": {"es": label, "en": label, "fr": label},
        "chip_label": {"es": short_label, "en": short_label, "fr": short_label},
        "summary": summary,
        "swatch": [palette["accent"], palette["accent_2"], palette["background"]],
    }


def build_override_css(theme_id: str, surface: str, palette: dict[str, str], heading_font: str, body_font: str) -> str:
    background = palette["background"]
    surface_1 = palette["surface"]
    surface_2 = palette["surface_2"]
    surface_3 = palette["surface_3"]
    text = palette["text"]
    muted = palette["muted"]
    accent = palette["accent"]
    accent_2 = palette["accent_2"]
    signal = palette["signal"]
    panel_alpha = 0.78 if surface == "dark" else 0.88
    panel_soft_alpha = 0.58 if surface == "dark" else 0.76
    panel_strong_alpha = 0.92 if surface == "dark" else 0.95
    header_alpha = 0.46 if surface == "dark" else 0.70
    border_alpha = 0.12 if surface == "dark" else 0.11
    border_strong_alpha = 0.22 if surface == "dark" else 0.20
    grid_alpha = 0.05 if surface == "dark" else 0.06
    hero_overlay_start = rgba(background, 0.94 if surface == "dark" else 0.96)
    hero_overlay_mid = rgba(background, 0.78 if surface == "dark" else 0.84)
    hero_overlay_end = rgba(background, 0.28 if surface == "dark" else 0.28)
    footer_end = rgba(background, 0.96 if surface == "dark" else 0.94)
    footer_mid = rgba(background, 0.78 if surface == "dark" else 0.82)
    footer_start = rgba(background, 0.0)
    primary_text = "#ffffff" if surface == "dark" else ("#ffffff" if luminance(accent) < 0.55 else darken(background, 0.55))
    secondary_bg = rgba(surface_1, 0.74 if surface == "dark" else 0.82)

    return f"""/* theme: {theme_id}:start */
[data-design-theme="{theme_id}"] {{
  color-scheme: {surface};
  --color-ink: {darken(background, 0.04) if surface == "light" else darken(background, 0.02)};
  --color-ink-2: {lighten(background, 0.04) if surface == "light" else lighten(background, 0.02)};
  --color-body: {background};
  --color-primary: {accent};
  --color-surface: {surface_1};
  --color-surface-2: {surface_2};
  --color-surface-3: {surface_3};
  --color-panel: {rgba(surface_1, panel_alpha)};
  --color-panel-soft: {rgba(surface_1, panel_soft_alpha)};
  --color-panel-strong: {rgba(darken(background, 0.02) if surface == "dark" else lighten(surface_1, 0.01), panel_strong_alpha)};
  --color-header: {rgba(background, header_alpha)};
  --color-text: {text};
  --color-muted: {muted};
  --color-accent: {accent};
  --color-accent-2: {accent_2};
  --color-signal: {signal};
  --color-gold: {mix(accent, accent_2, 0.35)};
  --color-success: {signal};
  --color-warning: {mix(accent, "#f2b84b", 0.4)};
  --color-error: {mix(accent, "#ff6b66", 0.45)};
  --color-border: {rgba(text, border_alpha)};
  --color-border-strong: {rgba(text, border_strong_alpha)};
  --color-grid: {rgba(text, grid_alpha)};
  --color-focus: {accent_2};
  --body-background:
    radial-gradient(circle at 12% 14%, {rgba(accent, 0.16 if surface == "light" else 0.22)}, transparent 22rem),
    radial-gradient(circle at 88% 18%, {rgba(accent_2, 0.12 if surface == "light" else 0.18)}, transparent 24rem),
    linear-gradient(180deg, {background}, {mix(background, surface_2, 0.22)} 34%, {mix(background, surface_3, 0.28)} 68%, {background});
  --body-atmosphere:
    radial-gradient(circle at 16% 12%, {rgba(accent, 0.08 if surface == "light" else 0.14)}, transparent 18rem),
    radial-gradient(circle at 78% 16%, {rgba(accent_2, 0.08 if surface == "light" else 0.12)}, transparent 18rem);
  --body-grid-size: {"72px" if surface == "light" else "88px"};
  --body-grid-opacity: {"0.20" if surface == "light" else "0.24"};
  --color-hero-overlay: linear-gradient(90deg, {hero_overlay_start} 0%, {hero_overlay_mid} 46%, {hero_overlay_end} 78%);
  --hero-after-background:
    radial-gradient(circle at 72% 42%, {rgba(accent_2, 0.14 if surface == "light" else 0.18)}, transparent 18rem),
    radial-gradient(circle at 84% 74%, {rgba(accent, 0.12 if surface == "light" else 0.18)}, transparent 20rem);
  --footer-background:
    radial-gradient(circle at 16% 12%, {rgba(accent, 0.10 if surface == "light" else 0.14)}, transparent 18rem),
    linear-gradient(180deg, {footer_start}, {footer_mid} 14%, {footer_end});
  --font-heading: {heading_font};
  --font-body: {body_font};
  --font-mono: "JetBrains Mono", "Aptos Mono", "Consolas", monospace;
  --header-shell-radius: {"20px" if surface == "light" else "24px"};
  --utility-shell-radius: {"14px" if surface == "light" else "18px"};
  --nav-shell-radius: {"14px" if surface == "light" else "18px"};
  --button-radius: {"14px" if surface == "light" else "18px"};
  --card-radius: {"18px" if surface == "light" else "22px"};
  --visual-radius: {"24px" if surface == "light" else "32px"};
  --field-radius: {"14px" if surface == "light" else "18px"};
  --eyebrow-radius: {"14px" if surface == "light" else "999px"};
  --hero-top-offset: {"220px" if surface == "light" else "224px"};
  --panel-blur: {"10px" if surface == "light" else "18px"};
  --panel-top-highlight: {rgba("#ffffff", 0.82 if surface == "light" else 0.06)};
  --panel-top-highlight-strong: {rgba("#ffffff", 0.90 if surface == "light" else 0.08)};
  --eyebrow-bg: {rgba(surface_1, 0.78 if surface == "light" else 0.72)};
  --eyebrow-border: {rgba(accent, 0.18 if surface == "light" else 0.22)};
  --eyebrow-color: {signal};
  --btn-primary-bg: linear-gradient(135deg, {accent}, {accent_2});
  --btn-primary-color: {primary_text};
  --btn-primary-shadow: 0 18px 40px {rgba(accent, 0.22 if surface == "light" else 0.30)};
  --btn-secondary-bg: {secondary_bg};
  --btn-secondary-border: {rgba(text, 0.12 if surface == "light" else 0.14)};
  --btn-secondary-color: {text};
  --section-background-accent:
    radial-gradient(circle at 12% 18%, {rgba(accent, 0.10 if surface == "light" else 0.16)}, transparent 16rem),
    radial-gradient(circle at 88% 84%, {rgba(accent_2, 0.08 if surface == "light" else 0.12)}, transparent 16rem);
  --section-number-color: {mix(accent, text, 0.42)};
  --heading-letter-spacing: -0.04em;
  --heading-line-height: 0.94;
  --hero-image-opacity: {"0.72" if surface == "light" else "0.80"};
  --hero-image-filter: {"saturate(0.94) contrast(1.02)" if surface == "light" else "saturate(1.08) contrast(1.06)"};
  --shadow-soft: 0 28px 72px {rgba(background, 0.14 if surface == "light" else 0.40)};
  --shadow-card: 0 18px 42px {rgba(background, 0.10 if surface == "light" else 0.34)};
  --shadow-hard: 0 10px 24px {rgba(background, 0.16 if surface == "light" else 0.44)};
  --shadow-hero: 0 38px 96px {rgba(background, 0.12 if surface == "light" else 0.48)};
}}
/* theme: {theme_id}:end */
"""


def update_theme_registry(theme_id: str, metadata: dict) -> None:
    payload = read_json(THEMES_PATH)
    themes = payload.get("themes", [])
    for index, theme in enumerate(themes):
        if theme.get("id") == theme_id:
            themes[index] = metadata
            break
    else:
        themes.append(metadata)
    payload["themes"] = themes
    write_json(THEMES_PATH, payload)


def update_override_css(theme_id: str, css_block: str) -> None:
    OVERRIDES_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing = OVERRIDES_PATH.read_text(encoding="utf-8") if OVERRIDES_PATH.exists() else ""
    pattern = re.compile(
        rf"/\* theme: {re.escape(theme_id)}:start \*/.*?/\* theme: {re.escape(theme_id)}:end \*/\n?",
        re.S,
    )
    if pattern.search(existing):
        updated = pattern.sub(css_block.rstrip() + "\n", existing)
    else:
        separator = "\n" if existing and not existing.endswith("\n") else ""
        updated = f"{existing}{separator}{css_block.rstrip()}\n"
    OVERRIDES_PATH.write_text(updated, encoding="utf-8")


def build_label(explicit: str | None, title: str | None, url: str) -> str:
    if explicit:
        return explicit.strip()
    if title:
        head = re.split(r"\s*[|:-]\s*", title)[0].strip()
        if head:
            return head[:36]
    hostname = urlparse(url).netloc.replace("www.", "").split(".")[0]
    return hostname.replace("-", " ").title()[:36]


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a replaceable theme slot from a reference URL.")
    parser.add_argument("url", help="Reference URL to analyze.")
    parser.add_argument("theme_id", help="Theme id to replace or create.")
    parser.add_argument("--label", help="Override the generated theme label.")
    parser.add_argument("--surface", choices=["auto", "light", "dark"], default="auto", help="Force light or dark mode.")
    parser.add_argument("--dry-run", action="store_true", help="Print the generated metadata and CSS without writing files.")
    args = parser.parse_args()

    _, colors, fonts, title, description = fetch_reference(args.url)
    surface = choose_surface(colors, args.surface)
    palette = pick_palette(colors, surface)
    heading_font, body_font = pick_fonts(fonts, surface)
    label = build_label(args.label, title, args.url)
    metadata = build_theme_metadata(args.theme_id, label, args.url, surface, palette)
    css_block = build_override_css(args.theme_id, surface, palette, heading_font, body_font)

    if args.dry_run:
        print(json.dumps(metadata, ensure_ascii=False, indent=2))
        print()
        print(css_block)
        return 0

    update_theme_registry(args.theme_id, metadata)
    update_override_css(args.theme_id, css_block)

    top_colors = [color for color, _ in Counter(colors).most_common(8)]
    print(f"Updated theme slot: {args.theme_id}")
    print(f"Label: {label}")
    print(f"Surface: {surface}")
    if title:
        print(f"Title: {title}")
    if description:
        print(f"Description: {description[:180]}")
    print(f"Top colors: {', '.join(top_colors) if top_colors else 'none detected'}")
    print(f"Fonts: {', '.join(fonts[:6]) if fonts else 'none detected'}")
    print(f"Wrote {THEMES_PATH.relative_to(ROOT)} and {OVERRIDES_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
