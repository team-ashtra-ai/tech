#!/usr/bin/env python3
# Build the Rotata static site into dist/.
from __future__ import annotations

import html
import json
import os
import re
import shutil
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

def esc(value: str) -> str:
    return html.escape(str(value or ""), quote=True)

def partial(path: str) -> str:
    return (SRC / "partials" / path).read_text(encoding="utf-8")

def render_template(template: str, mapping: dict[str, str]) -> str:
    for key, value in mapping.items():
        template = template.replace("{{" + key + "}}", value)
    return re.sub(r"{{[^}]+}}", "", template)

def page_url(page_key: str, lang: str) -> str:
    route = SITE["pages"][page_key]["routes"][lang]
    prefix = SITE["languages"][lang]["prefix"]
    pieces = [piece for piece in [prefix, route] if piece]
    return "/" + "/".join(pieces) + ("/" if pieces else "")

def article_url(slug: str) -> str:
    return f"/blog/{slug}/"

def output_path(url: str) -> Path:
    clean = url.strip("/")
    if not clean:
        return DIST / "index.html"
    return DIST / clean / "index.html"

def nav_links(lang: str, current: str, mobile: bool = False) -> str:
    links = []
    for item in NAV[lang]["items"]:
        href = page_url(item["page"], lang)
        current_attr = ' aria-current="page"' if item["page"] == current else ""
        links.append(f'<a href="{href}"{current_attr}>{esc(item["label"])}</a>')
    if mobile:
        cta = page_url("contact", lang)
        links.append(f'<a class="btn btn-primary" data-track="cta_click" href="{cta}">{esc(NAV[lang]["primary_cta"])}</a>')
    return "".join(links)

def language_switcher(lang: str, page_key: str) -> str:
    items = []
    for code, meta in SITE["languages"].items():
        href = page_url(page_key, code) if page_key in SITE["pages"] else page_url("home", code)
        current = ' aria-current="true"' if code == lang else ""
        items.append(f'<a href="{href}" data-language-link="{code}"{current}>{code}</a>')
    return render_template(partial("language/language-switcher.html"), {"items": "".join(items)})

def header(lang: str, page_key: str) -> str:
    ui = {
        "es": {
            "skip": "Saltar al contenido",
            "home": "Inicio de Rotata",
            "theme": "Cambiar modo claro y oscuro",
            "theme_mode": "Dark",
            "utility": "Sistemas B2B con CRM, datos, automatización y pipeline",
            "close": "Cerrar menú",
        },
        "en": {
            "skip": "Skip to content",
            "home": "Rotata home",
            "theme": "Toggle dark and light mode",
            "theme_mode": "Dark",
            "utility": "B2B systems with CRM, data, automation and pipeline",
            "close": "Close menu",
        },
        "fr": {
            "skip": "Aller au contenu",
            "home": "Accueil Rotata",
            "theme": "Changer le mode clair et sombre",
            "theme_mode": "Dark",
            "utility": "Systèmes B2B avec CRM, données, automatisation et pipeline",
            "close": "Fermer le menu",
        },
    }[lang]
    desktop = render_template(partial("navigation/nav-desktop.html"), {"items": nav_links(lang, page_key)})
    mobile = render_template(partial("header/header-mobile.html"), {
        "items": render_template(partial("navigation/nav-mobile.html"), {"items": nav_links(lang, page_key, True)}),
        "close_label": ui["close"],
    })
    return render_template(partial("header/header.html"), {
        "skip_label": ui["skip"],
        "home_label": ui["home"],
        "theme_label": ui["theme"],
        "theme_mode_label": ui["theme_mode"],
        "utility_label": ui["utility"],
        "home_url": page_url("home", lang),
        "logo": SITE["site"]["logo"],
        "nav_desktop": desktop,
        "nav_mobile": mobile,
        "language_switcher": language_switcher(lang, page_key),
        "cta_url": page_url("contact", lang),
        "cta_label": NAV[lang]["primary_cta"],
    })

