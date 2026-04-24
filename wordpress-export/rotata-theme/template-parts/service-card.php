<?php
$title = $args['title'] ?? '';
$text = $args['text'] ?? '';
$icon = $args['icon'] ?? get_template_directory_uri() . '/assets/images/assets/icons/rotata-system-icon.svg';
?>
<article class="system-card">
  <img src="<?php echo esc_url($icon); ?>" alt="" loading="lazy">
  <h3><?php echo esc_html($title); ?></h3>
  <p><?php echo esc_html($text); ?></p>
</article>
