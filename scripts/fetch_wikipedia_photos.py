#!/usr/bin/env python3
"""
Fetch photos from Wikipedia Commons for every museum in src/content/museums/.

Strategy per museum:
  1. Hit Wikipedia API with the museum's exact name -> find the canonical article
  2. Use prop=pageimages for the lead image (Wikipedia's chosen hero)
  3. Use prop=images to list all images on the page; filter to likely museum photos
  4. Write hero_image + up to 3 gallery_images into the museum's JSON

Validation:
  - Reject obvious icon/logo/map filenames
  - Reject SVGs (icons/logos)
  - Prefer files with "museum" or city/state terms in the name
  - Log everything to a report so Aaron can spot-check later
"""

import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
MUSEUMS_DIR = ROOT / "src" / "content" / "museums"
REPORT_PATH = ROOT / "data" / "wikipedia_photo_report.json"

WIKI_API = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "AmericasMuseums/1.0 (aaron.gold4@gmail.com)"}

# Filename patterns to reject
REJECT_PATTERNS = [
    r"logo", r"coat_of_arms", r"seal", r"icon", r"commons-logo",
    r"map_of", r"usa_[a-z]+_location", r"locator", r"street_map",
    r"plan_of", r"floor_plan", r"blueprint", r"diagram",
    r"portrait", r"autograph", r"signature",
    r"^file:question", r"ambox", r"cscr-", r"wiki_letter",
    r"^file:red_pog", r"edit-", r"commons_logo",
]
REJECT_RE = re.compile("|".join(REJECT_PATTERNS), re.IGNORECASE)


def http_get_json(url: str, max_retries: int = 5) -> dict:
    """GET with retry on 429 (rate limit) and transient errors."""
    for attempt in range(max_retries):
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                backoff = 10 * (attempt + 1)
                print(f"  rate limited, sleeping {backoff}s", flush=True)
                time.sleep(backoff)
                continue
            if 500 <= e.code < 600 and attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise
    raise RuntimeError(f"Failed after {max_retries} retries: {url}")


def search_article(museum_name: str, city: str) -> Optional[str]:
    """Find the exact Wikipedia article title for this museum."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": f"{museum_name} {city}",
        "srlimit": "10",
        "format": "json",
    }
    url = WIKI_API + "?" + urllib.parse.urlencode(params)
    data = http_get_json(url)

    hits = data.get("query", {}).get("search", [])
    if not hits:
        return None

    # Prefer hits whose title matches the museum name exactly, or starts with it
    name_lower = museum_name.lower()
    city_lower = city.lower()
    for hit in hits:
        title = hit["title"]
        tl = title.lower()
        # Exact match wins
        if tl == name_lower:
            return title
        # Match with city qualifier (e.g. "Field Museum" vs "Field Museum of Natural History")
        if name_lower in tl or tl in name_lower:
            if city_lower in tl or city_lower in hit.get("snippet", "").lower():
                return title

    # Fallback: first hit if it contains the museum's distinctive tokens
    first = hits[0]["title"]
    distinctive = [t for t in name_lower.split() if len(t) > 4 and t not in {"museum", "gallery", "national", "american"}]
    if distinctive and any(t in first.lower() for t in distinctive):
        return first

    return None


def get_lead_image(article_title: str) -> Optional[str]:
    """Get Wikipedia's canonical lead image for this article."""
    params = {
        "action": "query",
        "titles": article_title,
        "prop": "pageimages",
        "pithumbsize": "1000",
        "format": "json",
    }
    url = WIKI_API + "?" + urllib.parse.urlencode(params)
    data = http_get_json(url)

    pages = data.get("query", {}).get("pages", {})
    for _, page in pages.items():
        thumb = page.get("thumbnail", {}).get("source")
        if thumb:
            return thumb
    return None


