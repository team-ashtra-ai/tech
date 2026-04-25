#!/usr/bin/env python3
"""Generate reference-inspired concept visuals for the Rotata showcase pages."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "src/assets/theme-sites"
SIZE = (1600, 1000)


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
FONT_LG = font(52, True)


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.strip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


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
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(22)))


def panel(
    image: Image.Image,
    box: tuple[int, int, int, int],
    fill: str | tuple[int, int, int, int],
    outline: str | tuple[int, int, int, int],
    radius: int = 8,
) -> None:
    shadow(image, box, radius, (0, 0, 0, 34))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)


def label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, color: str, size: str = "sm", bold: bool = False) -> None:
    fonts = {"xs": FONT_XS, "sm": FONT_SM, "md": FONT_MD, "lg": FONT_LG}
    draw.text(xy, text, fill=color, font=FONT_MD if bold and size == "sm" else fonts[size])


def draw_databricks() -> Image.Image:
    image = gradient("#f7efe5", "#fff9f2")
    draw = ImageDraw.Draw(image)
    panel(image, (650, 140, 1470, 820), "#fffaf4", "#171717", 8)
    draw.rectangle((650, 140, 1470, 208), fill="#171717")
    label(draw, (690, 162), "Rotata system workspace", "#fffaf4", "sm")
    for index, title in enumerate(["CRM model", "Data quality", "Automation", "Pipeline proof"]):
        x = 700 + (index % 2) * 360
        y = 260 + (index // 2) * 210
        panel(image, (x, y, x + 310, y + 150), "#ffffff", "#ead7c8", 6)
        draw.rectangle((x + 18, y + 24, x + 90, y + 34), fill="#ff5f2e")
        label(draw, (x + 18, y + 54), title, "#171717", "sm", True)
        for row in range(3):
            draw.rectangle((x + 18, y + 94 + row * 18, x + 240 - row * 24, y + 104 + row * 18), fill="#e9dfd4")
    panel(image, (160, 500, 570, 820), "#171717", "#171717", 8)
    label(draw, (205, 548), "Lakehouse-style", "#ffb199", "sm", True)
    label(draw, (205, 595), "growth system", "#fffaf4", "lg", True)
    label(draw, (205, 690), "One operating layer for CRM, signals and revenue motion.", "#f5d7c7", "sm")
    return image


def draw_datagrail() -> Image.Image:
    image = gradient("#e8f7f0", "#ffffff")
    draw = ImageDraw.Draw(image)
    panel(image, (140, 150, 1450, 820), "#ffffff", "#c6eadf", 8)
    label(draw, (200, 205), "System privacy map", "#102a43", "lg", True)
    label(draw, (204, 282), "Human-governed operations across data, lifecycle and outreach.", "#456171", "sm")
    cx, cy = 930, 500
    draw.ellipse((cx - 115, cy - 115, cx + 115, cy + 115), fill="#dff8ee", outline="#18b88f", width=5)
    label(draw, (cx - 64, cy - 18), "Rotata", "#102a43", "md", True)
    nodes = [
        (600, 330, "CRM"),
        (1190, 330, "Signals"),
        (560, 655, "Routing"),
        (1210, 650, "Reports"),
        (930, 250, "Consent"),
        (930, 748, "Review"),
    ]
    for x, y, text in nodes:
        draw.line((cx, cy, x, y), fill="#a5ded0", width=5)
    for x, y, text in nodes:
        panel(image, (x - 95, y - 45, x + 95, y + 45), "#f3fffb", "#b6e8dc", 8)
        label(draw, (x - 48, y - 14), text, "#102a43", "sm", True)
    for index, item in enumerate(["Risk", "Access", "Quality"]):
        x = 210
        y = 390 + index * 92
        draw.rounded_rectangle((x, y, x + 260, y + 62), radius=8, fill="#102a43")
        draw.rectangle((x + 18, y + 20, x + 58, y + 30), fill="#18b88f")
        label(draw, (x + 78, y + 16), item, "#e7fff7", "xs", True)
    return image


def draw_atlan() -> Image.Image:
    image = gradient("#ffffff", "#f6f7f9")
    draw = ImageDraw.Draw(image)
    label(draw, (160, 122), "Context graph for growth operations", "#101828", "lg", True)
    label(draw, (164, 198), "Every object keeps its owner, lifecycle logic and decision context.", "#525c73", "sm")
    nodes = [
        (770, 265, "Data"),
        (1030, 350, "CRM"),
        (930, 600, "Pipeline"),
        (610, 620, "Sales"),
        (500, 390, "Signals"),
    ]
    for start in nodes:
        for end in nodes:
            if start == end:
                continue
            draw.line((start[0], start[1], end[0], end[1]), fill="#d8def0", width=3)
    for x, y, text in nodes:
        panel(image, (x - 105, y - 55, x + 105, y + 55), "#ffffff", "#e0e4eb", 8)
        draw.ellipse((x - 66, y - 14, x - 38, y + 14), fill="#00b28a")
        label(draw, (x - 24, y - 18), text, "#2026d2", "sm", True)
    panel(image, (170, 420, 450, 760), "#2026d2", "#2026d2", 8)
    label(draw, (205, 470), "Observation", "#dbe3ff", "sm", True)
    label(draw, (205, 520), "Fragmentation becomes visible when the system has context.", "#ffffff", "sm")
    return image


def draw_runpod() -> Image.Image:
    image = gradient("#07040d", "#12091f")
    draw = ImageDraw.Draw(image)
    for x in range(100, 1500, 120):
        draw.line((x, 120, x, 850), fill="#1b1230", width=1)
    for y in range(120, 900, 92):
        draw.line((80, y, 1500, y), fill="#1b1230", width=1)
    panel(image, (170, 155, 1430, 810), "#0f0a19", "#2b1f44", 8)
    draw.rectangle((170, 155, 1430, 220), fill="#5d29f0")
    label(draw, (210, 176), "Rotata system console", "#ffffff", "sm", True)
    for index, title in enumerate(["Diagnose", "Design", "Deploy", "Review"]):
        x = 230 + index * 295
        panel(image, (x, 300, x + 225, 555), "#151026", "#38295d", 8)
        label(draw, (x + 28, 335), title, "#ffffff", "sm", True)
        draw.rectangle((x + 28, 390, x + 160, 404), fill="#17b8ff")
        draw.rectangle((x + 28, 430, x + 128, 444), fill="#5d29f0")
        draw.rectangle((x + 28, 470, x + 175, 484), fill="#342753")
    panel(image, (290, 650, 1310, 745), "#090512", "#2b1f44", 8)
    for index, metric in enumerate(["CRM", "Signals", "Outbound", "Reporting"]):
        x = 340 + index * 240
        label(draw, (x, 680), metric, "#ccc6df", "xs", True)
        draw.rectangle((x, 714, x + 136, 724), fill="#17b8ff" if index % 2 else "#5d29f0")
    return image


def draw_vectara() -> Image.Image:
    image = gradient("#f8fafc", "#ffffff")
    draw = ImageDraw.Draw(image)
    panel(image, (150, 150, 1450, 830), "#ffffff", "#dbeafe", 8)
    label(draw, (210, 210), "Governed agent workflow", "#111827", "lg", True)
    label(draw, (214, 288), "Answers, automations and routing stay inside auditable system rules.", "#4b5563", "sm")
    panel(image, (210, 390, 650, 735), "#eff6ff", "#bfdbfe", 8)
    label(draw, (250, 430), "Query", "#0060e5", "sm", True)
    label(draw, (250, 484), "Which accounts need action this week?", "#111827", "sm")
    panel(image, (740, 330, 1350, 520), "#111827", "#111827", 8)
    label(draw, (780, 370), "Guardrails", "#60a5fa", "sm", True)
    for index, text in enumerate(["Data source verified", "Owner assigned", "Lifecycle rule checked"]):
        y = 420 + index * 36
        draw.rectangle((780, y, 805, y + 18), fill="#60a5fa")
        label(draw, (825, y - 6), text, "#ffffff", "xs")
    panel(image, (740, 570, 1350, 735), "#ffffff", "#dbeafe", 8)
    label(draw, (780, 610), "Auditable outcome", "#0060e5", "sm", True)
    draw.rectangle((780, 662, 1110, 674), fill="#dbeafe")
    draw.rectangle((780, 696, 1010, 708), fill="#bfdbfe")
    return image


PALETTES = {
    "databricks": ("#f7efe5", "#fffaf4", "#9d1d12", "#06191f"),
    "datagrail": ("#004957", "#effaf6", "#00d99a", "#111814"),
    "atlan": ("#2026d2", "#f7f8fb", "#50d7ff", "#171a3d"),
    "runpod": ("#05020a", "#12071f", "#7a39ff", "#17b8ff"),
    "vectara": ("#111318", "#1d2027", "#1677ff", "#65d36e"),
}

GROUPS = {
    "about": "Trust model",
    "solutions": "Solution system",
    "services": "Capability layer",
    "system": "Architecture map",
    "partners": "Ecosystem fit",
    "insights": "Decision library",
    "contact": "Consultation flow",
    "legal": "Governance policy",
}


def draw_group_asset(site_id: str, group: str, title: str) -> Image.Image:
    bg, surface, accent, ink = PALETTES[site_id]
    image = gradient(bg, surface)
    draw = ImageDraw.Draw(image)
    dark = site_id in {"runpod", "vectara", "datagrail"}
    text = "#ffffff" if dark else ink
    muted = "#cbd5e1" if dark else "#4b5563"
    panel_fill = (255, 255, 255, 28) if dark else (255, 255, 255, 220)
    panel_outline = (255, 255, 255, 54) if dark else hex_rgb(accent) + (120,)

    label(draw, (130, 110), f"Rotata {title}", text, "lg", True)
    label(draw, (136, 188), "Static concept asset generated for this website system.", muted, "sm")
    for i in range(5):
        x = 150 + i * 270
        y = 360 + (i % 2) * 80
        box = (x, y, x + 220, y + 220)
        panel(image, box, panel_fill, panel_outline, 8)
        draw.rectangle((x + 28, y + 34, x + 128, y + 46), fill=accent)
        label(draw, (x + 28, y + 78), ["Diagnose", "Design", "Implement", "Optimize", "Report"][i], text, "sm", True)
        for row in range(3):
            draw.rectangle((x + 28, y + 130 + row * 24, x + 170 - row * 20, y + 142 + row * 24), fill=muted)

    if site_id == "atlan":
        for i in range(4):
            draw.line((270 + i * 300, 700, 420 + i * 230, 310), fill="#9fb7ff", width=4)
    elif site_id == "runpod":
        draw.rounded_rectangle((210, 710, 1390, 810), radius=8, outline=accent, width=3)
    elif site_id == "datagrail":
        draw.ellipse((620, 655, 970, 900), outline=accent, width=5)
    elif site_id == "vectara":
        for x in range(100, 1500, 120):
            draw.line((x, 280, x, 900), fill=(255, 255, 255, 34), width=1)
    else:
        draw.rectangle((180, 720, 1420, 790), fill=ink)
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    assets = {
        "databricks-system.webp": draw_databricks(),
        "datagrail-privacy.webp": draw_datagrail(),
        "atlan-context.webp": draw_atlan(),
        "runpod-infra.webp": draw_runpod(),
        "vectara-agent.webp": draw_vectara(),
    }
    for site_id in PALETTES:
        for group, title in GROUPS.items():
            assets[f"{site_id}-{group}.webp"] = draw_group_asset(site_id, group, title)
    for filename, image in assets.items():
        image.convert("RGB").save(OUT / filename, "WEBP", quality=92, method=6)
    print(f"Generated {len(assets)} showcase assets in {OUT}")


if __name__ == "__main__":
    main()
