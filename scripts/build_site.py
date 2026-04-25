#!/usr/bin/env python3
# Build the Rotata static site into dist/.
from __future__ import annotations

import html
import json
import os
import re
import shutil
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DIST = ROOT / "dist"

def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

SITE = load_json(SRC / "data/site.json")
NAV = load_json(SRC / "data/navigation.json")
COOKIE = load_json(SRC / "data/cookie.json")
FORMS = load_json(SRC / "data/forms.json")
BLOG = load_json(SRC / "data/blog.json")
PARTNERS = load_json(SRC / "data/partners.json")
CASES = load_json(SRC / "data/cases.json")
THEMES = load_json(SRC / "data/themes.json")
SHOWCASE = load_json(SRC / "data/showcase-sites.json")
PAGE_DEFS = NAV["pages"]
BLOG_POST_CACHE: dict[tuple[str, str], dict] = {}
BLOG_LIST_CACHE: dict[str, list[dict]] = {}

def esc(value: str) -> str:
    return html.escape(str(value or ""), quote=True)

def partial(path: str) -> str:
    return (SRC / "partials" / path).read_text(encoding="utf-8")

def render_template(template: str, mapping: dict[str, str]) -> str:
    for key, value in mapping.items():
        template = template.replace("{{" + key + "}}", value)
    return re.sub(r"{{[^}]+}}", "", template)


def theme_logo_markup(width: int = 154, height: int = 40) -> str:
    light_logo = SITE["site"]["logo"]
    dark_logo = SITE["site"].get("logo_dark") or SITE["site"].get("logo_white") or light_logo
    return (
        '<span class="logo-swap" aria-hidden="true">'
        f'<img class="brand-logo brand-logo-theme-light" src="{esc(light_logo)}" width="{width}" height="{height}" alt="">'
        f'<img class="brand-logo brand-logo-theme-dark" src="{esc(dark_logo)}" width="{width}" height="{height}" alt="">'
        "</span>"
    )

def localized(value, lang: str, fallback=""):
    if isinstance(value, dict):
        if lang in value and value[lang] not in (None, ""):
            return value[lang]
        if "en" in value and value["en"] not in (None, ""):
            return value["en"]
        if value:
            return next(iter(value.values()))
        return fallback
    return value if value is not None else fallback


def theme_by_id(theme_id: str | None = None) -> dict:
    target = theme_id or THEMES.get("default_theme")
    for theme in THEMES["themes"]:
        if theme["id"] == target:
            return deepcopy(theme)
    return deepcopy(THEMES["themes"][0])


def page_meta(page_key: str) -> dict:
    return PAGE_DEFS[page_key]


def page_label(page_key: str, lang: str, field: str = "label") -> str:
    meta = page_meta(page_key)
    return localized(meta.get(field) or meta.get("label"), lang, page_key)


def page_url(page_key: str, lang: str) -> str:
    route = page_meta(page_key).get("route", "").strip("/")
    prefix = SITE["languages"][lang]["prefix"]
    pieces = [piece for piece in [prefix, route] if piece]
    return "/" + "/".join(pieces) + ("/" if pieces else "")


def showcase_sites() -> list[dict]:
    return SHOWCASE.get("sites", [])


def showcase_by_id(site_id: str | None = None) -> dict:
    target = site_id or SHOWCASE.get("default_site")
    for site in showcase_sites():
        if site["id"] == target:
            return deepcopy(site)
    return deepcopy(showcase_sites()[0])


def showcase_url(site_id: str, lang: str, page_key: str = "home") -> str:
    prefix = SITE["languages"][lang]["prefix"]
    route = "" if page_key == "home" else page_meta(page_key).get("route", "").strip("/")
    pieces = [piece for piece in [prefix, "showcase", site_id, route] if piece]
    return "/" + "/".join(pieces) + "/"


def legacy_page_url(page_key: str, lang: str) -> str:
    route = SITE["pages"][page_key]["routes"][lang]
    prefix = SITE["languages"][lang]["prefix"]
    pieces = [piece for piece in [prefix, route] if piece]
    return "/" + "/".join(pieces) + ("/" if pieces else "")


def article_url(slug: str, lang: str = "es") -> str:
    return f'{page_url("insights-blog", lang)}{slug}/'


def blog_post_path(slug: str, lang: str) -> Path:
    return SRC / "content" / lang / "blog" / f"{slug}.json"


def load_blog_post(slug: str, lang: str) -> dict:
    cache_key = (slug, lang)
    if cache_key in BLOG_POST_CACHE:
        return deepcopy(BLOG_POST_CACHE[cache_key])

    post = None
    for code in (lang, "es"):
        path = blog_post_path(slug, code)
        if path.exists():
            post = load_json(path)
            break

    if post is None:
        post = deepcopy(next((item for item in BLOG if item["slug"] == slug), {}))
        post.setdefault("content", "")

    BLOG_POST_CACHE[cache_key] = deepcopy(post)
    return deepcopy(post)


def blog_posts(lang: str) -> list[dict]:
    if lang not in BLOG_LIST_CACHE:
        BLOG_LIST_CACHE[lang] = [load_blog_post(item["slug"], lang) for item in BLOG]
    return deepcopy(BLOG_LIST_CACHE[lang])


def article_language_urls(slug: str) -> dict[str, str]:
    return {code: article_url(slug, code) for code in SITE["languages"]}


def format_blog_date(date_value: str, lang: str) -> str:
    try:
        parsed = datetime.fromisoformat(date_value)
    except ValueError:
        return date_value
    months = {
        "es": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
        "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "fr": ["janv.", "fevr.", "mars", "avr.", "mai", "juin", "juil.", "aout", "sept.", "oct.", "nov.", "dec."],
    }[lang]
    month = months[parsed.month - 1]
    if lang == "en":
        return f"{month} {parsed.day}, {parsed.year}"
    return f"{parsed.day:02d} {month} {parsed.year}"


def reading_time_copy(minutes: int, lang: str) -> str:
    labels = {
        "es": f"{minutes} min",
        "en": f"{minutes} min read",
        "fr": f"{minutes} min de lecture",
    }
    return labels[lang]


def runtime_config() -> dict[str, str]:
    return {
        "ga4Id": os.getenv("PUBLIC_GA4_ID", ""),
        "gtmId": os.getenv("PUBLIC_GTM_ID", ""),
        "linkedinPartnerId": os.getenv("PUBLIC_LINKEDIN_PARTNER_ID", ""),
        "clarityId": os.getenv("PUBLIC_CLARITY_ID", ""),
        "hubspotPortalId": os.getenv("PUBLIC_HUBSPOT_PORTAL_ID", ""),
        "hubspotFormId": os.getenv("PUBLIC_HUBSPOT_FORM_ID", ""),
        "formsEndpoint": os.getenv("PUBLIC_FORMS_ENDPOINT", ""),
    }

def output_path(url: str) -> Path:
    clean = url.strip("/")
    if not clean:
        return DIST / "index.html"
    return DIST / clean / "index.html"

def source_translation(source_page: str, lang: str) -> dict:
    translations = SITE["pages"][source_page]["translations"]
    return deepcopy(translations.get(lang) or translations["en"])


def source_seo_keyword(source_page: str) -> str:
    return SITE["pages"].get(source_page, {}).get("seo_keyword", "")


def compose_section(source_page: str, index: int, lang: str) -> dict:
    lang_sections = source_translation(source_page, lang).get("sections", [])
    if index < len(lang_sections):
        section = deepcopy(lang_sections[index])
    else:
        section = deepcopy(source_translation(source_page, "en")["sections"][index])
    section["_visual_page"] = source_page
    section["_visual_index"] = index
    return section


def localize_section(section: dict, lang: str, default_visual: str, visual_index: int) -> dict:
    items = section.get("items", [])
    if isinstance(items, dict):
        items = localized(items, lang, [])
    return {
        "variant": section.get("variant", "grid"),
        "heading": localized(section.get("heading", ""), lang, ""),
        "body": localized(section.get("body", ""), lang, ""),
        "items": items,
        "_visual_page": section.get("_visual_page", default_visual),
        "_visual_index": section.get("_visual_index", visual_index),
    }


PAGE_CACHE: dict[tuple[str, str], dict] = {}


def page_payload(page_key: str, lang: str) -> dict:
    cache_key = (page_key, lang)
    if cache_key in PAGE_CACHE:
        return deepcopy(PAGE_CACHE[cache_key])

    meta = page_meta(page_key)
    source_page = meta.get("source_page")
    translation = source_translation(source_page, lang) if source_page else {
        "title": "",
        "description": "",
        "eyebrow": "",
        "h1": "",
        "intro": "",
        "sections": [],
        "final_cta": "",
    }
    translation.setdefault("sections", [])

    if "section_sources" in meta:
        translation["sections"] = [
            compose_section(item["page"], item["index"], lang) for item in meta["section_sources"]
        ]

    if meta.get("custom_sections"):
        default_visual = meta.get("visual_source") or source_page or page_key
        for index, section in enumerate(meta["custom_sections"]):
            translation["sections"].append(localize_section(section, lang, default_visual, index))

    copy_block = localized(meta.get("copy", {}), lang, {})
    if copy_block:
        for field in (
            "title",
            "description",
            "eyebrow",
            "h1",
            "intro",
            "primary_cta",
            "primary_cta_url",
            "primary_cta_page",
            "secondary_cta",
            "secondary_cta_url",
            "secondary_cta_page",
            "final_cta",
            "final_cta_url",
            "final_cta_page",
        ):
            if copy_block.get(field) is not None:
                translation[field] = copy_block[field]
        if not copy_block.get("title") and translation.get("h1"):
            translation["title"] = f'Rotata | {translation["h1"]}'
        if not copy_block.get("description") and translation.get("intro"):
            translation["description"] = translation["intro"]

    default_visual = meta.get("visual_source") or source_page or page_key
    for index, section in enumerate(translation.get("sections", [])):
        section.setdefault("_visual_page", default_visual)
        section.setdefault("_visual_index", index)

    translation["_visual_source"] = default_visual

    payload = {
        "page_key": page_key,
        "group": meta.get("group", ""),
        "render": meta.get("render", "standard"),
        "source_page": source_page,
        "visual_source": translation["_visual_source"],
        "translation": translation,
        "seo_keyword": meta.get("seo_keyword") or source_seo_keyword(source_page or ""),
        "schema_service": bool(meta.get("schema_service")),
    }
    PAGE_CACHE[cache_key] = deepcopy(payload)
    return payload


def language_switcher(lang: str, page_key: str, language_urls: dict[str, str] | None = None) -> str:
    items = []
    target_page = page_key if page_key in PAGE_DEFS else "home"
    for code in SITE["languages"]:
        href = language_urls.get(code) if language_urls else page_url(target_page, code)
        current = ' aria-current="true"' if code == lang else ""
        items.append(f'<a href="{href}" data-language-link="{code}"{current}>{code}</a>')
    labels = {
        "es": "Idioma",
        "en": "Language",
        "fr": "Langue",
    }
    return render_template(partial("language/language-switcher.html"), {"items": "".join(items), "label": labels[lang]})


