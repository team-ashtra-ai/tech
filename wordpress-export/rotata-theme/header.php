<!doctype html><html <?php language_attributes(); ?>><head><?php wp_head(); ?></head><body <?php body_class(); ?>>
<a class="skip-link" href="#main"><?php esc_html_e('Saltar al contenido', 'rotata'); ?></a>
<header class="site-header" data-site-header>
  <div class="container header-shell">
      <a class="brand" href="<?php echo esc_url(home_url('/')); ?>" aria-label="<?php esc_attr_e('Inicio de Rotata', 'rotata'); ?>">
      <img src="<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/logo/rotata-b2b-growth-system-logo.svg'); ?>" width="154" height="40" alt="Rotata" />
    </a>
    <?php wp_nav_menu(['theme_location' => 'primary', 'container' => 'nav', 'container_class' => 'nav-desktop', 'fallback_cb' => false]); ?>
    <div class="header-actions">
      
      <button class="theme-toggle" type="button" data-theme-toggle aria-label="<?php esc_attr_e('Cambiar modo claro y oscuro', 'rotata'); ?>"><span></span></button>
      <a class="btn btn-primary" data-track="cta_click" href="<?php echo esc_url(home_url('/contacto/')); ?>"><?php esc_html_e('Diagnosticar sistema', 'rotata'); ?></a>
      <button class="menu-toggle" type="button" data-menu-toggle aria-expanded="false" aria-controls="mobile-menu"><span></span><span></span><span></span></button>
    </div>
  </div>
  <div class="mobile-panel" id="mobile-menu" data-mobile-menu hidden><?php wp_nav_menu(['theme_location' => 'primary', 'container' => 'nav', 'container_class' => 'nav-mobile', 'fallback_cb' => false]); ?></div>
</header>

<main id="main">
