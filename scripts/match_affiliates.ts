/**
 * Affiliate match — nightly job.
 *
 * Inputs:
 *   - data/02_enriched/imls_normalized.json   (museum directory)
 *   - data/02_enriched/affiliate_inventory/   (one .json file per network)
 *
 * For each museum, finds the best matching offer across all networks,
 * picks the highest-payout match, and writes:
 *   - data/02_enriched/affiliate_offers.json  (museum_id → best offer)
 *   - data/02_enriched/affiliate_unmatched.json (for review / manual match)
 *
 * Match strategy:
 *   1. Geographic prefilter — products within 1 km of the museum
 *   2. Name-token Jaccard similarity (museum tokens ∩ product tokens / union)
 *   3. Score = similarity × commission_pct × base_price (proxy for $ per click)
 *   4. Threshold ≥ 0.5 similarity to count as a match
 *
 * To wire up real networks:
 *   - GetYourGuide partner API: https://partner.getyourguide.com/en-us/integration/api
 *   - Tiqets affiliate feed: https://www.tiqets.com/en/affiliates/
 *   - Viator (via Awin product feed): https://www.awin.com
 *   Each network's nightly fetch should write to:
 *     data/02_enriched/affiliate_inventory/{network}.json
 *   matching the AffiliateProduct shape below.
 *
 * Run: npm run match:affiliates
 */

import { readFile, writeFile, mkdir, readdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';

// ---- Types ----
interface NormalizedMuseum {
  imls_id: string;
  slug: string;
  name: string;
  city: string;
  state: string;
  lat: number;
  lng: number;
  discipline: string;
}

interface AffiliateProduct {
  network: 'getyourguide' | 'tiqets' | 'viator' | 'gocity';
  product_id: string;
  product_name: string;
  deep_link: string;
  lat: number;
  lng: number;
  base_price_usd: number;
  commission_pct: number;     // 0.08 for 8%
}

interface MatchedOffer extends AffiliateProduct {
  imls_id: string;
  similarity: number;
  expected_value: number;     // similarity × commission × price (proxy for $/click)
}

// ---- Config ----
const NORMALIZED = 'data/02_enriched/imls_normalized.json';
const INVENTORY_DIR = 'data/02_enriched/affiliate_inventory';
const OUT_OFFERS = 'data/02_enriched/affiliate_offers.json';
const OUT_UNMATCHED = 'data/02_enriched/affiliate_unmatched.json';
const MAX_DISTANCE_KM = 1.0;
const MIN_SIMILARITY = 0.5;

// ---- Helpers ----
function tokens(s: string): Set<string> {
  return new Set(
    s
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, ' ')
      .split(/\s+/)
      .filter((t) => t.length > 2 && !STOPWORDS.has(t))
  );
}

const STOPWORDS = new Set([
  'the', 'and', 'for', 'with', 'museum', 'gallery', 'center', 'centre',
  'national', 'american', 'tour', 'ticket', 'tickets', 'entry', 'admission',
  'pass', 'skip', 'line', 'guided',
]);

function jaccard(a: Set<string>, b: Set<string>): number {
  if (a.size === 0 || b.size === 0) return 0;
  let intersect = 0;
  for (const t of a) if (b.has(t)) intersect++;
  return intersect / (a.size + b.size - intersect);
}

function kmBetween(lat1: number, lng1: number, lat2: number, lng2: number): number {
  // Haversine distance in km
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}

// ---- Main ----
async function loadInventory(): Promise<AffiliateProduct[]> {
  if (!existsSync(INVENTORY_DIR)) {
    console.warn(`No inventory dir at ${INVENTORY_DIR} — run network fetchers first.`);
    return [];
  }
  const files = await readdir(INVENTORY_DIR);
  const all: AffiliateProduct[] = [];
  for (const f of files) {
    if (!f.endsWith('.json')) continue;
    const items: AffiliateProduct[] = JSON.parse(
      await readFile(path.join(INVENTORY_DIR, f), 'utf8')
    );
    all.push(...items);
  }
  console.log(`Loaded ${all.length} affiliate products across ${files.length} networks`);
  return all;
}

async function main() {
  if (!existsSync(NORMALIZED)) {
    console.error(`Missing ${NORMALIZED} — run: npm run ingest:imls`);
    process.exit(1);
  }
  await mkdir(path.dirname(OUT_OFFERS), { recursive: true });

  const museums: NormalizedMuseum[] = JSON.parse(await readFile(NORMALIZED, 'utf8'));
  const products = await loadInventory();
  console.log(`Matching ${museums.length} museums against ${products.length} products...`);

  const offers: Record<string, MatchedOffer> = {};
  const unmatched: { imls_id: string; name: string; city: string }[] = [];

  for (const m of museums) {
    const mTokens = tokens(m.name);
    let best: MatchedOffer | null = null;

    for (const p of products) {
      const dist = kmBetween(m.lat, m.lng, p.lat, p.lng);
      if (dist > MAX_DISTANCE_KM) continue;

      const sim = jaccard(mTokens, tokens(p.product_name));
      if (sim < MIN_SIMILARITY) continue;

      const ev = sim * p.commission_pct * p.base_price_usd;
      if (!best || ev > best.expected_value) {
        best = { ...p, imls_id: m.imls_id, similarity: sim, expected_value: ev };
      }
    }

    if (best) offers[m.imls_id] = best;
    else unmatched.push({ imls_id: m.imls_id, name: m.name, city: m.city });
  }

  await writeFile(OUT_OFFERS, JSON.stringify(offers, null, 2));
  await writeFile(OUT_UNMATCHED, JSON.stringify(unmatched, null, 2));

  const totalEV = Object.values(offers).reduce((s, o) => s + o.expected_value, 0);
  console.log(`Matched ${Object.keys(offers).length}/${museums.length} museums`);
  console.log(`Σ expected value (proxy): $${totalEV.toFixed(2)}`);
  console.log(`Unmatched: ${unmatched.length} → ${OUT_UNMATCHED}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