def theme_preview_bar(lang: str) -> str:
    default_site = showcase_by_id()
    ui = {
        "es": {
            "label": "Conceptos web",
            "switcher": "Selector de conceptos web",
            "announcement": "Concepto abierto: {label}",
        },
        "en": {
            "label": "Website Concepts",
            "switcher": "Website concept switcher",
            "announcement": "Concept opened: {label}",
        },
        "fr": {
            "label": "Concepts web",
            "switcher": "Sélecteur de concepts web",
            "announcement": "Concept ouvert : {label}",
        },
    }[lang]
    items = []
    for site in showcase_sites():
        label = localized(site.get("label", site["id"]), lang, site["id"])
        summary = localized(site.get("summary", ""), lang, "")
        swatches = site.get("swatch") or []
        style = "".join(
            [
                f"--theme-chip-a:{swatches[0]};" if len(swatches) > 0 else "",
                f"--theme-chip-b:{swatches[1]};" if len(swatches) > 1 else "",
                f"--theme-chip-c:{swatches[2]};" if len(swatches) > 2 else "",
            ]
        )
        title = f' title="{esc(summary)}"' if summary else ""
        items.append(
            f'<a class="theme-chip" href="{showcase_url(site["id"], lang)}"'
            f' data-theme-label="{esc(label)}"'
            f' data-theme-summary="{esc(summary)}"'
            f' data-theme-color="{esc(site.get("theme_color", ""))}"'
            f'{title} style="{esc(style)}">'
            f'<span class="theme-chip-swatch" aria-hidden="true"></span>'
            f'<span class="theme-chip-label">{esc(label)}</span>'
            f"</a>"
        )
    return render_template(
        partial("theme/theme-preview-bar.html"),
        {
            "label": esc(ui["label"]),
            "summary": esc(localized(default_site.get("summary", ""), lang, "")),
            "switcher_label": esc(ui["switcher"]),
            "announcement": esc(ui["announcement"].format(label=localized(default_site.get("label", default_site["id"]), lang, default_site["id"]))),
            "items": "".join(items),
        },
    )


def render_desktop_nav(lang: str, current: str, nav_label: str) -> str:
    current_group = page_meta(current).get("group", "")
    items = []
    for group_key in NAV["desktop_primary"]:
        group = NAV["groups"][group_key]
        href = page_url(group["page"], lang)
        label = esc(localized(group["label"], lang))
        role = esc(localized(group.get("role", ""), lang))
        is_group_current = current_group == group_key or current == group["page"]
        current_attr = ' aria-current="page"' if current == group["page"] else ""
        current_class = " is-current" if is_group_current else ""
        if not group.get("children"):
            items.append(f'<a class="nav-link" href="{href}"{current_attr}>{label}</a>')
            continue
        dropdown = "".join(
            f'<a class="nav-dropdown-link" href="{page_url(child, lang)}"' + (' aria-current="page"' if child == current else "") + f'><span>{esc(page_label(child, lang, "dropdown_label"))}</span></a>'
            for child in group["children"]
        )
        items.append(
            f'<div class="nav-item has-dropdown{current_class}">'
            f'<a class="nav-link" href="{href}"{current_attr}>{label}<span class="nav-caret" aria-hidden="true"></span></a>'
            f'<div class="nav-dropdown">'
            f'<div class="nav-dropdown-head"><span class="nav-dropdown-role">{role}</span><strong>{label}</strong></div>'
            f'<div class="nav-dropdown-list">{dropdown}</div>'
            f'</div>'
            f"</div>"
        )
    return render_template(partial("navigation/nav-desktop.html"), {
        "items": "".join(items),
        "nav_label": esc(nav_label),
    })


def render_mobile_nav(lang: str, current: str, nav_label: str) -> str:
    current_group = page_meta(current).get("group", "")
    primary_items = []
    expanded = set(NAV["mobile_expanded"])
    for group_key in NAV["mobile_primary"]:
        group = NAV["groups"][group_key]
        label = esc(localized(group["label"], lang))
        if group_key in expanded:
            links = "".join(
                f'<a href="{page_url(child, lang)}"' + (' aria-current="page"' if child == current else "") + f'>{esc(page_label(child, lang, "dropdown_label"))}</a>'
                for child in group["children"]
            )
            open_attr = " open" if current_group == group_key else ""
            primary_items.append(
                f'<details class="mobile-group"{open_attr}>'
                f"<summary>{label}</summary>"
                f'<div class="mobile-subnav">{links}</div>'
                f"</details>"
            )
        else:
            href = page_url(group["page"], lang)
            current_attr = ' aria-current="page"' if current == group["page"] else ""
            primary_items.append(f'<a class="mobile-link" href="{href}"{current_attr}>{label}</a>')

    partners_group = NAV["groups"]["partners"]
    partner_links = "".join(
        f'<a href="{page_url(child, lang)}"' + (' aria-current="page"' if child == current else "") + f'>{esc(page_label(child, lang))}</a>'
        for child in partners_group["children"]
    )
    partner_open = " open" if current_group == "partners" else ""
    secondary_label = {
        "es": "Partners",
        "en": "Partners",
        "fr": "Partenaires",
    }[lang]
    secondary = (
        f'<div class="mobile-secondary-block"><span class="mobile-secondary-label">{secondary_label}</span>'
        f'<details class="mobile-group"{partner_open}>'
        f"<summary>{esc(localized(partners_group['label'], lang))}</summary>"
        f'<div class="mobile-subnav">{partner_links}</div>'
        f"</details>"
        f"</div>"
    )
    markup = f'<div class="mobile-nav-primary">{"".join(primary_items)}</div>{secondary}'
    return render_template(partial("navigation/nav-mobile.html"), {
        "items": markup,
        "nav_label": esc(nav_label),
    })

def header(lang: str, page_key: str, language_urls: dict[str, str] | None = None) -> str:
    ui = {
        "es": {
            "skip": "Saltar al contenido",
            "home": "Inicio de Rotata",
            "utility": "Construye el sistema detrás de tu crecimiento",
            "close": "Cerrar menú",
            "language": "Idioma",
            "accessibility": "Accesibilidad",
            "open_menu": "Abrir menú",
            "primary_nav": "Navegación principal",
            "menu_panel": "Menú del sitio",
        },
        "en": {
            "skip": "Skip to content",
            "home": "Rotata home",
            "utility": "Build the system behind your growth",
            "close": "Close menu",
            "language": "Language",
            "accessibility": "Accessibility",
            "open_menu": "Open menu",
            "primary_nav": "Primary navigation",
            "menu_panel": "Site menu",
        },
        "fr": {
            "skip": "Aller au contenu",
            "home": "Accueil Rotata",
            "utility": "Construisez le système derrière votre croissance",
            "close": "Fermer le menu",
            "language": "Langue",
            "accessibility": "Accessibilité",
            "open_menu": "Ouvrir le menu",
            "primary_nav": "Navigation principale",
            "menu_panel": "Menu du site",
        },
    }[lang]
    desktop = render_desktop_nav(lang, page_key, ui["primary_nav"])
    mobile = render_template(partial("header/header-mobile.html"), {
        "items": render_mobile_nav(lang, page_key, ui["primary_nav"]),
        "close_label": ui["close"],
        "menu_panel_label": ui["menu_panel"],
        "home_url": page_url("home", lang),
        "home_label": ui["home"],
        "logo_markup": theme_logo_markup(154, 40),
        "cta_url": page_url("contact-consult", lang),
        "cta_label": NAV["ui"][lang]["footer_cta"],
    })
    return render_template(partial("header/header.html"), {
        "skip_label": ui["skip"],
        "home_label": ui["home"],
        "theme_preview_bar": theme_preview_bar(lang),
        "utility_label": ui["utility"],
        "home_url": page_url("home", lang),
        "logo_markup": theme_logo_markup(154, 40),
        "nav_desktop": desktop,
        "nav_mobile": mobile,
        "language_switcher": language_switcher(lang, page_key, language_urls),
        "accessibility_url": page_url("legal-accessibility", lang),
        "accessibility_label": ui["accessibility"],
        "menu_label": ui["open_menu"],
        "cta_url": page_url("contact-consult", lang),
        "cta_label": NAV["ui"][lang]["header_cta"],
    })

def footer_columns(lang: str) -> str:
    columns = []
    for column in NAV["footer_columns"]:
        links = "".join(
            f'<a href="{page_url(item, lang)}">{esc(page_label(item, lang, "footer_label"))}</a>'
            for item in column["items"]
        )
        columns.append(
            f'<section class="footer-column">'
            f'<h2 class="footer-heading">{esc(localized(column["title"], lang))}</h2>'
            f'<nav class="footer-links" aria-label="{esc(localized(column["title"], lang))}">{links}</nav>'
            f"</section>"
        )
    return "".join(columns)


def mobile_footer_columns(lang: str) -> str:
    columns = []
    for column in NAV["footer_columns"]:
        links = "".join(
            f'<a href="{page_url(item, lang)}">{esc(page_label(item, lang, "footer_label"))}</a>'
            for item in column["items"]
        )
        columns.append(
            f'<details class="footer-accordion">'
            f'<summary>{esc(localized(column["title"], lang))}</summary>'
            f'<div class="footer-accordion-links" aria-label="{esc(localized(column["title"], lang))}">{links}</div>'
            f"</details>"
        )
    return "".join(columns)


def footer(lang: str) -> str:
    funding_text = {
        "es": "Financiado por la Unión Europea a través del programa Kit Digital, con fondos Next Generation EU del Mecanismo de Recuperación y Resiliencia.",
        "en": "Funded by the European Union through the Kit Digital programme, financed by the Next Generation EU funds of the Recovery and Resilience Mechanism.",
        "fr": "Financé par l'Union européenne via le programme Kit Digital, grâce aux fonds Next Generation EU du Mécanisme pour la reprise et la résilience.",
    }[lang]
    copy = {
        "es": {
            "cta_heading": "Construye el sistema detrás de tu crecimiento",
            "cta_text": "Convierte herramientas, datos y procesos desconectados en un sistema estructurado de crecimiento B2B.",
            "tagline": "Construye el sistema detrás de tu crecimiento",
            "summary": "Rotata diseña sistemas estructurados de crecimiento con soporte de IA para equipos B2B de marketing y ventas.",
            "email": "Email",
            "phone": "Teléfono",
            "location": "España",
            "location_worldwide": "España, servicio global",
            "copyright": f"© {datetime.now().year} Rotata Consulting SL"
        },
        "en": {
            "cta_heading": "Build the system behind your growth",
            "cta_text": "Turn disconnected tools, data, and processes into a structured B2B growth system.",
            "tagline": "Build the system behind your growth",
            "summary": "Rotata designs structured, AI-supported growth systems for B2B marketing and sales teams.",
            "email": "Email",
            "phone": "Phone",
            "location": "Spain",
            "location_worldwide": "Spain, serving Worldwide",
            "copyright": f"© {datetime.now().year} Rotata Consulting SL"
        },
        "fr": {
            "cta_heading": "Construisez le système derrière votre croissance",
            "cta_text": "Transformez des outils, données et processus déconnectés en système structuré de croissance B2B.",
            "tagline": "Construisez le système derrière votre croissance",
            "summary": "Rotata conçoit des systèmes de croissance structurés, assistés par IA, pour les équipes marketing et sales B2B.",
            "email": "Email",
            "phone": "Téléphone",
            "location": "Espagne",
            "location_worldwide": "Espagne, service mondial",
            "copyright": f"© {datetime.now().year} Rotata Consulting SL"
        },
    }[lang]
    brand_links = (
        f'<a class="footer-contact-link" href="{SITE["site"]["linkedin"]}" data-track="linkedin_click"><span class="footer-contact-icon">in</span><span>LinkedIn</span></a>'
        f'<a class="footer-contact-link" href="mailto:{SITE["site"]["email"]}"><span class="footer-contact-icon">@</span><span>{SITE["site"]["email"]}</span></a>'
        f'<a class="footer-contact-link" href="tel:{SITE["site"]["phone"].replace(" ", "")}"><span class="footer-contact-icon">+</span><span>{SITE["site"]["phone"]}</span></a>'
        f'<span class="footer-contact-link is-static"><span class="footer-contact-icon">es</span><span>{esc(copy["location"])}</span></span>'
    )
    funding_strip = (
        '<div class="container funding-strip">'
        '<img src="/assets/partners/rotata-kit-digital-eu-funding.png" '
        'alt="Kit Digital, Gobierno de España, Red.es, Next Generation EU y Plan de Recuperación">'
        f"<span>{esc(funding_text)}</span>"
        "</div>"
    )
    return render_template(partial("footer/footer.html"), {
        "logo_markup": theme_logo_markup(156, 40),
        "footer_cta_heading": copy["cta_heading"],
        "footer_cta_text": copy["cta_text"],
        "footer_cta_url": page_url("contact-consult", lang),
        "footer_cta_label": NAV["ui"][lang]["footer_cta"],
        "brand_name": SITE["site"]["name"],
        "brand_tagline": copy["tagline"],
        "brand_summary": copy["summary"],
        "brand_links": brand_links,
        "brand_location": copy["location"],
        "brand_location_mobile": copy["location_worldwide"],
        "footer_columns": footer_columns(lang),
        "footer_mobile_columns": mobile_footer_columns(lang),
        "funding_strip": funding_strip,
        "footer_bottom": esc(copy["copyright"]),
    })

