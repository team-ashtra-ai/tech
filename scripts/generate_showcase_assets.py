#!/usr/bin/env python3
"""Generate page and section visuals for every Rotata showcase concept route."""
from __future__ import annotations

import hashlib
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import build_site


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = Path(__file__).resolve()
OUT = ROOT / "src/assets/theme-sites"
SIZE = (1600, 1000)
DEPENDENCIES = [
    SCRIPT_PATH,
    ROOT / "scripts" / "build_site.py",
    ROOT / "src" / "data" / "site.json",
    ROOT / "src" / "data" / "navigation.json",
    ROOT / "src" / "data" / "showcase-sites.json",
]


def font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


FONT_XS = font(18)
FONT_SM = font(24)
FONT_MD = font(34, True)
FONT_LG = font(56, True)
FONT_HERO = font(76, True)


THEMES = {
    "databricks": {
        "top": "#f7efe5",
        "bottom": "#fffaf4",
        "surface": "#fff9f2",
        "panel": "#ffffff",
        "line": "#d9c7b8",
        "accent": "#9d1d12",
        "secondary": "#0f4554",
        "muted": "#5f6d72",
        "text": "#0b1f26",
        "tag": "#7f1208",
        "glow": "#ffbb9d",
    },
    "datagrail": {
        "top": "#eef8f5",
        "bottom": "#ffffff",
        "surface": "#f4fffb",
        "panel": "#ffffff",
        "line": "#bfe3d7",
        "accent": "#18b88f",
        "secondary": "#102a43",
        "muted": "#446171",
        "text": "#102a43",
        "tag": "#0d7b61",
        "glow": "#9ef0d5",
    },
    "atlan": {
        "top": "#ffffff",
        "bottom": "#f6f7fb",
        "surface": "#ffffff",
        "panel": "#ffffff",
        "line": "#dbe2f4",
        "accent": "#2026d2",
        "secondary": "#00b28a",
        "muted": "#5b6476",
        "text": "#111827",
        "tag": "#2026d2",
        "glow": "#96c2ff",
    },
    "runpod": {
        "top": "#05020a",
        "bottom": "#12071f",
        "surface": "#0f0919",
        "panel": "#130d21",
        "line": "#2b1f44",
        "accent": "#7a39ff",
        "secondary": "#17b8ff",
        "muted": "#b4a8d4",
        "text": "#f5f2ff",
        "tag": "#a781ff",
        "glow": "#4b24a6",
    },
    "vectara": {
        "top": "#f8fafc",
        "bottom": "#ffffff",
        "surface": "#ffffff",
        "panel": "#ffffff",
        "line": "#dbe6f6",
        "accent": "#1677ff",
        "secondary": "#0f172a",
        "muted": "#526072",
        "text": "#111827",
        "tag": "#0f5dcc",
        "glow": "#8fc1ff",
    },
}


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.strip("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def with_alpha(color: str, alpha: int) -> tuple[int, int, int, int]:
    red, green, blue = hex_rgb(color)
    return red, green, blue, alpha


def mix(color_a: str, color_b: str, ratio: float) -> tuple[int, int, int]:
    a = hex_rgb(color_a)
    b = hex_rgb(color_b)
    return tuple(round(a[index] * (1 - ratio) + b[index] * ratio) for index in range(3))


def gradient(top: str, bottom: str) -> Image.Image:
    width, height = SIZE
    top_rgb = hex_rgb(top)
    bottom_rgb = hex_rgb(bottom)
    image = Image.new("RGB", SIZE, top_rgb)
    draw = ImageDraw.Draw(image)
    for y in range(height):
        ratio = y / max(height - 1, 1)
        color = tuple(round(top_rgb[i] * (1 - ratio) + bottom_rgb[i] * ratio) for i in range(3))
        draw.line((0, y, width, y), fill=color)
    return image.convert("RGBA")


def shadow(base: Image.Image, box: tuple[int, int, int, int], radius: int, color: tuple[int, int, int, int]) -> None:
    layer = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    layer_draw = ImageDraw.Draw(layer)
    layer_draw.rounded_rectangle(box, radius=radius, fill=color)
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(26)))


def panel(
    image: Image.Image,
    box: tuple[int, int, int, int],
    fill: str | tuple[int, int, int, int],
    outline: str | tuple[int, int, int, int],
    radius: int = 12,
    shadow_alpha: int = 30,
) -> None:
    shadow(image, box, radius, (0, 0, 0, shadow_alpha))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)


def wrap_text(value: str, width: int) -> str:
    if not value:
        return ""
    return "\n".join(textwrap.wrap(value, width=width, break_long_words=False))