def get_gallery_images(article_title: str, museum_name: str, max_count: int = 3) -> list:
    """Get up to max_count additional museum images from the article."""
    params = {
        "action": "query",
        "titles": article_title,
        "prop": "images",
        "imlimit": "50",
        "format": "json",
    }
    url = WIKI_API + "?" + urllib.parse.urlencode(params)
    data = http_get_json(url)

    pages = data.get("query", {}).get("pages", {})
    all_images = []
    for _, page in pages.items():
        for img in page.get("images", []):
            all_images.append(img.get("title", ""))

    # Filter candidates
    candidates = []
    name_tokens = set(re.findall(r"\w{4,}", museum_name.lower()))
    for img_title in all_images:
        tl = img_title.lower()
        # Reject SVGs (icons/logos) and non-image files
        if not re.search(r"\.(jpe?g|png|tiff?)$", tl):
            continue
        # Reject blocked patterns
        if REJECT_RE.search(tl):
            continue
        # Score: how many of the museum's distinctive words appear in the filename?
        img_tokens = set(re.findall(r"\w{4,}", tl))
        overlap = len(name_tokens & img_tokens)
        candidates.append((overlap, img_title))

    # Sort by overlap descending, then by position (earlier = usually more prominent)
    candidates.sort(key=lambda x: (-x[0], all_images.index(x[1])))

    # Convert File:X.jpg titles into Special:FilePath URLs sized to 800px
    urls = []
    for _, img_title in candidates[:max_count]:
        # Strip "File:" prefix for the FilePath URL
        name = img_title.replace("File:", "").replace(" ", "_")
        encoded = urllib.parse.quote(name)
        url = f"https://en.wikipedia.org/wiki/Special:FilePath/{encoded}?width=800"
        urls.append(url)
    return urls


def process_museum(museum_file: Path, report: dict):
    with open(museum_file) as f:
        museum = json.load(f)

    name = museum["name"]
    city = museum.get("city", "")
    slug = museum_file.stem

    print(f"[{slug}] searching...", flush=True)

    try:
        article = search_article(name, city)
    except Exception as e:
        print(f"  search error: {e}", flush=True)
        report[slug] = {"status": "search_error", "name": name, "error": str(e)}
        return

    if not article:
        print(f"  no article found", flush=True)
        report[slug] = {"status": "no_article", "name": name}
        return

    print(f"  article: {article}", flush=True)
    hero = get_lead_image(article)
    if not hero:
        print(f"  no lead image", flush=True)
        report[slug] = {"status": "no_lead_image", "article": article, "name": name}
        return

    gallery = get_gallery_images(article, name, max_count=3)
    print(f"  hero + {len(gallery)} gallery images", flush=True)

    # Write back into the museum JSON
    museum["hero_image"] = hero
    if gallery:
        museum["gallery_images"] = gallery
    museum["photo_credit"] = f"via Wikipedia / {article}"

    with open(museum_file, "w") as f:
        json.dump(museum, f, indent=2, ensure_ascii=False)

    report[slug] = {
        "status": "ok",
        "name": name,
        "article": article,
        "hero": hero,
        "gallery": gallery,
    }

    # Be nice to the Wikipedia API (prevent rate limiting)
    time.sleep(2.0)


def main():
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Resume: load existing report so we skip museums that already succeeded
    report = {}
    if REPORT_PATH.exists():
        with open(REPORT_PATH) as f:
            report = json.load(f)
        done = sum(1 for v in report.values() if v.get("status") == "ok")
        print(f"Resuming — {done} already done, retrying the rest")

    files = sorted(MUSEUMS_DIR.glob("*.json"))
    print(f"Processing {len(files)} museums...")

    for i, museum_file in enumerate(files, 1):
        slug = museum_file.stem
        if report.get(slug, {}).get("status") == "ok":
            continue
        try:
            process_museum(museum_file, report)
        except Exception as e:
            print(f"  ERROR: {e}", flush=True)
            report[slug] = {"status": "error", "error": str(e)}

        if i % 5 == 0:
            # Save partial report in case we're interrupted
            with open(REPORT_PATH, "w") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Summary
    ok = sum(1 for r in report.values() if r.get("status") == "ok")
    no_article = sum(1 for r in report.values() if r.get("status") == "no_article")
    no_image = sum(1 for r in report.values() if r.get("status") == "no_lead_image")
    err = sum(1 for r in report.values() if r.get("status") == "error")

    print(f"\n{'='*60}")
    print(f"Done. {ok}/{len(files)} museums got photos.")
    print(f"  OK:          {ok}")
    print(f"  No article:  {no_article}")
    print(f"  No image:    {no_image}")
    print(f"  Errors:      {err}")
    print(f"\nReport written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
