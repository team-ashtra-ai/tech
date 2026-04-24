#!/usr/bin/env python3
"""Export the static Rotata source into a future-editable WordPress theme."""
from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
THEME = ROOT / "wordpress-export/rotata-theme"
SRC = ROOT / "src"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def hydrate_wordpress_partial(markup: str) -> str:
    """Replace static-build placeholders with WordPress-safe defaults."""
    replacements = {
        "{{skip_label}}": "<?php esc_html_e('Saltar al contenido', 'rotata'); ?>",
        "{{home_label}}": "<?php esc_attr_e('Inicio de Rotata', 'rotata'); ?>",
        "{{theme_label}}": "<?php esc_attr_e('Cambiar modo claro y oscuro', 'rotata'); ?>",
        "{{home_url}}": "<?php echo esc_url(home_url('/')); ?>",
        "{{logo}}": "<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/logo/rotata-b2b-growth-system-logo.svg'); ?>",
        "{{logo_white}}": "<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/logo/rotata-white-logo-dark-ui.svg'); ?>",
        "{{cta_url}}": "<?php echo esc_url(home_url('/contacto/')); ?>",
        "{{cta_label}}": "<?php esc_html_e('Diagnosticar sistema', 'rotata'); ?>",
        "{{positioning}}": "<?php esc_html_e('El sistema detrás del crecimiento B2B.', 'rotata'); ?>",
        "{{contact_title}}": "<?php esc_html_e('Contacto', 'rotata'); ?>",
        "{{language_switcher}}": "",
        "{{nav_desktop}}": "<?php wp_nav_menu(['theme_location' => 'primary', 'container' => 'nav', 'container_class' => 'nav-desktop', 'fallback_cb' => false]); ?>",
        "{{nav_mobile}}": "<div class=\"mobile-panel\" id=\"mobile-menu\" data-mobile-menu hidden><?php wp_nav_menu(['theme_location' => 'primary', 'container' => 'nav', 'container_class' => 'nav-mobile', 'fallback_cb' => false]); ?></div>",
        "{{footer_links}}": "<?php wp_nav_menu(['theme_location' => 'footer', 'container' => 'nav', 'container_class' => 'footer-links', 'fallback_cb' => false]); ?>",
        "{{footer_legal}}": "<div class=\"footer-legal container\"><span>© <?php echo esc_html(date('Y')); ?> Rotata Consulting SL</span><a href=\"<?php echo esc_url(home_url('/privacy/')); ?>\">Privacidad</a><a href=\"<?php echo esc_url(home_url('/legal/')); ?>\">Legal</a><a href=\"<?php echo esc_url(home_url('/cookies/')); ?>\">Cookies</a></div>",
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
    write(
        THEME / "header.php",
        "<!doctype html><html <?php language_attributes(); ?>><head><?php wp_head(); ?></head><body <?php body_class(); ?>>\n"
        + header
        + "\n<main id=\"main\">\n",
    )
    write(
        THEME / "footer.php",
        "</main>\n" + footer + "\n<?php wp_footer(); ?></body></html>\n",
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
$href = $args['href'] ?? home_url('/contacto/');
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
