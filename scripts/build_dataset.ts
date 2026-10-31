/**
 * Final dataset build.
 *
 * Joins:
 *   - data/02_enriched/imls_normalized.json      (the seed)
 *   - data/02_enriched/places_cache.json         (Google enrichment)
 *   - data/02_enriched/affiliate_offers.json     (nightly affiliate match)
 *
 * Writes one JSON file per museum into src/content/museums/{slug}.json,
 * matching the schema in src/content/config.ts. Astro picks them up
 * automatically as a content collection.
 *
 * For the starter you've already got 10 hand-written sample files in
 * src/content/museums/. This script overwrites them with real data once
 * the upstream files exist — so use git to protect the starter samples
 * before running, or rename the output dir.
 */

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';

const NORMALIZED = 'data/02_enriched/imls_normalized.json';
const PLACES = 'data/02_enriched/places_cache.json';
const AFFILIATE = 'data/02_enriched/affiliate_offers.json';
const OUT_DIR = 'src/content/museums';

interface MatchedOffer {
  network: 'getyourguide' | 'tiqets' | 'viator' | 'gocity';
  product_id: string;
  product_name: string;
  deep_link: string;
  base_price_usd: number;
  commission_pct: number;
  similarity: number;
  expected_value: number;
}

function ratingTo10(rating?: number): number | undefined {
  if (rating === undefined) return undefined;
  return Math.round(rating * 2 * 10) / 10;  // 4.6 → 9.2
}

function reviewLabel(rating10?: number): string | undefined {
  if (rating10 === undefined) return undefined;
  if (rating10 >= 9.0) return 'Wonderful';
  if (rating10 >= 8.0) return 'Excellent';
  if (rating10 >= 7.0) return 'Very good';
  if (rating10 >= 6.0) return 'Good';
  return 'Pleasant';
}

async function main() {
  const normalized: any[] = JSON.parse(await readFile(NORMALIZED, 'utf8'));
  const places: Record<string, any> = JSON.parse(await readFile(PLACES, 'utf8'));
  let affiliates: Record<string, MatchedOffer> = {};
  try {
    affiliates = JSON.parse(await readFile(AFFILIATE, 'utf8'));
  } catch {
    console.warn('No affiliate file — proceeding without bookable links');
  }

  await mkdir(OUT_DIR, { recursive: true });

  let written = 0;
  for (const m of normalized) {
    const place = places[m.imls_id];
    const aff = affiliates[m.imls_id];
    const rating10 = ratingTo10(place?.rating);

    const out = {
      name: m.name,
      city: m.city,
      state: m.state,
      address: m.address,
      lat: m.lat,
      lng: m.lng,
      discipline: m.discipline,
      rating: rating10,
      review_count: place?.user_ratings_total,
      review_label: reviewLabel(rating10),
      hours_summary: place?.current_opening_hours?.weekday_text?.join(' · '),
      // tagline + description: use Claude to generate from data, OR hand-write the top 1000 cities
      tagline: `${m.name} in ${m.city}, ${m.state}.`,
      description: `${m.name} is a ${m.discipline.toLowerCase()} museum in ${m.city}, ${m.state}.`,
      ...(aff && {
        admission_from: aff.base_price_usd,
        admission_text: 'general admission',
      }),
      affiliate: aff
        ? { network: aff.network, deep_link: aff.deep_link, product_name: aff.product_name }
        : { network: 'none' },
      ...(place?.formatted_phone_number && { phone: place.formatted_phone_number }),
      ...(place?.website && { website: place.website }),
    };

    const outPath = path.join(OUT_DIR, `${m.slug}.json`);
    await writeFile(outPath, JSON.stringify(out, null, 2));
    written++;
  }

  console.log(`Wrote ${written} museum entries to ${OUT_DIR}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
