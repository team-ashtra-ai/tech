#!/usr/bin/env python3
"""Generate premium section and hero visuals from Rotata's existing image library.

These assets are generated into `src/assets/section-visuals/` so they remain
static, Cloudflare-ready, and part of the WordPress export.
"""
from __future__ import annotations

import io
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = Path(__file__).resolve()
SRC = ROOT / "src"
ASSETS = SRC / "assets"
OUT = ASSETS / "section-visuals"
SITE_PATH = SRC / "data" / "site.json"
SITE = json.loads(SITE_PATH.read_text(encoding="utf-8"))

SECTION_SIZE = (1600, 1120)
HERO_SIZE = (1920, 1280)

DEFAULT_POOL = [
    "theme-sites/databricks-system.webp",
    "theme-sites/datagrail-privacy.webp",
    "theme-sites/atlan-context.webp",
    "theme-sites/runpod-infra.webp",
    "theme-sites/vectara-agent.webp",
    "blog/rotata-rotbot-auditando-errores-en-la-gestion-de-leads.png",
    "blog/rotata-rotbot-y-el-proceso-de-generacion-de-leads-con-roi.png",
    "blog/rotata-datos-de-intencion-estrategia-precisa-en-marketing-b2b.png",
    "blog/rotata-descubriendo-las-necesidades-del-cliente-con-intent-data.png",
    "blog/rotata-chatgpt-image-apr-30-2025-11-09-08-am.png",
    "blog/rotata-busqueda-generativa-sge-de-google-visibilidad-b2b-rotata.png",
    "partners/rotata-zoominfo-x-rotata-transformando-el-marketing-b2b-en-espana.png",
    "partners/rotata-hubspot-provider-rotata-partner-hubspot-en-espana.png",
    "partners/rotata-la-growth-machine-web.png",
    "images/rotata-rotbot-ai-assistant.png",
]