def footer(lang: str) -> str:
    footer_items = "".join(f'<a href="{page_url(item["page"], lang)}">{esc(item["label"])}</a>' for item in NAV[lang]["items"])
    legal_labels = {
        "es": [("privacy", "Privacidad"), ("legal", "Legal"), ("cookies", "Cookies"), ("accessibility", "Accesibilidad"), ("sitemap", "Mapa del sitio")],
        "en": [("privacy", "Privacy"), ("legal", "Legal"), ("cookies", "Cookies"), ("accessibility", "Accessibility"), ("sitemap", "Sitemap")],
        "fr": [("privacy", "Confidentialité"), ("legal", "Mentions légales"), ("cookies", "Cookies"), ("accessibility", "Accessibilité"), ("sitemap", "Plan du site")],
    }[lang]
    legal = "".join(f'<a href="{page_url(key, lang)}">{label}</a>' for key, label in legal_labels)
    funding_text = {
        "es": "Programa Kit Digital y financiación europea, conservado desde el sitio original de Rotata.",
        "en": "Kit Digital and European funding area, preserved from the original Rotata site.",
        "fr": "Espace Kit Digital et financement européen, conservé depuis le site original de Rotata.",
    }[lang]
    funding_strip = (
        '<div class="container funding-strip">'
        '<img src="/assets/partners/rotata-kit-digital-eu-funding.png" '
        'alt="Kit Digital, Gobierno de España, Red.es, Next Generation EU y Plan de Recuperación">'
        f"<span>{esc(funding_text)}</span>"
        "</div>"
    )
    return render_template(partial("footer/footer.html"), {
        "logo_white": SITE["site"]["logo_white"],
        "positioning": {"es": "El sistema detrás del crecimiento B2B.", "en": "The system behind B2B growth.", "fr": "Le système derrière la croissance B2B."}[lang],
        "language_switcher": language_switcher(lang, "home"),
        "footer_links": render_template(partial("footer/footer-links.html"), {"items": footer_items}),
        "contact_title": {"es": "Contacto", "en": "Contact", "fr": "Contact"}[lang],
        "funding_strip": funding_strip,
        "footer_legal": render_template(partial("footer/footer-legal.html"), {"year": str(datetime.now().year), "links": legal}),
    })

def cookie_banner(lang: str) -> str:
    data = COOKIE[lang]
    categories = []
    for key, label in data["categories"].items():
        checked = " checked disabled" if key == "necessary" else ""
        categories.append(f'<label><input type="checkbox" value="{key}" data-cookie-category{checked}> {esc(label)}</label>')
    return render_template(partial("cookie/cookie-consent.html"), {
        "title": esc(data["title"]),
        "body": esc(data["body"]),
        "accept": esc(data["accept"]),
        "reject": esc(data["reject"]),
        "manage": esc(data["manage"]),
        "save": esc(data["save"]),
        "categories": "".join(categories),
    })

def schema_for(page_key: str, lang: str, title: str, description: str, url: str) -> str:
    base = SITE["site"]["base_url"].rstrip("/")
    graph = [
        {"@type": "Organization", "@id": f"{base}/#organization", "name": SITE["site"]["company"], "url": base, "logo": base + SITE["site"]["logo"], "sameAs": [SITE["site"]["linkedin"]]},
        {"@type": "WebSite", "@id": f"{base}/#website", "url": base, "name": SITE["site"]["name"], "publisher": {"@id": f"{base}/#organization"}, "inLanguage": lang},
        {"@type": "WebPage", "@id": base + url, "url": base + url, "name": title, "description": description, "isPartOf": {"@id": f"{base}/#website"}, "inLanguage": lang},
    ]
    if page_key in {"solutions", "hubspot", "zoominfo", "outbound", "synapsale"}:
        graph.append({"@type": "Service", "name": title, "provider": {"@id": f"{base}/#organization"}, "areaServed": "Europe", "serviceType": SITE["pages"][page_key]["seo_keyword"]})
    if page_key in {"roi"}:
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
        if page_key in SITE["pages"]:
            alternates.append(f'<link rel="alternate" hreflang="{code}" href="{SITE["site"]["base_url"].rstrip()}{page_url(page_key, code)}">')
    config = {
        "ga4Id": os.getenv("PUBLIC_GA4_ID", ""),
        "gtmId": os.getenv("PUBLIC_GTM_ID", ""),
        "linkedinPartnerId": os.getenv("PUBLIC_LINKEDIN_PARTNER_ID", ""),
        "clarityId": os.getenv("PUBLIC_CLARITY_ID", ""),
        "hubspotPortalId": os.getenv("PUBLIC_HUBSPOT_PORTAL_ID", ""),
        "hubspotFormId": os.getenv("PUBLIC_HUBSPOT_FORM_ID", ""),
        "formsEndpoint": os.getenv("PUBLIC_FORMS_ENDPOINT", ""),
    }
    return f'''
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#08151D">
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
    <link rel="stylesheet" href="/styles/global.css">
    <script>window.ROTATA_CONFIG = {json.dumps(config)};</script>
    <script type="application/ld+json">{schema_for(page_key, lang, title, description, url)}</script>
    '''

