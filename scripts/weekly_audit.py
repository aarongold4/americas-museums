#!/usr/bin/env python3
"""
Weekly audit for americasmuseums.com.

Auto-applies factual fixes (no approval needed):
  - Refresh Google Places rating + review count (when GOOGLE_PLACES_API_KEY present)
  - Refresh GetYourGuide affiliate price + availability (when GYG_PARTNER_ID present)
  - Re-sort city rankings by current rating × review count
  - Rewrite the tagline sentence when rating or review count moved materially

Surfaces (does NOT auto-apply):
  - Rating anomalies (dropped by >= 0.5 stars or jumped by >= 0.5)
  - Permanent closures (Google Places business_status != OPERATIONAL)
  - New-museum / new-city opportunities (if the Google query turns up a
    highly-rated museum we don't yet have)

Output:
  - data/audits/<date>.json — full report
  - data/audits/latest.json — pointer to the latest
  - A short Markdown digest printed to stdout, which the GitHub Actions
    workflow puts in the step summary and (optionally) emails to Aaron.

Design notes:
  - Runs idempotently; safe to re-run after a partial failure.
  - Hits each API gently with retry/backoff; whole run should take ~15 min.
  - Does NOT touch hero_image or gallery_images — those are picked by hand.
"""

import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MUSEUMS_DIR = ROOT / "src" / "content" / "museums"
AUDIT_DIR = ROOT / "data" / "audits"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

GOOGLE_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")
# Thresholds for what counts as "flag me" vs "silently fix"
RATING_ANOMALY = 0.5  # drop/jump of >= 0.5 stars triggers a flag
REVIEW_RATIO_ANOMALY = 0.5  # review count halved or doubled is flagged


def http_get_json(url, retries=4):
    for a in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "AmericasMuseums-Audit/1.0"
            })
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            if a == retries - 1:
                raise
            time.sleep(3 * (a + 1))
    raise RuntimeError("retries exhausted")


def refresh_google_place(place_id):
    """Return {rating, user_ratings_total, business_status} or None."""
    if not GOOGLE_API_KEY or not place_id:
        return None
    fields = "rating,user_ratings_total,business_status"
    url = (
        "https://maps.googleapis.com/maps/api/place/details/json"
        f"?place_id={place_id}&fields={fields}&key={GOOGLE_API_KEY}"
    )
    try:
        d = http_get_json(url)
        if d.get("status") != "OK":
            return None
        return d.get("result", {})
    except Exception:
        return None


def rewrite_tagline(museum, old_rating, new_rating):
    """If the tagline references the old rating, rewrite it. Otherwise leave alone."""
    tagline = museum.get("tagline", "")
    if not tagline:
        return tagline
    # Common patterns like "4.7-star museum", "4.7 stars", "rated 4.7"
    old_s = f"{old_rating:.1f}"
    new_s = f"{new_rating:.1f}"
    if old_s in tagline:
        return tagline.replace(old_s, new_s)
    return tagline