PAGE_POOLS = {
    "home": [
        "theme-sites/databricks-system.webp",
        "theme-sites/datagrail-privacy.webp",
        "theme-sites/atlan-context.webp",
        "theme-sites/runpod-infra.webp",
        "theme-sites/vectara-agent.webp",
        "blog/rotata-datos-de-intencion-estrategia-precisa-en-marketing-b2b.png",
        "blog/rotata-rotbot-y-el-proceso-de-generacion-de-leads-con-roi.png",
        "blog/rotata-busqueda-generativa-sge-de-google-visibilidad-b2b-rotata.png",
        "partners/rotata-zoominfo-x-rotata-transformando-el-marketing-b2b-en-espana.png",
    ],
    "about": [
        "theme-sites/atlan-about.webp",
        "theme-sites/databricks-about.webp",
        "theme-sites/datagrail-about.webp",
        "theme-sites/runpod-about.webp",
        "theme-sites/vectara-about.webp",
        "blog/rotata-chatgpt-image-apr-30-2025-11-09-08-am.png",
        "blog/rotata-rotbot-auditando-errores-en-la-gestion-de-leads.png",
        "blog/rotata-descubriendo-las-necesidades-del-cliente-con-intent-data.png",
    ],
    "solutions": [
        "theme-sites/databricks-solutions.webp",
        "theme-sites/datagrail-solutions.webp",
        "theme-sites/atlan-solutions.webp",
        "theme-sites/runpod-solutions.webp",
        "theme-sites/vectara-solutions.webp",
        "blog/rotata-datos-de-intencion-estrategia-precisa-en-marketing-b2b.png",
        "blog/rotata-rotbot-y-el-proceso-de-generacion-de-leads-con-roi.png",
        "blog/rotata-chatgpt-image-apr-30-2025-11-09-08-am.png",
    ],
    "services": [
        "theme-sites/databricks-services.webp",
        "theme-sites/datagrail-services.webp",
        "theme-sites/atlan-services.webp",
        "theme-sites/runpod-services.webp",
        "theme-sites/vectara-services.webp",
    ],
    "system": [
        "theme-sites/databricks-system.webp",
        "theme-sites/datagrail-system.webp",
        "theme-sites/atlan-system.webp",
        "theme-sites/runpod-system.webp",
        "theme-sites/vectara-system.webp",
    ],
    "partners": [
        "theme-sites/databricks-partners.webp",
        "theme-sites/datagrail-partners.webp",
        "theme-sites/atlan-partners.webp",
        "theme-sites/runpod-partners.webp",
        "theme-sites/vectara-partners.webp",
    ],
    "insights": [
        "theme-sites/databricks-insights.webp",
        "theme-sites/datagrail-insights.webp",
        "theme-sites/atlan-insights.webp",
        "theme-sites/runpod-insights.webp",
        "theme-sites/vectara-insights.webp",
    ],
    "contact": [
        "theme-sites/databricks-contact.webp",
        "theme-sites/datagrail-contact.webp",
        "theme-sites/atlan-contact.webp",
        "theme-sites/runpod-contact.webp",
        "theme-sites/vectara-contact.webp",
        "images/rotata-rotbot-ai-assistant.png",
    ],
    "legal": [
        "theme-sites/databricks-legal.webp",
        "theme-sites/datagrail-legal.webp",
        "theme-sites/atlan-legal.webp",
        "theme-sites/runpod-legal.webp",
        "theme-sites/vectara-legal.webp",
    ],
    "hubspot": [
        "theme-sites/databricks-partners.webp",
        "partners/rotata-errores-de-estructura-en-hubspot-que-distorsionan-tus-informes.png",
        "partners/rotata-logo-hubspot-informe-2026.png",
        "partners/rotata-hubspot-provider-rotata-partner-hubspot-en-espana.png",
        "partners/rotata-logo-hubspot-informe-2025-v2.png",
    ],
    "zoominfo": [
        "theme-sites/datagrail-partners.webp",
        "partners/rotata-zoominfo-x-rotata-transformando-el-marketing-b2b-en-espana.png",
        "partners/rotata-zoominfo-logo-2024.png",
        "blog/rotata-descubriendo-las-necesidades-del-cliente-con-intent-data.png",
    ],
    "outbound": [
        "theme-sites/runpod-services.webp",
        "partners/rotata-la-growth-machine-prospeccion-automatizada-con-ia.png",
        "partners/rotata-la-growth-machine-web.png",
        "blog/rotata-chatgpt-image-apr-30-2025-11-09-08-am.png",
    ],
    "synapsale": [
        "theme-sites/vectara-partners.webp",
        "blog/rotata-descubriendo-las-necesidades-del-cliente-con-intent-data.png",
        "blog/rotata-datos-de-intencion-estrategia-precisa-en-marketing-b2b.png",
        "partners/rotata-zoominfo-x-rotata-transformando-el-marketing-b2b-en-espana.png",
    ],
    "blog": [
        "theme-sites/databricks-insights.webp",
        "theme-sites/vectara-insights.webp",
        "blog/rotata-busqueda-generativa-sge-de-google-visibilidad-b2b-rotata.png",
        "blog/rotata-imagen-correo-spam.png",
        "blog/rotata-rotbot-y-el-proceso-de-generacion-de-leads-con-roi.png",
        "blog/rotata-precision-del-marketing-abm-en-estrategias-b2b.png",
    ],
    "roi": [
        "theme-sites/databricks-insights.webp",
        "theme-sites/runpod-insights.webp",
        "blog/rotata-rotbot-y-el-proceso-de-generacion-de-leads-con-roi.png",
        "blog/rotata-busqueda-generativa-sge-de-google-visibilidad-b2b-rotata.png",
        "blog/rotata-datos-de-intencion-estrategia-precisa-en-marketing-b2b.png",
    ],
    "cases": [
        "theme-sites/atlan-about.webp",
        "theme-sites/databricks-about.webp",
        "blog/rotata-rotbot-auditando-errores-en-la-gestion-de-leads.png",
        "blog/rotata-datos-de-intencion-estrategia-precisa-en-marketing-b2b.png",
        "partners/rotata-la-growth-machine-web.png",
    ],
    "process": [
        "theme-sites/runpod-about.webp",
        "theme-sites/atlan-about.webp",
        "blog/rotata-rotbot-y-el-proceso-de-generacion-de-leads-con-roi.png",
        "blog/rotata-busqueda-generativa-sge-de-google-visibilidad-b2b-rotata.png",
        "blog/rotata-chatgpt-image-apr-30-2025-11-09-08-am.png",
    ],
    "privacy": ["theme-sites/datagrail-legal.webp", "blog/rotata-datos-de-intencion-estrategia-precisa-en-marketing-b2b.png"],
    "cookies": ["theme-sites/datagrail-legal.webp", "blog/rotata-imagen-correo-spam.png"],
    "accessibility": ["theme-sites/vectara-legal.webp", "blog/rotata-chatgpt-image-apr-30-2025-11-09-08-am.png"],
    "sitemap": ["theme-sites/atlan-legal.webp", "blog/rotata-descubriendo-las-necesidades-del-cliente-con-intent-data.png"],
}

