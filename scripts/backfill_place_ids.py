#!/usr/bin/env python3
"""
One-shot: query Google Places API (New) for each museum, write back the
place_id. Also refreshes rating + review_count while we're at it.

Needs GOOGLE_PLACES_API_KEY env var. Costs ~$0.017/call on Text Search.
"""

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MUSEUMS = ROOT / "src" / "content" / "museums"

API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")
if not API_KEY:
    print("ERROR: set GOOGLE_PLACES_API_KEY", file=sys.stderr)
    sys.exit(1)

ENDPOINT = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = "places.id,places.displayName,places.rating,places.userRatingCount,places.businessStatus,places.formattedAddress"


def search(text_query, retries=6):
    body = json.dumps({"textQuery": text_query}).encode("utf-8")
    for attempt in range(retries):
        req = urllib.request.Request(
            ENDPOINT,
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": API_KEY,
                "X-Goog-FieldMask": FIELD_MASK,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 10 * (attempt + 1)
                print(f"    429, waiting {wait}s", flush=True)
                time.sleep(wait)
                continue
            raise
    raise RuntimeError("retries exhausted")


def main():
    files = sorted(MUSEUMS.glob("*.json"))
    print(f"Backfilling place_ids for {len(files)} museums...")

    ok = 0
    no_match = []
    errors = []

    for i, mf in enumerate(files, 1):
        with open(mf) as f:
            m = json.load(f)
        slug = mf.stem
        # Resume: skip if already has place_id
        if m.get("google_place_id"):
            continue
        name = m["name"]
        city = m.get("city", "")
        state = m.get("state", "")
        query = f"{name} {city} {state}".strip()

        try:
            data = search(query)
            places = data.get("places", [])
            if not places:
                print(f"  [{i}/{len(files)}] {slug}: NO MATCH for {query!r}")
                no_match.append(slug)
                time.sleep(0.3)
                continue

            best = places[0]
            pid = best.get("id")
            rating = best.get("rating")
            reviews = best.get("userRatingCount")
            status = best.get("businessStatus")
            addr = best.get("formattedAddress", "")

            m["google_place_id"] = pid
            # Also refresh live rating/reviews/status if present
            if rating is not None:
                m["rating_google"] = rating
            if reviews is not None:
                m["review_count_google"] = reviews
            if status:
                m["business_status"] = status

            with open(mf, "w") as f:
                json.dump(m, f, indent=2, ensure_ascii=False)
            ok += 1
            closure = " 🚨 CLOSED" if status not in ("OPERATIONAL", None, "") else ""
            print(f"  [{i}/{len(files)}] {slug}: {pid}  (rating={rating}, reviews={reviews}){closure}")

        except Exception as e:
            print(f"  [{i}/{len(files)}] {slug}: ERROR {e}")
            errors.append((slug, str(e)))

        time.sleep(0.3)  # be gentle

    print(f"\n{'='*60}")
    print(f"OK: {ok}/{len(files)}")
    if no_match:
        print(f"No match ({len(no_match)}): {', '.join(no_match)}")
    if errors:
        print(f"Errors ({len(errors)}):")
        for slug, err in errors:
            print(f"  {slug}: {err}")


if __name__ == "__main__":
    main()