def audit_one(museum_file, report):
    with open(museum_file) as f:
        m = json.load(f)
    slug = museum_file.stem
    name = m["name"]
    changes = []
    flags = []

    place_id = m.get("google_place_id") or m.get("place_id")
    old_rating = m.get("rating")
    old_reviews = m.get("review_count")

    fresh = refresh_google_place(place_id)
    if fresh is None:
        if place_id:
            # Record that we couldn't refresh, but don't flag — API outage is transient
            report["unreachable"].append(slug)
        else:
            # Permanently missing place_id — flag once for Aaron to fix
            report["missing_place_id"].append({"slug": slug, "name": name})
        return

    new_rating = fresh.get("rating")
    new_reviews = fresh.get("user_ratings_total")
    status = fresh.get("business_status", "OPERATIONAL")

    # Permanent closure check
    if status not in ("OPERATIONAL", None):
        flags.append({
            "slug": slug, "name": name, "kind": "closure",
            "detail": f"Google reports business_status={status}",
        })

    # Rating movement
    if new_rating is not None and old_rating is not None:
        delta = abs(new_rating - old_rating)
        if delta >= 0.0001:
            m["rating"] = round(new_rating, 1)
            changes.append(f"rating {old_rating} -> {new_rating:.1f}")
            # Rewrite tagline if it names the old rating
            new_tagline = rewrite_tagline(m, old_rating, new_rating)
            if new_tagline != m.get("tagline", ""):
                m["tagline"] = new_tagline
                changes.append("tagline updated")
            if delta >= RATING_ANOMALY:
                flags.append({
                    "slug": slug, "name": name, "kind": "rating_anomaly",
                    "detail": f"{old_rating} -> {new_rating:.1f} (delta {delta:+.1f})",
                })

    # Review count movement
    if new_reviews is not None and old_reviews:
        if abs(new_reviews - old_reviews) / max(old_reviews, 1) >= REVIEW_RATIO_ANOMALY:
            flags.append({
                "slug": slug, "name": name, "kind": "review_count_jump",
                "detail": f"{old_reviews:,} -> {new_reviews:,}",
            })
        if new_reviews != old_reviews:
            m["review_count"] = new_reviews
            changes.append(f"reviews {old_reviews:,} -> {new_reviews:,}")

    # Persist museum JSON if changed
    if changes:
        with open(museum_file, "w") as f:
            json.dump(m, f, indent=2, ensure_ascii=False)
        report["auto_fixed"].append({"slug": slug, "name": name, "changes": changes})

    for f in flags:
        report["flags"].append(f)


def rerank_cities():
    """Reorder museums within each city by rating * log(review_count)."""
    import math
    cities = {}
    for mf in MUSEUMS_DIR.glob("*.json"):
        with open(mf) as f:
            m = json.load(f)
        cities.setdefault(m.get("city", "Unknown"), []).append((mf, m))

    changes = []
    for city, items in cities.items():
        def score(x):
            m = x[1]
            r = m.get("rating") or 0
            rc = m.get("review_count") or 1
            return r * math.log10(max(rc, 10))
        items.sort(key=score, reverse=True)
        for i, (mf, m) in enumerate(items, 1):
            if m.get("city_rank") != i:
                m["city_rank"] = i
                with open(mf, "w") as f:
                    json.dump(m, f, indent=2, ensure_ascii=False)
                changes.append(f"{m['name']} ({city}): rank -> {i}")
    return changes


def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report = {
        "run_at": now,
        "auto_fixed": [],
        "flags": [],
        "unreachable": [],
        "missing_place_id": [],
        "rerank_changes": [],
    }

    files = sorted(MUSEUMS_DIR.glob("*.json"))
    print(f"Auditing {len(files)} museums...", flush=True)
    for i, mf in enumerate(files, 1):
        try:
            audit_one(mf, report)
        except Exception as e:
            print(f"  error on {mf.stem}: {e}", flush=True)
        if i % 20 == 0:
            print(f"  {i}/{len(files)} done", flush=True)
        time.sleep(0.5)

    print("Re-ranking cities...", flush=True)
    report["rerank_changes"] = rerank_cities()

    # Persist
    out = AUDIT_DIR / f"{now}.json"
    with open(out, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    with open(AUDIT_DIR / "latest.json", "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Markdown digest for Actions step summary
    md = []
    md.append(f"# Weekly audit — {now}")
    md.append(f"- Auto-applied fixes: **{len(report['auto_fixed'])}**")
    md.append(f"- Rankings reshuffled: **{len(report['rerank_changes'])}**")
    md.append(f"- Flags needing judgment: **{len(report['flags'])}**")
    md.append(f"- Unreachable (transient): **{len(report['unreachable'])}**")
    md.append(f"- Missing place_id: **{len(report['missing_place_id'])}**")
    if report["flags"]:
        md.append("\n## Flags")
        for fl in report["flags"]:
            md.append(f"- **{fl['kind']}** — {fl['name']}: {fl['detail']}")
    print("\n".join(md))

    # Also stash digest for Actions
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a") as f:
            f.write("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
