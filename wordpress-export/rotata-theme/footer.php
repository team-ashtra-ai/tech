</main>
<footer class="site-footer">
  <div class="container footer-shell">
    <div class="footer-top">
      <div class="footer-brand">
        <p class="eyebrow"><?php esc_html_e('Sistema B2B', 'rotata'); ?></p>
        <img src="<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/logo/rotata-white-logo-dark-ui.svg'); ?>" width="156" height="40" alt="Rotata" />
        <p class="footer-positioning"><?php esc_html_e('El sistema detrás del crecimiento B2B.', 'rotata'); ?></p>
        <p class="footer-summary"><?php esc_html_e('Rotata estructura CRM, datos, automatización y pipeline dentro de un único sistema operativo comercial.', 'rotata'); ?></p>
        <div class="footer-inline-tools">
          
          <a class="btn btn-secondary" href="<?php echo esc_url(home_url('/contacto/')); ?>" data-track="cta_click"><?php esc_html_e('Diagnosticar sistema', 'rotata'); ?></a>
        </div>
      </div>
      <div class="footer-highlights">
        <article class="footer-highlight"><span>01</span><strong><?php esc_html_e('Estructura primero', 'rotata'); ?></strong><p><?php esc_html_e('La herramienta entra después de definir la lógica operativa.', 'rotata'); ?></p></article><article class="footer-highlight"><span>02</span><strong><?php esc_html_e('Una lectura compartida', 'rotata'); ?></strong><p><?php esc_html_e('Marketing, ventas y reporting trabajan sobre la misma estructura.', 'rotata'); ?></p></article><article class="footer-highlight"><span>03</span><strong><?php esc_html_e('Movimiento medible', 'rotata'); ?></strong><p><?php esc_html_e('La mejora se lee en datos, velocidad y calidad de pipeline.', 'rotata'); ?></p></article>
      </div>
    </div>
    <div class="footer-grid">
      <div class="footer-column">
        <h2 class="footer-heading"><?php esc_html_e('Explorar', 'rotata'); ?></h2>
        <?php wp_nav_menu(['theme_location' => 'footer', 'container' => 'nav', 'container_class' => 'footer-links', 'fallback_cb' => false]); ?>
      </div>
      <div class="footer-column">
        <h2 class="footer-heading"><?php esc_html_e('Lo que ordenamos', 'rotata'); ?></h2>
        <div class="footer-system-list"><span><?php esc_html_e('Arquitectura CRM', 'rotata'); ?></span><span><?php esc_html_e('Señales y priorización', 'rotata'); ?></span><span><?php esc_html_e('Automatización y handoffs', 'rotata'); ?></span><span><?php esc_html_e('Medición conectada al pipeline', 'rotata'); ?></span></div>
      </div>
      <div class="footer-column">
        <h2 class="footer-heading"><?php esc_html_e('Contacto', 'rotata'); ?></h2>
        <p><a href="tel:+34649498272">+34 649 49 82 72</a></p>
        <p><a href="mailto:info@rotata.com">info@rotata.com</a></p>
        <p><a href="https://www.linkedin.com/company/rotata-consulting-sl/" data-track="linkedin_click">LinkedIn</a></p>
        <p><a href="<?php echo esc_url(home_url('/cookies/')); ?>" data-open-cookie-preferences><?php esc_html_e('Preferencias de cookies', 'rotata'); ?></a></p>
        <p><a href="<?php echo esc_url(home_url('/cookies/')); ?>"><?php esc_html_e('Política de cookies', 'rotata'); ?></a></p>
      </div>
    </div>
  </div>
  <div class="container funding-strip"><img src="<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/partners/rotata-kit-digital-eu-funding.png'); ?>" alt="Kit Digital, Gobierno de España, Red.es, Next Generation EU y Plan de Recuperación"><span><?php esc_html_e('Programa Kit Digital y financiación europea, conservado desde el sitio original de Rotata.', 'rotata'); ?></span></div>
  <div class="footer-legal container"><span>© <?php echo esc_html(date('Y')); ?> Rotata Consulting SL</span><span><?php esc_html_e('Diseñado para claridad operativa, señal comercial y crecimiento medible.', 'rotata'); ?></span><div class="footer-legal-links"><a href="<?php echo esc_url(home_url('/privacy/')); ?>"><?php esc_html_e('Privacidad', 'rotata'); ?></a><a href="<?php echo esc_url(home_url('/legal/')); ?>"><?php esc_html_e('Legal', 'rotata'); ?></a><a href="<?php echo esc_url(home_url('/cookies/')); ?>" data-open-cookie-preferences><?php esc_html_e('Cookies', 'rotata'); ?></a><a href="<?php echo esc_url(home_url('/accessibility/')); ?>"><?php esc_html_e('Accesibilidad', 'rotata'); ?></a><a href="<?php echo esc_url(home_url('/sitemap/')); ?>"><?php esc_html_e('Mapa del sitio', 'rotata'); ?></a></div></div>