def cookie_banner(lang: str) -> str:
    data = COOKIE[lang]
    extra = {
        "es": {"eyebrow": "Cookies", "policy": "Leer política"},
        "en": {"eyebrow": "Cookies", "policy": "Read policy"},
        "fr": {"eyebrow": "Cookies", "policy": "Lire la politique"},
    }[lang]
    return render_template(partial("cookie/cookie-consent.html"), {
        "eyebrow": esc(extra["eyebrow"]),
        "title": esc(data["title"]),
        "body": esc(data["body"]),
        "accept": esc(data["accept"]),
        "necessary_only": esc(data["necessary_only"]),
        "reject": esc(data["reject"]),
        "policy": esc(extra["policy"]),
        "policy_url": page_url("legal-cookies", lang),
    })

def schema_for(page_key: str, lang: str, title: str, description: str, url: str) -> str:
    base = SITE["site"]["base_url"].rstrip("/")
    payload = page_payload(page_key, lang)
    graph = [
        {"@type": "Organization", "@id": f"{base}/#organization", "name": SITE["site"]["company"], "url": base, "logo": base + SITE["site"]["logo"], "sameAs": [SITE["site"]["linkedin"]]},
        {"@type": "WebSite", "@id": f"{base}/#website", "url": base, "name": SITE["site"]["name"], "publisher": {"@id": f"{base}/#organization"}, "inLanguage": lang},
        {"@type": "WebPage", "@id": base + url, "url": base + url, "name": title, "description": description, "isPartOf": {"@id": f"{base}/#website"}, "inLanguage": lang},
    ]
    if payload["schema_service"]:
        graph.append({"@type": "Service", "name": title, "provider": {"@id": f"{base}/#organization"}, "areaServed": "Europe", "serviceType": payload["seo_keyword"] or title})
    if payload["render"] == "roi":
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": "What drives ROI?", "acceptedAnswer": {"@type": "Answer", "text": "Data quality, conversion, sales velocity, automation and marketing-sales alignment."}},
            {"@type": "Question", "name": "Is the calculator exact?", "acceptedAnswer": {"@type": "Answer", "text": "It is an estimate used for diagnostic conversations, not a financial guarantee."}},
        ]})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)

def head(lang: str, page_key: str, title: str, description: str, url: str) -> str:
    if len(description or "") < 50:
        description = f"{description} Rotata Consulting SL estructura sistemas de crecimiento B2B con CRM, datos, automatización e IA."
    canonical = SITE["site"]["base_url"].rstrip("/") + url
    alternates = []
    for code in SITE["languages"]:
        if page_key in PAGE_DEFS:
            alternates.append(f'<link rel="alternate" hreflang="{code}" href="{SITE["site"]["base_url"].rstrip()}{page_url(page_key, code)}">')
    config = runtime_config()
    default_theme = theme_by_id()
    theme_color = esc(default_theme.get("theme_color", "#08151D"))
    bootstrap = """
    <script>
    (() => {
      try {
        const theme = localStorage.getItem("rotata-design-theme");
        const surface = localStorage.getItem("rotata-design-surface");
        const color = localStorage.getItem("rotata-design-theme-color");
        if (theme) document.documentElement.dataset.designTheme = theme;
        if (surface) document.documentElement.dataset.themeSurface = surface;
        if (color) {
          const meta = document.querySelector('meta[name="theme-color"]');
          if (meta) meta.setAttribute("content", color);
        }
      } catch (error) {}
    })();
    </script>
    """
    return f'''
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="{theme_color}">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}">
    <link rel="canonical" href="{canonical}">
    {"".join(alternates)}
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Rotata">
    <meta property="og:title" content="{esc(title)}">
    <meta property="og:description" content="{esc(description)}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:image" content="{SITE["site"]["base_url"].rstrip()}{SITE["site"]["og"]}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{esc(title)}">
    <meta name="twitter:description" content="{esc(description)}">
    <meta name="twitter:image" content="{SITE["site"]["base_url"].rstrip()}{SITE["site"]["og"]}">
    <link rel="icon" href="/assets/logo/rotata-favicon.png">
    <link rel="apple-touch-icon" href="/assets/logo/rotata-apple-touch-icon.png">
    {bootstrap}
    <link rel="stylesheet" href="/styles/global.css">
    <script>window.ROTATA_CONFIG = {json.dumps(config)};</script>
    <script type="application/ld+json">{schema_for(page_key, lang, title, description, url)}</script>
    '''

def layout(lang: str, page_key: str, body: str) -> str:
    t = page_payload(page_key, lang)["translation"]
    url = page_url(page_key, lang)
    default_theme = theme_by_id()
    return f'''<!doctype html>
    <html lang="{lang}" data-design-theme="{esc(default_theme["id"])}" data-theme-surface="{esc(default_theme.get("surface", "dark"))}">
    <head>{head(lang, page_key, t["title"], t["description"], url)}</head>
    <body class="page page-{esc(page_key)}">
      {header(lang, page_key)}
      <main id="main" class="site-main">{body}</main>
      {footer(lang)}
      {widgets(lang)}
      {cookie_banner(lang)}
      <script type="module" src="/scripts/global.js"></script>
    </body>
    </html>'''

def hero_visual_path(page_key: str) -> str:
    relative = f"/assets/section-visuals/hero-{page_key}.webp"
    if (SRC / relative.lstrip("/")).exists():
        return relative
    return "/assets/section-visuals/hero-home.webp"


def section_visual_path(page_key: str, index: int, variant: str) -> str:
    relative = f"/assets/section-visuals/{page_key}-{index + 1:02d}-{variant}.webp"
    if (SRC / relative.lstrip("/")).exists():
        return relative
    fallbacks = {
        "problem": "/assets/section-visuals/home-01-problem.webp",
        "cards": "/assets/section-visuals/home-02-cards.webp",
        "grid": "/assets/section-visuals/home-03-grid.webp",
        "process": "/assets/section-visuals/home-04-process.webp",
        "metrics": "/assets/section-visuals/home-05-metrics.webp",
        "partners": "/assets/section-visuals/home-06-partners.webp",
        "blog-preview": "/assets/section-visuals/home-07-blog-preview.webp",
        "text": "/assets/section-visuals/contact-01-text.webp",
    }
    return fallbacks.get(variant, "/assets/section-visuals/home-03-grid.webp")


def service_icon(title: str = "", text: str = "") -> str:
    target = f"{title} {text}".lower()
    if any(token in target for token in ("crm", "hubspot", "pipeline", "lifecycle", "reporting")):
        return "/assets/icons/rotata-crm-icon.svg"
    if any(token in target for token in ("automation", "workflow", "handoff", "outbound", "sequence")):
        return "/assets/icons/rotata-automation-icon.svg"
    if any(token in target for token in ("data", "signal", "intent", "account", "segment")):
        return "/assets/icons/rotata-data-icon.svg"
    if any(token in target for token in ("meeting", "velocity", "conversion", "roi")):
        return "/assets/icons/rotata-pipeline-icon.svg"
    if any(token in target for token in ("ai", "ia", "intelligence")):
        return "/assets/icons/rotata-ai-icon.svg"
    return "/assets/icons/rotata-system-icon.svg"


def resolve_cta_href(translation: dict, url_key: str, page_key_key: str, default_page: str) -> str:
    explicit_url = translation.get(url_key)
    if explicit_url:
        return explicit_url
    target = translation.get(page_key_key, default_page)
    if isinstance(target, str) and (target.startswith("/") or target.startswith("#") or target.startswith("http")):
        return target
    return page_url(target, CURRENT_LANG)


def hero(t: dict, page_key: str) -> str:
    visual_labels = {
        "es": {
            "board": "Vista operativa",
            "title": "Sistema conectado",
            "status": [("Modelo CRM", "estructurado"), ("Pipeline", "legible"), ("Automatización", "orquestada")],
            "footer": [("Datos", "seguros"), ("Señales", "priorizadas"), ("Seguimiento", "consistente")],
            "proof": ["Arquitectura CRM", "Claridad pipeline", "Automatización controlada"],
            "scroll": "Explorar sistema",
        },
        "en": {
            "board": "Operating view",
            "title": "Connected system",
            "status": [("CRM model", "structured"), ("Pipeline", "readable"), ("Automation", "orchestrated")],
            "footer": [("Data", "clean"), ("Signals", "prioritized"), ("Follow-up", "consistent")],
            "proof": ["CRM architecture", "Pipeline clarity", "Automation control"],
            "scroll": "Explore the system",
        },
        "fr": {
            "board": "Vue opérationnelle",
            "title": "Système connecté",
            "status": [("Modèle CRM", "structuré"), ("Pipeline", "lisible"), ("Automatisation", "orchestrée")],
            "footer": [("Données", "propres"), ("Signaux", "priorisés"), ("Suivi", "constant")],
            "proof": ["Architecture CRM", "Clarté pipeline", "Automatisation pilotée"],
            "scroll": "Explorer le système",
        },
    }[CURRENT_LANG]
    visual = '''
    <div class="hero-visual" aria-hidden="true">
      <div class="hero-visual-head">
        <span>{}</span>
        <strong>{}</strong>
      </div>
      <div class="hero-visual-surface">
        <div class="hero-panel">
          <div class="signal-row"><span>{}</span><strong>{}</strong></div>
          <div class="signal-row"><span>{}</span><strong>{}</strong></div>
          <div class="signal-row"><span>{}</span><strong>{}</strong></div>
        </div>
        <div class="hero-metric-strip">
          <div><span>{}</span><strong>{}</strong></div>
          <div><span>{}</span><strong>{}</strong></div>
          <div><span>{}</span><strong>{}</strong></div>
        </div>
      </div>
    </div>'''.format(
        esc(visual_labels["board"]),
        esc(visual_labels["title"]),
        *(esc(value) for pair in visual_labels["status"] for value in pair),
        *(esc(value) for pair in visual_labels["footer"] for value in pair),
    )
    media = f'<img src="{hero_visual_path(t.get("_visual_source", page_key))}" alt="" loading="eager" width="1920" height="1280">'
    proof = "".join(f"<span>{esc(item)}</span>" for item in visual_labels["proof"])
    scroll = ""
    if t.get("sections"):
        scroll = f'<a class="hero-scroll-cue" href="#section-01" aria-label="{esc(visual_labels["scroll"])}"><span></span><em>{esc(visual_labels["scroll"])}</em></a>'
    primary_href = resolve_cta_href(t, "primary_cta_url", "primary_cta_page", "contact-consult")
    secondary_href = resolve_cta_href(t, "secondary_cta_url", "secondary_cta_page", "solutions")
    return f'''
    <section class="hero hero-{esc(page_key)}">
      <div class="hero-media" aria-hidden="true">{media}</div>
      <div class="container hero-grid">
        <div class="hero-content" data-reveal>
          <p class="eyebrow">{esc(t["eyebrow"])}</p>
          <h1>{esc(t["h1"])}</h1>
          <p class="lead">{esc(t["intro"])}</p>
          <div class="button-row">
            <a class="btn btn-primary" data-track="cta_click" href="{primary_href}">{esc(t.get("primary_cta", t.get("final_cta", "Contact")))}</a>
            <a class="btn btn-secondary" data-track="cta_click" href="{secondary_href}">{esc(t.get("secondary_cta", "Solutions"))}</a>
          </div>
          <div class="hero-proof">{proof}</div>
        </div>
        {visual}
      </div>
      {scroll}
    </section>'''

