<?php
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
?>