</footer>

<div class="floating-actions" aria-label="Quick actions">
  <button class="float-button back-to-top" type="button" data-back-to-top aria-label="<?php esc_attr_e('Volver arriba', 'rotata'); ?>">↑</button>
  <a class="float-button whatsapp" href="https://wa.me/34649498272" aria-label="<?php esc_attr_e('Hablar por WhatsApp', 'rotata'); ?>" data-track="whatsapp_click">WA</a>
  <button class="float-button rotbot-button" type="button" data-rotbot-toggle aria-expanded="false" aria-controls="rotbot-panel" aria-label="<?php esc_attr_e('Abrir Soy Rotbot', 'rotata'); ?>"><img src="<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/images/rotata-rotbot-ai-assistant.png'); ?>" alt=""></button>
</div>
<aside class="rotbot-panel" id="rotbot-panel" data-rotbot-panel hidden>
  <div class="rotbot-head"><img src="<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/images/rotata-rotbot-ai-assistant.png'); ?>" alt=""><div><strong>Soy Rotbot</strong><span><?php esc_html_e('Asistente de sistemas B2B', 'rotata'); ?></span></div><button class="rotbot-close" type="button" data-rotbot-close aria-label="Close">×</button></div>
  <div class="rotbot-messages" data-rotbot-messages><p class="rotbot-message bot"><?php esc_html_e('Hola. Puedo ayudarte a ubicar el problema: CRM, datos, outbound, ROI o automatización.', 'rotata'); ?></p></div>
  <div class="rotbot-prompts"><a href="<?php echo esc_url(home_url('/contacto/')); ?>" data-track="cta_click"><?php esc_html_e('Hablar con Rotata', 'rotata'); ?></a></div>
</aside>
<section class="cookie-banner" data-cookie-banner hidden aria-label="Cookie preferences">
  <div class="cookie-copy">
    <p class="cookie-label"><?php esc_html_e('Cookies', 'rotata'); ?></p>
    <div>
      <strong><?php esc_html_e('Privacidad y cookies', 'rotata'); ?></strong>
      <span><?php esc_html_e('Usamos cookies necesarias para que el sitio funcione. Si aceptas, activamos también analítica, marketing y preferencias para mejorar la experiencia.', 'rotata'); ?></span>
    </div>
  </div>
  <div class="cookie-actions">
    <button class="cookie-chip cookie-chip-accept" type="button" data-cookie-accept><?php esc_html_e('Aceptar todo', 'rotata'); ?></button>
    <a class="cookie-chip" href="<?php echo esc_url(home_url('/cookies/')); ?>"><?php esc_html_e('Leer política', 'rotata'); ?></a>
    <button class="cookie-chip" type="button" data-cookie-necessary><?php esc_html_e('Solo necesarias', 'rotata'); ?></button>
    <button class="cookie-chip cookie-chip-reject" type="button" data-cookie-reject><?php esc_html_e('Rechazar', 'rotata'); ?></button>
  </div>
</section>

<?php wp_footer(); ?></body></html>
