#!/usr/bin/env python3
"""Export the static Rotata source into a future-editable WordPress theme."""
from __future__ import annotations

import html
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "wordpress-export/rotata-theme"
SRC = ROOT / "src"
THEMES = json.loads((SRC / "data/themes.json").read_text(encoding="utf-8"))
SHOWCASE = json.loads((SRC / "data/showcase-sites.json").read_text(encoding="utf-8"))


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def esc(value: str) -> str:
    return html.escape(str(value or ""), quote=True)


def localized(value, lang: str = "es", fallback: str = ""):
    if isinstance(value, dict):
        if lang in value and value[lang] not in (None, ""):
            return value[lang]
        if "en" in value and value["en"] not in (None, ""):
            return value["en"]
        if value:
            return next(iter(value.values()))
        return fallback
    return value if value is not None else fallback


def default_theme() -> dict:
    target = THEMES.get("default_theme")
    for theme in THEMES["themes"]:
        if theme["id"] == target:
            return theme
    return THEMES["themes"][0]


def showcase_sites() -> list[dict]:
    return SHOWCASE.get("sites", [])


def default_showcase() -> dict:
    target = SHOWCASE.get("default_site")
    for site in showcase_sites():
        if site["id"] == target:
            return site
    return showcase_sites()[0]


def wordpress_theme_preview_bar(lang: str = "es") -> str:
    default = default_showcase()
    items = []
    announcement_template = "Concepto abierto: {label}" if lang == "es" else "Concept opened: {label}"
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
        items.append(
            f'<a class="theme-chip"'
            f' href="<?php echo esc_url(home_url(\'/showcase/{esc(site["id"])}/\')); ?>"'
            f' data-theme-label="{esc(label)}"'
            f' data-theme-summary="{esc(summary)}"'
            f' data-theme-color="{esc(site.get("theme_color", ""))}"'
            f' style="{esc(style)}">'
            f'<span class="theme-chip-swatch" aria-hidden="true"></span>'
            f'<span class="theme-chip-label">{esc(label)}</span>'
            f"</a>"
        )

    return (
        '<div class="theme-demo-bar">'
        '<div class="container theme-demo-shell">'
        '<div class="theme-demo-copy">'
        '<span class="theme-demo-label">Conceptos web</span>'
        f'<p class="theme-demo-summary" data-theme-summary>{esc(localized(default.get("summary", ""), lang, ""))}</p>'
        "</div>"
        '<nav class="theme-switcher" aria-label="Selector de conceptos web">'
        + "".join(items)
        + "</nav>"
        f'<span class="sr-only" aria-live="polite" data-theme-announcer>{esc(announcement_template.format(label=localized(default.get("label", default["id"]), lang, default["id"])))}</span>'
        "</div>"
        "</div>"
    )