def draw_copy(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    color: str | tuple[int, int, int] | tuple[int, int, int, int],
    font_obj: ImageFont.FreeTypeFont,
    width: int,
    spacing: int = 8,
) -> None:
    draw.multiline_text(xy, wrap_text(text, width), fill=color, font=font_obj, spacing=spacing)


def stable_values(*parts: str, count: int = 12) -> list[int]:
    digest = hashlib.sha256("::".join(parts).encode("utf-8")).digest()
    while len(digest) < count:
        digest += hashlib.sha256(digest).digest()
    return list(digest[:count])


def stable_pick(options: list[str], *parts: str) -> str:
    values = stable_values(*parts, count=1)
    return options[values[0] % len(options)]


def dependency_mtime() -> float:
    return max(path.stat().st_mtime for path in DEPENDENCIES if path.exists())


def is_fresh(path: Path) -> bool:
    return path.exists() and path.stat().st_mtime >= dependency_mtime()


def write_if_changed(path: Path, image: Image.Image) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if is_fresh(path):
        return
    image.convert("RGB").save(path, "WEBP", quality=92, method=6)


def clean_token(value: str) -> str:
    value = " ".join(value.replace("/", " ").replace("—", " ").split())
    if len(value) > 28:
        value = value[:28].rsplit(" ", 1)[0]
    return value


def label_from_page(page_key: str) -> str:
    try:
        return build_site.page_label(page_key, "en")
    except KeyError:
        return page_key.replace("-", " ").title()


def page_translation(page_key: str) -> dict:
    try:
        return build_site.page_payload(page_key, "en")["translation"]
    except KeyError:
        source = build_site.SITE["pages"].get(page_key, {})
        return source.get("translations", {}).get("en", {})


def page_group(page_key: str) -> str:
    try:
        return build_site.page_meta(page_key).get("group") or "home"
    except KeyError:
        return page_key.split("-", 1)[0]


def section_tokens(section: dict) -> list[str]:
    items = section.get("items", [])
    tokens: list[str] = []
    for item in items:
        if isinstance(item, dict):
            candidate = item.get("title") or item.get("text") or ""
        else:
            candidate = str(item)
        candidate = clean_token(candidate)
        if candidate:
            tokens.append(candidate)
        if len(tokens) == 4:
            break
    if not tokens:
        tokens.append(clean_token(section.get("heading", "Rotata system")))
    return tokens


def theme_for(site_id: str) -> dict[str, str]:
    return THEMES[site_id]


def draw_motif(image: Image.Image, site_id: str, seed_key: str) -> None:
    theme = theme_for(site_id)
    draw = ImageDraw.Draw(image)
    values = stable_values(site_id, seed_key, count=18)
    if site_id == "databricks":
        for index in range(7):
            x = 90 + index * 200 + values[index] % 40
            y = 110 + (index % 2) * 90
            draw.line((x, y, x + 1260, y + 200), fill=with_alpha(theme["line"], 42), width=2)
        for index in range(6):
            x = 130 + index * 210
            draw.rectangle((x, 750, x + 120, 766), fill=with_alpha(theme["accent"], 24))
    elif site_id == "datagrail":
        for index in range(5):
            radius = 90 + index * 62
            offset_x = 1100 + values[index] % 120
            offset_y = 320 + values[index + 1] % 160
            draw.ellipse((offset_x - radius, offset_y - radius, offset_x + radius, offset_y + radius), outline=with_alpha(theme["accent"], 42), width=3)
        for index in range(4):
            x = 210 + index * 230
            y = 620 + (values[index + 3] % 90)
            draw.line((800, 430, x, y), fill=with_alpha(theme["line"], 110), width=4)
    elif site_id == "atlan":
        nodes = []
        for index in range(7):
            x = 260 + (values[index] % 920)
            y = 190 + (values[index + 3] % 560)
            nodes.append((x, y))
        for start, end in zip(nodes, nodes[1:]):
            draw.line((start, end), fill=with_alpha(theme["line"], 144), width=3)
        for x, y in nodes:
            draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill=with_alpha(theme["secondary"], 210), outline=with_alpha(theme["accent"], 180), width=3)
    elif site_id == "runpod":
        for x in range(80, 1520, 88):
            draw.line((x, 80, x, 920), fill=with_alpha(theme["line"], 72), width=1)
        for y in range(90, 930, 70):
            draw.line((70, y, 1530, y), fill=with_alpha(theme["line"], 64), width=1)
        for index in range(5):
            x = 160 + index * 250
            draw.rectangle((x, 180, x + 130, 196), fill=with_alpha(theme["secondary"], 96))
    elif site_id == "vectara":
        for index in range(5):
            x = 240 + index * 240
            draw.rounded_rectangle((x, 170, x + 164, 204), radius=17, fill=with_alpha(theme["glow"], 68))
        for index in range(6):
            y = 290 + index * 95
            draw.line((170, y, 1420, y), fill=with_alpha(theme["line"], 102), width=2)


