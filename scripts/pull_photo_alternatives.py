#!/usr/bin/env python3
"""
For a list of museum slugs, pull a bunch of candidate photos from
their Wikipedia article's full image list, filter to likely building/exterior
shots, and write them to data/photo_alternatives.json.

A second script turns that JSON into a per-museum picker gallery HTML.
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
OUT_PATH = ROOT / "data" / "photo_alternatives.json"

WIKI_API = "https://en.wikipedia.org/w/api.php"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "AmericasMuseums/1.0"}

# The 15 slugs Aaron flagged
TARGETS = [
    "boston-childrens-museum",
    "art-institute-of-chicago",
    "field-museum",
    "hammer-museum",
    "natural-history-museum-of-la-county",
    "cooper-hewitt-smithsonian-design-museum",
    "glbt-historical-society-museum",
    "legion-of-honor",
    "de-young-museum",
    "museum-of-flight",
    "museum-of-pop-culture",
    "international-spy-museum",
    "national-portrait-gallery",
    "united-states-holocaust-memorial-museum",
    "national-museum-of-african-american-history-and-culture",
]

REJECT_RE = re.compile(
    r"(logo|coat_of_arms|seal|icon|map_of|usa_[a-z]+_location|locator|street_map|"
    r"plan_of|floor_plan|blueprint|diagram|portrait|autograph|signature|"
    r"commons-logo|ambox|wiki_letter|edit-|\.svg$)",
    re.IGNORECASE,
)

# Keywords that boost score — these say "architecture / exterior / building"
BUILDING_KEYWORDS = [
    "exterior", "building", "facade", "front", "entrance", "main",
    "night", "aerial", "overview", "architecture", "corona", "pavilion",
    "wing", "hall", "rotunda", "atrium",
]


def get(url, retries=8):
    for a in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(20 * (a + 1))
                continue
            raise
        except Exception:
            time.sleep(5 * (a + 1))
            continue
    raise RuntimeError(f"Exhausted retries for {url}")


# Hard-wired article overrides (for cases where search matches the wrong page)
ARTICLE_OVERRIDES = {
    "natural-history-museum-of-la-county": "Natural History Museum of Los Angeles County",
    "legion-of-honor": "Legion of Honor (museum)",
    "boston-childrens-museum": "Boston Children's Museum",
    "hammer-museum": "Hammer Museum",
    "art-institute-of-chicago": "Art Institute of Chicago",
    "cooper-hewitt-smithsonian-design-museum": "Cooper Hewitt, Smithsonian Design Museum",
    "de-young-museum": "De Young Museum",
}


def search_article(name, city, slug=None):
    if slug and slug in ARTICLE_OVERRIDES:
        return ARTICLE_OVERRIDES[slug]
    params = {
        "action": "query",
        "list": "search",
        "srsearch": f"{name} {city}",
        "srlimit": "5",
        "format": "json",
    }
    data = get(WIKI_API + "?" + urllib.parse.urlencode(params))
    hits = data.get("query", {}).get("search", [])
    for hit in hits:
        tl = hit["title"].lower()
        nl = name.lower()
        if nl in tl or tl in nl:
            return hit["title"]
    return hits[0]["title"] if hits else None


def get_article_images(article_title):
    """Return the full list of File: titles on an article."""
    params = {
        "action": "query",
        "titles": article_title,
        "prop": "images",
        "imlimit": "100",
        "format": "json",
    }
    data = get(WIKI_API + "?" + urllib.parse.urlencode(params))
    pages = data.get("query", {}).get("pages", {})
    titles = []
    for _, page in pages.items():
        for img in page.get("images", []):
            titles.append(img.get("title", ""))
    return titles


def score_image(title):
    tl = title.lower()
    # Reject patterns
    if REJECT_RE.search(tl):
        return -1
    # Must be an image
    if not re.search(r"\.(jpe?g|png|tiff?)$", tl):
        return -1
    # Keyword bonus
    score = sum(1 for k in BUILDING_KEYWORDS if k in tl)
    # Longer filenames are usually more descriptive
    score += min(len(tl) // 25, 3)
    return score


def filepath_url(title, width=800):
    name = title.replace("File:", "").replace(" ", "_")
    return f"https://en.wikipedia.org/wiki/Special:FilePath/{urllib.parse.quote(name)}?width={width}"


def main():
    # Resume: load existing alternatives
    alternatives = {}
    if OUT_PATH.exists():
        with open(OUT_PATH) as f:
            alternatives = json.load(f)
        print(f"Resuming — {len(alternatives)} already done")

    for slug in TARGETS:
        # Skip only if slug has at least 1 option (empty options = failed, retry)
        if slug in alternatives and len(alternatives[slug].get("options", [])) > 0:
            print(f"[{slug}] already done ({len(alternatives[slug]['options'])} options), skipping")
            continue
        museum_file = MUSEUMS_DIR / f"{slug}.json"
        with open(museum_file) as f:
            m = json.load(f)
        name = m["name"]
        city = m.get("city", "")
        current = m.get("hero_image")

        print(f"\n[{slug}] {name}")
        print(f"  current: {current[:70] if current else 'NONE'}")

        try:
            article = search_article(name, city, slug)
            print(f"  article: {article}")
            if not article:
                alternatives[slug] = {"name": name, "current": current, "options": [], "note": "no article"}
                continue
            time.sleep(3)

            titles = get_article_images(article)
            print(f"  {len(titles)} images on article")

            # Score and sort
            scored = [(score_image(t), t) for t in titles]
            scored = [(s, t) for s, t in scored if s >= 0]
            scored.sort(key=lambda x: -x[0])

            # Take top 6
            options = []
            for _, t in scored[:8]:
                options.append({
                    "title": t,
                    "url_full": filepath_url(t, 1000),
                    "url_thumb": filepath_url(t, 400),
                })

            alternatives[slug] = {
                "name": name,
                "article": article,
                "current": current,
                "options": options,
            }
            print(f"  -> {len(options)} alternatives queued")

        except Exception as e:
            print(f"  ERROR: {e}")
            alternatives[slug] = {"name": name, "current": current, "options": [], "error": str(e)}

        # Incremental save
        with open(OUT_PATH, "w") as f:
            json.dump(alternatives, f, indent=2, ensure_ascii=False)

        time.sleep(10)  # longer between museums to avoid rate limit

    with open(OUT_PATH, "w") as f:
        json.dump(alternatives, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {OUT_PATH}")
    print(f"Total museums: {len(alternatives)}")
    total_opts = sum(len(v.get("options", [])) for v in alternatives.values())
    print(f"Total alternative photos: {total_opts}")


if __name__ == "__main__":
    main()