def widgets(lang: str) -> str:
    copy = {
        "es": {
            "top": "Volver arriba",
            "wa": "Hablar por WhatsApp",
            "bot": "Abrir Soy Rotbot",
            "title": "Soy Rotbot",
            "status": "Asistente de sistemas B2B",
            "hello": "Hola. Puedo ayudarte a ubicar el problema: CRM, datos, outbound, ROI o automatización.",
            "p1": "Quiero ordenar HubSpot",
            "r1": "Primero revisaríamos datos, lifecycle stages, pipeline, workflows y dashboards. Después priorizamos lo que bloquea decisiones.",
            "p2": "Necesito más reuniones cualificadas",
            "r2": "La ruta suele ser targeting, señales de cuenta, mensajes, secuencias y medición conectada al CRM.",
            "p3": "Calcular ROI",
            "r3": "Usa la calculadora ROI y después podemos revisar supuestos comerciales, conversión y velocidad de pipeline.",
            "contact": "Hablar con Rotata",
        },
        "en": {
            "top": "Back to top",
            "wa": "Talk on WhatsApp",
            "bot": "Open Soy Rotbot",
            "title": "Soy Rotbot",
            "status": "B2B systems assistant",
            "hello": "Hello. I can help locate the problem: CRM, data, outbound, ROI or automation.",
            "p1": "I need to structure HubSpot",
            "r1": "We would first audit data, lifecycle stages, pipeline, workflows and dashboards. Then we prioritize what blocks decisions.",
            "p2": "I need more qualified meetings",
            "r2": "The route is usually targeting, account signals, messaging, sequences and measurement connected to CRM.",
            "p3": "Calculate ROI",
            "r3": "Use the ROI calculator first, then we can review commercial assumptions, conversion and pipeline velocity.",
            "contact": "Talk to Rotata",
        },
        "fr": {
            "top": "Retour en haut",
            "wa": "Parler sur WhatsApp",
            "bot": "Ouvrir Soy Rotbot",
            "title": "Soy Rotbot",
            "status": "Assistant systèmes B2B",
            "hello": "Bonjour. Je peux aider à situer le problème : CRM, données, outbound, ROI ou automatisation.",
            "p1": "Je dois structurer HubSpot",
            "r1": "Nous auditerions d’abord les données, lifecycle stages, pipeline, workflows et dashboards. Ensuite nous priorisons ce qui bloque les décisions.",
            "p2": "Je veux plus de rendez-vous qualifiés",
            "r2": "Le parcours combine ciblage, signaux de compte, messages, séquences et mesure connectée au CRM.",
            "p3": "Calculer le ROI",
            "r3": "Utilisez d’abord la calculatrice ROI, puis nous pouvons revoir les hypothèses commerciales, la conversion et la vélocité du pipeline.",
            "contact": "Parler à Rotata",
        },
    }[lang]
    wa_text = {
        "es": "Hola Rotata, quiero revisar mi sistema de crecimiento B2B.",
        "en": "Hello Rotata, I want to review my B2B growth system.",
        "fr": "Bonjour Rotata, je veux revoir mon système de croissance B2B.",
    }[lang]
    contact = page_url("contact", lang)
    roi = page_url("insights-roi", lang)
    return f'''
    <div class="floating-actions" aria-label="Quick actions">
      <button class="float-button back-to-top" type="button" data-back-to-top aria-label="{esc(copy["top"])}">↑</button>
      <a class="float-button whatsapp" href="https://wa.me/34649498272?text={quote(wa_text)}" aria-label="{esc(copy["wa"])}" data-track="whatsapp_click">WA</a>
      <button class="float-button rotbot-button" type="button" data-rotbot-toggle aria-expanded="false" aria-controls="rotbot-panel" aria-label="{esc(copy["bot"])}">
        <img src="/assets/images/rotata-rotbot-ai-assistant.png" alt="">
      </button>
    </div>
    <aside class="rotbot-panel" id="rotbot-panel" data-rotbot-panel hidden>
      <div class="rotbot-head">
        <img src="/assets/images/rotata-rotbot-ai-assistant.png" alt="">
        <div><strong>{esc(copy["title"])}</strong><span>{esc(copy["status"])}</span></div>
        <button class="rotbot-close" type="button" data-rotbot-close aria-label="Close">×</button>
      </div>
      <div class="rotbot-messages" data-rotbot-messages>
        <p class="rotbot-message bot">{esc(copy["hello"])}</p>
      </div>
      <div class="rotbot-prompts">
        <button type="button" data-rotbot-prompt data-rotbot-reply="{esc(copy["r1"])}">{esc(copy["p1"])}</button>
        <button type="button" data-rotbot-prompt data-rotbot-reply="{esc(copy["r2"])}">{esc(copy["p2"])}</button>
        <button type="button" data-rotbot-prompt data-rotbot-reply="{esc(copy["r3"])}">{esc(copy["p3"])}</button>
        <a href="{roi}" data-track="roi_widget_click">{esc(copy["p3"])}</a>
        <a href="{contact}" data-track="cta_click">{esc(copy["contact"])}</a>
      </div>
    </aside>'''

def render_items(items, variant: str) -> str:
    if not items:
        return ""
    if variant == "process":
        return '<ol class="timeline">' + "".join(f"<li><strong>{index:02d}</strong><span>{esc(item)}</span></li>" for index, item in enumerate(items, start=1)) + "</ol>"
    if all(isinstance(item, dict) for item in items):
        return '<div class="grid-4">' + "".join(
            render_template(
                partial("cards/service-card.html"),
                {
                    "icon": service_icon(item.get("title", ""), item.get("text", "")),
                    "title": esc(item.get("title", "")),
                    "text": esc(item.get("text", "")),
                },
            )
            for item in items
        ) + "</div>"
    if variant == "metrics":
        return '<div class="pill-grid">' + "".join(f'<article class="pill-card"><span>{index:02d}</span><p>{esc(item)}</p></article>' for index, item in enumerate(items, start=1)) + "</div>"
    if variant in {"grid", "problem", "text"}:
        return '<div class="feature-list">' + "".join(f'<article class="feature-item"><span>{index:02d}</span><p>{esc(item)}</p></article>' for index, item in enumerate(items, start=1)) + "</div>"
    return '<ul class="pill-list">' + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"

def blog_cards(limit: int = 3, lang: str | None = None, posts: list[dict] | None = None) -> str:
    target_lang = lang or CURRENT_LANG
    items = posts or blog_posts(target_lang)
    cards = []
    for post in items[:limit]:
        cards.append(render_template(partial("cards/blog-card.html"), {
            "url": article_url(post["slug"], target_lang),
            "image": post["image"],
            "alt": esc(post["alt"]),
            "category": esc(post["category"]),
            "title": esc(post["title"]),
            "excerpt": esc(post["excerpt"]),
            "meta": esc(f'{format_blog_date(post["date"], target_lang)} · {reading_time_copy(post["reading_time"], target_lang)}'),
        }))
    return '<div class="grid-3">' + "".join(cards) + "</div>"

def section_visual(page_key: str, section: dict, index: int, label: str) -> str:
    visual_page = section.get("_visual_page", page_key)
    visual_index = section.get("_visual_index", index)
    return f'''
    <figure class="section-visual" aria-hidden="true">
      <img src="{section_visual_path(visual_page, visual_index, section.get("variant", "grid"))}" alt="" loading="lazy" width="1600" height="1120">
      <div class="section-visual-caption"><span>{index + 1:02d}</span><strong>{esc(label)}</strong></div>
    </figure>'''


def section_html(page_key: str, section: dict, index: int) -> str:
    variant = section.get("variant", "text")
    eyebrow_labels = {
        "es": {"problem": "Fricción", "cards": "Capas del sistema", "grid": "Modelo operativo", "process": "Cadencia", "metrics": "Lectura de impacto", "partners": "Stack conectado", "blog-preview": "Biblioteca", "text": "Contexto"},
        "en": {"problem": "Friction", "cards": "System layers", "grid": "Operating model", "process": "Execution rhythm", "metrics": "Impact readout", "partners": "Connected stack", "blog-preview": "Library", "text": "Context"},
        "fr": {"problem": "Friction", "cards": "Couches du système", "grid": "Modèle opératoire", "process": "Cadence", "metrics": "Lecture d’impact", "partners": "Stack connecté", "blog-preview": "Bibliothèque", "text": "Contexte"},
    }[CURRENT_LANG]
    if variant == "blog-preview":
        body = blog_cards(3)
    elif variant == "partners":
        partner_label = {"es": "Explorar", "en": "Explore", "fr": "Explorer"}[CURRENT_LANG]
        body = '<div class="grid-4">' + "".join(
            render_template(
                partial("cards/partner-card.html"),
                {
                    "name": esc(localized(p["name"], CURRENT_LANG)),
                    "role": esc(localized(p["role"], CURRENT_LANG)),
                    "url": page_url(p["page_key"], CURRENT_LANG) if p.get("page_key") else p["url"],
                    "label": partner_label,
                },
            )
            for p in PARTNERS
        ) + "</div>"
    else:
        body = render_items(section.get("items", []), variant)
    label = eyebrow_labels.get(variant, "Rotata")
    shell = f'''
        <div class="section-shell{' is-reversed' if index % 2 else ''}">
          <div class="section-copy">
            <div class="section-meta">
              <span class="section-number">{index + 1:02d}</span>
              <p class="eyebrow">{esc(label)}</p>
            </div>
            <div class="section-heading">
              <h2>{esc(section.get("heading", ""))}</h2>
              <p class="lead">{esc(section.get("body", ""))}</p>
            </div>
          </div>
          {section_visual(page_key, section, index, label)}
        </div>'''
    return f'''
    <section class="section section-{esc(variant)}" id="section-{index + 1:02d}" data-reveal>
      <div class="container {'wide' if variant in {'cards','partners','blog-preview'} else ''}">
        {shell}
        <div class="section-body section-body-{esc(variant)}">{body}</div>
      </div>
    </section>'''