VARIANT_POOLS = {
    "problem": [
        "theme-sites/datagrail-solutions.webp",
        "theme-sites/runpod-system.webp",
        "blog/rotata-rotbot-auditando-errores-en-la-gestion-de-leads.png",
        "partners/rotata-errores-de-estructura-en-hubspot-que-distorsionan-tus-informes.png",
        "blog/rotata-imagen-correo-spam.png",
    ],
    "cards": [
        "theme-sites/databricks-services.webp",
        "theme-sites/vectara-system.webp",
        "blog/rotata-chatgpt-image-apr-30-2025-11-09-08-am.png",
        "blog/rotata-descubriendo-las-necesidades-del-cliente-con-intent-data.png",
        "partners/rotata-la-growth-machine-web.png",
    ],
    "grid": [
        "theme-sites/atlan-system.webp",
        "theme-sites/databricks-solutions.webp",
        "blog/rotata-datos-de-intencion-estrategia-precisa-en-marketing-b2b.png",
        "blog/rotata-precision-del-marketing-abm-en-estrategias-b2b.png",
        "blog/rotata-descubriendo-las-necesidades-del-cliente-con-intent-data.png",
    ],
    "process": [
        "theme-sites/runpod-about.webp",
        "theme-sites/runpod-services.webp",
        "blog/rotata-rotbot-y-el-proceso-de-generacion-de-leads-con-roi.png",
        "partners/rotata-la-growth-machine-prospeccion-automatizada-con-ia.png",
        "partners/rotata-la-growth-machine-web.png",
    ],
    "metrics": [
        "theme-sites/vectara-insights.webp",
        "theme-sites/databricks-system.webp",
        "blog/rotata-busqueda-generativa-sge-de-google-visibilidad-b2b-rotata.png",
        "blog/rotata-rotbot-y-el-proceso-de-generacion-de-leads-con-roi.png",
        "blog/rotata-datos-de-intencion-estrategia-precisa-en-marketing-b2b.png",
    ],
    "partners": [
        "theme-sites/databricks-partners.webp",
        "theme-sites/datagrail-partners.webp",
        "partners/rotata-zoominfo-x-rotata-transformando-el-marketing-b2b-en-espana.png",
        "partners/rotata-hubspot-provider-rotata-partner-hubspot-en-espana.png",
        "partners/rotata-la-growth-machine-web.png",
    ],
    "blog-preview": [
        "theme-sites/databricks-insights.webp",
        "theme-sites/vectara-insights.webp",
        "blog/rotata-busqueda-generativa-sge-de-google-visibilidad-b2b-rotata.png",
        "blog/rotata-precision-del-marketing-abm-en-estrategias-b2b.png",
        "blog/rotata-imagen-correo-spam.png",
    ],
    "text": [
        "theme-sites/atlan-about.webp",
        "theme-sites/vectara-legal.webp",
        "blog/rotata-descubriendo-las-necesidades-del-cliente-con-intent-data.png",
        "blog/rotata-chatgpt-image-apr-30-2025-11-09-08-am.png",
        "images/rotata-rotbot-ai-assistant.png",
    ],
}

