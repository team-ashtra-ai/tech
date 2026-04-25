# Design System

The production site uses a shared token layer, and the design demo now uses five standalone concept sites so the same Rotata content can be shown through different design systems without duplicating source content.

- Base tokens live in `src/styles/tokens.css`.
- Legacy token presets live in `src/styles/themes.css`.
- URL-generated token overrides live in `src/styles/generated/theme-overrides.css`.
- Complete concept site metadata lives in `src/data/showcase-sites.json`.
- Concept partials live in `src/partials/theme-sites/`.
- Concept CSS lives in `src/styles/theme-sites/`.
- Concept JS lives in `src/scripts/theme-sites/`.
- Concept assets are generated into `src/assets/theme-sites/`.

Current concept sites:

- `databricks`
- `datagrail`
- `atlan`
- `runpod`
- `vectara`