def newsletter_form(lang: str, source_page: str) -> str:
    labels = FORMS["newsletter"][lang]
    fields = f'''
    <div class="form-grid">
      <label>{esc(labels["first_name"])}<input name="first_name" autocomplete="given-name" required></label>
      <label>{esc(labels["last_name"])}<input name="last_name" autocomplete="family-name"></label>
    </div>
    <label>{esc(labels["email"])}<input name="email" type="email" autocomplete="email" required></label>
    <label class="consent-line"><input type="checkbox" name="newsletter_consent" required> <span>{esc(labels["communications_consent"])}</span></label>
    <label class="consent-line"><input type="checkbox" name="privacy_consent" required> <span>{esc(labels["privacy_prefix"])}<a href="{page_url("legal-privacy", lang)}">{esc(labels["privacy_link"])}</a>{esc(labels["privacy_suffix"])}</span></label>
    '''
    return render_template(
        partial("forms/newsletter-form.html"),
        {
            "fields": fields,
            "source_page": source_page,
            "language": lang,
            "submit": esc(labels["submit"]),
        },
    )


def newsletter_panel(lang: str, source_page: str) -> str:
    labels = FORMS["newsletter"][lang]
    return f'''
    <section class="section">
      <div class="container wide">
        <div class="newsletter-page-grid glass-panel" id="newsletter-signup">
          <div class="newsletter-copy" data-reveal>
            <p class="eyebrow">{esc(labels["eyebrow"])}</p>
            <h2>{esc(labels["heading"])}</h2>
            <p class="lead">{esc(labels["body"])}</p>
          </div>
          <div class="newsletter-form-wrap" data-reveal>
            {newsletter_form(lang, source_page)}
          </div>
        </div>
      </div>
    </section>'''


def newsletter_modal(lang: str, source_page: str) -> str:
    labels = FORMS["newsletter"][lang]
    close_label = {"es": "Cerrar", "en": "Close", "fr": "Fermer"}[lang]
    return f'''
    <div class="newsletter-modal" data-newsletter-modal hidden>
      <button class="newsletter-backdrop" type="button" data-newsletter-close tabindex="-1" aria-hidden="true"></button>
      <section class="newsletter-dialog glass-panel" role="dialog" aria-modal="true" aria-labelledby="newsletter-modal-title" data-newsletter-dialog>
        <button class="newsletter-close" type="button" data-newsletter-close aria-label="{esc(close_label)}">×</button>
        <div class="newsletter-shell">
          <div class="newsletter-copy">
            <p class="eyebrow">{esc(labels["eyebrow"])}</p>
            <h2 id="newsletter-modal-title">{esc(labels["heading"])}</h2>
            <p class="lead">{esc(labels["body"])}</p>
          </div>
          <div class="newsletter-form-wrap">
            {newsletter_form(lang, source_page)}
          </div>
        </div>
      </section>
    </div>'''

def standard_page(lang: str, page_key: str) -> str:
    global CURRENT_LANG
    CURRENT_LANG = lang
    payload = page_payload(page_key, lang)
    t = payload["translation"]
    render_type = payload["render"]
    body = hero(t, page_key)
    sections = t.get("sections", [])
    if render_type == "roi":
        for index, section in enumerate(sections[:3]):
            body += section_html(page_key, section, index)
        body += roi_calculator(lang)
        for index, section in enumerate(sections[3:], start=3):
            body += section_html(page_key, section, index)
    elif render_type == "contact":
        for index, section in enumerate(sections[:3]):
            body += section_html(page_key, section, index)
        body += contact_form(lang)
        for index, section in enumerate(sections[3:], start=3):
            body += section_html(page_key, section, index)
    elif render_type == "newsletter":
        for index, section in enumerate(sections[:1]):
            body += section_html(page_key, section, index)
        body += newsletter_panel(lang, page_key)
        for index, section in enumerate(sections[1:], start=1):
            body += section_html(page_key, section, index)
    elif render_type == "cases":
        if sections:
            body += section_html(page_key, sections[0], 0)
        body += case_grid()
        for index, section in enumerate(sections[1:], start=1):
            body += section_html(page_key, section, index)
    else:
        for index, section in enumerate(sections):
            body += section_html(page_key, section, index)
    default_cta = {
        "es": "Construye el sistema detrás de tu crecimiento",
        "en": "Build the system behind your growth",
        "fr": "Construisez le système derrière votre croissance",
    }[lang]
    final_href = resolve_cta_href(t, "final_cta_url", "final_cta_page", "contact-consult")
    body += render_template(partial("cta/cta-primary.html"), {"heading": esc(t.get("final_cta", default_cta)), "href": final_href, "label": esc(NAV["ui"][lang]["footer_cta"])})
    return layout(lang, page_key, body)

def contact_form(lang: str) -> str:
    labels = FORMS["labels"][lang]
    service_options = "".join(f'<option value="{esc(item)}">{esc(item)}</option>' for item in FORMS["service_interests"])
    fields = f'''
    <div class="form-grid">
      <label>{esc(labels["first_name"])}<input name="first_name" autocomplete="given-name" required></label>
      <label>{esc(labels["last_name"])}<input name="last_name" autocomplete="family-name" required></label>
      <label>{esc(labels["email"])}<input name="email" type="email" autocomplete="email" required></label>
      <label>{esc(labels["phone"])}<input name="phone" type="tel" autocomplete="tel"></label>
      <label>{esc(labels["company"])}<input name="company" autocomplete="organization" required></label>
      <label>{esc(labels["website"])}<input name="website" type="url" autocomplete="url"></label>
    </div>
    <label>{esc(labels["service"])}<select name="service_interest" required>{service_options}</select></label>
    <label>{esc(labels["message"])}<textarea name="message" required></textarea></label>
    <label class="consent-line"><input type="checkbox" name="privacy_consent" required> <span>{esc(labels["consent"])}</span></label>
    '''
    form = render_template(partial("forms/contact-form.html"), {"fields": fields, "source_page": "contact", "language": lang, "submit": esc(labels["submit"])})
    return f'<section class="section" id="contact-form"><div class="container"><div class="glass-panel" style="padding:clamp(1.5rem,4vw,3rem)">{form}</div></div></section>'

def roi_calculator(lang: str) -> str:
    labels = {
        "es": ["Leads mensuales", "Conversión a oportunidad (%)", "Valor medio (€)", "Mejora esperada del sistema (%)", "Valor incremental estimado"],
        "en": ["Monthly leads", "Opportunity conversion (%)", "Average value (€)", "Expected system improvement (%)", "Estimated incremental value"],
        "fr": ["Leads mensuels", "Conversion opportunité (%)", "Valeur moyenne (€)", "Amélioration attendue (%)", "Valeur incrémentale estimée"],
    }[lang]
    return f'''
    <section class="section" id="roi-calculator">
      <div class="container">
        <form class="roi-calculator" data-roi-calculator>
          <div class="form-grid">
            <label>{labels[0]}<input type="number" name="monthly_leads" value="120" min="0"></label>
            <label>{labels[1]}<input type="number" name="conversion_rate" value="8" min="0" max="100"></label>
            <label>{labels[2]}<input type="number" name="average_value" value="12000" min="0"></label>
            <label>{labels[3]}<input type="number" name="system_improvement" value="20" min="0" max="100"></label>
          </div>
          <div class="roi-result"><p>{labels[4]}</p><strong class="metric" data-roi-output>€0</strong></div>
        </form>
      </div>
    </section>'''

def case_grid() -> str:
    labels = {
        "es": {"problem_label": "Problema", "system_label": "Sistema", "result_label": "Resultado"},
        "en": {"problem_label": "Problem", "system_label": "System", "result_label": "Result"},
        "fr": {"problem_label": "Problème", "system_label": "Système", "result_label": "Résultat"},
    }[CURRENT_LANG]
    cards = "".join(
        render_template(
            partial("cards/case-card.html"),
            {
                **labels,
                **{k: esc(localized(v, CURRENT_LANG)) for k, v in case.items()},
            },
        )
        for case in CASES
    )
    return f'<section class="section"><div class="container wide"><div class="grid-3">{cards}</div></div></section>'

def blog_page(lang: str, page_key: str) -> str:
    global CURRENT_LANG
    CURRENT_LANG = lang
    t = page_payload(page_key, lang)["translation"]
    posts = blog_posts(lang)
    body = hero(t, page_key)
    sections = t.get("sections", [])
    for index, section in enumerate(sections[:2]):
        body += section_html(page_key, section, index)
    latest_title = {"es": "Últimos artículos", "en": "Latest articles", "fr": "Derniers articles"}[lang]
    latest_label = {"es": "Artículos", "en": "Article Grid", "fr": "Articles"}[lang]
    latest_intro = {
        "es": "La biblioteca se ordena automáticamente por fecha para que el contenido nuevo aparezca primero.",
        "en": "The library is automatically ordered by date so new content appears first.",
        "fr": "La bibliothèque est automatiquement triée par date pour afficher les nouveaux contenus en premier.",
    }[lang]
    body += f'<section class="section"><div class="container wide"><div class="section-heading"><p class="eyebrow">{latest_label}</p><h2>{latest_title}</h2><p class="lead">{latest_intro}</p></div>' + blog_cards(len(posts), lang, posts) + "</div></section>"
    for index, section in enumerate(sections[2:], start=2):
        body += section_html(page_key, section, index)
    final_href = resolve_cta_href(t, "final_cta_url", "final_cta_page", "contact-consult")
    body += render_template(partial("cta/cta-primary.html"), {"heading": esc(t.get("final_cta", latest_title)), "href": final_href, "label": esc(NAV["ui"][lang]["footer_cta"])})
    return layout(lang, page_key, body)

