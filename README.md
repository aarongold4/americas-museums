# americasmuseums.com — starter

Astro + Tailwind + content collections. Travel Utility design system, conversion-tight museum pages, ready for a 33,000-page programmatic build.

## Quick start

```bash
npm install
npm run dev      # localhost:4321
```

You'll see:
- `/` — directory landing
- `/best-museums-in-chicago/` — the city hub
- `/museum/art-institute-of-chicago/` — a museum page (and 10 others)

```bash
npm run build    # production build → ./dist/
npm run preview  # serve the built site
```

## Architecture

```
src/
├── content/
│   ├── config.ts                # Zod schema for museums + cities collections
│   ├── museums/                 # one JSON file per museum (slug = filename)
│   └── cities/
│       └── chicago.mdx          # editorial intro + ranked museum slugs in frontmatter
├── pages/
│   ├── index.astro
│   ├── best-museums-in-[city].astro    # /best-museums-in-chicago/
│   └── museum/[slug].astro      # /museum/art-institute-of-chicago/
├── components/
│   ├── NavBar.astro
│   ├── MuseumCard.astro         # the Booking-style card
│   ├── TicketBox.astro          # the conversion-tight CTA
│   ├── Schema.astro             # JSON-LD Museum/LocalBusiness markup
│   └── Footer.astro
├── layouts/
│   └── BaseLayout.astro         # head, OG/Twitter tags, GA4, GSC verify
└── styles/globals.css

scripts/
├── ingest_imls.ts                # IMLS CSV → normalized JSON (skeleton)
├── enrich_places.ts              # Google Places enrichment (skeleton)
├── match_affiliates.ts           # museum × inventory → best offer (RUNNABLE)
└── build_dataset.ts              # joins everything into per-museum JSON

public/
├── _headers                      # Cloudflare Pages cache + security headers
├── _redirects                    # path-level redirects
├── favicon.svg
├── og-default.png                # 1200×630 OG card
└── robots.txt
```

## Adding content

**A new museum:** create `src/content/museums/{slug}.json` matching `src/content/config.ts`. Page at `/museum/{slug}/` is generated on next build.

**A new city hub:** create `src/content/cities/{city-slug}.mdx`. In frontmatter, set `museum_slugs` to the ranking. Body is markdown for the editorial intro.

## Photos

Each museum supports `hero_image` (one URL) and `gallery_images` (array of URLs). When present, the museum page and city-hub card use them; when absent, a discipline-colored swatch is shown — so the site is launchable before any photos are wired up.

**Recommended production source:** Google Places `photo_reference`, proxied through a Cloudflare Worker.

The flow:
1. `enrich_places.ts` writes `photo_refs[]` per museum (Google `photo_reference` tokens).
2. `build_dataset.ts` writes proxy URLs into each museum JSON: `https://americasmuseums.com/img/{photo_ref}?w=600`.
3. A Worker at `/img/*` calls Google's Place Photo API server-side and caches the response.

About 30 lines of Worker code; ready to add when we have a Places API key. Alternative: Cloudflare Images ($5/mo + delivery) — simpler, paid.

## Going to scale (the 33K-page version)

### 1. Get the IMLS Museum Universe Data File
Download from https://www.imls.gov/research-evaluation/data-collection/museum-data-files. Drop it as `data/01_raw/imls_museums.csv`.

### 2. Normalize
```bash
npm run ingest:imls
```
Writes `data/02_enriched/imls_normalized.json`.

### 3. Enrich with Google Places
```bash
GOOGLE_PLACES_API_KEY=xxx npm run enrich:places
```
Cost: ~$0.005 per museum, ~$165 for the full dataset, then a few dollars/week to refresh the top traffic pages. Caches in `places_cache.json`.

### 4. Match affiliate offers (nightly)
```bash
npm run match:affiliates
```
Reads inventory from `data/02_enriched/affiliate_inventory/{network}.json`, fuzzy-matches each museum to the highest-payout offer within 1 km. Writes `affiliate_offers.json` plus an unmatched list.

The matcher is fully runnable — it's the per-network inventory fetchers that are still TODO. Each fetcher needs ~50 lines and an auth pattern:

