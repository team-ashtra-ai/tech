#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import build_site as builder

LANG = "en"
SITE_ID = "datagrail"
OUTPUT = builder.ROOT / "docs" / "datagrail-copy-inventory.md"


def page_order() -> list[str]:
    ordered = ["home"]
    seen = set(ordered)
    for group_key in ["about", "solutions", "services", "system", "partners", "insights", "contact"]:
        group = builder.NAV["groups"][group_key]
        for page_key in [group["page"], *group.get("children", [])]:
            if page_key not in seen:
                seen.add(page_key)
                ordered.append(page_key)
    ordered.extend(
        [
            "legal",
            "legal-privacy",
            "legal-cookies",
            "legal-accessibility",
            "legal-sitemap",
            "legal-robots",
        ]
    )
    return ordered


def showcase_site() -> dict:
    return builder.showcase_by_id(SITE_ID)


def site_label() -> str:
    site = showcase_site()
    return builder.localized(site.get("label", site["id"]), LANG, site["id"])


def site_summary() -> str:
    return builder.localized(showcase_site().get("summary", ""), LANG, "")


def page_route(page_key: str) -> str:
    return builder.showcase_url(SITE_ID, LANG, page_key)


def page_payload(page_key: str) -> dict:
    return builder.page_payload(page_key, LANG)


def page_translation(page_key: str) -> dict:
    return page_payload(page_key)["translation"]


def page_title(page_key: str) -> str:
    translation = page_translation(page_key)
    return f"Rotata {site_label()} concept | {translation.get('title', '')}"


def page_description(page_key: str) -> str:
    translation = page_translation(page_key)
    return f"{site_summary()} {translation.get('description', '')}".strip()


def variant_label(variant: str) -> str:
    return {
        "problem": "Friction",
        "cards": "System layer",
        "grid": "Operating model",
        "process": "Process",
        "metrics": "Proof",
        "partners": "Ecosystem",
        "blog-preview": "Insights",
        "text": "Context",
    }.get(variant, "Context")


def lines_for_item(item, index: int) -> list[str]:
    if isinstance(item, dict):
        title = str(item.get("title", "")).strip()
        text = str(item.get("text", "")).strip()
        lines = [f"  - Item {index} title: {title}"]
        if text:
            lines.append(f"    Item {index} text: {text}")
        return lines
    return [f"  - Item {index}: {str(item).strip()}"]


def lines_for_items(items) -> list[str]:
    if not items:
        return ["- Items: none"]
    lines = ["- Items:"]
    for index, item in enumerate(items, start=1):
        lines.extend(lines_for_item(item, index))
    return lines


def section_block(index: int, section: dict) -> list[str]:
    variant = section.get("variant", "text")
    lines = [
        f"#### Section {index:02d} - {variant_label(variant)}",
        f"- Variant: `{variant}`",
        f"- Heading: {section.get('heading', '')}",
        f"- Body: {section.get('body', '')}",
    ]
    lines.extend(lines_for_items(section.get("items", [])))
    lines.append("")
    return lines


def shared_header_nav() -> list[str]:
    groups = ["home", "about", "solutions", "services", "system", "partners", "insights", "contact", "legal"]
    lines = []
    for group_key in groups:
        if group_key == "home":
            lines.append("- Home")
            continue
        if group_key == "legal":
            children = ["legal-privacy", "legal", "legal-cookies", "legal-accessibility", "legal-sitemap", "legal-robots"]
            lines.append("- Legal")
        else:
            group = builder.NAV["groups"][group_key]
            children = group.get("children", [])
            lines.append(f"- {builder.localized(group['label'], LANG, group_key)}")
        for child in children:
            lines.append(f"  - {builder.page_label(child, LANG, 'dropdown_label')}")
    return lines


def shared_footer() -> list[str]:
    lines = [
        "## Shared Footer",
        f"- Summary: {page_translation('home').get('intro', '')}",
    ]
    for column in builder.NAV["footer_columns"][:4]:
        lines.append(f"- Column: {builder.localized(column['title'], LANG, '')}")
        for page_key in column["items"][:5]:
            lines.append(f"  - {builder.page_label(page_key, LANG, 'footer_label')}")
    lines.append("")
    return lines


def shared_chrome() -> list[str]:
    lines = [
        "## Shared Chrome",
        "### Sticky header note bar",
        "- Badge: Vera agent",
        "- Text: Human controls for the growth system.",
        "- CTA: Map system",
        "",
        "### Sticky header main row",
        "- Header secondary CTA: Contact Us",
        "- Header primary CTA: Get a demo",
        "- Mobile menu button: Menu",
        "- Mobile menu close button: Close",
        "",
        "### Desktop and mobile navigation",
    ]
    lines.extend(shared_header_nav())
    lines.extend(
        [
            "",
            "### Concept switcher",
            "- Label: Website concepts",
            "- Option: Databricks",
            "- Option: DataGrail",
            "- Option: Atlan",
            "- Option: Runpod",
            "- Option: Vectara",
            "",
        ]
    )
    lines.extend(shared_footer())
    return lines


