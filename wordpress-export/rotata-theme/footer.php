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
  <div class="footer-legal container"><span>© <?php echo esc_html(date('Y')); ?> Rotata Consulting SL</span><a href="<?php echo esc_url(home_url('/privacy/')); ?>">Privacidad</a><a href="<?php echo esc_url(home_url('/legal/')); ?>">Legal</a><a href="<?php echo esc_url(home_url('/cookies/')); ?>">Cookies</a></div>
</footer>

<?php wp_footer(); ?></body></html>
