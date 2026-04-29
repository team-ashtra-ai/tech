# DataGrail Visual Handoff

This document covers the current English DataGrail showcase implementation under `/en/showcase/datagrail/`. It is meant to give a designer and engineer enough detail to restyle, enhance, and rebuild the same experience on another site without reverse-engineering the current codebase first.

## Scope

- Home route uses a custom template: `src/partials/theme-sites/datagrail.html`
- All subpages use the shared showcase detail renderer in `scripts/build_site.py`
- DataGrail-specific styling lives in `src/styles/theme-sites/datagrail.css`
- Shared subpage styling lives in `src/styles/theme-sites/shared-pages.css`
- DataGrail JS is thin: `src/scripts/theme-sites/datagrail.js` imports `src/scripts/theme-sites/shared.js`
- Page and section imagery is generated into `src/assets/theme-sites/`

## Visual identity

The theme reads as operational privacy software with a human-control layer, not as a generic SaaS marketing site.

- Primary dark surface: deep teal `#004957`
- Header gradient anchors: `#07130f`, `#102c24`, `#171b2c`
- Accent mint: `#00d99a`
- Light mint background: `#effaf6`
- Base page background: white `#ffffff`
- Main text: `#111814`
- Secondary text: `#4c5d58`
- Border tone: `#dfe5e1`

Typography is mixed on purpose:

- Display and major section headings use `Georgia, "Times New Roman", serif`
- Body, nav, buttons, cards, and utility text use `Aptos`, `Segoe UI`, or fallback sans

Shape language is soft but not playful:

- Major cards and image frames: `22px` radius
- Secondary panels: `18px` to `26px`
- Buttons and chips: full pill radius
- Shadows are broad and soft, especially on hero/browser panels

## Overall page shell

Every DataGrail page has three persistent layers before the main content:

1. Sticky header
2. Sticky concept switcher
3. Main page body

### Sticky header

The header is the strongest brand signal in the theme.

- It is sticky with a dark gradient background and a faint grid/glow overlay
- Top note bar contains:
  - `Vera agent` pill
  - `Human controls for the growth system.`
  - `Map system` link
- Main row contains:
  - Rotata logo
  - desktop nav on large screens
  - `Contact Us` secondary action
  - `Get a demo` primary action
  - mobile menu button on smaller screens

Desktop nav styling:

- Rounded container with translucent dark background
- Parent nav items are compact pills
- Hover/current state uses mint-tinted fill
- Dropdowns open as light cards with dark text

Mobile nav styling:

- Full-screen overlay
- Same dark gradient background as header
- Large stacked links inside rounded bordered blocks
- Grouped sections expand with `+` / `-`

### Sticky concept switcher

The showcase switcher sits below the header and is also sticky.

- Light background
- Thin bottom border
- Horizontal pill links with small gradient swatches
- Current site chip becomes dark with white text
- Label reads `Website concepts`

## Home page anatomy

The home page is not rendered from the shared subpage shell. It is a custom composition with five main content bands.

### 1. Hero

Layout:

- Two-column grid on desktop
- Left: copy block
- Right: HTML-built browser/dashboard mockup
- Background is a dark teal field with the generated hero image placed at the right edge

Copy style:

- Small uppercase mint eyebrow
- Large serif headline
- Supporting body in a larger sans treatment
- Two pill CTAs

The hero mockup is not an image. It is assembled in HTML with:

- Browser dots
- Left sidebar labels
- Two white dashboard cards
- Mint outline on the primary card

### 2. Trust strip

- White background
- Center-aligned serif heading
- Partner names laid out as a simple logo-text strip

### 3. Program section

- White background
- Centered heading block
- Large serif intro line above the main heading
- Three-up risk card grid on desktop
- Each card uses a geometric mint-to-teal icon block generated with `clip-path`

### 4. Agent section

- Light mint background
- Two-column layout
- Left: copy
- Right: bordered white panel containing process steps
- Process cards are stacked vertically and feel like workflow states

### 5. Controls section

- Full dark teal band
- White text
- Two-column layout: copy left, metric/control grid right
- Control cards use translucent dark-over-light panels with mint copy accents

### 6. Resources section

- White background
- Serif heading
- Three article cards on desktop
- Card CTA text stays text-link simple rather than buttoned

### Footer

- Dark teal background
- Left column: logo plus one-paragraph summary
- Right area: four-column link grid

## Detail page template

All non-home DataGrail routes share one rendering pattern.

### Hero

- Two-column layout from `shared-pages.css`
- Left: eyebrow, H1, intro, two CTAs
- Right: framed visual
- Visual uses an image with a bottom caption overlay
- Caption shows page label on the left and `DataGrail` on the right
- Background is a flat or softly glowing field driven by `--concept-hero-bg`

### Content sections

Each content section follows the same structure:

- Section number
- Small uppercase kicker derived from content variant
- Large serif H2
- Supporting paragraph
- Optional grid/process/metrics cards
- Right-side image frame with bottom caption

Alternation:

- Even sections switch to the pale mint alternate background
- Image/copy order alternates left-right on each section

Card behavior by variant:

