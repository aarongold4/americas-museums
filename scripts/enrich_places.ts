/**
 * Google Places enrichment.
 *
 * For each normalized IMLS record, query Places API to get:
 *   - place_id, current opening hours, phone, website
 *   - star rating, user_ratings_total
 *   - up to 10 photo references (we'll store URLs, not blobs)
 *   - price_level
 *
 * Strategy: Nearby Search within 100m of IMLS coords + fuzzy name match.
 * Records that don't match cleanly get queued for manual review.
 *
 * Cost: ~$0.005 per place (one Nearby + one Place Details call).
 *       Full 33K dataset = ~$165 to enrich once.
 *
 * Caching: All API responses cached in places_cache.json. Re-running this
 * only re-fetches records older than REFRESH_DAYS (default 30) — safe to run
 * weekly to refresh hours/ratings on the top traffic pages.
 */

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';

const PLACES_KEY = process.env.GOOGLE_PLACES_API_KEY;
const IN_PATH = 'data/02_enriched/imls_normalized.json';
const OUT_PATH = 'data/02_enriched/places_cache.json';
const REVIEW_QUEUE = 'data/02_enriched/manual_review_needed.json';
const REFRESH_DAYS = 30;

interface NormalizedMuseum {
  imls_id: string;
  slug: string;
  name: string;
  city: string;
  state: string;
  lat: number;
  lng: number;
  [key: string]: any;
}

interface PlacesEnrichment {
  imls_id: string;
  fetched_at: string;
  match_confidence: number;
  place_id?: string;
  rating?: number;
  user_ratings_total?: number;
  price_level?: number;
  current_opening_hours?: any;
  formatted_phone_number?: string;
  website?: string;
  photo_refs?: string[];
}

function nameSimilarity(a: string, b: string): number {
  const A = a.toLowerCase().replace(/[^a-z0-9 ]/g, '').split(/\s+/);
  const B = b.toLowerCase().replace(/[^a-z0-9 ]/g, '').split(/\s+/);
  const setB = new Set(B);
  const overlap = A.filter((t) => setB.has(t)).length;
  return overlap / Math.max(A.length, B.length);
}

async function nearbySearch(lat: number, lng: number, name: string) {
  // TODO: replace with the actual Places API call
  // GET https://maps.googleapis.com/maps/api/place/nearbysearch/json
  //   ?location=${lat},${lng}&radius=100&keyword=${encodeURIComponent(name)}&key=${PLACES_KEY}
  throw new Error('Not implemented — wire up Places API call');
}

async function placeDetails(placeId: string) {
  // GET https://maps.googleapis.com/maps/api/place/details/json
  //   ?place_id=${placeId}&fields=name,formatted_address,opening_hours,
  //     current_opening_hours,rating,user_ratings_total,price_level,photos,
  //     website,formatted_phone_number&key=${PLACES_KEY}
  throw new Error('Not implemented — wire up Places API call');
}

async function main() {
  if (!PLACES_KEY) {
    console.error('GOOGLE_PLACES_API_KEY not set in env');
    process.exit(1);
  }

  await mkdir(path.dirname(OUT_PATH), { recursive: true });

  const museums: NormalizedMuseum[] = JSON.parse(await readFile(IN_PATH, 'utf8'));
  let cache: Record<string, PlacesEnrichment> = {};
  try {
    cache = JSON.parse(await readFile(OUT_PATH, 'utf8'));
  } catch {
    cache = {};
  }

  const reviewQueue: any[] = [];
  const cutoff = Date.now() - REFRESH_DAYS * 86400_000;

  for (const m of museums) {
    const cached = cache[m.imls_id];
    if (cached && new Date(cached.fetched_at).getTime() > cutoff) continue;

    try {
      const results = (await nearbySearch(m.lat, m.lng, m.name)) as any[];
      // Pick the best match by name similarity
      let bestMatch: any = null;
      let bestScore = 0;
      for (const r of results) {
        const score = nameSimilarity(m.name, r.name);
        if (score > bestScore) {
          bestMatch = r;
          bestScore = score;
        }
      }

      if (!bestMatch || bestScore < 0.5) {
        reviewQueue.push({ imls_id: m.imls_id, name: m.name, candidates: results });
        continue;
      }

      const details = await placeDetails(bestMatch.place_id);
      cache[m.imls_id] = {
        imls_id: m.imls_id,
        fetched_at: new Date().toISOString(),
        match_confidence: bestScore,
        place_id: bestMatch.place_id,
        rating: details.rating,
        user_ratings_total: details.user_ratings_total,
        price_level: details.price_level,
        current_opening_hours: details.current_opening_hours,
        formatted_phone_number: details.formatted_phone_number,
        website: details.website,
        photo_refs: details.photos?.map((p: any) => p.photo_reference) ?? [],
      };

      // Polite throttle — Places allows ~50 QPS but we don't need to push it
      await new Promise((r) => setTimeout(r, 50));
    } catch (err) {
      console.error(`Failed for ${m.imls_id}:`, err);
    }
  }

  await writeFile(OUT_PATH, JSON.stringify(cache, null, 2));
  await writeFile(REVIEW_QUEUE, JSON.stringify(reviewQueue, null, 2));
  console.log(`Enriched ${Object.keys(cache).length} records, ${reviewQueue.length} need manual review`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