def hydrate_wordpress_partial(markup: str) -> str:
    """Replace static-build placeholders with WordPress-safe defaults."""
    replacements = {
        "{{skip_label}}": "<?php esc_html_e('Saltar al contenido', 'rotata'); ?>",
        "{{home_label}}": "<?php esc_attr_e('Inicio de Rotata', 'rotata'); ?>",
        "{{theme_preview_bar}}": wordpress_theme_preview_bar(),
        "{{utility_label}}": "<?php esc_html_e('Construye el sistema detrás de tu crecimiento', 'rotata'); ?>",
        "{{close_label}}": "<?php esc_attr_e('Cerrar menú', 'rotata'); ?>",
        "{{home_url}}": "<?php echo esc_url(home_url('/')); ?>",
        "{{logo}}": "<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/logo/rotata-b2b-growth-system-logo.svg'); ?>",
        "{{logo_markup}}": "<span class=\"logo-swap\" aria-hidden=\"true\"><img class=\"brand-logo brand-logo-theme-light\" src=\"<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/logo/rotata-b2b-growth-system-logo.svg'); ?>\" width=\"154\" height=\"40\" alt=\"\" /><img class=\"brand-logo brand-logo-theme-dark\" src=\"<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/logo/rotata-b2b-growth-system-logo-dark.svg'); ?>\" width=\"154\" height=\"40\" alt=\"\" /></span>",
        "{{cta_url}}": "<?php echo esc_url(home_url('/contact/consult/')); ?>",
        "{{cta_label}}": "<?php esc_html_e('Consultar Rotata', 'rotata'); ?>",
        "{{accessibility_url}}": "<?php echo esc_url(home_url('/legal/accessibility/')); ?>",
        "{{accessibility_label}}": "<?php esc_html_e('Accesibilidad', 'rotata'); ?>",
        "{{menu_label}}": "<?php esc_attr_e('Abrir menú', 'rotata'); ?>",
        "{{language_switcher}}": "",
        "{{nav_desktop}}": "<?php wp_nav_menu(['theme_location' => 'primary', 'container' => 'nav', 'container_class' => 'nav-desktop', 'fallback_cb' => false]); ?>",
        "{{nav_mobile}}": "<div class=\"mobile-panel\" id=\"mobile-menu\" data-mobile-menu hidden><div class=\"mobile-panel-head\"><a class=\"brand\" href=\"<?php echo esc_url(home_url('/')); ?>\" aria-label=\"<?php esc_attr_e('Inicio de Rotata', 'rotata'); ?>\"><span class=\"logo-swap\" aria-hidden=\"true\"><img class=\"brand-logo brand-logo-theme-light\" src=\"<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/logo/rotata-b2b-growth-system-logo.svg'); ?>\" width=\"154\" height=\"40\" alt=\"\" /><img class=\"brand-logo brand-logo-theme-dark\" src=\"<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/logo/rotata-b2b-growth-system-logo-dark.svg'); ?>\" width=\"154\" height=\"40\" alt=\"\" /></span></a><button class=\"mobile-close\" type=\"button\" data-menu-close aria-label=\"<?php esc_attr_e('Cerrar menú', 'rotata'); ?>\">×</button></div><div class=\"mobile-panel-body\"><?php wp_nav_menu(['theme_location' => 'primary', 'container' => 'nav', 'container_class' => 'nav-mobile', 'fallback_cb' => false]); ?></div><div class=\"mobile-panel-footer\"><a class=\"btn btn-primary\" href=\"<?php echo esc_url(home_url('/contact/consult/')); ?>\"><?php esc_html_e('Consulta', 'rotata'); ?></a></div></div>",
        "{{footer_cta_heading}}": "<?php esc_html_e('Construye el sistema detrás de tu crecimiento', 'rotata'); ?>",
        "{{footer_cta_text}}": "<?php esc_html_e('Convierte herramientas, datos y procesos desconectados en un sistema estructurado de crecimiento B2B.', 'rotata'); ?>",
        "{{footer_cta_url}}": "<?php echo esc_url(home_url('/contact/consult/')); ?>",
        "{{footer_cta_label}}": "<?php esc_html_e('Consulta', 'rotata'); ?>",
        "{{brand_name}}": "Rotata",
        "{{brand_tagline}}": "<?php esc_html_e('Construye el sistema detrás de tu crecimiento', 'rotata'); ?>",
        "{{brand_summary}}": "<?php esc_html_e('Rotata diseña sistemas estructurados de crecimiento con soporte de IA para equipos B2B de marketing y ventas.', 'rotata'); ?>",
        "{{brand_links}}": "<a href=\"https://www.linkedin.com/company/rotata-consulting-sl/\" data-track=\"linkedin_click\">LinkedIn</a><a href=\"mailto:info@rotata.com\">Email</a><a href=\"tel:+34649498272\"><?php esc_html_e('Teléfono', 'rotata'); ?></a><span><?php esc_html_e('España', 'rotata'); ?></span>",
        "{{brand_location}}": "<?php esc_html_e('España', 'rotata'); ?>",
        "{{brand_location_mobile}}": "<?php esc_html_e('España, servicio global', 'rotata'); ?>",
        "{{footer_columns}}": "<section class=\"footer-column\"><h2 class=\"footer-heading\"><?php esc_html_e('Resumen', 'rotata'); ?></h2><nav class=\"footer-links\"><a href=\"<?php echo esc_url(home_url('/about/')); ?>\"><?php esc_html_e('Sobre', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/about/values/')); ?>\"><?php esc_html_e('Valores', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/about/mission/')); ?>\"><?php esc_html_e('Misión', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/about/process/')); ?>\"><?php esc_html_e('Proceso', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/about/cases/')); ?>\"><?php esc_html_e('Casos', 'rotata'); ?></a></nav></section><section class=\"footer-column\"><h2 class=\"footer-heading\"><?php esc_html_e('Solutions', 'rotata'); ?></h2><nav class=\"footer-links\"><a href=\"<?php echo esc_url(home_url('/solutions/pipeline/')); ?>\">Pipeline</a><a href=\"<?php echo esc_url(home_url('/solutions/intelligence/')); ?>\">Intelligence</a><a href=\"<?php echo esc_url(home_url('/solutions/conversion/')); ?>\">Conversion</a><a href=\"<?php echo esc_url(home_url('/solutions/alignment/')); ?>\">Alignment</a></nav></section><section class=\"footer-column\"><h2 class=\"footer-heading\"><?php esc_html_e('Services', 'rotata'); ?></h2><nav class=\"footer-links\"><a href=\"<?php echo esc_url(home_url('/services/crm/')); ?>\">CRM</a><a href=\"<?php echo esc_url(home_url('/services/data/')); ?>\">Data</a><a href=\"<?php echo esc_url(home_url('/services/outbound/')); ?>\">Outbound</a><a href=\"<?php echo esc_url(home_url('/services/signals/')); ?>\">Signals</a><a href=\"<?php echo esc_url(home_url('/services/sales/')); ?>\">Sales</a></nav></section><section class=\"footer-column\"><h2 class=\"footer-heading\"><?php esc_html_e('System', 'rotata'); ?></h2><nav class=\"footer-links\"><a href=\"<?php echo esc_url(home_url('/system/')); ?>\"><?php esc_html_e('Architecture', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/system/workflows/')); ?>\"><?php esc_html_e('Workflows', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/system/automation/')); ?>\"><?php esc_html_e('Automation', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/system/reporting/')); ?>\"><?php esc_html_e('Reporting', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/system/integrations/')); ?>\"><?php esc_html_e('Integrations', 'rotata'); ?></a></nav></section><section class=\"footer-column\"><h2 class=\"footer-heading\"><?php esc_html_e('Ecosystem', 'rotata'); ?></h2><nav class=\"footer-links\"><a href=\"<?php echo esc_url(home_url('/partners/')); ?>\"><?php esc_html_e('Partners', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/partners/hubspot/')); ?>\">HubSpot</a><a href=\"<?php echo esc_url(home_url('/partners/zoominfo/')); ?>\">ZoomInfo</a><a href=\"<?php echo esc_url(home_url('/partners/synapsale/')); ?>\">Synapsale</a><a href=\"<?php echo esc_url(home_url('/insights/roi/')); ?>\">ROI</a></nav></section><section class=\"footer-column\"><h2 class=\"footer-heading\"><?php esc_html_e('Insights', 'rotata'); ?></h2><nav class=\"footer-links\"><a href=\"<?php echo esc_url(home_url('/insights/blog/')); ?>\">Blog</a><a href=\"<?php echo esc_url(home_url('/insights/newsletter/')); ?>\">Newsletter</a><a href=\"<?php echo esc_url(home_url('/insights/roi/')); ?>\">ROI</a></nav></section><section class=\"footer-column\"><h2 class=\"footer-heading\"><?php esc_html_e('Legal', 'rotata'); ?></h2><nav class=\"footer-links\"><a href=\"<?php echo esc_url(home_url('/legal/privacy/')); ?>\"><?php esc_html_e('Privacidad', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/legal/')); ?>\"><?php esc_html_e('Legal', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/legal/cookies/')); ?>\">Cookies</a><a href=\"<?php echo esc_url(home_url('/legal/accessibility/')); ?>\"><?php esc_html_e('Accesibilidad', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/legal/sitemap/')); ?>\"><?php esc_html_e('Mapa del sitio', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/legal/robots/')); ?>\">Robots</a></nav></section>",
        "{{footer_mobile_columns}}": "<details class=\"footer-accordion\"><summary><?php esc_html_e('Resumen', 'rotata'); ?></summary><div class=\"footer-accordion-links\"><a href=\"<?php echo esc_url(home_url('/about/')); ?>\"><?php esc_html_e('Sobre', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/about/values/')); ?>\"><?php esc_html_e('Valores', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/about/mission/')); ?>\"><?php esc_html_e('Misión', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/about/process/')); ?>\"><?php esc_html_e('Proceso', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/about/cases/')); ?>\"><?php esc_html_e('Casos', 'rotata'); ?></a></div></details><details class=\"footer-accordion\"><summary>Solutions</summary><div class=\"footer-accordion-links\"><a href=\"<?php echo esc_url(home_url('/solutions/pipeline/')); ?>\">Pipeline</a><a href=\"<?php echo esc_url(home_url('/solutions/intelligence/')); ?>\">Intelligence</a><a href=\"<?php echo esc_url(home_url('/solutions/conversion/')); ?>\">Conversion</a><a href=\"<?php echo esc_url(home_url('/solutions/alignment/')); ?>\">Alignment</a></div></details><details class=\"footer-accordion\"><summary>Services</summary><div class=\"footer-accordion-links\"><a href=\"<?php echo esc_url(home_url('/services/crm/')); ?>\">CRM</a><a href=\"<?php echo esc_url(home_url('/services/data/')); ?>\">Data</a><a href=\"<?php echo esc_url(home_url('/services/outbound/')); ?>\">Outbound</a><a href=\"<?php echo esc_url(home_url('/services/signals/')); ?>\">Signals</a><a href=\"<?php echo esc_url(home_url('/services/sales/')); ?>\">Sales</a></div></details><details class=\"footer-accordion\"><summary>System</summary><div class=\"footer-accordion-links\"><a href=\"<?php echo esc_url(home_url('/system/')); ?>\"><?php esc_html_e('Architecture', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/system/workflows/')); ?>\"><?php esc_html_e('Workflows', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/system/automation/')); ?>\"><?php esc_html_e('Automation', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/system/reporting/')); ?>\"><?php esc_html_e('Reporting', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/system/integrations/')); ?>\"><?php esc_html_e('Integrations', 'rotata'); ?></a></div></details><details class=\"footer-accordion\"><summary><?php esc_html_e('Ecosistema', 'rotata'); ?></summary><div class=\"footer-accordion-links\"><a href=\"<?php echo esc_url(home_url('/partners/')); ?>\"><?php esc_html_e('Partners', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/partners/hubspot/')); ?>\">HubSpot</a><a href=\"<?php echo esc_url(home_url('/partners/zoominfo/')); ?>\">ZoomInfo</a><a href=\"<?php echo esc_url(home_url('/partners/synapsale/')); ?>\">Synapsale</a><a href=\"<?php echo esc_url(home_url('/insights/roi/')); ?>\">ROI</a></div></details><details class=\"footer-accordion\"><summary>Insights</summary><div class=\"footer-accordion-links\"><a href=\"<?php echo esc_url(home_url('/insights/blog/')); ?>\">Blog</a><a href=\"<?php echo esc_url(home_url('/insights/newsletter/')); ?>\">Newsletter</a><a href=\"<?php echo esc_url(home_url('/insights/roi/')); ?>\">ROI</a></div></details><details class=\"footer-accordion\"><summary><?php esc_html_e('Legal', 'rotata'); ?></summary><div class=\"footer-accordion-links\"><a href=\"<?php echo esc_url(home_url('/legal/privacy/')); ?>\"><?php esc_html_e('Privacidad', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/legal/')); ?>\"><?php esc_html_e('Legal', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/legal/cookies/')); ?>\">Cookies</a><a href=\"<?php echo esc_url(home_url('/legal/accessibility/')); ?>\"><?php esc_html_e('Accesibilidad', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/legal/sitemap/')); ?>\"><?php esc_html_e('Mapa del sitio', 'rotata'); ?></a><a href=\"<?php echo esc_url(home_url('/legal/robots/')); ?>\">Robots</a></div></details>",
        "{{funding_strip}}": "<div class=\"container funding-strip\"><img src=\"<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/partners/rotata-kit-digital-eu-funding.png'); ?>\" alt=\"Kit Digital, Gobierno de España, Red.es, Next Generation EU y Plan de Recuperación\"><span><?php esc_html_e('Financiado por la Unión Europea a través del programa Kit Digital, con fondos Next Generation EU del Mecanismo de Recuperación y Resiliencia.', 'rotata'); ?></span></div>",
        "{{footer_bottom}}": "© <?php echo esc_html(date('Y')); ?> Rotata Consulting SL",
        "{{eyebrow}}": "<?php esc_html_e('Cookies', 'rotata'); ?>",
        "{{title}}": "<?php esc_html_e('Privacidad y cookies', 'rotata'); ?>",
        "{{body}}": "<?php esc_html_e('Usamos cookies necesarias para que el sitio funcione. Si aceptas, activamos también analítica, marketing y preferencias para mejorar la experiencia.', 'rotata'); ?>",
        "{{accept}}": "<?php esc_html_e('Aceptar todo', 'rotata'); ?>",
        "{{necessary_only}}": "<?php esc_html_e('Solo necesarias', 'rotata'); ?>",
        "{{reject}}": "<?php esc_html_e('Rechazar', 'rotata'); ?>",
        "{{policy}}": "<?php esc_html_e('Leer política', 'rotata'); ?>",
        "{{policy_url}}": "<?php echo esc_url(home_url('/legal/cookies/')); ?>",
    }
    for token, value in replacements.items():
        markup = markup.replace(token, value)
    return markup


