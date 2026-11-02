#!/usr/bin/env python3
"""
Fallback photo fetcher for museums where the main script got no lead image.

For each unresolved museum, try:
  1. A direct Wikipedia search with alternative name variants (strip qualifiers)
  2. Wikimedia Commons category search (categories named after the museum)
  3. If still nothing, write a note to the report so Aaron sees the gap

Only touches museums whose status in wikipedia_photo_report.json is NOT 'ok'.
"""

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MUSEUMS_DIR = ROOT / "src" / "content" / "museums"
REPORT_PATH = ROOT / "data" / "wikipedia_photo_report.json"

WIKI_API = "https://en.wikipedia.org/w/api.php"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "AmericasMuseums/1.0 (aaron.gold4@gmail.com)"}

REJECT_RE = re.compile(
    r"(logo|coat_of_arms|seal|icon|map_of|locator|plan_of|floor_plan|blueprint|"
    r"portrait|autograph|signature|svg$)",
    re.IGNORECASE,
)


def http_get_json(url, max_retries=5):
    for attempt in range(max_retries):
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(10 * (attempt + 1))
                continue
            if 500 <= e.code < 600 and attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise
    raise RuntimeError(f"Failed: {url}")


def try_alternate_articles(museum_name, city):
    """Try multiple Wikipedia title variants."""
    variants = [
        museum_name,
        museum_name.replace(" and ", " & "),
        museum_name.replace(" & ", " and "),
    ]
    # Strip common qualifiers
    for suffix in [", and Botanical Gardens", " Art Museum", " and Museum"]:
        if museum_name.endswith(suffix):
            variants.append(museum_name[: -len(suffix)])

    for variant in variants:
        params = {
            "action": "query",
            "list": "search",
            "srsearch": f"{variant} {city} museum",
            "srlimit": "5",
            "format": "json",
        }
        try:
            data = http_get_json(WIKI_API + "?" + urllib.parse.urlencode(params))
            hits = data.get("query", {}).get("search", [])
            for hit in hits:
                title = hit["title"]
                tl = title.lower()
                nl = variant.lower()
                if nl in tl or tl in nl:
                    return title
            if hits:
                return hits[0]["title"]
        except Exception as e:
            print(f"  variant {variant!r} search error: {e}")
        time.sleep(1.0)
    return None


def get_lead_image(article_title):
    params = {
        "action": "query",
        "titles": article_title,
        "prop": "pageimages",
        "pithumbsize": "1000",
        "format": "json",
    }
    data = http_get_json(WIKI_API + "?" + urllib.parse.urlencode(params))
    pages = data.get("query", {}).get("pages", {})
    for _, page in pages.items():
        thumb = page.get("thumbnail", {}).get("source")
        if thumb:
            return thumb
    return None


def commons_category_search(museum_name):
    """Search Wikimedia Commons for a category matching this museum, pull first image."""
    # Try finding a category
    params = {
        "action": "query",
        "list": "search",
        "srsearch": f'incategory:"{museum_name}"',
        "srnamespace": "6",  # File namespace
        "srlimit": "10",
        "format": "json",
    }
    try:
        data = http_get_json(COMMONS_API + "?" + urllib.parse.urlencode(params))
        hits = data.get("query", {}).get("search", [])
    except Exception as e:
        print(f"  commons search error: {e}")
        return None, []

    good = []
    for hit in hits:
        title = hit["title"]
        if REJECT_RE.search(title):
            continue
        if not re.search(r"\.(jpe?g|png|tiff?)$", title, re.IGNORECASE):
            continue
        name = title.replace("File:", "").replace(" ", "_")
        encoded = urllib.parse.quote(name)
        url = f"https://commons.wikimedia.org/wiki/Special:FilePath/{encoded}?width=1000"
        good.append(url)
        if len(good) >= 4:
            break

    if not good:
        return None, []
    return good[0], good[1:4]


def main():
    with open(REPORT_PATH) as f:
        report = json.load(f)

    unresolved = [
        (slug, v) for slug, v in report.items()
        if v.get("status") != "ok"
    ]
    print(f"Attempting fallback for {len(unresolved)} museums")

    for slug, v in unresolved:
        museum_file = MUSEUMS_DIR / f"{slug}.json"
        if not museum_file.exists():
            continue
        with open(museum_file) as f:
            museum = json.load(f)

        name = museum["name"]
        city = museum.get("city", "")
        print(f"\n[{slug}] {name}")

        hero = None
        article = None
        gallery = []

        # Try alternate article titles
        article = try_alternate_articles(name, city)
        if article:
            print(f"  found article: {article}")
            try:
                hero = get_lead_image(article)
            except Exception as e:
                print(f"  lead image error: {e}")

        # Fall back to Commons category
        if not hero:
            print(f"  trying Commons category search...")
            hero, gallery = commons_category_search(name)
            if hero:
                print(f"  commons hero: {hero[:80]}")

        if hero:
            museum["hero_image"] = hero
            if gallery:
                museum["gallery_images"] = gallery
            museum["photo_credit"] = f"via Wikimedia Commons / {article or 'category search'}"
            with open(museum_file, "w") as f:
                json.dump(museum, f, indent=2, ensure_ascii=False)
            report[slug] = {
                "status": "ok_fallback",
                "name": name,
                "article": article or "commons",
                "hero": hero,
                "gallery": gallery,
            }
            print(f"  SAVED")
        else:
            report[slug] = {
                "status": "needs_manual",
                "name": name,
                "note": "No Wikipedia or Commons photo found; needs manual swap",
            }
            print(f"  needs manual")

        time.sleep(1.5)

    with open(REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    ok = sum(1 for r in report.values() if r.get("status") in ("ok", "ok_fallback"))
    manual = sum(1 for r in report.values() if r.get("status") == "needs_manual")
    print(f"\n{'='*60}")
    print(f"Final: {ok}/{len(report)} museums with photos")
    print(f"       {manual} need manual intervention")


if __name__ == "__main__":
    main()
