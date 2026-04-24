<?php
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
