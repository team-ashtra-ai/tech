# Deployment

Cloudflare Pages deploys from GitHub.

For the main generated site:

- Build command: `npm run build`
- Output directory: `dist`
- Keep env vars in Cloudflare.
- Use deployment rollback for emergency recovery.

For the independent static concept sites:

- Root directory: one folder under `static-sites/`
- Build command: leave blank
- Output directory: `/`
- Keep Formspree endpoint IDs in that folder's `content/forms.json`.

These no-build folders are copied out from the authored exports and should be deployed as standalone static roots.
