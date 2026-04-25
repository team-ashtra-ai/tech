# Theme System

The current design demo is a five-site showcase, not a token-only skin switcher. The same Rotata content is rendered through five standalone concept routes with different HTML partials, CSS files, JS files and generated WebP assets.

## Source Of Truth

- `src/data/showcase-sites.json` defines the five concept sites, labels, summaries, reference URLs, assets, stylesheets, scripts and preview swatches.
- `src/partials/theme-sites/` stores the standalone HTML partial for each concept.
- `src/styles/theme-sites/` stores independent CSS for each concept.
- `src/scripts/theme-sites/` stores small concept-specific interactions.
- `src/assets/theme-sites/` stores generated WebP concept assets created by `scripts/generate_showcase_assets.py`.
- `src/partials/theme/theme-preview-bar.html` remains the reusable thin bar above the normal site controls; it now links to the standalone concept routes.

## Concept Routes

- `/en/showcase/databricks/`
- `/en/showcase/datagrail/`
- `/en/showcase/atlan/`
- `/en/showcase/runpod/`
- `/en/showcase/vectara/`

Spanish and French variants are generated at `/showcase/<id>/` and `/fr/showcase/<id>/`.

## Reference Direction

- Databricks: clear editorial platform layout.
- DataGrail: operational privacy and control-map layout.
- Atlan: context graph and data marketplace layout.
- Runpod: dark infrastructure console layout.
- Vectara: enterprise agent and guardrail layout.

The concepts are reference-inspired only. They reuse Rotata positioning and generated Rotata assets; they do not copy reference text or proprietary assets.

## URL Builder

The older token builder is still available for future experiments, but it does not create complete concept sites. Use it only to analyze a reference URL into token overrides:

```bash
python3 scripts/theme_builder.py https://example.com signal-paper --label "Example Theme"
```

Useful options:

- `--surface light`
- `--surface dark`
- `--dry-run`

The builder updates:

- `src/data/themes.json`
- `src/styles/generated/theme-overrides.css`

Then rebuild the site:

```bash
npm run build
npm run wp:export
```
