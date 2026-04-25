# Multilingual

Spanish is default. English and French use prefixed URLs, translated nav/footer/CTAs/forms/cookie text, hreflang and canonical logic.

- Core page copy lives in `src/data/site.json`.
- Spanish blog source articles live in `src/content/es/blog/`.
- Generated blog translations live in `src/content/en/blog/` and `src/content/fr/blog/`.
- Run `npm run blog:translate` after updating Spanish blog articles so localized article pages stay in sync.
- Blog article pages now publish under `/insights/blog/<slug>/`, `/en/insights/blog/<slug>/` and `/fr/insights/blog/<slug>/`.
