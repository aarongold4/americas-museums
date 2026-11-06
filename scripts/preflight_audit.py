#!/usr/bin/env python3
"""
Pre-deploy audit: walks every museum JSON + every built page and reports:
  - Required-field coverage (name, city, hours, admission, rating, review_count, etc.)
  - Hero image coverage + logo detection
  - Affiliate link presence
  - Page build coverage vs. museum count
  - Sitemap/robots/SEO coverage
  - GitHub Actions workflow presence
  - Any obvious schema violations

Prints a readiness checklist with PASS / WARN / FAIL per item.
"""

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MUSEUMS = ROOT / "src" / "content" / "museums"
DIST = ROOT / "dist"


def main():
    lines = []
    total_pass = 0
    total_warn = 0
    total_fail = 0

    def row(level, label, detail=""):
        nonlocal total_pass, total_warn, total_fail
        icon = {"PASS": "✓", "WARN": "!", "FAIL": "✗"}[level]
        if level == "PASS": total_pass += 1
        elif level == "WARN": total_warn += 1
        else: total_fail += 1
        lines.append(f"  [{icon}] {label}{' — ' + detail if detail else ''}")

    # ---------- MUSEUM CONTENT ----------
    lines.append("\n## MUSEUM CONTENT")
    museums = []
    for mf in sorted(MUSEUMS.glob("*.json")):
        with open(mf) as f:
            museums.append((mf.stem, json.load(f)))

    row("PASS" if len(museums) == 107 else "WARN",
        f"107 museums expected", f"found {len(museums)}")

    # Required field coverage
    req_fields = ["name", "city", "state", "hours_summary", "admission_text", "admission_from", "tagline", "description"]
    missing_any = []
    for slug, m in museums:
        # Use key presence, not falsy check (admission_from=0 for free museums is valid)
        gaps = [f for f in req_fields if f not in m or m[f] in (None, "")]
        if gaps:
            missing_any.append((slug, gaps))
    if missing_any:
        row("FAIL", f"Required fields complete", f"{len(missing_any)} museums missing fields")
        for slug, gaps in missing_any[:5]:
            lines.append(f"       - {slug}: missing {', '.join(gaps)}")
        if len(missing_any) > 5:
            lines.append(f"       - ...and {len(missing_any) - 5} more")
    else:
        row("PASS", "Required fields complete")

    # Rating + review_count
    no_rating = [s for s, m in museums if m.get("rating") is None]
    no_reviews = [s for s, m in museums if not m.get("review_count")]
    row("PASS" if not no_rating else "WARN",
        "Rating populated", "" if not no_rating else f"{len(no_rating)} without rating")
    row("PASS" if not no_reviews else "WARN",
        "Review count populated", "" if not no_reviews else f"{len(no_reviews)} without review count")

    # Google place_id (needed for weekly audit)
    no_pid = [s for s, m in museums if not (m.get("google_place_id") or m.get("place_id"))]
    row("PASS" if not no_pid else "WARN",
        "Google place_id set (for weekly audit)",
        "" if not no_pid else f"{len(no_pid)} without place_id — audit will skip these")

    # ---------- PHOTOS ----------
    lines.append("\n## PHOTOS")
    no_hero = []
    is_logo = []
    for slug, m in museums:
        hero = m.get("hero_image") or ""
        fname = hero.split("/")[-1].split("?")[0].lower()
        if not hero:
            no_hero.append(slug)
        elif "logo" in fname or "famsf" in fname:
            is_logo.append((slug, fname))

    row("PASS" if not no_hero else "WARN",
        "Every museum has a hero image",
        "" if not no_hero else f"{len(no_hero)} without — swatch fallback used: {', '.join(no_hero)}")
    row("WARN" if is_logo else "PASS",
        "No logo files as hero",
        f"{len(is_logo)} still using logos (user chose to keep)" if is_logo else "")

    # ---------- AFFILIATE ----------
    lines.append("\n## AFFILIATE")
    has_aff = 0
    none_aff = 0
    for slug, m in museums:
        aff = m.get("affiliate", {})
        if aff and aff.get("network") != "none" and aff.get("deep_link"):
            has_aff += 1
        else:
            none_aff += 1
    row("PASS" if has_aff > 0 else "WARN",
        f"Affiliate links present", f"{has_aff} museums with affiliate link, {none_aff} without (use 'Visit official site' fallback)")

    # ---------- BUILD ----------
    lines.append("\n## BUILD")
    if not DIST.exists():
        row("FAIL", "dist/ exists", "Run `npm run build`")
    else:
        row("PASS", "dist/ exists")
        museum_pages = list(DIST.glob("museum/*/index.html"))
        city_pages = list(DIST.glob("best-museums-in-*/index.html"))
        row("PASS" if len(museum_pages) == 107 else "FAIL",
            "107 museum detail pages built", f"found {len(museum_pages)}")
        row("PASS" if len(city_pages) == 9 else "FAIL",
            "9 city hub pages built", f"found {len(city_pages)}")
        row("PASS" if (DIST / "index.html").exists() else "FAIL", "Homepage built")
        row("PASS" if (DIST / "sitemap-index.xml").exists() else "FAIL", "Sitemap built")
        row("PASS" if (DIST / "robots.txt").exists() else "FAIL", "robots.txt present")

    # ---------- SEO ----------
    lines.append("\n## SEO")
    if (DIST / "index.html").exists():
        html = (DIST / "index.html").read_text()
        row("PASS" if "<title>" in html else "FAIL", "Page title tag")
        row("PASS" if 'name="description"' in html else "FAIL", "Meta description")
        row("PASS" if 'rel="canonical"' in html else "FAIL", "Canonical URL")
        row("PASS" if 'property="og:' in html else "FAIL", "Open Graph tags")

    # ---------- DEPLOY PIPELINE ----------
    lines.append("\n## DEPLOY PIPELINE")
    gha = ROOT / ".github" / "workflows"
    if (gha / "deploy.yml").exists():
        row("PASS", "GitHub Actions deploy workflow present")
    else:
        row("FAIL", "GitHub Actions deploy workflow missing")
    if (gha / "weekly-audit.yml").exists():
        row("PASS", "Weekly audit workflow present")
    else:
        row("FAIL", "Weekly audit workflow missing")
    if (ROOT / "scripts" / "weekly_audit.py").exists():
        row("PASS", "Weekly audit script present")
    else:
        row("FAIL", "Weekly audit script missing")

    # ---------- MANUAL STEPS ----------
    lines.append("\n## MANUAL STEPS STILL REQUIRED")
    lines.append("  [ ] Add americasmuseums.com to Hostinger as a website/domain")
    lines.append("  [ ] Point DNS at Hostinger (change nameservers, or set A records)")
    lines.append("  [ ] Create/note FTP credentials in Hostinger")
    lines.append("  [ ] Push the updated tarball to github.com/aarongold4/americas-museums")
    lines.append("  [ ] Add 4 GitHub secrets: FTP_HOST, FTP_USER, FTP_PASS, FTP_SERVER_DIR")
    lines.append("  [ ] (Optional) Add GOOGLE_PLACES_API_KEY secret for weekly audit")
    lines.append("  [ ] Verify first GitHub Actions run goes green")

    header = f"\n# PRE-DEPLOY AUDIT — americasmuseums.com\n{'='*60}\nPASS: {total_pass}   WARN: {total_warn}   FAIL: {total_fail}\n"
    print(header + "\n".join(lines))


if __name__ == "__main__":
    main()