def main() -> None:
    if THEME.exists():
        shutil.rmtree(THEME)

    for subdir in ["template-parts", "assets/css", "assets/js", "assets/images", "languages"]:
        (THEME / subdir).mkdir(parents=True, exist_ok=True)

    shutil.copytree(SRC / "styles", THEME / "assets/css/styles")
    shutil.copytree(SRC / "scripts", THEME / "assets/js/scripts")
    shutil.copytree(SRC / "assets", THEME / "assets/images/assets")

    write(
        THEME / "style.css",
        """/*
Theme Name: Rotata Growth System
Author: Ashtra AI
Description: Static-first Rotata theme export preserving the premium system design.
Version: 1.0.0
Text Domain: rotata
*/
@import url('assets/css/styles/global.css');
""",
    )

    write(
        THEME / "functions.php",
        """<?php
function rotata_setup() {
  add_theme_support('title-tag');
  add_theme_support('post-thumbnails');
  add_theme_support('custom-logo');
  add_theme_support('editor-styles');
  add_editor_style('assets/css/styles/global.css');
  register_nav_menus([
    'primary' => __('Primary Menu', 'rotata'),
    'footer' => __('Footer Menu', 'rotata'),
  ]);
}
add_action('after_setup_theme', 'rotata_setup');

function rotata_assets() {
  wp_enqueue_style('rotata-global', get_template_directory_uri() . '/assets/css/styles/global.css', [], '1.0.0');
  wp_enqueue_script('rotata-global', get_template_directory_uri() . '/assets/js/scripts/global.js', [], '1.0.0', true);
}
add_action('wp_enqueue_scripts', 'rotata_assets');
?>""",
    )

    header = hydrate_wordpress_partial((SRC / "partials/header/header.html").read_text(encoding="utf-8"))
    footer = hydrate_wordpress_partial((SRC / "partials/footer/footer.html").read_text(encoding="utf-8"))
    cookie_banner = hydrate_wordpress_partial((SRC / "partials/cookie/cookie-consent.html").read_text(encoding="utf-8"))
    default = default_theme()
    write(
        THEME / "header.php",
        f"<!doctype html><html <?php language_attributes(); ?> data-design-theme=\"{esc(default['id'])}\" data-theme-surface=\"{esc(default.get('surface', 'dark'))}\"><head><?php wp_head(); ?></head><body <?php body_class(); ?>>\n"
        + header
        + "\n<main id=\"main\">\n",
    )
    widgets_markup = """<div class=\"floating-actions\" aria-label=\"Quick actions\">
  <button class=\"float-button back-to-top\" type=\"button\" data-back-to-top aria-label=\"<?php esc_attr_e('Volver arriba', 'rotata'); ?>\">↑</button>
  <a class=\"float-button whatsapp\" href=\"https://wa.me/34649498272\" aria-label=\"<?php esc_attr_e('Hablar por WhatsApp', 'rotata'); ?>\" data-track=\"whatsapp_click\">WA</a>
  <button class=\"float-button rotbot-button\" type=\"button\" data-rotbot-toggle aria-expanded=\"false\" aria-controls=\"rotbot-panel\" aria-label=\"<?php esc_attr_e('Abrir Soy Rotbot', 'rotata'); ?>\"><img src=\"<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/images/rotata-rotbot-ai-assistant.png'); ?>\" alt=\"\"></button>
</div>
<aside class=\"rotbot-panel\" id=\"rotbot-panel\" data-rotbot-panel hidden>
  <div class=\"rotbot-head\"><img src=\"<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/images/rotata-rotbot-ai-assistant.png'); ?>\" alt=\"\"><div><strong>Soy Rotbot</strong><span><?php esc_html_e('Asistente de sistemas B2B', 'rotata'); ?></span></div><button class=\"rotbot-close\" type=\"button\" data-rotbot-close aria-label=\"Close\">×</button></div>
  <div class=\"rotbot-messages\" data-rotbot-messages><p class=\"rotbot-message bot\"><?php esc_html_e('Hola. Puedo ayudarte a ubicar el problema: CRM, datos, outbound, ROI o automatización.', 'rotata'); ?></p></div>
  <div class=\"rotbot-prompts\"><a href=\"<?php echo esc_url(home_url('/contact/')); ?>\" data-track=\"cta_click\"><?php esc_html_e('Hablar con Rotata', 'rotata'); ?></a></div>
</aside>"""
    write(
        THEME / "footer.php",
        "</main>\n" + footer + "\n" + widgets_markup + "\n" + cookie_banner + "\n<?php wp_footer(); ?></body></html>\n",
    )

    standard_template = """<?php get_header(); ?>
<section class="section">
  <div class="container">
    <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
      <p class="eyebrow">Rotata</p>
      <h1><?php the_title(); ?></h1>
      <div class="article-content"><?php the_content(); ?></div>
    <?php endwhile; endif; ?>
  </div>
</section>
<?php get_footer(); ?>
"""
    for name in ["front-page.php", "page.php", "single.php", "archive.php"]:
        write(THEME / name, standard_template)

    write(
        THEME / "404.php",
        """<?php get_header(); ?>
<section class="section"><div class="container"><h1><?php esc_html_e('Page not found', 'rotata'); ?></h1></div></section>
<?php get_footer(); ?>
""",
    )

    template_parts = {
        "blog-card.php": """<?php
$post_id = $args['post_id'] ?? get_the_ID();
?>
<article class="blog-card">
  <a href="<?php echo esc_url(get_permalink($post_id)); ?>">
    <?php echo get_the_post_thumbnail($post_id, 'large', ['loading' => 'lazy']); ?>
    <span><?php echo esc_html(get_the_category($post_id)[0]->name ?? __('Insights', 'rotata')); ?></span>
    <h3><?php echo esc_html(get_the_title($post_id)); ?></h3>
    <p><?php echo esc_html(get_the_excerpt($post_id)); ?></p>
    <small><?php echo esc_html(get_the_date('', $post_id)); ?></small>
  </a>
</article>
""",
        "service-card.php": """<?php
$title = $args['title'] ?? '';
$text = $args['text'] ?? '';
$icon = $args['icon'] ?? get_template_directory_uri() . '/assets/images/assets/icons/rotata-system-icon.svg';
?>
<article class="system-card">
  <img src="<?php echo esc_url($icon); ?>" alt="" loading="lazy">
  <h3><?php echo esc_html($title); ?></h3>
  <p><?php echo esc_html($text); ?></p>
</article>
""",
        "cta-primary.php": """<?php
$heading = $args['heading'] ?? __('Construyamos tu sistema de crecimiento', 'rotata');
$href = $args['href'] ?? home_url('/contact/consult/');
$label = $args['label'] ?? __('Diagnosticar sistema', 'rotata');
?>
<section class="section final-cta">
  <div class="container cta-panel">
    <p class="eyebrow">Rotata</p>
    <h2><?php echo esc_html($heading); ?></h2>
    <a class="btn btn-primary" data-track="cta_click" href="<?php echo esc_url($href); ?>"><?php echo esc_html($label); ?></a>
  </div>
</section>
""",
        "contact-form.php": """<form class="form contact-form" data-form="contact" novalidate>
  <div class="form-grid">
    <label><?php esc_html_e('Nombre', 'rotata'); ?><input name="first_name" required></label>
    <label><?php esc_html_e('Apellidos', 'rotata'); ?><input name="last_name" required></label>
    <label><?php esc_html_e('Email', 'rotata'); ?><input name="email" type="email" required></label>
    <label><?php esc_html_e('Empresa', 'rotata'); ?><input name="company" required></label>
  </div>
  <label><?php esc_html_e('Qué necesitas ordenar', 'rotata'); ?><textarea name="message" required></textarea></label>
  <label class="consent-line"><input type="checkbox" name="privacy_consent" required> <span><?php esc_html_e('Acepto la política de privacidad', 'rotata'); ?></span></label>
  <button class="btn btn-primary" type="submit"><?php esc_html_e('Enviar diagnóstico', 'rotata'); ?></button>
  <p class="form-status" role="status" aria-live="polite"></p>
</form>
""",
        "case-card.php": """<?php
$title = $args['title'] ?? '';
$problem = $args['problem'] ?? '';
$system = $args['system'] ?? '';
$result = $args['result'] ?? '';
?>
<article class="case-card">
  <h3><?php echo esc_html($title); ?></h3>
  <p><strong><?php esc_html_e('Problema', 'rotata'); ?>:</strong> <?php echo esc_html($problem); ?></p>
  <p><strong><?php esc_html_e('Sistema', 'rotata'); ?>:</strong> <?php echo esc_html($system); ?></p>
  <p><strong><?php esc_html_e('Resultado', 'rotata'); ?>:</strong> <?php echo esc_html($result); ?></p>
</article>
""",
    }
    for target, content in template_parts.items():
        write(THEME / "template-parts" / target, content)

    print(f"Exported {THEME}")


if __name__ == "__main__":
    main()