def draw_chip(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, fill: tuple[int, int, int, int], outline: tuple[int, int, int, int], text_color: str) -> None:
    draw.rounded_rectangle(box, radius=16, fill=fill, outline=outline, width=2)
    draw.text((box[0] + 16, box[1] + 10), clean_token(text), fill=text_color, font=FONT_XS)


def draw_variant_scene(
    image: Image.Image,
    site_id: str,
    variant: str,
    box: tuple[int, int, int, int],
    key: str,
    tokens: list[str],
) -> None:
    theme = theme_for(site_id)
    draw = ImageDraw.Draw(image)
    values = stable_values(site_id, variant, key, count=16)
    radius = 18 if site_id in {"databricks", "runpod"} else 22
    panel(image, box, theme["panel"], theme["line"], radius=radius, shadow_alpha=40)
    left, top, right, bottom = box
    width = right - left
    height = bottom - top
    inner = (left + 28, top + 28, right - 28, bottom - 28)

    if variant == "problem":
        draw.line(
            (
                inner[0],
                inner[3] - 90,
                inner[0] + width * 0.24,
                inner[1] + height * 0.56,
                inner[0] + width * 0.47,
                inner[3] - 170,
                inner[0] + width * 0.7,
                inner[1] + 120,
                inner[2],
                inner[1] + 90,
            ),
            fill=with_alpha(theme["accent"], 205),
            width=7,
        )
        for index, token in enumerate(tokens[:3]):
            y = inner[1] + 46 + index * 92
            draw_chip(draw, (inner[0] + 22, y, inner[0] + 280, y + 52), token, with_alpha(theme["surface"], 255), with_alpha(theme["accent"], 110), theme["text"])
        draw.ellipse((inner[2] - 140, inner[1] + 46, inner[2] - 34, inner[1] + 152), outline=with_alpha(theme["accent"], 160), width=7)
    elif variant == "cards":
        for index in range(4):
            card_x = inner[0] + (index % 2) * (width // 2 - 12)
            card_y = inner[1] + (index // 2) * (height // 2 - 16)
            card = (card_x, card_y, card_x + width // 2 - 48, card_y + height // 2 - 52)
            panel(image, card, with_alpha(theme["surface"], 255), with_alpha(theme["line"], 180), radius=16, shadow_alpha=18)
            draw.rectangle((card[0] + 18, card[1] + 18, card[0] + 86, card[1] + 28), fill=with_alpha(theme["accent"], 170))
            draw_copy(draw, (card[0] + 18, card[1] + 48), tokens[index % len(tokens)], theme["text"], FONT_SM, 18)
            for row in range(3):
                draw.rectangle((card[0] + 18, card[1] + 102 + row * 24, card[0] + 180 - row * 16, card[1] + 114 + row * 24), fill=with_alpha(theme["line"], 140))
    elif variant == "process":
        line_y = top + height // 2
        draw.line((inner[0] + 40, line_y, inner[2] - 40, line_y), fill=with_alpha(theme["line"], 180), width=5)
        step_width = (inner[2] - inner[0] - 120) // max(4, len(tokens[:4]))
        for index, token in enumerate(tokens[:4]):
            cx = inner[0] + 60 + index * step_width
            draw.ellipse((cx - 28, line_y - 28, cx + 28, line_y + 28), fill=with_alpha(theme["accent"], 230), outline=with_alpha(theme["panel"], 255), width=4)
            draw.text((cx - 10, line_y - 15), f"{index + 1}", fill=theme["panel"], font=FONT_XS)
            draw_copy(draw, (cx - 36, line_y + 48), token, theme["text"], FONT_XS, 12, spacing=4)
    elif variant == "metrics":
        for index in range(4):
            x = inner[0] + index * ((inner[2] - inner[0]) // 4) + 10
            card = (x, inner[1] + 12, x + 210, inner[3] - 16)
            panel(image, card, with_alpha(theme["surface"], 255), with_alpha(theme["line"], 170), radius=16, shadow_alpha=14)
            draw.text((card[0] + 18, card[1] + 18), f"0{index + 1}", fill=theme["tag"], font=FONT_XS)
            draw_copy(draw, (card[0] + 18, card[1] + 52), tokens[index % len(tokens)], theme["text"], FONT_SM, 14)
            bar_height = 70 + values[index] % 120
            draw.rounded_rectangle((card[0] + 26, card[3] - bar_height - 28, card[0] + 74, card[3] - 28), radius=16, fill=with_alpha(theme["accent"], 210))
            draw.rounded_rectangle((card[0] + 90, card[3] - bar_height * 0.7 - 28, card[0] + 138, card[3] - 28), radius=16, fill=with_alpha(theme["secondary"], 205))
    elif variant == "partners":
        center_x = (left + right) // 2
        center_y = (top + bottom) // 2
        draw.ellipse((center_x - 110, center_y - 110, center_x + 110, center_y + 110), fill=with_alpha(theme["surface"], 255), outline=with_alpha(theme["accent"], 140), width=5)
        draw.text((center_x - 44, center_y - 18), "Rotata", fill=theme["text"], font=FONT_SM)
        orbit_positions = [
            (center_x - 290, center_y - 110),
            (center_x + 190, center_y - 120),
            (center_x - 250, center_y + 170),
            (center_x + 220, center_y + 160),
        ]
        for index, token in enumerate(tokens[:4]):
            x, y = orbit_positions[index]
            draw.line((center_x, center_y, x + 70, y + 24), fill=with_alpha(theme["line"], 180), width=4)
            draw_chip(draw, (x, y, x + 170, y + 48), token, with_alpha(theme["panel"], 255), with_alpha(theme["line"], 180), theme["text"])
    else:
        # Covers grid, text and blog-preview with a readable operating matrix.
        columns = 3 if variant == "grid" else 2
        rows = 2 if variant == "grid" else 3
        gap = 18
        card_width = (inner[2] - inner[0] - gap * (columns - 1)) // columns
        card_height = (inner[3] - inner[1] - gap * (rows - 1)) // rows
        for index in range(columns * rows):
            x = inner[0] + (index % columns) * (card_width + gap)
            y = inner[1] + (index // columns) * (card_height + gap)
            card = (x, y, x + card_width, y + card_height)
            panel(image, card, with_alpha(theme["surface"], 255), with_alpha(theme["line"], 170), radius=16, shadow_alpha=12)
            draw.rectangle((card[0] + 16, card[1] + 16, card[0] + 72, card[1] + 26), fill=with_alpha(theme["accent"], 164))
            draw_copy(draw, (card[0] + 16, card[1] + 44), tokens[index % len(tokens)], theme["text"], FONT_XS if variant == "grid" else FONT_SM, 14)
            line_fill = with_alpha(theme["line"], 140)
            for row in range(3 if variant == "grid" else 2):
                draw.rectangle((card[0] + 16, card[1] + card_height - 64 + row * 18, card[0] + card_width - 26 - row * 24, card[1] + card_height - 54 + row * 18), fill=line_fill)


def draw_page_asset(site_id: str, page_key: str) -> Image.Image:
    theme = theme_for(site_id)
    translation = page_translation(page_key)
    sections = translation.get("sections", [])
    first_section = sections[0] if sections else {"heading": label_from_page(page_key), "variant": "grid", "items": []}
    tokens = section_tokens(first_section)
    image = gradient(theme["top"], theme["bottom"])
    image.alpha_composite(Image.new("RGBA", SIZE, with_alpha(theme["secondary"] if site_id == "runpod" else theme["surface"], 28)))
    draw_motif(image, site_id, f"page:{page_key}")
    draw = ImageDraw.Draw(image)

    left_panel = (92, 112, 640, 890)
    right_panel = (690, 112, 1506, 890)
    panel(image, left_panel, with_alpha(theme["panel"], 238), with_alpha(theme["line"], 190), radius=22, shadow_alpha=44)
    panel(image, right_panel, with_alpha(theme["surface"], 244), with_alpha(theme["line"], 170), radius=22, shadow_alpha=50)

    group = page_group(page_key).upper()
    draw_chip(draw, (128, 152, 308, 200), group, with_alpha(theme["surface"], 255), with_alpha(theme["line"], 170), theme["tag"])
    draw_copy(draw, (128, 236), translation.get("h1") or label_from_page(page_key), theme["text"], FONT_LG, 18)
    draw_copy(draw, (128, 486), translation.get("intro", ""), theme["muted"], FONT_SM, 30)

    tag_y = 708
    for index, section in enumerate(sections[:3]):
        draw_chip(
            draw,
            (128, tag_y + index * 64, 448, tag_y + 48 + index * 64),
            section.get("heading", ""),
            with_alpha(theme["surface"], 255),
            with_alpha(theme["line"], 150),
            theme["text"],
        )

    draw_variant_scene(image, site_id, first_section.get("variant", "grid"), (732, 154, 1462, 694), f"page:{page_key}", tokens)

    metrics_box = (732, 728, 1462, 850)
    panel(image, metrics_box, with_alpha(theme["panel"], 232), with_alpha(theme["line"], 170), radius=18, shadow_alpha=18)
    values = stable_values(site_id, page_key, count=8)
    metric_labels = [clean_token(value) for value in tokens[:3]] + ["System fit"]
    for index, label in enumerate(metric_labels[:4]):
        x = metrics_box[0] + 26 + index * 174
        draw.text((x, metrics_box[1] + 22), f"0{index + 1}", fill=theme["tag"], font=FONT_XS)
        draw.text((x, metrics_box[1] + 54), label, fill=theme["text"], font=FONT_XS)
        draw.rounded_rectangle((x, metrics_box[3] - 26 - (42 + values[index] % 36), x + 48, metrics_box[3] - 26), radius=14, fill=with_alpha(theme["accent"], 210))

    return image


def draw_section_asset(site_id: str, page_key: str, section: dict, index: int) -> Image.Image:
    theme = theme_for(site_id)
    variant = section.get("variant", "grid")
    tokens = section_tokens(section)
    image = gradient(theme["top"], theme["bottom"])
    draw_motif(image, site_id, f"section:{page_key}:{index}:{variant}")
    draw = ImageDraw.Draw(image)

    head_box = (92, 86, 1508, 242)
    panel(image, head_box, with_alpha(theme["panel"], 228), with_alpha(theme["line"], 190), radius=20, shadow_alpha=28)
    draw.text((126, 122), f"{label_from_page(page_key)} / {index + 1:02d}", fill=theme["tag"], font=FONT_XS)
    draw_copy(draw, (126, 154), section.get("heading", ""), theme["text"], FONT_MD, 36, spacing=6)

    visual_box = (92, 288, 1508, 900)
    draw_variant_scene(image, site_id, variant, visual_box, f"section:{page_key}:{index}", tokens)

    caption_box = (1112, 746, 1468, 868)
    panel(image, caption_box, with_alpha(theme["panel"], 230), with_alpha(theme["line"], 160), radius=18, shadow_alpha=20)
    draw.text((1140, 776), variant.upper(), fill=theme["tag"], font=FONT_XS)
    draw_copy(draw, (1140, 808), tokens[0], theme["text"], FONT_SM, 16)
    return image


def page_asset_name(site_id: str, page_key: str) -> str:
    return f"{site_id}-{page_key}.webp"


def group_asset_name(site_id: str, group: str) -> str:
    return f"{site_id}-{group}.webp"


def section_asset_name(site_id: str, page_key: str, index: int) -> str:
    return f"{site_id}-{page_key}-{index + 1:02d}.webp"


def generate_for_site(site_id: str) -> int:
    count = 0
    home_path = OUT / page_asset_name(site_id, "home")
    if not is_fresh(home_path):
        home_image = draw_page_asset(site_id, "home")
        write_if_changed(home_path, home_image)
    count += 1

    seen_groups: set[str] = set()
    for page_key in build_site.PAGE_DEFS:
        page_path = OUT / page_asset_name(site_id, page_key)
        group = page_group(page_key)
        group_path = OUT / group_asset_name(site_id, group)
        needs_page = not is_fresh(page_path)
        needs_group = group not in seen_groups and not is_fresh(group_path)
        page_image = None
        if needs_page or needs_group:
            page_image = draw_page_asset(site_id, page_key)
        if needs_page and page_image is not None:
            write_if_changed(page_path, page_image)
        count += 1

        if group not in seen_groups:
            if needs_group and page_image is not None:
                write_if_changed(group_path, page_image)
            seen_groups.add(group)
            count += 1

        translation = page_translation(page_key)
        for index, section in enumerate(translation.get("sections", [])):
            section_path = OUT / section_asset_name(site_id, page_key, index)
            if is_fresh(section_path):
                count += 1
                continue
            section_image = draw_section_asset(site_id, page_key, section, index)
            write_if_changed(section_path, section_image)
            count += 1
    return count


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    generated = 0
    for site in build_site.showcase_sites():
        generated += generate_for_site(site["id"])
    print(f"Generated {generated} showcase assets in {OUT}")


if __name__ == "__main__":
    main()
