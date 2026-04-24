<form class="form contact-form" data-form="contact" novalidate>
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
