</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <div>
      <img src="<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/logo/rotata-white-logo-dark-ui.svg'); ?>" width="156" height="40" alt="Rotata" />
      <p><?php esc_html_e('El sistema detrás del crecimiento B2B.', 'rotata'); ?></p>
      
    </div>
    <?php wp_nav_menu(['theme_location' => 'footer', 'container' => 'nav', 'container_class' => 'footer-links', 'fallback_cb' => false]); ?>
    <div>
      <h2 class="footer-heading"><?php esc_html_e('Contacto', 'rotata'); ?></h2>
      <p><a href="tel:+34649498272">+34 649 49 82 72</a></p>
      <p><a href="mailto:info@rotata.com">info@rotata.com</a></p>
      <p><a href="https://www.linkedin.com/company/rotata-consulting-sl/" data-track="linkedin_click">LinkedIn</a></p>
    </div>
  </div>
  <div class="container funding-strip"><img src="<?php echo esc_url(get_template_directory_uri() . '/assets/images/assets/partners/rotata-kit-digital-eu-funding.png'); ?>" alt="Kit Digital, Gobierno de España, Red.es, Next Generation EU y Plan de Recuperación"><span><?php esc_html_e('Programa Kit Digital y financiación europea, conservado desde el sitio original de Rotata.', 'rotata'); ?></span></div>
  <div class="footer-legal container"><span>© <?php echo esc_html(date('Y')); ?> Rotata Consulting SL</span><a href="<?php echo esc_url(home_url('/privacy/')); ?>">Privacidad</a><a href="<?php echo esc_url(home_url('/legal/')); ?>">Legal</a><a href="<?php echo esc_url(home_url('/cookies/')); ?>">Cookies</a></div>
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
<?php wp_footer(); ?></body></html>
