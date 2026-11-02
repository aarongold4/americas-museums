#!/usr/bin/env python3
"""
Build a per-museum picker gallery: for each flagged museum, show the current
hero photo + up to 8 alternatives from its Wikipedia article. Each candidate
has a radio button. Aaron picks one per museum and the page outputs a JSON
blob he can paste back for the swap.
"""

import json
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALT_PATH = ROOT / "data" / "photo_alternatives.json"
OUT_PATH = ROOT / "data" / "picker_gallery.html"


def main():
    with open(ALT_PATH) as f:
        alts = json.load(f)

    sections = []
    for slug, info in alts.items():
        name = info.get("name", slug)
        current = info.get("current")
        options = info.get("options", [])
        article = info.get("article", "")

        current_html = f'<img src="{current}" alt="current" />' if current else '<div class="no-photo">NO PHOTO</div>'

        option_cards = []
        # First tile: "keep current"
        option_cards.append(f'''
<label class="option option--keep">
  <input type="radio" name="pick_{slug}" value="__keep__" checked />
  <div class="option-img">{current_html}</div>
  <div class="option-label">Keep current</div>
</label>''')

        for i, opt in enumerate(options):
            title_clean = html.escape(opt["title"].replace("File:", ""))
            option_cards.append(f'''
<label class="option">
  <input type="radio" name="pick_{slug}" value="{html.escape(opt['url_full'])}" data-title="{title_clean}" />
  <div class="option-img"><img src="{opt['url_thumb']}" alt="{title_clean}" loading="lazy" /></div>
  <div class="option-label">{title_clean[:60]}</div>
</label>''')

        # Also offer "none / needs manual"
        option_cards.append(f'''
<label class="option option--none">
  <input type="radio" name="pick_{slug}" value="__none__" />
  <div class="option-img"><div class="no-photo">None of these work</div></div>
  <div class="option-label">Flag — I'll find another</div>
</label>''')

        wiki = f'<a href="https://en.wikipedia.org/wiki/{article.replace(" ", "_")}" target="_blank">Wikipedia source</a>' if article else ''

        sections.append(f'''
<section class="museum" id="museum-{slug}">
  <header>
    <h2>{html.escape(name)}</h2>
    <div class="slug">slug: <code>{slug}</code> · {wiki}</div>
  </header>
  <div class="options">
    {''.join(option_cards)}
  </div>
</section>
''')

    html_out = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Museum Photo Picker — Americas Museums</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    margin: 0; padding: 0; background: #f5f5f0; color: #222;
  }}
  header.page-header {{
    position: sticky; top: 0; z-index: 10;
    background: #fff; border-bottom: 1px solid #ddd;
    padding: 16px 24px; display: flex; align-items: center; gap: 24px;
  }}
  header.page-header h1 {{ margin: 0; font-size: 20px; font-weight: 600; }}
  header.page-header .count {{ font-size: 13px; color: #666; }}
  header.page-header button {{
    margin-left: auto; padding: 10px 16px; font-size: 14px;
    background: #003B95; color: #fff; border: none; border-radius: 4px; cursor: pointer;
  }}
  main {{ padding: 24px; max-width: 1400px; margin: 0 auto; }}
  section.museum {{
    background: #fff; border: 1px solid #ddd; border-radius: 6px;
    padding: 16px 20px; margin-bottom: 20px;
  }}
  section.museum header {{ margin-bottom: 12px; }}
  section.museum h2 {{ margin: 0 0 4px; font-size: 17px; }}
  section.museum .slug {{ font-size: 12px; color: #666; }}
  section.museum .slug code {{ background: #eee; padding: 1px 4px; border-radius: 2px; }}
  section.museum .slug a {{ color: #003B95; margin-left: 8px; }}
  .options {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 10px;
  }}
  .option {{
    display: block; cursor: pointer; border: 2px solid transparent; border-radius: 4px;
    overflow: hidden; background: #fafafa;
  }}
  .option input {{ position: absolute; opacity: 0; }}
  .option:has(input:checked) {{ border-color: #0a7; background: #e6f5ec; }}
  .option--keep:has(input:checked) {{ border-color: #888; background: #f0f0f0; }}
  .option--none:has(input:checked) {{ border-color: #c33; background: #fff5f5; }}
  .option-img {{
    aspect-ratio: 4/3; background: #eee; overflow: hidden;
  }}
  .option-img img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
  .no-photo {{
    width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
    color: #999; font-size: 12px; font-weight: 500; text-align: center; padding: 8px;
  }}
  .option-label {{
    padding: 6px 8px; font-size: 11px; color: #666; line-height: 1.3;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }}
  #result-box {{
    position: fixed; bottom: 20px; right: 20px; z-index: 20;
    background: #fff; border: 2px solid #003B95; border-radius: 6px;
    padding: 16px; max-width: 500px; width: 90%; font-size: 13px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2); display: none; max-height: 60vh; overflow: auto;
  }}
  #result-box.active {{ display: block; }}
  #result-box h3 {{ margin: 0 0 8px; font-size: 14px; }}
  #result-box textarea {{
    width: 100%; min-height: 200px; font-family: monospace; font-size: 11px;
    border: 1px solid #ddd; border-radius: 3px; padding: 8px;
  }}
  #result-box button {{
    margin-top: 8px; margin-right: 6px; padding: 6px 12px; font-size: 12px;
    background: #003B95; color: #fff; border: none; border-radius: 3px; cursor: pointer;
  }}
  #result-box .close {{ background: #888; }}
</style>
</head>
<body>
<header class="page-header">
  <h1>Pick a hero photo for each museum</h1>
  <div class="count">{len(alts)} museums</div>
  <button onclick="showPicks()">Show my picks →</button>
</header>
<main>
  {''.join(sections)}
</main>

<div id="result-box">
  <h3>Your picks</h3>
  <textarea readonly id="result-text"></textarea>
  <button onclick="copyPicks()">Copy to clipboard</button>
  <button class="close" onclick="document.getElementById('result-box').classList.remove('active')">Close</button>
</div>

<script>
  function showPicks() {{
    const picks = {{}};
    document.querySelectorAll('.museum').forEach(section => {{
      const slug = section.id.replace('museum-', '');
      const checked = section.querySelector('input[type=radio]:checked');
      if (checked && checked.value !== '__keep__') {{
        picks[slug] = {{
          url: checked.value,
          title: checked.dataset.title || checked.value,
        }};
      }}
    }});
    document.getElementById('result-text').value = JSON.stringify(picks, null, 2);
    document.getElementById('result-box').classList.add('active');
  }}
  function copyPicks() {{
    const t = document.getElementById('result-text');
    t.select();
    document.execCommand('copy');
  }}
</script>
</body>
</html>
'''

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(html_out)
    print(f"Picker gallery written to {OUT_PATH}")
    print(f"  {len(alts)} museums")
    total_opts = sum(len(v.get("options", [])) for v in alts.values())
    print(f"  {total_opts} total alternative photos")


if __name__ == "__main__":
    main()
