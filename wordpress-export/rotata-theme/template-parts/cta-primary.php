<?php
$heading = $args['heading'] ?? __('Construyamos tu sistema de crecimiento', 'rotata');
$href = $args['href'] ?? home_url('/contact/consult/');
$label = $args['label'] ?? __('Diagnosticar sistema', 'rotata');
?>
<section class="section final-cta">
  <div class="container cta-panel">
    <p class="eyebrow">Rotata</p>
    <h2><?php echo esc_html($heading); ?></h2>
    <a class="btn btn-primary" data-track="cta_click" href="<?php echo esc_url($href); ?>"><?php echo esc_html($label); ?></a>
  </div>
</section>