def article_page(slug: str, lang: str) -> str:
    post = load_blog_post(slug, lang)
    global CURRENT_LANG
    CURRENT_LANG = lang
    title = post["title"]
    description = post["excerpt"][:158]
    if len(description or "") < 50:
        fallback = {
            "es": "Artículo de Rotata sobre sistemas de crecimiento B2B, CRM, datos, automatización e IA.",
            "en": "Rotata article about B2B growth systems, CRM, data, automation and AI.",
            "fr": "Article Rotata sur les systèmes de croissance B2B, le CRM, la data, l'automatisation et l'IA.",
        }[lang]
        description = f"{description} {fallback}".strip()
    url = article_url(slug, lang)
    canonical = SITE["site"]["base_url"].rstrip("/") + url
    alternates = "".join(
        f'<link rel="alternate" hreflang="{code}" href="{SITE["site"]["base_url"].rstrip()}{href}">'
        for code, href in article_language_urls(slug).items()
    )
    schema = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": title,
            "description": description,
            "datePublished": post["date"],
            "author": {"@type": "Person", "name": post["author"]},
            "publisher": {
                "@type": "Organization",
                "name": SITE["site"]["company"],
                "logo": {
                    "@type": "ImageObject",
                    "url": SITE["site"]["base_url"].rstrip("/") + SITE["site"]["logo"],
                },
            },
            "image": SITE["site"]["base_url"].rstrip("/") + post["image"],
            "mainEntityOfPage": canonical,
            "inLanguage": lang,
        },
        ensure_ascii=False,
    )
    content = post["content"]
    content = re.sub(r"<h1([^>]*)>", r"<h2\1>", content, flags=re.I)
    content = re.sub(r"</h1>", "</h2>", content, flags=re.I)
    related = [item for item in blog_posts(lang) if item["slug"] != slug][:3]
    related_copy = {
        "es": {"eyebrow": "Related", "heading": "Lecturas relacionadas", "cta_heading": "Ordenemos tu sistema de crecimiento"},
        "en": {"eyebrow": "Related", "heading": "Related reading", "cta_heading": "Build the system behind your growth"},
        "fr": {"eyebrow": "Related", "heading": "Lectures associées", "cta_heading": "Construisez le système derrière votre croissance"},
    }[lang]
    article_meta = f'{post["author"]} · {format_blog_date(post["date"], lang)} · {reading_time_copy(post["reading_time"], lang)}'
    body = f'''
    <article class="article-shell">
      <p class="eyebrow">{esc(post["category"])}</p>
      <h1>{esc(title)}</h1>
      <p class="lead">{esc(post["excerpt"])}</p>
      <p><small>{esc(article_meta)}</small></p>
      <img src="{post["image"]}" alt="{esc(post["alt"])}" loading="eager" style="border-radius:28px;border:1px solid var(--color-border);margin:2rem 0;">
      <div class="article-content">{content}</div>
    </article>
    <section class="section"><div class="container wide"><div class="section-heading"><p class="eyebrow">{esc(related_copy["eyebrow"])}</p><h2>{esc(related_copy["heading"])}</h2></div>{blog_cards(len(related), lang, related)}</div></section>
    {render_template(partial("cta/cta-primary.html"), {"heading": esc(related_copy["cta_heading"]), "href": page_url("contact-consult", lang), "label": esc(NAV["ui"][lang]["footer_cta"])})}
    {newsletter_modal(lang, f"article:{slug}")}
    '''
    head_tags = f'''
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="{esc(theme_by_id().get("theme_color", "#08151D"))}">
    <title>{esc(title)} | Rotata</title><meta name="description" content="{esc(description)}">
    <link rel="canonical" href="{canonical}">
    {alternates}
    <meta property="og:type" content="article"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:image" content="{SITE["site"]["base_url"].rstrip()}{post["image"]}"><meta property="og:url" content="{canonical}">
    <meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(description)}"><meta name="twitter:image" content="{SITE["site"]["base_url"].rstrip()}{post["image"]}">
    <link rel="icon" href="/assets/logo/rotata-favicon.png"><link rel="apple-touch-icon" href="/assets/logo/rotata-apple-touch-icon.png">
    <script>
    (() => {{
      try {{
        const theme = localStorage.getItem("rotata-design-theme");
        const surface = localStorage.getItem("rotata-design-surface");
        const color = localStorage.getItem("rotata-design-theme-color");
        if (theme) document.documentElement.dataset.designTheme = theme;
        if (surface) document.documentElement.dataset.themeSurface = surface;
        if (color) {{
          const meta = document.querySelector('meta[name="theme-color"]');
          if (meta) meta.setAttribute("content", color);
        }}
      }} catch (error) {{}}
    }})();
    </script>
    <link rel="stylesheet" href="/styles/global.css">
    <script>window.ROTATA_CONFIG = {json.dumps(runtime_config())};</script><script type="application/ld+json">{schema}</script>
    '''
    default_theme = theme_by_id()
    return f'<!doctype html><html lang="{lang}" data-design-theme="{esc(default_theme["id"])}" data-theme-surface="{esc(default_theme.get("surface", "dark"))}"><head>{head_tags}</head><body class="page page-article">{header(lang, "insights-blog", article_language_urls(slug))}<main id="main" class="site-main">{body}</main>{footer(lang)}{widgets(lang)}{cookie_banner(lang)}<script type="module" src="/scripts/global.js"></script></body></html>'


def showcase_cta_href(translation: dict, lang: str, url_key: str, page_key_key: str, default_page: str) -> str:
    explicit_url = translation.get(url_key)
    if explicit_url:
        return explicit_url
    target = translation.get(page_key_key, default_page)
    if isinstance(target, str) and (target.startswith("/") or target.startswith("#") or target.startswith("http")):
        return target
    return page_url(target, lang)


def showcase_switcher(current_id: str, lang: str, page_key: str = "home") -> str:
    label = {
        "es": "Conceptos web",
        "en": "Website concepts",
        "fr": "Concepts web",
    }[lang]
    items = []
    for site in showcase_sites():
        swatches = site.get("swatch") or []
        style = "".join(
            [
                f"--a:{swatches[0]};" if len(swatches) > 0 else "",
                f"--b:{swatches[1]};" if len(swatches) > 1 else "",
                f"--c:{swatches[2]};" if len(swatches) > 2 else "",
            ]
        )
        current = ' aria-current="page"' if site["id"] == current_id else ""
        items.append(
            f'<a href="{showcase_url(site["id"], lang, page_key)}"{current} style="{esc(style)}">'
            '<i class="concept-swatch" aria-hidden="true"></i>'
            f'{esc(localized(site.get("label", site["id"]), lang, site["id"]))}'
            "</a>"
        )
    return f'<nav class="concept-switcher" aria-label="{esc(label)}"><span>{esc(label)}</span>{"".join(items)}</nav>'


def showcase_nav(lang: str, site_id: str, current_page: str) -> str:
    groups = ["home", "about", "solutions", "services", "system", "partners", "insights", "contact", "legal"]
    current_group = page_meta(current_page).get("group", "")
    items = []
    for group_key in groups:
        if group_key == "legal":
            parent_page = "legal"
            children = ["legal-privacy", "legal", "legal-cookies", "legal-accessibility", "legal-sitemap", "legal-robots"]
            label = page_label("legal", lang)
        elif group_key == "home":
            parent_page = "home"
            children = []
            label = page_label("home", lang)
        else:
            group = NAV["groups"][group_key]
            parent_page = group["page"]
            children = group.get("children", [])
            label = localized(group["label"], lang, group_key)
        current_attr = ' aria-current="page"' if current_page == parent_page else ""
        if not children:
            items.append(f'<a class="concept-nav-link" href="{showcase_url(site_id, lang, parent_page)}"{current_attr}>{esc(label)}</a>')
            continue
        open_class = " is-current" if current_group == group_key or current_page == parent_page or current_page in children else ""
        child_links = "".join(
            f'<a href="{showcase_url(site_id, lang, child)}"' + (' aria-current="page"' if child == current_page else "") + f'>{esc(page_label(child, lang, "dropdown_label"))}</a>'
            for child in children
        )
        items.append(
            f'<div class="concept-nav-group{open_class}">'
            f'<a class="concept-nav-link" href="{showcase_url(site_id, lang, parent_page)}"{current_attr}>{esc(label)}</a>'
            f'<div class="concept-nav-menu">{child_links}</div>'
            "</div>"
        )
    return "".join(items)


def showcase_mobile_nav(lang: str, site_id: str, current_page: str) -> str:
    groups = ["home", "about", "solutions", "services", "system", "partners", "insights", "contact", "legal"]
    blocks = []
    for group_key in groups:
        if group_key == "legal":
            parent_page = "legal"
            children = ["legal-privacy", "legal", "legal-cookies", "legal-accessibility", "legal-sitemap", "legal-robots"]
            label = page_label("legal", lang)
        elif group_key == "home":
            parent_page = "home"
            children = []
            label = page_label("home", lang)
        else:
            group = NAV["groups"][group_key]
            parent_page = group["page"]
            children = group.get("children", [])
            label = localized(group["label"], lang, group_key)
        if children:
            links = "".join(
                f'<a href="{showcase_url(site_id, lang, child)}"' + (' aria-current="page"' if child == current_page else "") + f'>{esc(page_label(child, lang, "dropdown_label"))}</a>'
                for child in children
            )
            open_attr = " open" if current_page == parent_page or current_page in children else ""
            blocks.append(f'<details{open_attr}><summary>{esc(label)}</summary>{links}</details>')
        else:
            current_attr = ' aria-current="page"' if current_page == parent_page else ""
            blocks.append(f'<a href="{showcase_url(site_id, lang, parent_page)}"{current_attr}>{esc(label)}</a>')
    close_label = {"es": "Cerrar", "en": "Close", "fr": "Fermer"}[lang]
    return (
        '<div class="concept-mobile-panel" data-concept-mobile hidden>'
        f'<button class="concept-mobile-close" type="button" data-concept-menu-close>{esc(close_label)}</button>'
        f'<nav>{"".join(blocks)}</nav>'
        "</div>"
    )


def showcase_menu_button(lang: str) -> str:
    label = {"es": "Menú", "en": "Menu", "fr": "Menu"}[lang]
    return f'<button class="concept-menu-button" type="button" data-concept-menu aria-expanded="false">{esc(label)}</button>'


def showcase_item_text(item) -> tuple[str, str]:
    if isinstance(item, dict):
        return str(item.get("title", "")), str(item.get("text", ""))
    return str(item), ""


def showcase_card(site_id: str, item, index: int, kind: str) -> str:
    title, text = showcase_item_text(item)
    body = f"<p>{esc(text)}</p>" if text else ""
    number = f"{index:02d}"
    if kind == "service":
        classes = {
            "databricks": "db-card",
            "datagrail": "dg-risk-card",
            "atlan": "at-market-card",
            "runpod": "rp-card",
            "vectara": "vc-agent",
        }
        prefix = f"<span>{number}</span>" if site_id == "atlan" else ""
        return f'<article class="{classes[site_id]}">{prefix}<strong>{esc(title)}</strong>{body}</article>'
    if kind == "grid":
        if site_id == "databricks":
            return f'<article class="db-feature"><span>{number}</span><p>{esc(title)}</p></article>'
        if site_id == "datagrail":
            return f'<article class="dg-control"><strong>{esc(title)}</strong>{body}</article>'
        if site_id == "atlan":
            return f'<article class="at-node" data-at-node><span>Node {number}</span><p>{esc(title)}</p></article>'
        if site_id == "runpod":
            return f'<article class="rp-feature"><strong>{esc(title)}</strong>{body}</article>'
        return f'<article class="vc-outcome"><strong>{esc(title)}</strong>{body}</article>'
    if kind == "metric":
        if site_id == "databricks":
            return f'<article class="db-metric"><span>{number}</span><p>{esc(title)}</p></article>'
        if site_id == "datagrail":
            return f'<article class="dg-control"><strong>{esc(title)}</strong>{body}</article>'
        if site_id == "atlan":
            return f'<article class="at-metric"><span>{number}</span><p>{esc(title)}</p></article>'
        if site_id == "runpod":
            return f'<article class="rp-metric"><strong>{esc(title)}</strong>{body}</article>'
        return f'<article class="vc-guardrail"><strong>{esc(title)}</strong>{body}</article>'
    if site_id == "runpod":
        return f'<article class="rp-flow-step"><strong>{number}</strong><p>{esc(title)}</p></article>'
    return f'<article class="dg-step"><strong>{number}</strong><p>{esc(title)}</p></article>'


def showcase_items(site_id: str, items, kind: str) -> str:
    return "".join(showcase_card(site_id, item, index, kind) for index, item in enumerate(items or [], start=1))


def showcase_partners(lang: str, limit: int = 8) -> str:
    return "".join(f'<span>{esc(localized(partner["name"], lang))}</span>' for partner in PARTNERS[:limit])


def showcase_resources(site_id: str, lang: str, limit: int = 3) -> str:
    class_name = {
        "databricks": "db-spotlight-card",
        "datagrail": "dg-proof-card",
        "atlan": "at-customer-card",
        "runpod": "rp-news-card",
        "vectara": "vc-deploy-card",
    }[site_id]
    items = []
    for post in blog_posts(lang)[:limit]:
        items.append(
            f'<article class="{class_name}">'
            f'<span>{esc(post.get("category", "Insight"))}</span>'
            f'<h3>{esc(post.get("title", ""))}</h3>'
            f'<p>{esc(post.get("excerpt", ""))}</p>'
            f'<a href="{article_url(post["slug"], lang)}">Read more</a>'
            "</article>"
        )
    return "".join(items)


def showcase_article_cards(site_id: str, lang: str, limit: int = 9) -> str:
    return showcase_resources(site_id, lang, limit)