def article_cards(limit: int) -> list[str]:
    lines = []
    for index, post in enumerate(builder.blog_posts(LANG)[:limit], start=1):
        lines.extend(
            [
                f"  - Article {index} category: {post.get('category', '')}",
                f"    Article {index} title: {post.get('title', '')}",
                f"    Article {index} excerpt: {post.get('excerpt', '')}",
                f"    Article {index} CTA: Read more",
            ]
        )
    return lines


def partner_cards() -> list[str]:
    lines = []
    for index, partner in enumerate(builder.PARTNERS, start=1):
        lines.extend(
            [
                f"  - Partner card {index} title: {builder.localized(partner.get('name', ''), LANG, '')}",
                f"    Partner card {index} body: {builder.localized(partner.get('role', ''), LANG, '')}",
                f"    Partner card {index} CTA: View fit",
            ]
        )
    return lines


def case_cards() -> list[str]:
    lines = []
    for index, case in enumerate(builder.CASES, start=1):
        lines.extend(
            [
                f"  - Case card {index} label: Case",
                f"    Case card {index} title: {builder.localized(case.get('title', case.get('name', '')), LANG, '')}",
                f"    Case card {index} problem label: Problem",
                f"    Case card {index} problem: {builder.localized(case.get('problem', ''), LANG, '')}",
                f"    Case card {index} system label: System",
                f"    Case card {index} system: {builder.localized(case.get('system', ''), LANG, '')}",
                f"    Case card {index} result label: Result",
                f"    Case card {index} result: {builder.localized(case.get('result', ''), LANG, '')}",
            ]
        )
    return lines


def roi_block() -> list[str]:
    labels = [
        "Monthly leads",
        "Opportunity conversion (%)",
        "Average value (€)",
        "Expected improvement (%)",
        "Estimated incremental value",
    ]
    defaults = ["120", "8", "12000", "20", "€0"]
    lines = [
        "### Special Block - ROI panel",
        "- Kicker: ROI",
        f"- Heading: {labels[4]}",
        f"- Default output: {defaults[4]}",
        f"- Input 1 label: {labels[0]}",
        f"  Input 1 default: {defaults[0]}",
        f"- Input 2 label: {labels[1]}",
        f"  Input 2 default: {defaults[1]}",
        f"- Input 3 label: {labels[2]}",
        f"  Input 3 default: {defaults[2]}",
        f"- Input 4 label: {labels[3]}",
        f"  Input 4 default: {defaults[3]}",
        "",
    ]
    return lines


def contact_block() -> list[str]:
    labels = builder.FORMS["labels"][LANG]
    lines = [
        "### Special Block - Contact panel",
        "- Kicker: Consult",
        "- Heading: Tell us which part of the system is not working.",
        "- Body: We review context, CRM, data, signals and commercial process before recommending work.",
        f"- Field: {labels['first_name']}",
        f"- Field: {labels['last_name']}",
        f"- Field: {labels['email']}",
        f"- Field: {labels['company']}",
        f"- Field: {labels['service']}",
        f"- Field: {labels['message']}",
        "- Service options:",
    ]
    for option in builder.FORMS["service_interests"]:
        lines.append(f"  - {option}")
    lines.extend([f"- Submit button: {labels['submit']}", ""])
    return lines