PAGE_ALIASES = {
    "process": ["about"],
    "cases": ["about"],
    "blog": ["insights"],
    "newsletter": ["insights"],
    "roi": ["insights"],
    "contact-consult": ["contact"],
    "privacy": ["legal"],
    "cookies": ["legal"],
    "accessibility": ["legal"],
    "sitemap": ["legal"],
    "legal-robots": ["legal"],
    "404": ["legal"],
}

VARIANT_STYLE = {
    "problem": {"accent": (255, 105, 120), "secondary": (231, 48, 77), "highlight": (255, 210, 221)},
    "cards": {"accent": (96, 197, 255), "secondary": (39, 121, 217), "highlight": (206, 237, 255)},
    "grid": {"accent": (112, 232, 215), "secondary": (18, 153, 142), "highlight": (217, 255, 247)},
    "process": {"accent": (255, 188, 97), "secondary": (231, 139, 48), "highlight": (255, 240, 219)},
    "metrics": {"accent": (181, 122, 255), "secondary": (110, 74, 232), "highlight": (235, 225, 255)},
    "partners": {"accent": (85, 221, 255), "secondary": (21, 110, 181), "highlight": (213, 248, 255)},
    "blog-preview": {"accent": (255, 142, 87), "secondary": (230, 83, 57), "highlight": (255, 227, 207)},
    "text": {"accent": (156, 215, 255), "secondary": (52, 111, 194), "highlight": (225, 243, 255)},
}


def asset_path(relative_path: str) -> Path:
    return ASSETS / relative_path


def available(relative_paths: list[str]) -> list[Path]:
    return [path for value in relative_paths if (path := asset_path(value)).exists()]


def palette(variant: str) -> dict[str, tuple[int, int, int]]:
    return VARIANT_STYLE.get(variant, VARIANT_STYLE["grid"])


