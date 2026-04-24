<!doctype html><html <?php language_attributes(); ?>><head><?php wp_head(); ?></head><body <?php body_class(); ?>>
<a class="skip-link" href="#main"><?php esc_html_e('Saltar al contenido', 'rotata'); ?></a>
<header class="site-header" data-site-header>
  <div class="utility-bar">
    <div class="container utility-shell">
      <span class="utility-line"><?php esc_html_e('Sistemas B2B con CRM, datos, automatización y pipeline', 'rotata'); ?></span>
      <div class="utility-controls">
        
        <button class="theme-toggle" type="button" data-theme-toggle data-theme-dark-label="<?php esc_attr_e('Oscuro', 'rotata'); ?>" data-theme-light-label="<?php esc_attr_e('Claro', 'rotata'); ?>" aria-label="<?php esc_attr_e('Cambiar modo claro y oscuro', 'rotata'); ?>">
          <span aria-hidden="true"></span>
          <em data-theme-label><?php esc_html_e('Dark', 'rotata'); ?></em>
        </button>
      </div>
    </div>
  </div>
  <div class="container header-shell">
    <a class="brand" href="<?php echo esc_url(home_url('/')); ?>" aria-label="<?php esc_attr_e('Inicio de Rotata', 'rotata'); ?>">
      <img src="<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/logo/rotata-b2b-growth-system-logo.svg'); ?>" width="154" height="40" alt="Rotata" />
    </a>
    <?php wp_nav_menu(['theme_location' => 'primary', 'container' => 'nav', 'container_class' => 'nav-desktop', 'fallback_cb' => false]); ?>
    <div class="header-actions">
      <a class="btn btn-primary" data-track="cta_click" href="<?php echo esc_url(home_url('/contacto/')); ?>"><?php esc_html_e('Diagnosticar sistema', 'rotata'); ?></a>
      <button class="menu-toggle" type="button" data-menu-toggle aria-expanded="false" aria-controls="mobile-menu"><span></span><span></span><span></span></button>
    </div>
  </div>
  <div class="mobile-panel" id="mobile-menu" data-mobile-menu hidden><button class="mobile-close" type="button" data-menu-close aria-label="<?php esc_attr_e('Cerrar menú', 'rotata'); ?>">×</button><?php wp_nav_menu(['theme_location' => 'primary', 'container' => 'nav', 'container_class' => 'nav-mobile', 'fallback_cb' => false]); ?></div>
</header>

<main id="main">
