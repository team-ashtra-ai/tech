# Cloudflare Pages

## Generated main site

- Framework preset: None
- Build command: `npm run build`
- Output directory: `dist`
- Production branch: `main`

Add analytics, HubSpot and form IDs as environment variables. Do not commit secrets. Rollbacks are handled from the Cloudflare Pages deployments screen.

## Independent static variations

The folders under `static-sites/` are separate no-build Cloudflare Pages roots.

- Framework preset: None
- Build command: leave blank
- Output directory: `/`
- Root directory: one of `static-sites/rotata.es-1`, `static-sites/rotata.es-2`, `static-sites/rotata.ai-3`, `static-sites/rotata.systems-4`, `static-sites/rotata.growth-5`, or `static-sites/rotata.es-6`

Each variation includes its own `sitemap.xml`, `robots.txt`, `_headers`, `_redirects`, local assets, static routes and Formspree endpoint JSON.
