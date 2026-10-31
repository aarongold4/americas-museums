/**
 * IMLS Museum Universe Data File ingestion.
 *
 * Source: Institute of Museum and Library Services publishes a Museum Data File
 * approximately every 5 years. As of 2026 the latest is the 2018 Museum Data
 * File at https://www.imls.gov/research-evaluation/data-collection/museum-data-files.
 * Download the .csv (or the .xlsx and convert), drop it in data/01_raw/,
 * then run: npm run ingest:imls
 *
 * What this does:
 *   1. Reads data/01_raw/imls_museums.csv
 *   2. Filters out closed/inactive records
 *   3. Normalizes discipline codes to our 8-bucket taxonomy
 *   4. Generates stable slugs (city + name, with disambiguation suffixes)
 *   5. Writes data/02_enriched/imls_normalized.json — one record per museum
 *
 * Does NOT enrich with Google Places yet — that's enrich_places.ts.
 */

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';

const RAW_PATH = 'data/01_raw/imls_museums.csv';
const OUT_DIR = 'data/02_enriched';
const OUT_PATH = path.join(OUT_DIR, 'imls_normalized.json');

// IMLS discipline code → our taxonomy
const DISCIPLINE_MAP: Record<string, string> = {
  'ART':   'Art',
  'HST':   'History',
  'NAT':   'Natural History',
  'SCI':   'Science',
  'CMU':   'Children',
  'GMU':   'General',
  'HSC':   'Specialized',
  'ZAW':   'Specialized',
  'ARB':   'Specialized',
  'NAH':   'Natural History',
  // ... add the rest from the IMLS data dictionary
};

interface ImlsRecord {
  COMMONNAME: string;
  PHYSCITY: string;
  PHYSSTATE: string;
  PHYSADDRESS1: string;
  PHYSZIP: string;
  LATITUDE: string;
  LONGITUDE: string;
  DISCIPL: string;
  STATUS: string;  // 'A' = active
}

interface NormalizedMuseum {
  imls_id: string;
  slug: string;
  name: string;
  city: string;
  state: string;
  address: string;
  lat: number;
  lng: number;
  discipline: string;
}

function slugify(s: string): string {
  return s
    .toLowerCase()
    .replace(/&/g, 'and')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}

// Naive CSV parser; replace with papaparse for production
function parseCsv(text: string): ImlsRecord[] {
  const lines = text.split(/\r?\n/).filter(Boolean);
  const headers = lines[0]!.split(',').map((h) => h.trim().replace(/"/g, ''));
  return lines.slice(1).map((line) => {
    const cells = line.split(','); // TODO: real CSV parsing
    const row: any = {};
    headers.forEach((h, i) => (row[h] = cells[i]?.trim().replace(/^"|"$/g, '') ?? ''));
    return row as ImlsRecord;
  });
}

async function main() {
  if (!existsSync(RAW_PATH)) {
    console.error(`Missing ${RAW_PATH}`);
    console.error('Download from https://www.imls.gov/research-evaluation/data-collection/museum-data-files');
    process.exit(1);
  }
  await mkdir(OUT_DIR, { recursive: true });

  const text = await readFile(RAW_PATH, 'utf8');
  const rows = parseCsv(text);
  console.log(`Read ${rows.length} raw rows`);

  // 1. Filter to active records with coords
  const active = rows.filter(
    (r) => r.STATUS === 'A' && r.LATITUDE && r.LONGITUDE
  );
  console.log(`${active.length} active records with coords`);

  // 2. Normalize + slug-with-disambiguation
  const slugCounts = new Map<string, number>();
  const out: NormalizedMuseum[] = [];

  for (const r of active) {
    const baseName = r.COMMONNAME.trim();
    const baseSlug = slugify(`${baseName}-${r.PHYSCITY}`);
    const count = slugCounts.get(baseSlug) ?? 0;
    slugCounts.set(baseSlug, count + 1);
    const slug = count === 0 ? baseSlug : `${baseSlug}-${r.PHYSSTATE.toLowerCase()}-${count + 1}`;

    out.push({
      imls_id: `${r.PHYSSTATE}-${slugify(baseName)}`,
      slug,
      name: baseName,
      city: r.PHYSCITY,
      state: r.PHYSSTATE,
      address: `${r.PHYSADDRESS1}, ${r.PHYSCITY}, ${r.PHYSSTATE} ${r.PHYSZIP}`,
      lat: parseFloat(r.LATITUDE),
      lng: parseFloat(r.LONGITUDE),
      discipline: DISCIPLINE_MAP[r.DISCIPL] ?? 'General',
    });
  }

  await writeFile(OUT_PATH, JSON.stringify(out, null, 2));
  console.log(`Wrote ${out.length} normalized records to ${OUT_PATH}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