def showcase_cases(site_id: str, lang: str) -> str:
    return "".join(
        f'<article class="concept-case-card">'
        f'<span>{esc(localized(case.get("industry", "Case"), lang, "Case"))}</span>'
        f'<h3>{esc(localized(case.get("name", ""), lang, ""))}</h3>'
        f'<p><strong>{esc({"es": "Problema", "en": "Problem", "fr": "Problème"}[lang])}:</strong> {esc(localized(case.get("problem", ""), lang, ""))}</p>'
        f'<p><strong>{esc({"es": "Sistema", "en": "System", "fr": "Système"}[lang])}:</strong> {esc(localized(case.get("system", ""), lang, ""))}</p>'
        f'<p><strong>{esc({"es": "Resultado", "en": "Result", "fr": "Résultat"}[lang])}:</strong> {esc(localized(case.get("result", ""), lang, ""))}</p>'
        "</article>"
        for case in CASES
    )


def showcase_partner_cards(site_id: str, lang: str) -> str:
    return "".join(
        f'<article class="concept-partner-card">'
        f'<h3>{esc(localized(partner.get("name", ""), lang, ""))}</h3>'
        f'<p>{esc(localized(partner.get("role", ""), lang, ""))}</p>'
        f'<a href="{showcase_url(site_id, lang, partner["page_key"])}">{esc({"es": "Ver encaje", "en": "View fit", "fr": "Voir le rôle"}[lang])}</a>'
        "</article>"
        for partner in PARTNERS
        if partner.get("page_key")
    )


def showcase_contact_panel(site_id: str, lang: str, page_key: str) -> str:
    labels = FORMS["labels"][lang]
    service_options = "".join(f'<option value="{esc(item)}">{esc(item)}</option>' for item in FORMS["service_interests"])
    return f'''
    <section class="concept-special concept-contact-panel">
      <div>
        <p class="concept-kicker">{esc({"es": "Consulta", "en": "Consult", "fr": "Consultation"}[lang])}</p>
        <h2>{esc({"es": "Cuéntanos qué parte del sistema no está funcionando.", "en": "Tell us which part of the system is not working.", "fr": "Dites-nous quelle partie du système ne fonctionne pas."}[lang])}</h2>
        <p>{esc({"es": "Revisamos contexto, CRM, datos, señales y proceso comercial antes de recomendar trabajo.", "en": "We review context, CRM, data, signals and commercial process before recommending work.", "fr": "Nous examinons le contexte, le CRM, les données, les signaux et le processus commercial avant de recommander un travail."}[lang])}</p>
      </div>
      <form class="concept-form" action="{page_url("contact-consult", lang)}" method="get">
        <div class="concept-form-grid">
          <label>{esc(labels["first_name"])}<input name="first_name" autocomplete="given-name" required></label>
          <label>{esc(labels["last_name"])}<input name="last_name" autocomplete="family-name" required></label>
          <label>{esc(labels["email"])}<input name="email" type="email" autocomplete="email" required></label>
          <label>{esc(labels["company"])}<input name="company" autocomplete="organization" required></label>
        </div>
        <label>{esc(labels["service"])}<select name="service_interest" required>{service_options}</select></label>
        <label>{esc(labels["message"])}<textarea name="message" required></textarea></label>
        <button type="submit">{esc(labels["submit"])}</button>
      </form>
    </section>'''


def showcase_roi_panel(lang: str) -> str:
    labels = {
        "es": ["Leads mensuales", "Conversión a oportunidad (%)", "Valor medio (€)", "Mejora esperada (%)", "Valor incremental estimado"],
        "en": ["Monthly leads", "Opportunity conversion (%)", "Average value (€)", "Expected improvement (%)", "Estimated incremental value"],
        "fr": ["Leads mensuels", "Conversion opportunité (%)", "Valeur moyenne (€)", "Amélioration attendue (%)", "Valeur incrémentale estimée"],
    }[lang]
    return f'''
    <section class="concept-special concept-roi-panel">
      <div>
        <p class="concept-kicker">ROI</p>
        <h2>{esc(labels[4])}</h2>
        <strong class="concept-roi-output">€0</strong>
      </div>
      <form class="concept-form" data-concept-roi>
        <label>{esc(labels[0])}<input type="number" name="monthly_leads" value="120" min="0"></label>
        <label>{esc(labels[1])}<input type="number" name="conversion_rate" value="8" min="0" max="100"></label>
        <label>{esc(labels[2])}<input type="number" name="average_value" value="12000" min="0"></label>
        <label>{esc(labels[3])}<input type="number" name="system_improvement" value="20" min="0" max="100"></label>
      </form>
    </section>'''


def showcase_footer_columns(lang: str) -> str:
    columns = []
    for column in NAV["footer_columns"][:4]:
        links = "".join(
            f'<a href="{page_url(item, lang)}">{esc(page_label(item, lang, "footer_label"))}</a>'
            for item in column["items"][:5]
        )
        columns.append(
            f'<section><h2>{esc(localized(column["title"], lang))}</h2><nav>{links}</nav></section>'
        )
    return "".join(columns)


SITE_PREFIX = {
    "databricks": "db",
    "datagrail": "dg",
    "atlan": "at",
    "runpod": "rp",
    "vectara": "vc",
}


def showcase_header(site: dict, lang: str, page_key: str) -> str:
    prefix = SITE_PREFIX[site["id"]]
    contact = showcase_url(site["id"], lang, "contact-consult")
    action_labels = {
        "databricks": ("Login", "Try Rotata"),
        "datagrail": ("Contact Us", "Get a demo"),
        "atlan": ("Talk to Us", "Book a Demo"),
        "runpod": ("Contact Sales", "Sign Up"),
        "vectara": ("Log in", "Book a demo"),
    }[site["id"]]
    top = ""
    if site["id"] == "datagrail":
        top = '<div class="dg-announcement">Introducing Vera for Rotata: a human-governed system agent. <a href="#main">Learn more.</a></div>'
    elif site["id"] == "runpod":
        top = '<div class="rp-topline">Rotata x system operators: pipeline infrastructure challenge is live <a href="#main">Read more</a></div>'
    elif site["id"] == "vectara":
        top = '<div class="vc-blog-strip">Read more about how Rotata is pioneering system engineering. <a href="#main">Read the blog</a></div>'
    return (
        top
        + f'<header class="{prefix}-header concept-site-header">'
        + f'<a class="{prefix}-brand" href="{showcase_url(site["id"], lang)}" aria-label="Rotata home">{theme_logo_markup(154, 40)}</a>'
        + f'<nav class="{prefix}-nav" aria-label="Rotata concept navigation">{showcase_nav(lang, site["id"], page_key)}</nav>'
        + showcase_menu_button(lang)
        + f'<div class="concept-actions"><a href="{contact}">{esc(action_labels[0])}</a><a href="{contact}">{esc(action_labels[1])}</a></div>'
        + "</header>"
        + showcase_mobile_nav(lang, site["id"], page_key)
    )


def showcase_footer(site: dict, lang: str) -> str:
    prefix = SITE_PREFIX[site["id"]]
    intro = page_payload("home", lang)["translation"].get("intro", SITE["site"]["name"])
    return (
        f'<footer class="{prefix}-footer concept-site-footer" id="footer">'
        f'<div>{theme_logo_markup(154, 40)}<p>{esc(intro)}</p></div>'
        f'<div class="concept-footer-grid">{showcase_footer_columns(lang)}</div>'
        "</footer>"
    )


def showcase_page_asset(site_id: str, page_key: str) -> str:
    group = page_meta(page_key).get("group") or "home"
    exact = f"/assets/theme-sites/{site_id}-{page_key}.webp"
    if (SRC / exact.lstrip("/")).exists():
        return exact
    candidate = f"/assets/theme-sites/{site_id}-{group}.webp"
    if (SRC / candidate.lstrip("/")).exists():
        return candidate
    return showcase_by_id(site_id)["asset"]


def showcase_section_asset(site_id: str, page_key: str, index: int) -> str:
    exact = f"/assets/theme-sites/{site_id}-{page_key}-{index + 1:02d}.webp"
    if (SRC / exact.lstrip("/")).exists():
        return exact
    return showcase_page_asset(site_id, page_key)


def showcase_section_items(site_id: str, section: dict, variant: str) -> str:
    if variant == "partners":
        return showcase_partner_cards(site_id, CURRENT_LANG)
    if variant == "blog-preview":
        return showcase_resources(site_id, CURRENT_LANG)
    items = section.get("items", [])
    if not items:
        return ""
    if variant == "process":
        return '<div class="concept-process-list">' + showcase_items(site_id, items, "process") + "</div>"
    if variant == "metrics":
        return '<div class="concept-metric-grid">' + showcase_items(site_id, items, "metric") + "</div>"
    kind = "service" if all(isinstance(item, dict) for item in items or []) else "grid"
    return '<div class="concept-card-grid">' + showcase_items(site_id, items, kind) + "</div>"


def showcase_content_section(site_id: str, page_key: str, section: dict, index: int) -> str:
    variant = section.get("variant", "text")
    eyebrow = {
        "es": {
            "problem": "Fricción",
            "cards": "Capa del sistema",
            "grid": "Modelo operativo",
            "process": "Proceso",
            "metrics": "Prueba",
            "partners": "Ecosistema",
            "blog-preview": "Insights",
            "text": "Contexto",
        },
        "en": {
            "problem": "Friction",
            "cards": "System layer",
            "grid": "Operating model",
            "process": "Process",
            "metrics": "Proof",
            "partners": "Ecosystem",
            "blog-preview": "Insights",
            "text": "Context",
        },
        "fr": {
            "problem": "Friction",
            "cards": "Couche système",
            "grid": "Modèle opératoire",
            "process": "Processus",
            "metrics": "Preuve",
            "partners": "Écosystème",
            "blog-preview": "Insights",
            "text": "Contexte",
        },
    }[CURRENT_LANG].get(variant, "Rotata")
    body = showcase_section_items(site_id, section, variant)
    visual = showcase_section_asset(site_id, page_key, index)
    return f'''
    <section class="concept-section concept-section-{esc(variant)}" id="section-{index + 1:02d}">
      <div class="concept-section-shell{' is-reversed' if index % 2 else ''}">
        <div class="concept-section-copy">
          <div class="concept-section-head">
            <span>{index + 1:02d}</span>
            <p class="concept-kicker">{esc(eyebrow)}</p>
            <h2>{esc(section.get("heading", ""))}</h2>
            <p>{esc(section.get("body", ""))}</p>
          </div>
          {body}
        </div>
        <figure class="concept-section-visual" aria-hidden="true">
          <img src="{esc(visual)}" alt="" loading="lazy" width="1600" height="1000">
          <figcaption><span>{index + 1:02d}</span><strong>{esc(section.get("heading", ""))}</strong></figcaption>
        </figure>
      </div>
    </section>'''


def showcase_special_block(site_id: str, page_key: str, lang: str, render_type: str) -> str:
    if render_type == "blog":
        title = {"es": "Artículos recientes", "en": "Recent articles", "fr": "Articles récents"}[lang]
        return f'<section class="concept-special concept-blog-grid"><h2>{esc(title)}</h2><div>{showcase_article_cards(site_id, lang, 9)}</div></section>'
    if render_type == "roi":
        return showcase_roi_panel(lang)
    if render_type == "contact":
        return showcase_contact_panel(site_id, lang, page_key)
    if render_type == "cases":
        return f'<section class="concept-special concept-cases-grid"><h2>Case grid</h2><div>{showcase_cases(site_id, lang)}</div></section>'
    if page_key == "partners":
        return f'<section class="concept-special concept-partner-grid"><h2>Partner roles</h2><div>{showcase_partner_cards(site_id, lang)}</div></section>'
    return ""


