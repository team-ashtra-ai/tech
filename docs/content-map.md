# Content Map

Content is modular in `src/data/site.json`, `src/data/*.json` and `src/content/<lang>/`. Blog articles are JSON files under `src/content/es/blog`, with generated English and French variants under `src/content/en/blog` and `src/content/fr/blog`.

- `src/data/site.json` is the source-of-truth content library for both reusable source pages and route-specific page keys used by `src/data/navigation.json`.
- Route section models also live in `src/data/site.json`. Keep each page's section order aligned to its narrative model: `hero -> context/problem -> system -> outcome -> action`.
- `src/data/showcase-sites.json` is the source-of-truth metadata for the five standalone concept sites shown in the header demo bar.
- `src/data/themes.json` is retained for legacy token experiments and generated CSS overrides.
- Page-level CTA targets can be controlled in `src/data/site.json` with `primary_cta_page`, `secondary_cta_page`, `final_cta_page` or direct `*_cta_url` values.
- Newsletter page routing and copy live in `src/data/navigation.json`, `src/data/site.json` and `src/data/forms.json`, while the reusable form partial is `src/partials/forms/newsletter-form.html`.
