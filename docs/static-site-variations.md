# Static Site Variations

The `static-sites/` directory contains six independent no-build website roots for Rotata concept deployment tests.

Each folder is self-contained and can be connected to Cloudflare Pages directly from GitHub:

| Folder | Variation | Direction | Cloudflare build command | Cloudflare output directory |
| --- | --- | --- | --- | --- |
| `static-sites/rotata.es-1` | rotata.es 1 | Editorial platform system | blank | `/` |
| `static-sites/rotata.es-2` | rotata.es 2 | Operating control center | blank | `/` |
| `static-sites/rotata.ai-3` | rotata.ai 3 | Context graph system | blank | `/` |
| `static-sites/rotata.systems-4` | rotata.systems 4 | Infrastructure console | blank | `/` |
| `static-sites/rotata.growth-5` | rotata.growth 5 | Governed enterprise agent system | blank | `/` |
| `static-sites/rotata.es-6` | rotata.es 6 | Current Rotata-inspired AI system | blank | `/` |

## Structure

Each variation uses only static HTML, CSS, vanilla JavaScript, JSON and local assets.

- `en/`, `es/`, `fr/` hold localized route trees.
- Variations `1` through `5` are rebuilt from the authored showcase exports for the Databricks, DataGrail, Atlan, Runpod and Vectara concepts.
- Variation `6` is rebuilt from the authored Rotata export.
- `styles/` and `scripts/` are copied into each root so every site is deployable on its own with no build step.
- `assets/` holds local logos, WebP visuals, OG images, blog images and partner assets.
- `content/forms.json` stores the Formspree endpoint placeholders for the concept-layer form enhancer.
- `sitemap.xml`, `robots.txt`, `_headers`, `_redirects` are included for Cloudflare Pages.

## Deployment

Create a separate Cloudflare Pages project per variation when comparing concepts.

1. Connect the GitHub repository.
2. Set the root directory to the desired `static-sites/...` folder.
3. Leave the build command blank.
4. Set the output directory to `/`.
5. Deploy from the production branch.

Do not point these folders at the existing generated `dist/` build. They are copied out as independent, no-build static roots.

## Notes

The page structure, static SEO tags, schema, sitemap entries and local assets are present in every variation. The concept roots also inject a shared support layer for locale switching, floating support widgets, cookie consent, scroll reveal and Formspree-compatible contact handling.
