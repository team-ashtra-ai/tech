<?php get_header(); ?>
<section class="section">
  <div class="container">
    <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
      <p class="eyebrow">Rotata</p>
      <h1><?php the_title(); ?></h1>
      <div class="article-content"><?php the_content(); ?></div>
    <?php endwhile; endif; ?>
  </div>
</section>
<?php get_footer(); ?>
