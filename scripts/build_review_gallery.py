#!/usr/bin/env python3
"""
Build a single scrollable HTML page showing every museum's hero photo
alongside its name, city, and the Wikipedia article it came from.

Aaron scans this before publishing to confirm each photo is accurate.
Any bad photo gets flagged by slug, and the next-best candidate from
the museum's gallery (or a Commons category pull) replaces it.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MUSEUMS_DIR = ROOT / "src" / "content" / "museums"
REPORT_PATH = ROOT / "data" / "wikipedia_photo_report.json"
OUT_PATH = ROOT / "data" / "review_gallery.html"


def main():
    with open(REPORT_PATH) as f:
        report = json.load(f)

    museums = []
    for museum_file in sorted(MUSEUMS_DIR.glob("*.json")):
        slug = museum_file.stem
        with open(museum_file) as f:
            m = json.load(f)
        r = report.get(slug, {})
        museums.append({
            "slug": slug,
            "name": m.get("name", slug),
            "city": m.get("city", ""),
            "state": m.get("state", ""),
            "discipline": m.get("discipline", ""),
            "hero": m.get("hero_image"),
            "gallery": m.get("gallery_images", []),
            "credit": m.get("photo_credit", ""),
            "status": r.get("status", "unknown"),
            "article": r.get("article", ""),
        })

    # Sort: missing photos first (so Aaron sees gaps immediately), then by city, then name
    museums.sort(key=lambda m: (0 if m["hero"] else -1, m["city"], m["name"]))

    ok = sum(1 for m in museums if m["hero"])
    missing = sum(1 for m in museums if not m["hero"])

    cards = []
    for m in museums:
        hero_html = f'<img src="{m["hero"]}" alt="{m["name"]}" loading="lazy" />' if m["hero"] else '<div class="no-photo">No photo found</div>'
        gallery_links = ""
        if m["gallery"]:
            gallery_links = '<div class="gallery">' + "".join(
                f'<a href="{g}" target="_blank"><img src="{g}" alt="alt {i+1}" loading="lazy" /></a>'
                for i, g in enumerate(m["gallery"])
            ) + '</div>'
        wiki_link = f'<a href="https://en.wikipedia.org/wiki/{m["article"].replace(" ", "_")}" target="_blank">Wikipedia source</a>' if m["article"] else '<span class="warn">No Wikipedia article</span>'
        cards.append(f'''
<div class="card {'card--missing' if not m['hero'] else ''}" id="{m['slug']}">
  <div class="hero">{hero_html}</div>
  <div class="meta">
    <h2>{m['name']}</h2>
    <div class="loc">{m['city']}, {m['state']} · {m['discipline']}</div>
    <div class="src">{wiki_link}</div>
    <div class="slug">slug: <code>{m['slug']}</code></div>
    {gallery_links}
    <div class="flag">
      <label><input type="checkbox" data-slug="{m['slug']}" /> Flag this photo as wrong</label>
    </div>
  </div>
</div>
''')

    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Museum Photo Review — Americas Museums</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    margin: 0; padding: 0; background: #f5f5f0; color: #222;
  }}
  header {{
    position: sticky; top: 0; z-index: 10;
    background: #fff; border-bottom: 1px solid #ddd;
    padding: 16px 24px; display: flex; align-items: center; gap: 24px;
  }}
  header h1 {{ margin: 0; font-size: 20px; font-weight: 600; }}
  header .stats {{ font-size: 13px; color: #666; }}
  header .ok {{ color: #0a7; font-weight: 600; }}
  header .missing {{ color: #c33; font-weight: 600; }}
  header button {{
    margin-left: auto; padding: 8px 14px; font-size: 14px;
    background: #003B95; color: #fff; border: none; border-radius: 4px; cursor: pointer;
  }}
  main {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 16px; padding: 24px;
  }}
  .card {{
    background: #fff; border: 1px solid #ddd; border-radius: 6px;
    overflow: hidden; display: flex; flex-direction: column;
  }}
  .card--missing {{ border-color: #c33; background: #fff5f5; }}
  .hero {{ aspect-ratio: 16/10; background: #eee; overflow: hidden; }}
  .hero img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
  .no-photo {{
    width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
    color: #c33; font-size: 14px; font-weight: 600; background: #fff5f5;
  }}
  .meta {{ padding: 12px 14px; }}
  .meta h2 {{ margin: 0 0 4px; font-size: 15px; font-weight: 600; }}
  .loc {{ font-size: 12px; color: #666; margin-bottom: 6px; }}
  .src {{ font-size: 12px; margin-bottom: 4px; }}
  .src a {{ color: #003B95; }}
  .slug {{ font-size: 11px; color: #888; margin-bottom: 8px; }}
  .slug code {{ background: #eee; padding: 1px 4px; border-radius: 2px; }}
  .warn {{ color: #c33; }}
  .gallery {{
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; margin-bottom: 8px;
  }}
  .gallery img {{ width: 100%; aspect-ratio: 1; object-fit: cover; border-radius: 2px; }}
  .flag {{ margin-top: 6px; font-size: 13px; }}
  .flag label {{ cursor: pointer; user-select: none; }}
  .flagged {{ outline: 3px solid #c33; }}
  #flagged-list {{
    position: fixed; bottom: 20px; right: 20px; z-index: 20;
    background: #fff; border: 2px solid #c33; border-radius: 6px;
    padding: 12px 16px; max-width: 320px; font-size: 13px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15); display: none;
  }}
  #flagged-list.active {{ display: block; }}
  #flagged-list h3 {{ margin: 0 0 8px; font-size: 14px; }}
  #flagged-list textarea {{
    width: 100%; min-height: 80px; font-family: monospace; font-size: 12px;
    border: 1px solid #ddd; border-radius: 3px; padding: 6px;
  }}
  #flagged-list button {{
    margin-top: 6px; padding: 4px 10px; font-size: 12px;
    background: #003B95; color: #fff; border: none; border-radius: 3px; cursor: pointer;
  }}
</style>
</head>
<body>
<header>
  <h1>Americas Museums — Photo Review</h1>
  <div class="stats">
    <span class="ok">{ok}/{len(museums)} with photos</span>
    {' · <span class="missing">' + str(missing) + ' missing</span>' if missing else ''}
  </div>
  <button onclick="toggleFlagged()">Show flagged list</button>
</header>
<main>
{''.join(cards)}
</main>

<div id="flagged-list">
  <h3>Flagged slugs</h3>
  <textarea readonly id="flagged-text" placeholder="No photos flagged yet"></textarea>
  <button onclick="copyFlagged()">Copy to clipboard</button>
</div>

<script>
  const flagged = new Set();
  document.querySelectorAll('.flag input').forEach(cb => {{
    cb.addEventListener('change', e => {{
      const slug = e.target.dataset.slug;
      const card = document.getElementById(slug);
      if (e.target.checked) {{
        flagged.add(slug);
        card.classList.add('flagged');
      }} else {{
        flagged.delete(slug);
        card.classList.remove('flagged');
      }}
      document.getElementById('flagged-text').value = [...flagged].join('\\n');
    }});
  }});
  function toggleFlagged() {{
    document.getElementById('flagged-list').classList.toggle('active');
  }}
  function copyFlagged() {{
    const t = document.getElementById('flagged-text');
    t.select();
    document.execCommand('copy');
  }}
</script>
</body>
</html>
'''

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(html)
    print(f"Gallery written to {OUT_PATH}")
    print(f"  {ok} museums with photos")
    print(f"  {missing} museums missing photos")


if __name__ == "__main__":
    main()