def home_page() -> list[str]:
    translation = page_translation("home")
    sections = translation.get("sections", [])
    program = sections[2]
    process = sections[4]
    proof = sections[5]
    resources = sections[7]
    lines = [
        "## Home",
        f"- Route: {page_route('home')}",
        "- Page key: `home`",
        "- Template: `src/partials/theme-sites/datagrail.html`",
        f"- Meta title: {page_title('home')}",
        f"- Meta description: {page_description('home')}",
        "",
        "### Hero",
        f"- Eyebrow: {translation.get('eyebrow', '')}",
        f"- H1: {translation.get('h1', '')}",
        f"- Intro: {translation.get('intro', '')}",
        f"- Primary CTA: {translation.get('primary_cta', '')}",
        f"- Secondary CTA: {translation.get('secondary_cta', '')}",
        "",
        "#### Browser mockup",
        "- Sidebar item: Dashboard",
        "- Sidebar item: Risk",
        "- Sidebar item: Consent",
        "- Sidebar item: Live Map",
        "- Sidebar item: DSR",
        "- Card 1 title: Risk Detection",
        "- Card 1 body: New sensitive process detected",
        "- Card 1 status: Review",
        "- Card 2 title: Assessment Autofill",
        "- Card 2 line 1: System responses added",
        "- Card 2 line 2: Owner and SLA attached",
        "",
        "### Trust strip",
        "- Heading: The teams that rely on system clarity",
    ]
    for partner in builder.PARTNERS[:8]:
        lines.append(f"- Partner name: {builder.localized(partner.get('name', ''), LANG, '')}")
    lines.extend(
        [
            "",
        "### Program section",
            "- Intro line: Your growth program, upgraded",
            f"- Heading: {program.get('heading', '')}",
            f"- Body: {program.get('body', '')}",
        ]
    )
    lines.extend(lines_for_items(program.get("items", [])))
    lines.extend(
        [
            "",
        "### Agent section",
            "- Eyebrow: POWERED BY SYSTEM LOGIC",
            f"- Heading: {process.get('heading', '')}",
            f"- Body: {process.get('body', '')}",
        ]
    )
    lines.extend(lines_for_items(process.get("items", [])))
    lines.extend(
        [
            "",
        "### Controls section",
            "- Eyebrow: CONTROL CENTER",
            f"- Heading: {proof.get('heading', '')}",
        ]
    )
    lines.extend(lines_for_items(proof.get("items", [])))
    lines.extend(
        [
            "",
        "### Resources section",
            f"- Heading: {resources.get('heading', '')}",
        ]
    )
    lines.extend(article_cards(3))
    lines.append("")
    return lines


def detail_page(page_key: str) -> list[str]:
    payload = page_payload(page_key)
    translation = payload["translation"]
    lines = [
        f"## {builder.page_label(page_key, LANG)}",
        f"- Route: {page_route(page_key)}",
        f"- Page key: `{page_key}`",
        f"- Source page: `{payload.get('source_page', '')}`",
        f"- Render type: `{payload.get('render', 'standard')}`",
        f"- Meta title: {page_title(page_key)}",
        f"- Meta description: {page_description(page_key)}",
        "",
        "### Hero",
        f"- Eyebrow: {translation.get('eyebrow', builder.page_label(page_key, LANG))}",
        f"- H1: {translation.get('h1', '')}",
        f"- Intro: {translation.get('intro', '')}",
        f"- Primary CTA: {translation.get('primary_cta', builder.NAV['ui'][LANG]['header_cta'])}",
        f"- Secondary CTA: {translation.get('secondary_cta', builder.page_label('solutions', LANG))}",
        f"- Visual caption left label: {builder.page_label(page_key, LANG)}",
        f"- Visual caption right label: {site_label()}",
        "",
    ]
    for index, section in enumerate(translation.get("sections", []), start=1):
        lines.extend(section_block(index, section))
    render_type = payload.get("render", "standard")
    if render_type == "blog":
        lines.extend(["### Special Block - Recent articles"])
        lines.extend(article_cards(9))
        lines.append("")
    elif render_type == "roi":
        lines.extend(roi_block())
    elif render_type == "contact":
        lines.extend(contact_block())
    elif render_type == "cases":
        lines.extend(["### Special Block - Case grid"])
        lines.extend(case_cards())
        lines.append("")
    elif page_key == "partners":
        lines.extend(["### Special Block - Partner roles"])
        lines.extend(partner_cards())
        lines.append("")
    final_heading = translation.get("final_cta") or page_translation("home").get("final_cta", "")
    lines.extend(
        [
            "### Final CTA",
            f"- Heading: {final_heading}",
            f"- Button: {builder.NAV['ui'][LANG]['footer_cta']}",
            "",
        ]
    )
    return lines


def build_document() -> str:
    lines = [
        "# DataGrail Showcase Copy Inventory",
        "",
        f"Generated from source content on {builder.datetime.now().date().isoformat()} for the English DataGrail showcase routes under `/en/showcase/datagrail/`.",
        "",
        "## Scope",
        "- Included: shared DataGrail chrome, every English DataGrail showcase page, each visible page section, CTA labels, form labels, partner cards, case cards, ROI labels, and the blog card copy that appears inside the showcase.",
        "- Excluded: the non-showcase article detail template at `/en/insights/blog/<slug>/`, because those pages are not rendered inside the DataGrail showcase shell.",
        "",
        "## Page Index",
    ]
    for index, page_key in enumerate(page_order(), start=1):
        lines.append(f"{index}. {builder.page_label(page_key, LANG)} - `{page_route(page_key)}`")
    lines.append("")
    lines.extend(shared_chrome())
    lines.extend(home_page())
    for page_key in page_order()[1:]:
        lines.extend(detail_page(page_key))
    return "\n".join(lines).strip() + "\n"


def main() -> None:
    OUTPUT.write_text(build_document(), encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