| Network          | Inventory source                       | Auth                  |
|------------------|----------------------------------------|-----------------------|
| GetYourGuide     | Partner API: `/v1/locations/{loc}/tours` | Partner ID + API key  |
| Tiqets           | Affiliate JSON feed                    | Affiliate ID          |
| Viator           | Awin product feed (CSV)                | Awin publisher ID     |
| Go City          | Affiliate-product API                  | API key               |

### 5. Build the final dataset
```bash
npm run build:dataset
```
Joins everything into per-museum JSON files in `src/content/museums/`. **Caution:** overwrites the 11 hand-written sample files — protect them with git first, or change `OUT_DIR` in the script.

### 6. Astro build
```bash
npm run build
```
Generates 33K+ static pages plus a sitemap index.

## Deployment — Cloudflare Pages

### 1. Push to GitHub
```bash
git init
git add -A
git commit -m "Initial commit"
git remote add origin git@github.com:{your-username}/americas-museums.git
git push -u origin main
```

### 2. Connect to Cloudflare Pages
- https://dash.cloudflare.com → Pages → Create a project → Connect to Git
- Build command: `npm run build`
- Build output directory: `dist`
- Environment variables → add:
  - `PUBLIC_GA_ID` = `G-XXXXXXXXXX`
  - `PUBLIC_GSC_VERIFY` = the content of the GSC meta tag

The first deploy lands at `{project-name}.pages.dev`. Verify it loads, then move on to the custom domain.

### 3. Point americasmuseums.com to Cloudflare
- Cloudflare → Add a Site → `americasmuseums.com`
- Cloudflare gives you two nameservers (e.g. `kim.ns.cloudflare.com`, `walt.ns.cloudflare.com`)
- Dynadot → Domain → Nameservers → set to those two
- Propagation: 5 min – 24 hr (check with `dig americasmuseums.com NS`)

Then in your Pages project → Custom domains → Add → `americasmuseums.com`. CNAME is added automatically.

### 4. 301 the secondary domain
- Add `americasbestmuseums.com` to Cloudflare (same nameserver flip)
- In its zone → Rules → Single Redirects → Create a rule:
  - When: `Hostname` equals `americasbestmuseums.com`
  - Then: Static redirect to `https://americasmuseums.com${http.request.uri.path}`, 301
- This preserves every path: `/foo/bar` on the secondary redirects to the same path on the primary.

### 5. Verify SEO endpoints
- `https://americasmuseums.com/sitemap-index.xml` → returns XML
- `https://americasmuseums.com/robots.txt` → references the sitemap
- `https://americasmuseums.com/og-default.png` → loads
- View-source any page → GA4 `gtag('config', ...)` is rendered

### 6. Submit to GSC and Bing
- GSC → Add property → URL prefix `https://americasmuseums.com/` → verify via meta tag (`PUBLIC_GSC_VERIFY`) → Sitemaps → submit `sitemap-index.xml`
- Bing Webmaster Tools → Add a site → import from GSC

## Affiliate setup (apply in this order)

1. **GetYourGuide partner program** — https://partner.getyourguide.com/ — 8%, broadest US museum coverage
2. **Tiqets** — https://www.tiqets.com/en/affiliates/ — 10% on entries
3. **Viator** (via Awin) — https://www.viator.com/affiliate/
4. **Go City / CityPASS** — multi-attraction passes
5. **Booking.com** — for hotel CTAs on "where to stay near {museum}" later
6. **Amazon Associates** — books, audio guides, art prints

## Display ad strategy

- **AdSense first**, once 30+ pages have meaningful editorial content (not just programmatic stubs).
- **Migrate to Mediavine or Raptive at 50K monthly sessions.** Travel-niche RPM is roughly 2× AdSense.
- The two AdSense rejection traps: thin programmatic city pages (write the editorial intro first, always) and broken affiliate links (the affiliate-match job prevents this).

## Performance

The Travel Utility theme is close to vanilla CSS — DM Sans loaded once, no client JS, just Astro's static output. A typical museum page weighs ~30KB without photos. Lighthouse should hit 95+ across the board. Don't break this lightly: every third-party script eats into the SEO advantage of being faster than competitors.