def layout(lang: str, page_key: str, body: str) -> str:
    page = SITE["pages"][page_key]
    t = page["translations"][lang]
    url = page_url(page_key, lang)
    return f'''<!doctype html>
    <html lang="{lang}" data-theme="dark">
    <head>{head(lang, page_key, t["title"], t["description"], url)}</head>
    <body>
      {header(lang, page_key)}
      <main id="main">{body}</main>
      {footer(lang)}
      {widgets(lang)}
      {cookie_banner(lang)}
      <script type="module" src="/scripts/global.js"></script>
    </body>
    </html>'''

def hero(t: dict, page_key: str) -> str:
    visual_labels = {
        "es": [("Modelo de datos", "limpio"), ("Pipeline", "visible"), ("Automatización", "controlada")],
        "en": [("Data model", "clean"), ("Pipeline", "visible"), ("Automation", "controlled")],
        "fr": [("Modèle de données", "propre"), ("Pipeline", "visible"), ("Automatisation", "contrôlée")],
    }[CURRENT_LANG]
    visual = '''
    <div class="hero-visual" aria-hidden="true">
      <img src="/assets/diagrams/rotata-growth-system-overlay.svg" alt="">
      <div class="hero-panel">
        <div class="signal-row"><span>{}</span><strong>{}</strong></div>
        <div class="signal-row"><span>{}</span><strong>{}</strong></div>
        <div class="signal-row"><span>{}</span><strong>{}</strong></div>
      </div>
    </div>'''.format(*(esc(value) for pair in visual_labels for value in pair))
    if page_key == "home":
        media = (
            '<video autoplay muted loop playsinline poster="/assets/diagrams/rotata-growth-system-overlay.svg">'
            '<source src="/assets/video/rotata-ai-marketing-hero-video.mp4" type="video/mp4">'
            "</video>"
        )
    else:
        media = '<img src="/assets/diagrams/rotata-crm-architecture.svg" alt="">'
    return f'''
    <section class="hero hero-{esc(page_key)}">
      <div class="hero-media" aria-hidden="true">{media}</div>
      <div class="container hero-grid">
        <div class="hero-content" data-reveal>
          <p class="eyebrow">{esc(t["eyebrow"])}</p>
          <h1>{esc(t["h1"])}</h1>
          <p class="lead">{esc(t["intro"])}</p>
          <div class="button-row">
            <a class="btn btn-primary" data-track="cta_click" href="{page_url("contact", CURRENT_LANG)}">{esc(t.get("primary_cta", t.get("final_cta", "Contact")))}</a>
            <a class="btn btn-secondary" data-track="cta_click" href="{page_url("solutions", CURRENT_LANG)}">{esc(t.get("secondary_cta", "Solutions"))}</a>
          </div>
        </div>
        {visual}
      </div>
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
    roi = page_url("roi", lang)
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
        return '<ol class="timeline">' + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ol>"
    if all(isinstance(item, dict) for item in items):
        return '<div class="grid-4">' + "".join(render_template(partial("cards/service-card.html"), {"icon": "/assets/icons/rotata-system-icon.svg", "title": esc(item.get("title", "")), "text": esc(item.get("text", ""))}) for item in items) + "</div>"
    return '<ul class="pill-list">' + "".join(f"<li>{esc(item)}</li>" for item in items) + "</ul>"

def blog_cards(limit: int = 3) -> str:
    cards = []
    for post in BLOG[:limit]:
        cards.append(render_template(partial("cards/blog-card.html"), {
            "url": article_url(post["slug"]),
            "image": post["image"],
            "alt": esc(post["alt"]),
            "category": esc(post["category"]),
            "title": esc(post["title"]),
            "excerpt": esc(post["excerpt"]),
            "date": esc(post["date"]),
            "reading_time": str(post["reading_time"]),
        }))
    return '<div class="grid-3">' + "".join(cards) + "</div>"

def section_html(section: dict, index: int) -> str:
    variant = section.get("variant", "text")
    eyebrow_labels = {
        "es": {"problem": "Diagnóstico", "cards": "Sistema", "grid": "Arquitectura", "process": "Proceso", "metrics": "Medición", "partners": "Plataformas", "blog-preview": "Insights", "text": "Rotata"},
        "en": {"problem": "Diagnosis", "cards": "System", "grid": "Architecture", "process": "Process", "metrics": "Measurement", "partners": "Platforms", "blog-preview": "Insights", "text": "Rotata"},
        "fr": {"problem": "Diagnostic", "cards": "Système", "grid": "Architecture", "process": "Processus", "metrics": "Mesure", "partners": "Plateformes", "blog-preview": "Insights", "text": "Rotata"},
    }[CURRENT_LANG]
    if variant == "blog-preview":
        body = blog_cards(3)
    elif variant == "partners":
        partner_label = {"es": "Explorar", "en": "Explore", "fr": "Explorer"}[CURRENT_LANG]
        body = '<div class="grid-4">' + "".join(render_template(partial("cards/partner-card.html"), {"name": esc(p["name"]), "role": esc(p["role"]), "url": p["url"], "label": partner_label}) for p in PARTNERS) + "</div>"
    else:
        body = render_items(section.get("items", []), variant)
    band = " section-band" if index % 2 else ""
    return f'''
    <section class="section{band}" data-reveal>
      <div class="container {'wide' if variant in {'cards','partners','blog-preview'} else ''}">
        <div class="section-heading">
          <p class="eyebrow">{esc(eyebrow_labels.get(variant, "Rotata"))}</p>
          <h2>{esc(section.get("heading", ""))}</h2>
          <p class="lead">{esc(section.get("body", ""))}</p>
        </div>
        {body}
      </div>
    </section>'''

def standard_page(lang: str, page_key: str) -> str:
    global CURRENT_LANG
    CURRENT_LANG = lang
    t = SITE["pages"][page_key]["translations"][lang]
    body = hero(t, page_key)
    sections = t.get("sections", [])
    if page_key == "roi":
        for index, section in enumerate(sections[:2]):
            body += section_html(section, index)
        body += roi_calculator(lang)
        for index, section in enumerate(sections[2:], start=2):
            body += section_html(section, index)
    elif page_key == "contact":
        for index, section in enumerate(sections[:3]):
            body += section_html(section, index)
        body += contact_form(lang)
        for index, section in enumerate(sections[3:], start=3):
            body += section_html(section, index)
    elif page_key == "cases":
        body += case_grid()
        for index, section in enumerate(sections):
            body += section_html(section, index)
    else:
        for index, section in enumerate(sections):
            body += section_html(section, index)
    body += render_template(partial("cta/cta-primary.html"), {"heading": esc(t.get("final_cta", "")), "href": page_url("contact", lang), "label": esc(NAV[lang]["primary_cta"])})
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
    return f'<section class="section"><div class="container"><div class="glass-panel" style="padding:clamp(1.5rem,4vw,3rem)">{form}</div></div></section>'

def roi_calculator(lang: str) -> str:
    labels = {
        "es": ["Leads mensuales", "Conversión a oportunidad (%)", "Valor medio (€)", "Mejora esperada del sistema (%)", "Valor incremental estimado"],
        "en": ["Monthly leads", "Opportunity conversion (%)", "Average value (€)", "Expected system improvement (%)", "Estimated incremental value"],
        "fr": ["Leads mensuels", "Conversion opportunité (%)", "Valeur moyenne (€)", "Amélioration attendue (%)", "Valeur incrémentale estimée"],
    }[lang]
    return f'''
    <section class="section">
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
    cards = "".join(render_template(partial("cards/case-card.html"), {**labels, **{k: esc(v) for k, v in case.items()}}) for case in CASES)
    return f'<section class="section"><div class="container wide"><div class="grid-3">{cards}</div></div></section>'