def crop_to_fill(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    width, height = image.size
    target_width, target_height = size
    scale = max(target_width / width, target_height / height)
    resized = image.resize((max(1, int(width * scale)), max(1, int(height * scale))), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - target_width) // 2)
    top = max(0, (resized.height - target_height) // 2)
    return resized.crop((left, top, left + target_width, top + target_height))


def hex_overlay(size: tuple[int, int], color: tuple[int, int, int], opacity: int) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    spacing = 92
    radius = 32
    for row in range(-1, size[1] // spacing + 2):
        y = row * spacing
        x_shift = spacing // 2 if row % 2 else 0
        for col in range(-1, size[0] // spacing + 2):
            x = col * spacing + x_shift
            points = [
                (x + radius * 0.86, y),
                (x + radius * 1.72, y + radius * 0.5),
                (x + radius * 1.72, y + radius * 1.5),
                (x + radius * 0.86, y + radius * 2),
                (x, y + radius * 1.5),
                (x, y + radius * 0.5),
            ]
            draw.line(points + [points[0]], fill=(*color, opacity), width=1)
    return layer


def radial_glow(size: tuple[int, int], color: tuple[int, int, int], origin: tuple[float, float], radius: float, max_alpha: int) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    center_x = int(size[0] * origin[0])
    center_y = int(size[1] * origin[1])
    max_distance = max(1, int(min(size) * radius))
    draw = ImageDraw.Draw(layer)
    steps = 7
    for step in range(steps, 0, -1):
        current_radius = int(max_distance * step / steps)
        alpha = int(max_alpha * (step / steps) ** 2 * .42)
        draw.ellipse(
            (
                center_x - current_radius,
                center_y - current_radius,
                center_x + current_radius,
                center_y + current_radius,
            ),
            fill=(*color, alpha),
        )
    return layer.filter(ImageFilter.GaussianBlur(max(18, max_distance // 8)))


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def paste_rounded(base: Image.Image, layer: Image.Image, box: tuple[int, int, int, int], radius: int) -> None:
    width = box[2] - box[0]
    height = box[3] - box[1]
    prepared = crop_to_fill(layer.convert("RGB"), (width, height)).convert("RGBA")
    mask = rounded_mask((width, height), radius)
    base.paste(prepared, box[:2], mask)


def draw_system_accents(canvas: Image.Image, style: dict[str, tuple[int, int, int]], hero: bool) -> None:
    draw = ImageDraw.Draw(canvas)
    accent = style["accent"]
    secondary = style["secondary"]
    width, height = canvas.size
    line_alpha = 92 if hero else 118
    points = [
        (int(width * 0.08), int(height * 0.82)),
        (int(width * 0.26), int(height * 0.67)),
        (int(width * 0.44), int(height * 0.71)),
        (int(width * 0.58), int(height * 0.56)),
        (int(width * 0.84), int(height * 0.34)),
    ]
    for index in range(len(points) - 1):
        draw.line((points[index], points[index + 1]), fill=(*accent, line_alpha), width=4)
    for point in points:
        draw.ellipse((point[0] - 9, point[1] - 9, point[0] + 9, point[1] + 9), fill=(*secondary, 188), outline=(*style["highlight"], 255), width=3)

    chart_origin = (int(width * 0.08), int(height * 0.18))
    bar_width = 22 if hero else 18
    gap = 16
    values = [0.32, 0.58, 0.46, 0.76, 0.9]
    max_height = int(height * (0.17 if hero else 0.14))
    for index, value in enumerate(values):
        bar_height = max(18, int(max_height * value))
        x0 = chart_origin[0] + index * (bar_width + gap)
        y0 = chart_origin[1] + max_height - bar_height
        draw.rounded_rectangle((x0, y0, x0 + bar_width, chart_origin[1] + max_height), radius=9, fill=(*accent, 148))

    ring_box = (
        int(width * 0.74),
        int(height * 0.12),
        int(width * 0.9),
        int(height * 0.34),
    )
    draw.arc(ring_box, start=210, end=20, fill=(*style["highlight"], 180), width=10)
    inner = (
        ring_box[0] + 26,
        ring_box[1] + 26,
        ring_box[2] - 26,
        ring_box[3] - 26,
    )
    draw.arc(inner, start=120, end=300, fill=(*accent, 188), width=8)


def build_canvas(source: Path, variant: str, size: tuple[int, int], hero: bool) -> Image.Image:
    style = palette(variant)
    base = Image.open(source).convert("RGB")
    background = crop_to_fill(base, size)
    background = ImageEnhance.Color(background).enhance(0.72)
    background = ImageEnhance.Contrast(background).enhance(1.08)
    background = ImageEnhance.Brightness(background).enhance(0.42)
    background = background.filter(ImageFilter.GaussianBlur(26))

    canvas = Image.new("RGBA", size, (7, 16, 28, 255))
    canvas.alpha_composite(background.convert("RGBA"))
    canvas.alpha_composite(Image.new("RGBA", size, (6, 13, 24, 116)))
    canvas.alpha_composite(hex_overlay(size, style["highlight"], 22 if hero else 28))
    canvas.alpha_composite(radial_glow(size, style["accent"], (0.18, 0.16), 0.28, 136))
    canvas.alpha_composite(radial_glow(size, style["secondary"], (0.82, 0.78), 0.34, 118))

    width, height = size
    if hero:
        primary_box = (int(width * 0.48), int(height * 0.14), int(width * 0.94), int(height * 0.82))
        secondary_box = (int(width * 0.56), int(height * 0.56), int(width * 0.78), int(height * 0.9))
        orbit_box = (int(width * 0.42), int(height * 0.08), int(width * 0.96), int(height * 0.88))
    else:
        primary_box = (int(width * 0.34), int(height * 0.12), int(width * 0.94), int(height * 0.84))
        secondary_box = (int(width * 0.08), int(height * 0.58), int(width * 0.3), int(height * 0.88))
        orbit_box = (int(width * 0.18), int(height * 0.08), int(width * 0.94), int(height * 0.88))

    shadow = Image.new("RGBA", size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(primary_box, radius=42, fill=(0, 0, 0, 138))
    shadow_draw.rounded_rectangle(secondary_box, radius=30, fill=(0, 0, 0, 106))
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    canvas.alpha_composite(shadow)

    paste_rounded(canvas, base, primary_box, 42)
    inset = ImageEnhance.Color(base).enhance(1.08)
    inset = ImageEnhance.Contrast(inset).enhance(1.12)
    paste_rounded(canvas, inset, secondary_box, 30)

    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle(primary_box, radius=42, outline=(*style["highlight"], 128), width=2)
    overlay_draw.rounded_rectangle(secondary_box, radius=30, outline=(*style["highlight"], 118), width=2)
    overlay_draw.arc(orbit_box, start=214, end=342, fill=(*style["highlight"], 96), width=2)
    overlay_draw.arc(
        (orbit_box[0] + 38, orbit_box[1] + 38, orbit_box[2] - 44, orbit_box[3] - 64),
        start=222,
        end=358,
        fill=(*style["accent"], 124),
        width=3,
    )
    canvas.alpha_composite(overlay)

    glass = Image.new("RGBA", size, (0, 0, 0, 0))
    glass_draw = ImageDraw.Draw(glass)
    glass_draw.rounded_rectangle((int(width * 0.06), int(height * 0.08), int(width * 0.28), int(height * 0.3)), radius=26, fill=(8, 18, 30, 124), outline=(*style["highlight"], 78), width=1)
    glass_draw.rounded_rectangle((int(width * 0.66), int(height * 0.72), int(width * 0.92), int(height * 0.92)), radius=26, fill=(8, 18, 30, 118), outline=(*style["highlight"], 72), width=1)
    canvas.alpha_composite(glass.filter(ImageFilter.GaussianBlur(1)))

    draw_system_accents(canvas, style, hero)
    return canvas


def image_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="WEBP", quality=90, method=6)
    return buffer.getvalue()


def write_if_changed(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() == content:
        path.touch()
        return
    path.write_bytes(content)


def is_fresh(target: Path, source: Path) -> bool:
    if not target.exists():
        return False
    threshold = max(SCRIPT_PATH.stat().st_mtime, SITE_PATH.stat().st_mtime, source.stat().st_mtime)
    return target.stat().st_mtime >= threshold


def choose_source(page_key: str, variant: str, index: int) -> Path:
    related = [page_key]
    for alias in PAGE_ALIASES.get(page_key, []):
        if alias not in related:
            related.append(alias)
    family = page_key.split("-", 1)[0]
    if family not in related:
        related.append(family)
    pools = [
        *[available(PAGE_POOLS.get(key, [])) for key in related],
        available(VARIANT_POOLS.get(variant, [])),
        available(DEFAULT_POOL),
    ]
    for pool in pools:
        if pool:
            return pool[index % len(pool)]
    raise FileNotFoundError("No source images available to generate section visuals.")


def section_visual_name(page_key: str, index: int, variant: str) -> str:
    return f"{page_key}-{index + 1:02d}-{variant}.webp"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    for page_key, page in SITE["pages"].items():
        sections = page["translations"]["en"].get("sections", [])
        if sections:
            hero_source = choose_source(page_key, sections[0].get("variant", "grid"), 0)
        else:
            hero_source = choose_source(page_key, "grid", 0)
        hero_output = OUT / f"hero-{page_key}.webp"
        if not is_fresh(hero_output, hero_source):
            hero_bytes = image_bytes(build_canvas(hero_source, sections[0].get("variant", "grid") if sections else "grid", HERO_SIZE, hero=True))
            write_if_changed(hero_output, hero_bytes)

        for index, section in enumerate(sections):
            variant = section.get("variant", "grid")
            source = choose_source(page_key, variant, index)
            output = OUT / section_visual_name(page_key, index, variant)
            if is_fresh(output, source):
                continue
            visual_bytes = image_bytes(build_canvas(source, variant, SECTION_SIZE, hero=False))
            write_if_changed(output, visual_bytes)

    print(f"Generated visuals in {OUT}")


if __name__ == "__main__":
    main()