- `grid`: three-up card layout
- `metrics`: four-up card layout
- `process`: four-up process layout
- `partners` and `blog-preview`: specialized card grids

### Final CTA

- Full-width mint/accent block at the bottom of each detail page
- Large heading on the left
- White pill button on the right

## Special page types

### Partners overview

- Same shared hero and section pattern
- Ends with a `Partner roles` card grid

### Blog page

- Same shared hero and section pattern
- Ends with a `Recent articles` card grid
- Article cards use category, title, excerpt, and `Read more`

### ROI page

- Same shared hero and section pattern
- Ends with a two-column ROI panel
- Left side shows the `€0` default output
- Right side shows four numeric fields

### Contact and consult pages

- Same shared hero and section pattern
- Ends with a two-column contact panel
- Left side explains the consultation
- Right side holds the form

### Legal pages

Legal pages keep the same shell, not a stripped compliance template.

- They still use the showcase hero
- They still use alternating content bands
- Generated visuals are schematic card-grid illustrations, not document screenshots

## Component inventory

Primary reusable components in this theme:

- Sticky announcement bar
- Desktop dropdown nav
- Mobile fullscreen nav overlay
- Concept switcher chips
- Home hero browser mockup
- Risk cards
- Process step cards
- Control/metric cards
- Article proof cards
- Detail-page image frame with caption overlay
- Final CTA band
- Footer link grid

## Responsive behavior

Key breakpoints:

- `520px`: primary header CTA appears
- `760px`: header padding opens up and note-bar CTA appears
- `1121px`: full header spacing and sticky switcher offset change
- `1280px`: desktop nav appears; mobile menu button disappears
- `980px` and below for home sections: major home layouts collapse to one column
- `1120px` and below for detail pages: shared page hero, sections, forms, and CTA grids collapse to one column

Mobile behavior is simple:

- No split-screen hero
- No sidebar in the browser mockup
- Card grids stack to one column
- Footer becomes one column

## Motion and interaction

Current JS behavior is intentionally light.

- Menu button toggles the mobile panel
- `Escape` closes the mobile panel
- `html.concept-menu-open` locks page scroll while the mobile menu is open
- Smooth scrolling is enabled at the document level

There is no complex animation system unique to DataGrail beyond CSS hover/open states.

## Imagery and art direction

The visual system does not use product screenshots. It uses generated editorial-tech illustrations.

Shared characteristics of the generated assets:

- Very pale mint/white canvas
- Thin mint line work
- Soft glow around panels
- Left content rail plus right diagram/dashboard composition
- Rounded boxes, short chip labels, charts, tables, or schematic cards
- Abstract circular line motifs behind the main composition

Observed page-family differences:

- Growth/system pages lean on charts, progress lines, and dashboard panels
- Legal pages lean on repeated document-card grids
- Contact and consult pages lean on structured card/panel layouts
- Partner pages lean on labeled system blocks and fit mapping

Asset rules:

- Primary page hero assets follow `src/assets/theme-sites/datagrail-{page_key}.webp`
- Section assets follow `src/assets/theme-sites/datagrail-{page_key}-{nn}.webp`
- If a section-specific asset is missing, the renderer falls back to the page-level asset

## Implementation map

If another engineer is rebuilding this theme, these files are the current source of truth:

- Home markup: [src/partials/theme-sites/datagrail.html](/home/ash/www.ash-tra.com/tech/src/partials/theme-sites/datagrail.html)
- DataGrail theme CSS: [src/styles/theme-sites/datagrail.css](/home/ash/www.ash-tra.com/tech/src/styles/theme-sites/datagrail.css)
- Shared detail-page CSS: [src/styles/theme-sites/shared-pages.css](/home/ash/www.ash-tra.com/tech/src/styles/theme-sites/shared-pages.css)
- Theme JS entry: [src/scripts/theme-sites/datagrail.js](/home/ash/www.ash-tra.com/tech/src/scripts/theme-sites/datagrail.js)
- Shared showcase menu JS: [src/scripts/theme-sites/shared.js](/home/ash/www.ash-tra.com/tech/src/scripts/theme-sites/shared.js)
- Route and page rendering logic: [scripts/build_site.py](/home/ash/www.ash-tra.com/tech/scripts/build_site.py)
- Showcase site registry: [src/data/showcase-sites.json](/home/ash/www.ash-tra.com/tech/src/data/showcase-sites.json)
- Source copy library: [src/data/site.json](/home/ash/www.ash-tra.com/tech/src/data/site.json)
- Generated DataGrail imagery: [src/assets/theme-sites](/home/ash/www.ash-tra.com/tech/src/assets/theme-sites)

## Rebuild notes

If this is being moved to another site, preserve these structural decisions unless there is a deliberate redesign:

- Keep the serif/sans split
- Keep the dark privacy-control header separate from the light content body
- Keep the mint accent restrained and functional
- Keep the home page distinct from the generic detail-page shell
- Keep the subpages on a numbered, alternating section rhythm
- Keep the generated-image system replaceable without changing the page structure

The main architectural fact is that this is not a screenshot-led product site. It is a premium operational-system concept built from structured copy, card grids, and generated schematic visuals.