def showcase_detail_page(lang: str, site: dict, page_key: str) -> str:
    payload = page_payload(page_key, lang)
    translation = payload["translation"]
    prefix = SITE_PREFIX[site["id"]]
    primary_href = showcase_url(site["id"], lang, translation.get("primary_cta_page", "contact-consult") if not translation.get("primary_cta_url") else "contact-consult")
    secondary_target = translation.get("secondary_cta_page", "solutions")
    secondary_href = showcase_url(site["id"], lang, secondary_target if secondary_target in PAGE_DEFS else "solutions")
    sections = "".join(showcase_content_section(site["id"], page_key, section, index) for index, section in enumerate(translation.get("sections", [])))
    special = showcase_special_block(site["id"], page_key, lang, payload["render"])
    final_label = NAV["ui"][lang]["footer_cta"]
    return f'''
      {showcase_header(site, lang, page_key)}
      {showcase_switcher(site["id"], lang, page_key)}
      <main id="main" class="concept-page concept-page-{esc(site["id"])} {prefix}-detail concept-group-{esc(payload.get("group", "home"))}">
        <section class="concept-page-hero" style="--hero-bg:url('{esc(showcase_page_asset(site["id"], page_key))}')">
          <div class="concept-hero-copy">
            <p class="concept-kicker">{esc(translation.get("eyebrow", page_label(page_key, lang)))}</p>
            <h1>{esc(translation.get("h1", ""))}</h1>
            <p>{esc(translation.get("intro", ""))}</p>
            <div class="concept-hero-actions">
              <a href="{primary_href}">{esc(translation.get("primary_cta", NAV["ui"][lang]["header_cta"]))}</a>
              <a href="{secondary_href}">{esc(translation.get("secondary_cta", page_label("solutions", lang)))}</a>
            </div>
          </div>
          <figure class="concept-hero-visual" aria-hidden="true">
            <img src="{esc(showcase_page_asset(site["id"], page_key))}" alt="" loading="eager" width="1600" height="1000">
            <figcaption><span>{esc(page_label(page_key, lang))}</span><strong>{esc(localized(site.get("label", site["id"]), lang, site["id"]))}</strong></figcaption>
          </figure>
        </section>
        {sections}
        {special}
        <section class="concept-final-cta">
          <h2>{esc(translation.get("final_cta", page_payload("home", lang)["translation"].get("final_cta", "")))}</h2>
          <a href="{showcase_url(site["id"], lang, "contact-consult")}">{esc(final_label)}</a>
        </section>
      </main>
      {showcase_footer(site, lang)}
    '''


def showcase_section(sections: list[dict], index: int) -> dict:
    if index < len(sections):
        return sections[index]
    return {"heading": "", "body": "", "items": []}


def showcase_mapping(lang: str, site: dict) -> dict[str, str]:
    translation = page_payload("home", lang)["translation"]
    sections = translation.get("sections", [])
    problem = showcase_section(sections, 0)
    overview = showcase_section(sections, 1)
    pillars = showcase_section(sections, 2)
    services = showcase_section(sections, 3)
    process = showcase_section(sections, 4)
    proof = showcase_section(sections, 5)
    roi = showcase_section(sections, 7)
    return {
        "home_url": page_url("home", lang),
        "logo_markup": theme_logo_markup(154, 40),
        "concept_nav": showcase_nav(lang, site["id"], "home"),
        "concept_menu_button": showcase_menu_button(lang),
        "concept_mobile_nav": showcase_mobile_nav(lang, site["id"], "home"),
        "showcase_switcher": showcase_switcher(site["id"], lang, "home"),
        "asset": esc(showcase_page_asset(site["id"], "home")),
        "contact_href": page_url("contact-consult", lang),
        "primary_href": showcase_cta_href(translation, lang, "primary_cta_url", "primary_cta_page", "contact-consult"),
        "primary_label": esc(translation.get("primary_cta", NAV["ui"][lang]["header_cta"])),
        "secondary_label": esc(translation.get("secondary_cta", page_label("solutions", lang))),
        "eyebrow": esc(translation.get("eyebrow", "")),
        "h1": esc(translation.get("h1", "")),
        "intro": esc(translation.get("intro", "")),
        "final_cta": esc(translation.get("final_cta", "")),
        "section_one_heading": esc(problem.get("heading", "")),
        "section_one_body": esc(problem.get("body", "")),
        "section_two_heading": esc(pillars.get("heading", "")),
        "section_two_body": esc(pillars.get("body", "")),
        "section_three_heading": esc(overview.get("heading", "")),
        "section_three_body": esc(overview.get("body", "")),
        "section_four_heading": esc(process.get("heading", "")),
        "section_four_body": esc(process.get("body", "")),
        "section_five_heading": esc(proof.get("heading", "")),
        "section_five_body": esc(proof.get("body", "")),
        "section_six_heading": esc(services.get("heading", "")),
        "section_six_body": esc(services.get("body", "")),
        "section_eight_heading": esc(roi.get("heading", "")),
        "section_eight_body": esc(roi.get("body", "")),
        "service_cards": showcase_items(site["id"], pillars.get("items", []), "service"),
        "grid_items": showcase_items(site["id"], overview.get("items", []), "grid"),
        "service_grid_items": showcase_items(site["id"], services.get("items", []), "grid"),
        "process_items": showcase_items(site["id"], process.get("items", []), "process"),
        "metrics": showcase_items(site["id"], proof.get("items", []), "metric"),
        "roi_items": showcase_items(site["id"], roi.get("items", []), "metric"),
        "partners": showcase_partners(lang),
        "resource_cards": showcase_resources(site["id"], lang),
        "footer_columns": showcase_footer_columns(lang),
        "footer_summary": esc(translation.get("intro", SITE["site"]["name"])),
        "linkedin": esc(SITE["site"].get("linkedin", "")),
        "email": esc(SITE["site"].get("email", "")),
        "phone": esc(SITE["site"].get("phone", "")),
    }


def showcase_schema(lang: str, site: dict, page_key: str, title: str, description: str, url: str) -> str:
    base = SITE["site"]["base_url"].rstrip("/")
    payload = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": f"{base}/#organization",
                "name": SITE["site"]["company"],
                "url": base,
                "logo": base + SITE["site"]["logo"],
                "sameAs": [SITE["site"]["linkedin"]],
            },
            {
                "@type": "WebPage",
                "@id": base + url,
                "url": base + url,
                "name": title,
                "description": description,
                "isPartOf": {"@id": f"{base}/#website"},
                "inLanguage": lang,
                "about": f"Rotata B2B growth system website concept: {page_label(page_key, lang)}",
                "citation": site.get("reference_url", ""),
            },
        ],
    }
    return json.dumps(payload, ensure_ascii=False)


def showcase_head(lang: str, site: dict, page_key: str, title: str, description: str, url: str) -> str:
    canonical = SITE["site"]["base_url"].rstrip("/") + url
    alternates = "".join(
        f'<link rel="alternate" hreflang="{code}" href="{SITE["site"]["base_url"].rstrip("/")}{showcase_url(site["id"], code, page_key)}">'
        for code in SITE["languages"]
    )
    return f'''
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="{esc(site.get("theme_color", "#08151D"))}">
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}">
    <link rel="canonical" href="{canonical}">
    {alternates}
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Rotata">
    <meta property="og:title" content="{esc(title)}">
    <meta property="og:description" content="{esc(description)}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:image" content="{SITE["site"]["base_url"].rstrip()}{showcase_page_asset(site["id"], page_key)}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{esc(title)}">
    <meta name="twitter:description" content="{esc(description)}">
    <meta name="twitter:image" content="{SITE["site"]["base_url"].rstrip()}{showcase_page_asset(site["id"], page_key)}">
    <link rel="icon" href="/assets/logo/rotata-favicon.png">
    <link rel="apple-touch-icon" href="/assets/logo/rotata-apple-touch-icon.png">
    <link rel="stylesheet" href="{esc(site["stylesheet"])}">
    <link rel="stylesheet" href="/styles/theme-sites/shared-pages.css">
    <script type="application/ld+json">{showcase_schema(lang, site, page_key, title, description, url)}</script>
    '''


def showcase_page(lang: str, site_id: str, page_key: str = "home") -> str:
    global CURRENT_LANG
    CURRENT_LANG = lang
    site = showcase_by_id(site_id)
    translation = page_payload(page_key, lang)["translation"]
    label = localized(site.get("label", site["id"]), lang, site["id"])
    summary = localized(site.get("summary", ""), lang, "")
    title = f"Rotata {label} concept | {translation['title']}"
    description = f"{summary} {translation['description']}".strip()
    url = showcase_url(site["id"], lang, page_key)
    if page_key == "home":
        body = render_template(partial(f"theme-sites/{site['id']}.html"), showcase_mapping(lang, site))
    else:
        body = showcase_detail_page(lang, site, page_key)
    return f'''<!doctype html>
    <html lang="{lang}" class="showcase showcase-{esc(site["id"])}" data-showcase-site="{esc(site["id"])}" data-theme-surface="{esc(site.get("surface", "light"))}">
    <head>{showcase_head(lang, site, page_key, title, description, url)}</head>
    <body>{body}<script type="module" src="{esc(site["script"])}"></script></body>
    </html>'''

def write_page(url: str, content: str) -> None:
    path = output_path(url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(re.sub(r"\n\s+", "\n", content).strip() + "\n", encoding="utf-8")

def copy_static() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    for folder in ["assets", "styles", "scripts"]:
        shutil.copytree(SRC / folder, DIST / folder)
    public = ROOT / "public"
    if public.exists():
        for item in public.iterdir():
            if item.is_file():
                shutil.copy2(item, DIST / item.name)


def write_redirects() -> None:
    redirects = set()
    for page_key, meta in PAGE_DEFS.items():
        for legacy in meta.get("legacy_source_pages", []):
            for lang in SITE["languages"]:
                old_url = legacy_page_url(legacy, lang)
                new_url = page_url(page_key, lang)
                if old_url != new_url:
                    redirects.add(f"{old_url} {new_url} 301")
    for post in BLOG:
        old_url = f'/blog/{post["slug"]}/'
        new_url = article_url(post["slug"])
        if old_url != new_url:
            redirects.add(f"{old_url} {new_url} 301")
    if redirects:
        (DIST / "_redirects").write_text("\n".join(sorted(redirects)) + "\n", encoding="utf-8")

def main() -> None:
    copy_static()
    for lang in SITE["languages"]:
        for page_key in PAGE_DEFS:
            if page_key == "404":
                continue
            if page_payload(page_key, lang)["render"] == "blog":
                html_out = blog_page(lang, page_key)
            else:
                html_out = standard_page(lang, page_key)
            write_page(page_url(page_key, lang), html_out)
    for lang in SITE["languages"]:
        for post in BLOG:
            write_page(article_url(post["slug"], lang), article_page(post["slug"], lang))
    for lang in SITE["languages"]:
        for site in showcase_sites():
            for page_key in PAGE_DEFS:
                if page_key == "404":
                    continue
                write_page(showcase_url(site["id"], lang, page_key), showcase_page(lang, site["id"], page_key))
    for lang in SITE["languages"]:
        write_page(page_url("404", lang), standard_page(lang, "404"))
    shutil.copy2(output_path("/404/"), DIST / "404.html")
    write_redirects()
    (DIST / "_headers").write_text("/*\n  X-Frame-Options: SAMEORIGIN\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n", encoding="utf-8")
    print(f"Built {DIST}")

if __name__ == "__main__":
    CURRENT_LANG = "es"
    main()
