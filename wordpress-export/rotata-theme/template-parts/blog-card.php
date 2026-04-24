<?php
$post_id = $args['post_id'] ?? get_the_ID();
?>
<article class="blog-card">
  <a href="<?php echo esc_url(get_permalink($post_id)); ?>">
    <?php echo get_the_post_thumbnail($post_id, 'large', ['loading' => 'lazy']); ?>
    <span><?php echo esc_html(get_the_category($post_id)[0]->name ?? __('Insights', 'rotata')); ?></span>
    <h3><?php echo esc_html(get_the_title($post_id)); ?></h3>
    <p><?php echo esc_html(get_the_excerpt($post_id)); ?></p>
    <small><?php echo esc_html(get_the_date('', $post_id)); ?></small>
  </a>
</article>