def blog_page(lang: str) -> str:
    global CURRENT_LANG
    CURRENT_LANG = lang
    t = SITE["pages"]["blog"]["translations"][lang]
    body = hero(t, "blog")
    if t.get("sections"):
        for index, section in enumerate(t["sections"]):
            body += section_html(section, index)
    latest_title = {"es": "Últimos artículos", "en": "Latest articles", "fr": "Derniers articles"}[lang]
    latest_intro = {
        "es": "La biblioteca se ordena automáticamente por fecha para que el contenido nuevo aparezca primero.",
        "en": "The library is automatically ordered by date so new content appears first.",
        "fr": "La bibliothèque est automatiquement triée par date pour afficher les nouveaux contenus en premier.",
    }[lang]
    body += f'<section class="section"><div class="container wide"><div class="section-heading"><p class="eyebrow">Featured</p><h2>{latest_title}</h2><p class="lead">{latest_intro}</p></div>' + blog_cards(len(BLOG)) + "</div></section>"
    body += render_template(partial("cta/cta-primary.html"), {"heading": esc(t["final_cta"]), "href": page_url("contact", lang), "label": esc(NAV[lang]["primary_cta"])})
    return layout(lang, "blog", body)

def article_page(post: dict) -> str:
    lang = "es"
    title = post["title"]
    description = post["excerpt"][:158]
    if len(description or "") < 50:
        description = f"{description} Artículo de Rotata sobre sistemas de crecimiento B2B, CRM, datos, automatización e IA."
    url = article_url(post["slug"])
    canonical = SITE["site"]["base_url"].rstrip("/") + url
    schema = json.dumps({"@context": "https://schema.org", "@type": "BlogPosting", "headline": title, "description": description, "datePublished": post["date"], "author": {"@type": "Person", "name": post["author"]}, "publisher": {"@type": "Organization", "name": SITE["site"]["company"]}, "image": SITE["site"]["base_url"].rstrip() + post["image"]}, ensure_ascii=False)
    content = load_json(SRC / "content/es/blog" / f'{post["slug"]}.json')["content"]
    content = re.sub(r"<h1([^>]*)>", r"<h2\1>", content, flags=re.I)
    content = re.sub(r"</h1>", "</h2>", content, flags=re.I)
    related = [p for p in BLOG if p["slug"] != post["slug"]][:3]
    related_cards = "".join(render_template(partial("cards/blog-card.html"), {"url": article_url(p["slug"]), "image": p["image"], "alt": esc(p["alt"]), "category": esc(p["category"]), "title": esc(p["title"]), "excerpt": esc(p["excerpt"]), "date": p["date"], "reading_time": str(p["reading_time"])}) for p in related)
    body = f'''
    <article class="article-shell">
      <p class="eyebrow">{esc(post["category"])}</p>
      <h1>{esc(title)}</h1>
      <p class="lead">{esc(post["excerpt"])}</p>
      <p><small>{esc(post["author"])} · {esc(post["date"])} · {post["reading_time"]} min</small></p>
      <img src="{post["image"]}" alt="{esc(post["alt"])}" loading="eager" style="border-radius:28px;border:1px solid var(--color-border);margin:2rem 0;">
      <div class="article-content">{content}</div>
    </article>
    <section class="section"><div class="container wide"><div class="section-heading"><p class="eyebrow">Related</p><h2>Lecturas relacionadas</h2></div><div class="grid-3">{related_cards}</div></div></section>
    {render_template(partial("cta/cta-primary.html"), {"heading": "Ordenemos tu sistema de crecimiento", "href": page_url("contact", "es"), "label": "Contactar"})}
    '''
    head_tags = f'''
    <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{esc(title)} | Rotata</title><meta name="description" content="{esc(description)}">
    <link rel="canonical" href="{canonical}">
    <meta property="og:type" content="article"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:image" content="{SITE["site"]["base_url"].rstrip()}{post["image"]}">
    <meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(description)}">
    <link rel="icon" href="/assets/logo/rotata-favicon.png"><link rel="apple-touch-icon" href="/assets/logo/rotata-apple-touch-icon.png"><link rel="stylesheet" href="/styles/global.css">
    <script>window.ROTATA_CONFIG = {{}};</script><script type="application/ld+json">{schema}</script>
    '''
    return f'<!doctype html><html lang="es" data-theme="dark"><head>{head_tags}</head><body>{header("es", "blog")}<main id="main">{body}</main>{footer("es")}{widgets("es")}{cookie_banner("es")}<script type="module" src="/scripts/global.js"></script></body></html>'

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

def main() -> None:
    copy_static()
    for lang in SITE["languages"]:
        for page_key, page in SITE["pages"].items():
            if page_key == "404":
                continue
            if page_key == "blog":
                html_out = blog_page(lang)
            else:
                html_out = standard_page(lang, page_key)
            write_page(page_url(page_key, lang), html_out)
    for post in BLOG:
        write_page(article_url(post["slug"]), article_page(post))
    for lang in SITE["languages"]:
        write_page(page_url("404", lang), standard_page(lang, "404"))
    shutil.copy2(output_path("/404/"), DIST / "404.html")
    (DIST / "_headers").write_text("/*\n  X-Frame-Options: SAMEORIGIN\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n", encoding="utf-8")
    print(f"Built {DIST}")

if __name__ == "__main__":
    CURRENT_LANG = "es"
    main()
