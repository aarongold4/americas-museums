#!/usr/bin/env python3
"""
Seed the content collections with 8 new city hubs and 96 museums.

Voice: neutral Lonely Planet — practical, factual, highlights what makes the
place worth visiting and the practical details. No first-person opinions.

Run once:
    python3 scripts/seed_top_cities.py

Writes:
    src/content/museums/{slug}.json   (96 new files)
    src/content/cities/{city}.mdx     (8 new files)

Re-running is idempotent — overwrites are explicit.
"""
import json, os, textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MUSEUMS_DIR = ROOT / "src" / "content" / "museums"
CITIES_DIR  = ROOT / "src" / "content" / "cities"

# ---------- Helpers ----------
def gyg_link(slug, city_slug):
    return f"https://www.getyourguide.com/{city_slug}/{slug}/?partner_id=PLACEHOLDER"

def m(name, slug, city, state, address, lat, lng, discipline, founded,
      rating, reviews, admission_from, admission_text="general admission",
      visit_time=None, best_for=None, hours_today=None, hours_summary=None,
      tagline="", description="", review_long=None,
      tips=None, highlights=None, badges=None,
      affiliate_network="getyourguide", distance_landmark=None):
    """Build one museum dict matching the Zod schema."""
    label = "Wonderful" if rating >= 9.0 else ("Excellent" if rating >= 8.0 else "Very good")
    out = {
        "name": name, "city": city, "state": state, "address": address,
        "lat": lat, "lng": lng, "discipline": discipline,
        "founded": founded, "rating": rating, "review_count": reviews,
        "review_label": label,
        "admission_from": admission_from, "admission_text": admission_text,
        "tagline": tagline, "description": description,
    }
    if hours_today: out["hours_today"] = hours_today
    if hours_summary: out["hours_summary"] = hours_summary
    if visit_time: out["visit_time"] = visit_time
    if best_for: out["best_for"] = best_for
    if review_long: out["review_long"] = review_long
    if badges: out["badges"] = badges
    if tips: out["tips"] = tips
    if highlights: out["highlights"] = highlights
    if distance_landmark: out["distance_landmark"] = distance_landmark
    if affiliate_network == "none" or admission_from == 0:
        out["affiliate"] = {"network": "none"}
    else:
        city_slug = city.lower().replace(" ", "-")
        out["affiliate"] = {
            "network": affiliate_network,
            "deep_link": gyg_link(slug, city_slug),
            "product_name": f"{name} entry"
        }
    return slug, out


# ============================================================
# NEW YORK CITY (12)
# ============================================================
NEW_YORK = [
    m("Metropolitan Museum of Art", "metropolitan-museum-of-art",
      "New York", "NY", "1000 5th Ave, New York, NY 10028",
      40.7794, -73.9632, "Art", 1870, 9.4, 87000, 30,
      visit_time="3–5 hours", best_for="Art lovers, all-day visits",
      hours_today="10 AM – 5 PM", hours_summary="Sun–Tue, Thu 10 AM – 5 PM · Fri–Sat 10 AM – 9 PM · closed Wed",
      tagline="The largest art museum in the Western Hemisphere. Plan a full day.",
      description="The Met spans 5,000 years of art across two million objects, from Egyptian tombs and Greek statuary to Vermeer, Van Gogh, and the American Wing. Pay-what-you-wish for NY/NJ/CT residents.",
      review_long="Two million objects, 5,000 years of human creativity, all under one roof. The Met's collection is broader than any single museum visit can cover — Egyptian temples reassembled stone by stone, the only Vermeer paintings on permanent display in the Western Hemisphere, the entire American Wing — so most visitors do well to pick three departments and accept that they won't see the rest.\n\nNY/NJ/CT residents pay what they wish; everyone else pays the full $30. The Met Cloisters in Fort Tryon Park is included on the same ticket if used within three days.",
      badges=[{"label": "Pay-what-you-wish (NY/NJ/CT)", "tone": "ok"}],
      tips=[{"tag": "TIP", "tone": "warn", "text": "Enter from the 81st St side to skip the Fifth Avenue queue."},
            {"tag": "TIP", "tone": "warn", "text": "The Roof Garden is open seasonally — check on the way in."}],
      highlights=[{"location": "American Wing", "item": "Washington Crossing the Delaware, Emanuel Leutze"},
                  {"location": "Egyptian Wing", "item": "Temple of Dendur, intact Roman-era temple"},
                  {"location": "European Paintings", "item": "Vermeer, Caravaggio, Velázquez"}],
      distance_landmark="On 5th Ave between 80th and 84th Streets"),

    m("Museum of Modern Art", "museum-of-modern-art",
      "New York", "NY", "11 W 53rd St, New York, NY 10019",
      40.7614, -73.9776, "Art", 1929, 9.2, 65000, 30,
      visit_time="2–3 hours", best_for="Modern and contemporary art",
      hours_today="10:30 AM – 5:30 PM", hours_summary="Daily 10:30 AM – 5:30 PM (Sat until 7 PM)",
      tagline="Van Gogh's Starry Night, Picasso's Demoiselles, Dalí's Persistence of Memory.",
      description="Founded in 1929 as the first museum dedicated to modernism. Collection includes the most-photographed painting in the building (Starry Night), the most-debated (Les Demoiselles d'Avignon), and the entire arc of 20th-century art on six floors.",
      review_long="MoMA's permanent collection on the fifth floor is one of the densest concentrations of canonical modern paintings anywhere — Starry Night, The Persistence of Memory, Demoiselles d'Avignon, Number 31 by Pollock, all within a few rooms of each other. The temporary exhibitions on the lower floors are worth as much time as the permanent collection.\n\nFridays after 4 PM are free for everyone but extremely crowded; weekday mornings are the best time to see the masterpieces without a phone in front of every one of them.",
      badges=[{"label": "Free Fri 4–8 PM", "tone": "ok"}],
      tips=[{"tag": "TIP", "tone": "warn", "text": "Free Fridays are packed — go a weekday morning if you can."}],
      highlights=[{"location": "Floor 5", "item": "The Starry Night, Vincent van Gogh"},
                  {"location": "Floor 5", "item": "Les Demoiselles d'Avignon, Pablo Picasso"}],
      distance_landmark="Midtown, between 5th and 6th Ave"),

    m("American Museum of Natural History", "american-museum-of-natural-history",
      "New York", "NY", "200 Central Park West, New York, NY 10024",
      40.7813, -73.9740, "Natural History", 1869, 9.1, 72000, 28,
      visit_time="3–4 hours", best_for="Families, dinosaurs",
      hours_today="10 AM – 5:30 PM", hours_summary="Daily 10 AM – 5:30 PM",
      tagline="The dinosaur halls, the blue whale, the Hayden Planetarium — all under one roof.",
      description="One of the largest natural history museums in the world. The fourth-floor dinosaur halls are the headline attraction; the Hayden Planetarium and the 94-foot fiberglass blue whale in the Hall of Ocean Life are close behind.",
      review_long="The fourth floor is what most visitors come for: the world's largest collection of mounted dinosaur skeletons arranged by evolutionary cladistics rather than period, so you walk through the actual branches of the dinosaur family tree. The Hall of Ocean Life with its life-size blue whale model overhead is the second draw, and the Hayden Planetarium next door rounds out a half-day visit.\n\nThe new Richard Gilder Center, opened in 2023, added 230,000 square feet including the Insectarium and Butterfly Vivarium. Worth folding into the trip.",
      badges=[{"label": "Family favorite", "tone": "warn"},
              {"label": "NY residents pay-what-you-wish", "tone": "ok"}],
      tips=[{"tag": "TIP", "tone": "warn", "text": "The Gilder Center entrance on Columbus Ave has shorter lines."}],
      highlights=[{"location": "Floor 4", "item": "T. rex, Apatosaurus, and the dinosaur cladogram"},
                  {"location": "Hall of Ocean Life", "item": "94-foot blue whale model"},
                  {"location": "Gilder Center", "item": "Insectarium and Butterfly Vivarium"}],
      distance_landmark="Upper West Side, on Central Park West at 79th"),

    m("Solomon R. Guggenheim Museum", "solomon-r-guggenheim-museum",
      "New York", "NY", "1071 5th Ave, New York, NY 10128",
      40.7830, -73.9590, "Art", 1939, 8.8, 32000, 25,
      visit_time="1.5–2 hours", best_for="Architecture, modern art",
      hours_today="11 AM – 6 PM", hours_summary="Daily 11 AM – 6 PM (Sat until 8 PM)",
      tagline="Frank Lloyd Wright's spiral. Walk to the top, descend through the galleries.",
      description="Wright's only major NYC building and one of the great works of American architecture. The collection inside — Kandinsky, Picasso, Mondrian — is strong, but the building is the headline.",
      review_long="The strategy is to take the elevator to the top of Wright's spiral and descend at your own pace, which is how the building is designed to be used. The continuous ramp is a mile long if walked corner to corner.\n\nKandinsky and other early-20th-century European painters dominate the permanent collection; the museum's strength in non-objective art is unmatched in New York.",
      badges=[{"label": "Pay-what-you-wish Sat 6–8 PM", "tone": "ok"}],
      tips=[{"tag": "TIP", "tone": "warn", "text": "Take the elevator to the top, walk down. The architect intended it."}],
      highlights=[{"location": "Rotunda", "item": "Frank Lloyd Wright's spiral interior, completed 1959"}],
      distance_landmark="Upper East Side, opposite Central Park"),

    m("Whitney Museum of American Art", "whitney-museum-of-american-art",
      "New York", "NY", "99 Gansevoort St, New York, NY 10014",
      40.7397, -74.0089, "Art", 1930, 8.9, 18000, 30,
      visit_time="2 hours", best_for="20th & 21st-century American art",
      hours_today="10:30 AM – 6 PM", hours_summary="Wed–Mon 10:30 AM – 6 PM (Fri until 10 PM) · closed Tue",
      tagline="Renzo Piano building at the foot of the High Line. Strong American collection.",
      description="The country's most important collection of 20th- and 21st-century American art — Hopper, O'Keeffe, Calder, Basquiat — in a Renzo Piano building anchoring the south end of the High Line. Outdoor terraces overlook the Hudson.",
      review_long="The Whitney moved from the Upper East Side to the Meatpacking District in 2015, and the new Renzo Piano building has been the right fit for the collection: outdoor terraces on every level, generous gallery heights, an entrance that pours visitors out onto the foot of the High Line. The biennial — every other year — is the closest thing American contemporary art has to a regular cultural event.",
      badges=[{"label": "Pay-what-you-wish Fri 5–10 PM", "tone": "ok"}],
      tips=[{"tag": "TIP", "tone": "warn", "text": "Combine with a walk on the High Line — the museum sits at its southern end."}],
      highlights=[{"location": "Permanent", "item": "Edward Hopper's largest single collection"},
                  {"location": "Permanent", "item": "Calder, O'Keeffe, Hartley, Marsden"}],
      distance_landmark="Meatpacking District, foot of the High Line"),

    m("The Met Cloisters", "met-cloisters",
      "New York", "NY", "99 Margaret Corbin Dr, New York, NY 10040",
      40.8649, -73.9319, "Art", 1938, 9.2, 14000, 30,
      visit_time="2 hours", best_for="Medieval art, quiet escape",
      hours_today="10 AM – 5 PM", hours_summary="Thu–Tue 10 AM – 5 PM · closed Wed",
      tagline="Medieval Europe at the northern tip of Manhattan. Same ticket as the Met.",
      description="The Met's medieval branch, built from fragments of five French abbeys reassembled in Fort Tryon Park. Houses the Unicorn Tapestries and Romanesque cloisters in a setting more contemplative than anything else in Manhattan.",
      review_long="The Cloisters were built in the 1930s using stone from five medieval French abbeys, shipped to New York and reassembled on the high ground of Fort Tryon Park. The building feels older than anything actually in Manhattan should — the cloisters around the herb garden, the Romanesque chapel, the Unicorn Tapestries hanging in their own purpose-lit gallery.\n\nIncluded on the Met's three-day ticket. Easiest from the A train to 190th.",
      badges=[{"label": "Same ticket as the Met (3 days)", "tone": "ok"}],
      tips=[{"tag": "TIP", "tone": "warn", "text": "Take the A train to 190th and walk through Fort Tryon Park."}],
      highlights=[{"location": "Unicorn Gallery", "item": "The Hunt of the Unicorn tapestries, c. 1500"},
                  {"location": "Cuxa Cloister", "item": "12th-century Romanesque arcade, herb garden in spring"}],
      distance_landmark="Fort Tryon Park, far Upper Manhattan"),

    m("Brooklyn Museum", "brooklyn-museum",
      "New York", "NY", "200 Eastern Pkwy, Brooklyn, NY 11238",
      40.6712, -73.9636, "Art", 1895, 8.7, 16000, 20,
      visit_time="2–3 hours", best_for="Egyptian, American, less crowded",
      hours_today="11 AM – 6 PM", hours_summary="Wed, Fri–Sun 11 AM – 6 PM · Thu 11 AM – 10 PM · closed Mon–Tue",
      tagline="Strong Egyptian, feminist, and American collections in a McKim Mead & White building.",
      description="The Brooklyn Museum's Egyptian collection is among the country's most important, the feminist art galleries house Judy Chicago's Dinner Party, and the American period rooms cover three centuries. Far less crowded than its Manhattan counterparts.",
      review_long="The Brooklyn Museum often gets called the city's most underrated, partly because it sits across the Brooklyn Bridge from the better-known Manhattan institutions. The Egyptian galleries on the third floor rival the Met's; the Elizabeth A. Sackler Center for Feminist Art on the fourth holds Judy Chicago's Dinner Party as its centerpiece. First Saturdays — free programming until 11 PM — are the city's best free museum night.",
      badges=[{"label": "First Saturdays free + late", "tone": "ok"}],
      tips=[{"tag": "TIP", "tone": "warn", "text": "Combine with Prospect Park or the Botanic Garden across the street."}],
      highlights=[{"location": "Floor 3", "item": "Egyptian collection, including the Mummy Chamber"},
                  {"location": "Floor 4", "item": "The Dinner Party, Judy Chicago"}],
      distance_landmark="Prospect Park / Eastern Parkway, Brooklyn"),

    m("Frick Collection", "frick-collection",
      "New York", "NY", "1 E 70th St, New York, NY 10021",
      40.7710, -73.9672, "Art", 1935, 9.3, 9500, 30,
      visit_time="1.5 hours", best_for="Old Masters, intimate setting",
      hours_today="10 AM – 6 PM", hours_summary="Wed–Sat 10 AM – 6 PM · Sun 11 AM – 5 PM · closed Mon–Tue",
      tagline="Vermeer, Rembrandt, Bellini in Henry Clay Frick's Gilded Age mansion.",
      description="Industrialist Henry Clay Frick's 1914 mansion preserved as a museum, holding Old Masters chosen by Frick himself: three Vermeers, multiple Rembrandts, Bellini's St. Francis, the largest Boucher cycle outside France. Reopened in 2025 after a major renovation.",
      review_long="A small museum of the highest possible quality: Frick bought paintings the way he bought coke ovens, and what he assembled before his death in 1919 includes three Vermeers (one of just 34 known), a Bellini St. Francis ranked among the greatest paintings of the Italian Renaissance, and a complete Fragonard cycle. The 2025 renovation added the second floor — formerly the family's private rooms — to public viewing for the first time.\n\nNo strollers, no children under 10. The Frick is genuinely quiet, even on weekends.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "Reserve in advance — same-day walk-ins are often turned away."}],
      highlights=[{"location": "West Gallery", "item": "Three Vermeers and Bellini's St. Francis in the Desert"},
                  {"location": "Fragonard Room", "item": "The Progress of Love panels, complete cycle"}],
      distance_landmark="Upper East Side, 70th and Fifth"),

    m("New-York Historical Society", "new-york-historical-society",
      "New York", "NY", "170 Central Park West, New York, NY 10024",
      40.7795, -73.9740, "History", 1804, 8.5, 6800, 22,
      visit_time="1.5–2 hours",
      hours_today="11 AM – 5 PM", hours_summary="Tue–Thu, Sat 11 AM – 5 PM · Fri 11 AM – 9 PM · Sun 11 AM – 5 PM",
      tagline="The city's oldest museum. Tiffany lamps, Audubon originals, founding-era documents.",
      description="New York's oldest museum, founded 1804. Holdings include the city's largest Tiffany lamp collection, all 435 original Audubon Birds of America watercolors (rotating), and an exhaustive Civil War archive. Pay-what-you-wish Friday evenings.",
      review_long="A serious history collection that doesn't get the foot traffic it deserves because it sits across the street from the much louder American Museum of Natural History. The Tiffany lamp collection on the fourth floor is the largest in the country; the Audubon watercolors rotate through the year because of light sensitivity.",
      badges=[{"label": "Pay-what-you-wish Fri 6–9 PM", "tone": "ok"}],
      tips=[{"tag": "TIP", "tone": "warn", "text": "Combine with the American Museum of Natural History across the street."}],
      highlights=[{"location": "Floor 4", "item": "Tiffany Gallery, 100+ original lamps"},
                  {"location": "Rotating", "item": "Audubon's original Birds of America watercolors"}],
      distance_landmark="Upper West Side, opposite the Natural History Museum"),

    m("Tenement Museum", "tenement-museum",
      "New York", "NY", "103 Orchard St, New York, NY 10002",
      40.7188, -73.9904, "History", 1988, 9.1, 11000, 30,
      visit_time="1 hour (per tour)", best_for="Immigrant history, guided tours",
      hours_today="10 AM – 6 PM", hours_summary="Daily 10 AM – 6 PM (tours every hour)",
      tagline="A Lower East Side tenement preserved as a time capsule. Tour-only entry.",
      description="Two preserved 19th-century tenement buildings on Orchard Street, where 15,000 immigrants from 20+ countries lived between 1863 and 2011. Tour-only — book in advance and pick a specific apartment story.",
      review_long="One of New York's most particular museums: tour-only, with each tour focused on a specific apartment and the family who lived in it. The buildings at 97 and 103 Orchard Street were sealed in the 1930s by their landlord and reopened decades later untouched, which is why the wallpaper, fixtures, and even toys in some rooms are originals.\n\nThe Hard Times tour through 97 Orchard is the most-booked; the Reagan Era tour through 103 Orchard is newer and covers later 20th-century immigration. Tours sell out a week ahead in summer.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "Book online a week ahead in summer — walk-ins rarely succeed."}],
      highlights=[{"location": "97 Orchard", "item": "Preserved 1863–1935 tenement apartments"},
                  {"location": "103 Orchard", "item": "Later 20th-century immigrant stories"}],
      distance_landmark="Lower East Side, 1 block off Delancey"),

    m("Cooper Hewitt, Smithsonian Design Museum", "cooper-hewitt-smithsonian-design-museum",
      "New York", "NY", "2 E 91st St, New York, NY 10128",
      40.7847, -73.9576, "Specialized", 1897, 8.6, 5400, 22,
      visit_time="1.5 hours", best_for="Design, decorative arts",
      hours_today="10 AM – 6 PM", hours_summary="Daily 10 AM – 6 PM",
      tagline="The Smithsonian's design museum, in Andrew Carnegie's Fifth Avenue mansion.",
      description="The only museum in the US devoted entirely to historical and contemporary design, housed in Andrew Carnegie's 1902 mansion. Visitors get an interactive 'Pen' on entry to save objects to a personal digital scrapbook.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "The Pen interaction is the museum's best feature — make sure to scan things you like."}],
      highlights=[{"location": "Mansion", "item": "Carnegie's preserved 1902 library and dining room"}],
      distance_landmark="Upper East Side, in the Carnegie Mansion at 91st"),

    m("Intrepid Sea, Air & Space Museum", "intrepid-sea-air-and-space-museum",
      "New York", "NY", "Pier 86, W 46th St, New York, NY 10036",
      40.7644, -74.0007, "Military", 1982, 8.7, 28000, 36,
      visit_time="2.5 hours", best_for="Aircraft carriers, families",
      hours_today="10 AM – 5 PM", hours_summary="Daily 10 AM – 5 PM",
      tagline="Aircraft carrier, Concorde, space shuttle, submarine — all docked in Manhattan.",
      description="The retired carrier USS Intrepid hosts a Concorde, the space shuttle Enterprise, the Cold War submarine Growler, and 28+ aircraft on its flight deck. One of the most physical museums in the city.",
      review_long="The Intrepid is the carrier; the Concorde, the space shuttle Enterprise, and the Growler submarine are all part of the same combined ticket. Allow extra time for the Concorde tour, which is worth the upcharge for anyone who has any interest in supersonic civil aviation.\n\nFamily traffic is heavy on weekends — weekdays are quieter and let you actually walk the flight deck without queueing.",
      badges=[{"label": "Family favorite", "tone": "warn"}],
      tips=[{"tag": "TIP", "tone": "warn", "text": "Pay the extra few dollars for the Concorde tour. Flight deck tickets don't include it."}],
      highlights=[{"location": "Flight Deck", "item": "F-14 Tomcat, A-12 Blackbird, plus 28 other aircraft"},
                  {"location": "Pier 86", "item": "Space Shuttle Enterprise pavilion"},
                  {"location": "Pier 86", "item": "USS Growler, a guided-missile submarine you can walk through"}],
      distance_landmark="Pier 86, Hell's Kitchen waterfront"),
]


# ============================================================
# LOS ANGELES (12)
# ============================================================
LOS_ANGELES = [
    m("Getty Center", "getty-center",
      "Los Angeles", "CA", "1200 Getty Center Dr, Los Angeles, CA 90049",
      34.0780, -118.4741, "Art", 1997, 9.4, 60000, 0, "always free",
      visit_time="3–4 hours", best_for="Art, architecture, free entry",
      hours_today="10 AM – 5:30 PM", hours_summary="Tue–Sun 10 AM – 5:30 PM · closed Mon",
      tagline="Richard Meier's hilltop campus. European paintings, plus the views.",
      description="J. Paul Getty's 110-acre hilltop museum, designed by Richard Meier and reached by a tram from the parking lot. Strong European paintings (Van Gogh's Irises, Cézanne, Rembrandt), but the campus and gardens compete with the collection for attention.",
      review_long="The Getty Center is two things at once: a serious museum of pre-20th-century European art (Van Gogh's Irises, Rembrandt, Cézanne, Manet, illuminated manuscripts) and Richard Meier's most extensive American work, a 110-acre hilltop in travertine and aluminum. The tram from the parking lot to the museum is part of the architectural sequence.\n\nFree admission (parking is the only paid element), open until late on Saturdays, with arguably the best museum café terrace in the country.",
      badges=[{"label": "Always free", "tone": "ok"}, {"label": "Skip-the-tram via shuttle", "tone": "neutral"}],
      tips=[{"tag": "FREE", "tone": "ok", "text": "Admission is free, but parking is $25 (cheaper after 3 PM)."},
            {"tag": "TIP", "tone": "warn", "text": "The Central Garden by Robert Irwin changes seasonally — worth its own loop."}],
      highlights=[{"location": "North Pavilion", "item": "Irises, Vincent van Gogh, 1889"},
                  {"location": "South Pavilion", "item": "Rembrandt's Old Man in Military Costume"},
                  {"location": "Central Garden", "item": "Robert Irwin's living-art installation"}],
      affiliate_network="none",
      distance_landmark="Brentwood, just off the 405"),

    m("Los Angeles County Museum of Art", "los-angeles-county-museum-of-art",
      "Los Angeles", "CA", "5905 Wilshire Blvd, Los Angeles, CA 90036",
      34.0639, -118.3592, "Art", 1965, 8.7, 35000, 25,
      visit_time="2–3 hours", best_for="Encyclopedic art, public sculpture",
      hours_today="11 AM – 6 PM", hours_summary="Mon, Tue, Thu 11 AM – 6 PM · Fri 11 AM – 8 PM · Sat–Sun 10 AM – 7 PM · closed Wed",
      tagline="The largest art museum in the western US. Currently mid-rebuild.",
      description="LACMA's encyclopedic collection spans Mesoamerican, Korean, Islamic, and modern Western art. The campus is mid-redesign by Peter Zumthor — several buildings are closed during construction; check before visiting. Urban Light by Chris Burden out front is the most-photographed sculpture in LA.",
      review_long="LACMA is in the middle of a major Peter Zumthor redesign that closed several of its buildings; check the website before going. What's open is still substantial — the Resnick Pavilion, the Broad Contemporary Art Museum building, plus the Japanese Pavilion. The forecourt with Chris Burden's Urban Light and Michael Heizer's Levitated Mass are open and free.",
      badges=[{"label": "LA County residents free after 3 PM", "tone": "ok"}],
      tips=[{"tag": "TIP", "tone": "warn", "text": "Construction is ongoing through 2026 — confirm what's open before visiting."}],
      highlights=[{"location": "Forecourt", "item": "Urban Light, 202 restored cast-iron streetlamps"},
                  {"location": "BCAM", "item": "Levitated Mass, a 340-ton boulder over a walkway"}],
      distance_landmark="Mid-Wilshire, on Museum Row"),

    m("The Broad", "the-broad",
      "Los Angeles", "CA", "221 S Grand Ave, Los Angeles, CA 90012",
      34.0540, -118.2503, "Art", 2015, 9.0, 33000, 0, "always free",
      visit_time="1.5–2 hours", best_for="Contemporary art, Instagrammable",
      hours_today="11 AM – 5 PM", hours_summary="Tue–Fri 11 AM – 5 PM · Sat 10 AM – 6 PM · Sun 10 AM – 6 PM · closed Mon",
      tagline="Free contemporary art museum downtown. Yayoi Kusama Infinity Mirrored Room.",
      description="Eli and Edythe Broad's 2,000-piece contemporary collection in a Diller Scofidio + Renfro building downtown. Always free; advance reservations for the Yayoi Kusama Infinity Mirrored Room are released two weeks ahead.",
      review_long="The Broad opened in 2015 with one of the world's largest collections of post-1980 contemporary art — Koons, Basquiat, Kruger, Murakami, Sherman — all on permanent rotating display. Always free. The Yayoi Kusama Infinity Mirrored Room (one of two on permanent view in the country) requires a separate timed reservation released two weeks in advance and books out within minutes.",
      badges=[{"label": "Always free", "tone": "ok"}, {"label": "Advance reservation", "tone": "info"}],
      tips=[{"tag": "FREE", "tone": "ok", "text": "Reserve free entry online — walk-up lines are long."},
            {"tag": "TIP", "tone": "warn", "text": "Kusama Infinity Room reservations open 2 weeks ahead and disappear in minutes."}],
      highlights=[{"location": "Floor 3", "item": "Yayoi Kusama, Infinity Mirrored Room"},
                  {"location": "Floor 1", "item": "Jeff Koons' Tulips and Balloon Dog"}],
      affiliate_network="none",
      distance_landmark="Bunker Hill, next to Walt Disney Concert Hall"),

    m("Getty Villa", "getty-villa",
      "Los Angeles", "CA", "17985 Pacific Coast Hwy, Pacific Palisades, CA 90272",
      34.0461, -118.5650, "Art", 1974, 9.2, 14000, 0, "always free",
      visit_time="2 hours", best_for="Greek and Roman antiquities",
      hours_today="10 AM – 5 PM", hours_summary="Wed–Mon 10 AM – 5 PM · closed Tue",
      tagline="Roman villa replica on the Pacific Coast. Antiquities only.",
      description="The Getty's antiquities collection, housed in a recreation of the 1st-century Villa dei Papiri at Herculaneum, perched above the Pacific. Free, but timed reservations and parking required.",
      review_long="A faithful reconstruction of the Villa dei Papiri buried by Vesuvius in 79 AD, scaled to fit a Pacific Palisades hillside. The collection inside is Greek, Roman, and Etruscan only — about 44,000 objects, of which a few hundred are on view at any time. The setting genuinely earns the comparison to the Mediterranean.",
      badges=[{"label": "Always free (timed entry)", "tone": "ok"}],
      tips=[{"tag": "FREE", "tone": "ok", "text": "Entry is free but reservations and $25 parking are mandatory."},
            {"tag": "TIP", "tone": "warn", "text": "The outer peristyle and herb gardens are as worth a visit as the galleries."}],
      highlights=[{"location": "Outer Peristyle", "item": "Reconstructed Roman colonnaded garden"},
                  {"location": "Galleries", "item": "Lansdowne Heracles, 2nd-century AD"}],
      affiliate_network="none",
      distance_landmark="Pacific Coast Highway, 30 minutes north of Santa Monica"),

    m("Norton Simon Museum", "norton-simon-museum",
      "Los Angeles", "CA", "411 W Colorado Blvd, Pasadena, CA 91105",
      34.1456, -118.1605, "Art", 1969, 9.1, 7800, 20,
      visit_time="2 hours", best_for="European paintings, Asian sculpture",
      hours_today="12 PM – 5 PM", hours_summary="Mon, Thu, Sat–Sun 12 PM – 5 PM · Fri 12 PM – 7 PM · closed Tue–Wed",
      tagline="Pasadena's quietly world-class painting collection. Often empty.",
      description="A small museum holding one of the country's best privately-assembled European painting collections — Degas bronzes, Goya, Rembrandt, Picasso — alongside a deep South and Southeast Asian sculpture wing. Often near-empty even on weekends.",
      review_long="The Norton Simon's collection is depth over breadth: the largest single collection of Degas bronzes in the world, a Rembrandt self-portrait, Picasso's Woman with a Book, plus several Zurbaráns and Goyas. The Asian collection in the lower level is comparable to the LACMA's. Pasadena traffic is the only thing keeping the museum from being on every LA must-do list.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "The garden is a Galen Cranz design — worth circling on the way out."}],
      highlights=[{"location": "Galleries", "item": "Largest collection of Degas bronzes in the world"},
                  {"location": "Asian Wing", "item": "10th-century Buddhist sculpture from Cambodia"}],
      distance_landmark="Pasadena, near the Rose Bowl"),

    m("Hammer Museum", "hammer-museum",
      "Los Angeles", "CA", "10899 Wilshire Blvd, Los Angeles, CA 90024",
      34.0589, -118.4438, "Art", 1990, 8.6, 4900, 0, "always free",
      visit_time="1–1.5 hours", best_for="Contemporary art, free entry",
      hours_today="11 AM – 6 PM", hours_summary="Tue–Sun 11 AM – 6 PM · closed Mon",
      tagline="UCLA's contemporary art museum. Always free, low crowds.",
      description="UCLA-operated contemporary art museum with strong rotating shows and a permanent print collection. Always free since 2014, never overcrowded, with one of the better courtyards in the city.",
      affiliate_network="none",
      badges=[{"label": "Always free", "tone": "ok"}],
      distance_landmark="Westwood, on the UCLA campus edge"),

    m("Natural History Museum of Los Angeles County", "natural-history-museum-of-la-county",
      "Los Angeles", "CA", "900 Exposition Blvd, Los Angeles, CA 90007",
      34.0173, -118.2870, "Natural History", 1913, 8.7, 19000, 18,
      visit_time="2.5 hours", best_for="Families, dinosaurs, gem hall",
      hours_today="9:30 AM – 5 PM", hours_summary="Daily 9:30 AM – 5 PM",
      tagline="Three T. rex skeletons in a row, a Hall of Gems, a butterfly pavilion seasonally.",
      description="LA's main natural history museum in Exposition Park, with an unusual row of three T. rex skeletons (juvenile, sub-adult, adult), a strong Hall of Gems and Minerals, and the seasonal Butterfly Pavilion in spring.",
      badges=[{"label": "Family favorite", "tone": "warn"}],
      highlights=[{"location": "Dinosaur Hall", "item": "T. rex growth series — three skeletons by age"}],
      distance_landmark="Exposition Park, next to USC and the LA Coliseum"),

    m("Petersen Automotive Museum", "petersen-automotive-museum",
      "Los Angeles", "CA", "6060 Wilshire Blvd, Los Angeles, CA 90036",
      34.0625, -118.3614, "Specialized", 1994, 8.8, 12500, 21,
      visit_time="2 hours", best_for="Cars, families, design",
      hours_today="10 AM – 5 PM", hours_summary="Daily 10 AM – 5 PM",
      tagline="Four floors of cars, a Hollywood vehicles wing, and a vault tour.",
      description="One of the world's largest automotive museums, in a Kohn Pedersen Fox-redesigned building on Museum Row. The Vault tour ($30 surcharge) accesses the lower-level collection of 250 cars not on the main floors.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "The Vault tour is the highlight if you care about cars at all — book on arrival."}],
      highlights=[{"location": "Hollywood Gallery", "item": "Bumblebee Camaro, the De Lorean from Back to the Future"},
                  {"location": "The Vault", "item": "Steve McQueen's Jaguar XKSS, Patton's staff car"}],
      distance_landmark="Mid-Wilshire, across from LACMA"),

    m("California Science Center", "california-science-center",
      "Los Angeles", "CA", "700 Exposition Park Dr, Los Angeles, CA 90037",
      34.0156, -118.2864, "Science", 1951, 9.0, 22000, 0, "always free",
      visit_time="2 hours", best_for="Families, free entry, space shuttle",
      hours_today="10 AM – 5 PM", hours_summary="Daily 10 AM – 5 PM",
      tagline="Permanent home of the Space Shuttle Endeavour. Always free.",
      description="One of the few free major science museums. Permanent exhibits include the Space Shuttle Endeavour (one of three retired orbiters on public view), an ecosystems wing with a kelp forest tank, and a hands-on World of Life gallery.",
      review_long="Free admission was the founding policy and remains so. The Endeavour is the headline — the orbiter is being prepared for vertical display in the new Samuel Oschin Air and Space Center, expected to open with the shuttle mounted on real boosters as if ready for launch (a unique configuration).\n\nIMAX is a paid add-on and worth it for the space documentaries.",
      badges=[{"label": "Always free", "tone": "ok"}, {"label": "Family favorite", "tone": "warn"}],
      affiliate_network="none",
      highlights=[{"location": "Endeavour Pavilion", "item": "Space Shuttle Endeavour, OV-105"}],
      distance_landmark="Exposition Park, next to the Natural History Museum"),

    m("Huntington Library, Art Museum, and Botanical Gardens", "huntington-library",
      "Los Angeles", "CA", "1151 Oxford Rd, San Marino, CA 91108",
      34.1297, -118.1142, "Specialized", 1919, 9.4, 18000, 29,
      visit_time="3–5 hours", best_for="Gardens, rare books, full-day visit",
      hours_today="10 AM – 5 PM", hours_summary="Wed–Mon 10 AM – 5 PM · closed Tue",
      tagline="120 acres of gardens, a Gainsborough collection, and a Gutenberg Bible.",
      description="Henry Huntington's San Marino estate split into three: a research library (with one of 50 surviving Gutenberg Bibles), an art collection of British and French portraiture (Blue Boy by Gainsborough, Pinkie by Lawrence), and 120 acres of themed gardens.",
      review_long="Effectively three museums on one ticket: a rare books library where you can see one of 50 surviving Gutenberg Bibles, an art collection of British grand-manner portraiture (Blue Boy and Pinkie hang facing each other), and 16 themed botanical gardens — including the largest Chinese garden outside China and a desert garden with 5,000 species.\n\nA full day. The tea room books up weeks ahead.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "Allow at least 4 hours. The Chinese and Japanese gardens are at opposite ends of the estate."}],
      highlights=[{"location": "Library", "item": "Gutenberg Bible (1455), Ellesmere Chaucer manuscript"},
                  {"location": "Huntington Art Gallery", "item": "The Blue Boy, Thomas Gainsborough, 1770"},
                  {"location": "Liu Fang Yuan", "item": "1.5-acre Chinese scholar's garden"}],
      distance_landmark="San Marino, 30 minutes east of downtown LA"),

    m("Museum of Contemporary Art Los Angeles", "museum-of-contemporary-art-los-angeles",
      "Los Angeles", "CA", "250 S Grand Ave, Los Angeles, CA 90012",
      34.0530, -118.2502, "Art", 1979, 8.4, 7200, 18,
      visit_time="1.5 hours", best_for="Contemporary art",
      hours_today="11 AM – 5 PM", hours_summary="Wed, Fri–Sun 11 AM – 5 PM · Thu 11 AM – 8 PM · closed Mon–Tue",
      tagline="Downtown LA's contemporary art museum. Free since 2023.",
      description="MOCA's main Grand Avenue location, in an Arata Isozaki building. Permanent collection of post-1940 art (Rothko, Pollock, Twombly) plus rotating exhibits. Admission has been free since 2023.",
      affiliate_network="none",
      badges=[{"label": "Always free since 2023", "tone": "ok"}],
      distance_landmark="Bunker Hill, opposite The Broad"),

    m("La Brea Tar Pits and Museum", "la-brea-tar-pits-and-museum",
      "Los Angeles", "CA", "5801 Wilshire Blvd, Los Angeles, CA 90036",
      34.0633, -118.3553, "Natural History", 1977, 8.5, 16000, 18,
      visit_time="1.5–2 hours", best_for="Families, fossils, Ice Age",
      hours_today="9:30 AM – 5 PM", hours_summary="Daily 9:30 AM – 5 PM",
      tagline="Active Ice Age fossil excavation in the middle of Wilshire Blvd.",
      description="Active asphalt seeps that have been trapping animals for 50,000 years, in the middle of Hancock Park. Most-visited collection: thousands of dire wolf skulls. Excavations continue daily and visitors can watch.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "The outdoor pits and Pit 91 viewing platform are free; only the museum costs money."}],
      highlights=[{"location": "Fossil Lab", "item": "Live preparation of fossils excavated this season"},
                  {"location": "Wall of Skulls", "item": "404 dire wolf skulls in one display"}],
      distance_landmark="Hancock Park, on Museum Row"),
]


# ============================================================
# WASHINGTON DC (12)
# ============================================================
WASHINGTON_DC = [
    m("National Gallery of Art", "national-gallery-of-art",
      "Washington", "DC", "Constitution Ave NW, Washington, DC 20565",
      38.8913, -77.0200, "Art", 1937, 9.4, 47000, 0, "always free",
      visit_time="3–4 hours", best_for="European and American painting",
      hours_today="10 AM – 5 PM", hours_summary="Mon–Sat 10 AM – 5 PM · Sun 11 AM – 6 PM",
      tagline="The only Leonardo painting in the Americas, a free Calder mobile, a sculpture garden.",
      description="One of the world's great encyclopedic art museums and entirely free. The West Building (John Russell Pope, 1941) holds the European and American old masters; the East Building (I. M. Pei, 1978) holds modern and contemporary. A separate sculpture garden across 7th Street.",
      review_long="The West Building's painting galleries are arranged chronologically by national school — Italian, Flemish, Dutch, French, Spanish — and include Ginevra de' Benci, the only Leonardo da Vinci painting on permanent display in the Americas. The East Building has a permanent Calder mobile in the atrium and rotating modern exhibitions.\n\nFree, including the major special exhibitions. The sculpture garden adds a whole half-day in good weather.",
      badges=[{"label": "Always free", "tone": "ok"}],
      tips=[{"tag": "FREE", "tone": "ok", "text": "Always free. So is the sculpture garden across 7th Street."}],
      highlights=[{"location": "West Building, Gallery 6", "item": "Ginevra de' Benci, Leonardo da Vinci"},
                  {"location": "East Building Atrium", "item": "Untitled (Calder), suspended mobile"}],
      affiliate_network="none",
      distance_landmark="On the National Mall, between 4th and 7th"),

    m("National Air and Space Museum", "national-air-and-space-museum",
      "Washington", "DC", "Independence Ave SW, Washington, DC 20560",
      38.8882, -77.0199, "Science", 1976, 9.0, 80000, 0, "always free",
      visit_time="2.5–3 hours", best_for="Aviation, space, families",
      hours_today="10 AM – 5:30 PM", hours_summary="Daily 10 AM – 5:30 PM",
      tagline="The Wright Flyer, Spirit of St. Louis, Apollo 11 capsule. Always free.",
      description="The Smithsonian's flagship aviation museum on the Mall. Houses the original Wright Flyer, the Spirit of St. Louis, the Apollo 11 command module Columbia, and Glamorous Glennis (the X-1 that broke the sound barrier). The Udvar-Hazy Center near Dulles Airport holds the larger aircraft including a Concorde and the shuttle Discovery.",
      review_long="Major renovation that began in 2018 has reopened in phases; check which galleries are open before visiting. The Wright Flyer, Spirit of St. Louis, and Apollo 11 capsule are the consistent headliners. For the larger aircraft — Concorde, B-29 Enola Gay, Space Shuttle Discovery — visit the companion Udvar-Hazy Center near Dulles, also free.",
      badges=[{"label": "Always free", "tone": "ok"}, {"label": "Timed entry passes", "tone": "info"}],
      tips=[{"tag": "FREE", "tone": "ok", "text": "Free entry, but timed passes are required — reserve online ahead of time."}],
      highlights=[{"location": "Milestones of Flight", "item": "Wright Flyer, Spirit of St. Louis, X-1, Apollo 11 capsule"}],
      affiliate_network="none",
      distance_landmark="On the National Mall"),

    m("National Museum of Natural History", "national-museum-of-natural-history",
      "Washington", "DC", "10th St & Constitution Ave NW, Washington, DC 20560",
      38.8913, -77.0260, "Natural History", 1910, 8.9, 65000, 0, "always free",
      visit_time="2–3 hours", best_for="Families, gems, fossils",
      hours_today="10 AM – 5:30 PM", hours_summary="Daily 10 AM – 5:30 PM",
      tagline="The Hope Diamond, a T. rex eating a Triceratops, the dome rotunda elephant.",
      description="The Smithsonian's most-visited museum. Hope Diamond in the gem hall, the Tyrannosaurus rex 'Wankel Rex' in the David H. Koch Hall of Fossils, a 13-foot African elephant in the rotunda, and a Sant Ocean Hall.",
      badges=[{"label": "Always free", "tone": "ok"}, {"label": "Family favorite", "tone": "warn"}],
      affiliate_network="none",
      highlights=[{"location": "Hall of Geology", "item": "Hope Diamond, 45.52 carats"},
                  {"location": "Hall of Fossils", "item": "T. rex devouring a Triceratops, mounted as a single tableau"}],
      distance_landmark="On the National Mall, opposite the Capitol"),

    m("National Museum of African American History and Culture", "national-museum-of-african-american-history-and-culture",
      "Washington", "DC", "1400 Constitution Ave NW, Washington, DC 20560",
      38.8911, -77.0327, "History", 2016, 9.4, 40000, 0, "always free",
      visit_time="3–4 hours", best_for="History, all-day visit",
      hours_today="10 AM – 5:30 PM", hours_summary="Daily 10 AM – 5:30 PM",
      tagline="The Smithsonian's African American history museum. Plan a full visit.",
      description="The newest Smithsonian on the Mall (opened 2016), in a David Adjaye corona-shaped building. The lower-level history galleries are the headline; the cultural galleries upstairs cover music, sports, and art. Plan to enter at the bottom and work up.",
      review_long="The architecture is intentional: visitors descend three levels into the History Galleries and then ascend back to the cultural galleries above. The history portion — slavery, Reconstruction, Jim Crow, civil rights — takes most visitors 2–3 hours by itself.\n\nTimed entry passes are still required and the most popular times release at 8:15 AM thirty days ahead. Same-day passes appear at 8:15 AM the day-of and disappear within minutes.",
      badges=[{"label": "Always free", "tone": "ok"}, {"label": "Timed entry required", "tone": "info"}],
      tips=[{"tag": "TIP", "tone": "warn", "text": "Timed passes book a month out. Same-day passes drop at 8:15 AM."}],
      highlights=[{"location": "Concourse 3", "item": "Slavery and Freedom Gallery"}],
      affiliate_network="none",
      distance_landmark="On the National Mall, near the Washington Monument"),

    m("United States Holocaust Memorial Museum", "united-states-holocaust-memorial-museum",
      "Washington", "DC", "100 Raoul Wallenberg Pl SW, Washington, DC 20024",
      38.8870, -77.0327, "History", 1993, 9.5, 32000, 0, "always free",
      visit_time="2.5–3 hours",
      hours_today="10 AM – 5:20 PM", hours_summary="Daily 10 AM – 5:20 PM",
      tagline="Permanent exhibition tells the history of the Holocaust over three floors.",
      description="The country's official Holocaust memorial museum. The Permanent Exhibition is a single self-guided sequence over three descending floors, recommended for visitors 11 and older. Always free; timed passes recommended in peak season.",
      review_long="The Permanent Exhibition is structured as a single descending journey over three floors and takes 2–3 hours. Children under 11 should visit Daniel's Story instead, on the first floor. The museum is intense and intentionally so; allow recovery time afterward.",
      badges=[{"label": "Always free", "tone": "ok"}],
      tips=[{"tag": "TIP", "tone": "warn", "text": "Reserve free timed passes online in spring/summer. The lobby is open without one."}],
      affiliate_network="none",
      distance_landmark="Just south of the Mall, near the Tidal Basin"),

    m("National Museum of American History", "national-museum-of-american-history",
      "Washington", "DC", "1300 Constitution Ave NW, Washington, DC 20560",
      38.8911, -77.0300, "History", 1964, 8.7, 38000, 0, "always free",
      visit_time="2–3 hours",
      hours_today="10 AM – 5:30 PM", hours_summary="Daily 10 AM – 5:30 PM",
      tagline="The Star-Spangled Banner, the Greensboro lunch counter, Dorothy's ruby slippers.",
      description="Smithsonian's American history museum. Star-Spangled Banner in its low-light chamber, the Greensboro lunch counter from the 1960 sit-in, Dorothy's ruby slippers from The Wizard of Oz, and Julia Child's preserved kitchen.",
      badges=[{"label": "Always free", "tone": "ok"}],
      affiliate_network="none",
      highlights=[{"location": "Floor 2", "item": "Star-Spangled Banner — the actual flag from Fort McHenry"},
                  {"location": "Floor 1", "item": "Greensboro lunch counter, 1960 sit-in site"}],
      distance_landmark="On the National Mall"),

    m("Smithsonian American Art Museum", "smithsonian-american-art-museum",
      "Washington", "DC", "8th and G Streets NW, Washington, DC 20004",
      38.8975, -77.0228, "Art", 1829, 8.8, 9100, 0, "always free",
      visit_time="2 hours",
      hours_today="11:30 AM – 7 PM", hours_summary="Daily 11:30 AM – 7 PM",
      tagline="American art from colonial to contemporary, in the Old Patent Office.",
      description="The Smithsonian's American-art-only collection, sharing the Old Patent Office Building (1836) with the National Portrait Gallery. Strong holdings in 19th-century American landscape, folk art, and Modernism. The Robert and Arlene Kogod Courtyard (Norman Foster) connects the two museums.",
      badges=[{"label": "Always free", "tone": "ok"}],
      affiliate_network="none",
      highlights=[{"location": "Folk Art Gallery", "item": "James Hampton's Throne of the Third Heaven"}],
      distance_landmark="Penn Quarter / Chinatown"),

    m("National Portrait Gallery", "national-portrait-gallery",
      "Washington", "DC", "8th and F Streets NW, Washington, DC 20001",
      38.8978, -77.0231, "Art", 1968, 8.9, 12000, 0, "always free",
      visit_time="1.5–2 hours",
      hours_today="11:30 AM – 7 PM", hours_summary="Daily 11:30 AM – 7 PM",
      tagline="The Obama portraits, the presidential portrait series, the Hall of Presidents.",
      description="Shares the Old Patent Office Building with the American Art Museum. America's Presidents Gallery includes every U.S. president; the Obama official portraits by Kehinde Wiley and Amy Sherald are displayed nearby.",
      badges=[{"label": "Always free", "tone": "ok"}],
      affiliate_network="none",
      highlights=[{"location": "America's Presidents", "item": "All U.S. presidential portraits"},
                  {"location": "20th Century", "item": "Obama official portraits, Wiley and Sherald"}],
      distance_landmark="Penn Quarter / Chinatown"),

    m("Hirshhorn Museum and Sculpture Garden", "hirshhorn-museum-and-sculpture-garden",
      "Washington", "DC", "Independence Ave SW & 7th St SW, Washington, DC 20560",
      38.8884, -77.0226, "Art", 1974, 8.6, 7200, 0, "always free",
      visit_time="1.5 hours",
      hours_today="10 AM – 5:30 PM", hours_summary="Daily 10 AM – 5:30 PM",
      tagline="Round modernist drum on the Mall. Contemporary art and a sunken sculpture garden.",
      description="The Smithsonian's modern and contemporary art museum, in a Gordon Bunshaft cylinder on the south side of the Mall. The sunken sculpture garden across Jefferson Drive is being renovated by Hiroshi Sugimoto.",
      badges=[{"label": "Always free", "tone": "ok"}],
      affiliate_network="none",
      distance_landmark="On the National Mall, south side"),

    m("International Spy Museum", "international-spy-museum",
      "Washington", "DC", "700 L'Enfant Plaza SW, Washington, DC 20024",
      38.8842, -77.0259, "Specialized", 2002, 8.7, 24000, 30,
      visit_time="2–3 hours", best_for="Families, espionage history",
      hours_today="10 AM – 6 PM", hours_summary="Daily 10 AM – 6 PM",
      tagline="The largest collection of international espionage artifacts on public display.",
      description="A privately-run museum (and one of the few paid museums in DC) covering the history of intelligence work. Visitors are issued a cover identity at the start and tested throughout. Rebuilt in 2019 in a larger L'Enfant Plaza building.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "It's not a Smithsonian — admission is $30, unlike the Mall museums."}],
      distance_landmark="L'Enfant Plaza"),

    m("Phillips Collection", "phillips-collection",
      "Washington", "DC", "1600 21st St NW, Washington, DC 20009",
      38.9112, -77.0467, "Art", 1921, 9.0, 5800, 16,
      visit_time="1.5 hours", best_for="Modernism, intimate setting",
      hours_today="10 AM – 5 PM", hours_summary="Tue–Sun 10 AM – 5 PM · closed Mon",
      tagline="America's first museum of modern art. Renoir's Luncheon of the Boating Party.",
      description="Founded in 1921 as the country's first museum of modern art. Renoir's Luncheon of the Boating Party is the headline; Rothko, Klee, and a Bonnard collection round out the holdings. Housed in Duncan Phillips's former Dupont Circle home.",
      review_long="The country's oldest museum of modern art, opened 1921 — older than MoMA. Renoir's Luncheon of the Boating Party hangs in its own room. The Rothko Room, four large canvases in a 12-by-12-foot space, is the only permanent Rothko-only installation in any museum.",
      highlights=[{"location": "Main Gallery", "item": "Luncheon of the Boating Party, Pierre-Auguste Renoir"},
                  {"location": "Rothko Room", "item": "Four Rothko canvases in a single small room"}],
      distance_landmark="Dupont Circle"),

    m("National Museum of the American Indian", "national-museum-of-the-american-indian",
      "Washington", "DC", "4th St & Independence Ave SW, Washington, DC 20560",
      38.8884, -77.0163, "History", 2004, 8.5, 12000, 0, "always free",
      visit_time="2 hours",
      hours_today="10 AM – 5:30 PM", hours_summary="Daily 10 AM – 5:30 PM",
      tagline="Smithsonian's Indigenous history museum. The Mitsitam Café is the city's best museum food.",
      description="The Smithsonian's museum of Native American history and culture, in a Douglas Cardinal building shaped like a wind-eroded mesa. Permanent exhibitions cover Indigenous nations across the Americas. Mitsitam Café serves regional Indigenous foods and is widely considered the best museum café in DC.",
      badges=[{"label": "Always free", "tone": "ok"}],
      affiliate_network="none",
      tips=[{"tag": "TIP", "tone": "warn", "text": "The Mitsitam Café is the best museum food in Washington — go for lunch."}],
      distance_landmark="On the National Mall, near the Capitol"),
]


# ============================================================
# BOSTON (12)
# ============================================================
BOSTON = [
    m("Museum of Fine Arts, Boston", "museum-of-fine-arts-boston",
      "Boston", "MA", "465 Huntington Ave, Boston, MA 02115",
      42.3394, -71.0941, "Art", 1870, 9.2, 31000, 27,
      visit_time="3 hours", best_for="Encyclopedic art collection",
      hours_today="10 AM – 5 PM", hours_summary="Wed–Sun 10 AM – 5 PM (Wed, Fri until 10 PM) · closed Mon–Tue",
      tagline="One of the country's great encyclopedic museums. Strong American and Asian wings.",
      description="500,000 works across all eras and continents. The Art of the Americas wing (Foster + Partners, 2010) is the most comprehensive American art collection outside the Smithsonian; the Asian collection is the largest in the West.",
      review_long="The MFA's permanent collection rivals the Met for American painting and the Asian collection rivals anything in the West (the Egyptian collection is in the same league as well). The 2010 Art of the Americas wing reorganized the American collection chronologically, and the result reads as the museum-as-textbook of US art history.",
      badges=[{"label": "Free for under-17s with adult", "tone": "ok"}],
      highlights=[{"location": "Americas Wing", "item": "Watson and the Shark, John Singleton Copley"},
                  {"location": "Asian Wing", "item": "Largest Japanese collection outside Japan"}],
      distance_landmark="Fenway, near Northeastern University"),

    m("Isabella Stewart Gardner Museum", "isabella-stewart-gardner-museum",
      "Boston", "MA", "25 Evans Way, Boston, MA 02115",
      42.3389, -71.0993, "Art", 1903, 9.4, 14000, 22,
      visit_time="1.5 hours", best_for="Atmosphere, art history",
      hours_today="11 AM – 5 PM", hours_summary="Wed–Mon 11 AM – 5 PM · closed Tue",
      tagline="A Venetian palazzo built in Boston. Empty frames where the Vermeer once hung.",
      description="Isabella Stewart Gardner's 1903 palazzo, designed to display her collection in the same arrangement she lived with. The 1990 robbery — still unsolved, $500M in art — left empty frames hanging where the Vermeer and Rembrandts were cut out.",
      review_long="By Gardner's will, the collection is displayed exactly as she arranged it in 1903 — no labels on most works, no rearrangement, no replacement of the 13 paintings stolen in the 1990 robbery (still unsolved, the largest art theft in history). The empty frames where Vermeer's The Concert and three Rembrandts once hung are still there. The interior courtyard with its four-season floral installation is the architectural highlight.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "Free admission for life if your first name is Isabella."}],
      highlights=[{"location": "Courtyard", "item": "Roman mosaic surrounded by seasonal flowers"},
                  {"location": "Dutch Room", "item": "Empty frames marking the 1990 art heist"}],
      distance_landmark="Fenway, next to the MFA"),

    m("Harvard Art Museums", "harvard-art-museums",
      "Boston", "MA", "32 Quincy St, Cambridge, MA 02138",
      42.3742, -71.1144, "Art", 1895, 8.9, 8500, 20,
      visit_time="2 hours", best_for="Concentrated collections, less-trafficked",
      hours_today="10 AM – 5 PM", hours_summary="Daily 10 AM – 5 PM",
      tagline="Three Harvard collections in one Renzo Piano building. Free for everyone since 2022.",
      description="Three formerly-separate Harvard collections (Fogg, Busch-Reisinger, Sackler) consolidated in a 2014 Renzo Piano building. Strong in German Expressionism (Busch-Reisinger), Asian and Mediterranean antiquity (Sackler), and pre-1900 European/American (Fogg). Free since 2022.",
      badges=[{"label": "Always free", "tone": "ok"}],
      affiliate_network="none",
      distance_landmark="Harvard Square, Cambridge"),

    m("Institute of Contemporary Art Boston", "institute-of-contemporary-art-boston",
      "Boston", "MA", "25 Harbor Shore Dr, Boston, MA 02210",
      42.3536, -71.0466, "Art", 1936, 8.5, 5400, 20,
      visit_time="1.5 hours", best_for="Contemporary art, harbor views",
      hours_today="10 AM – 5 PM", hours_summary="Tue–Sun 10 AM – 5 PM (Thu, Fri until 9 PM) · closed Mon",
      tagline="Diller Scofidio + Renfro cantilever over Boston Harbor. Strong rotating shows.",
      description="Boston's contemporary art museum, in a 2006 Diller Scofidio + Renfro building cantilevered over the harbor. The Watershed satellite gallery in East Boston (free, open seasonally) is part of the same institution.",
      badges=[{"label": "Free Thu 5–9 PM", "tone": "ok"}],
      distance_landmark="Seaport District, on the harbor"),

    m("Museum of Science Boston", "museum-of-science-boston",
      "Boston", "MA", "1 Science Park, Boston, MA 02114",
      42.3679, -71.0708, "Science", 1830, 8.8, 21000, 31,
      visit_time="3 hours", best_for="Families",
      hours_today="9 AM – 5 PM", hours_summary="Sat–Thu 9 AM – 5 PM · Fri 9 AM – 9 PM",
      tagline="One of America's oldest science museums. Lightning shows, IMAX, planetarium.",
      description="Founded 1830 as the Boston Society of Natural History. Now a sprawling science museum on a peninsula in the Charles River, with a Theater of Electricity (regular live lightning demonstrations on a 6-million-volt Van de Graaff generator), an Omni IMAX dome, and the Charles Hayden Planetarium.",
      badges=[{"label": "Family favorite", "tone": "warn"}],
      highlights=[{"location": "Theater of Electricity", "item": "World's largest air-insulated Van de Graaff generator"}],
      distance_landmark="On the Charles River, between Boston and Cambridge"),

    m("New England Aquarium", "new-england-aquarium",
      "Boston", "MA", "1 Central Wharf, Boston, MA 02110",
      42.3592, -71.0490, "Specialized", 1969, 8.8, 26000, 36,
      visit_time="2 hours", best_for="Families, marine life",
      hours_today="9 AM – 5 PM", hours_summary="Mon–Fri 9 AM – 5 PM · Sat–Sun 9 AM – 6 PM",
      tagline="Four-story Giant Ocean Tank with a coral reef and 1,000+ animals.",
      description="The four-story Giant Ocean Tank — a 200,000-gallon coral reef cylinder you spiral down around — is the centerpiece. Penguin colony at the base, IMAX theater attached, harbor seal exhibit out front (free to view).",
      badges=[{"label": "Family favorite", "tone": "warn"}],
      distance_landmark="Central Wharf, downtown waterfront"),

    m("John F. Kennedy Presidential Library and Museum", "john-f-kennedy-presidential-library-and-museum",
      "Boston", "MA", "Columbia Point, Boston, MA 02125",
      42.3168, -71.0345, "History", 1979, 8.9, 7200, 18,
      visit_time="2 hours",
      hours_today="10 AM – 5 PM", hours_summary="Daily 10 AM – 5 PM",
      tagline="JFK's archive in an I. M. Pei building on Columbia Point.",
      description="The official archive of the Kennedy presidency, in an I. M. Pei building on a peninsula south of downtown. Permanent exhibits cover the 1960 campaign, the Cuban Missile Crisis, and the assassination. The harbor view from the pavilion is part of the architectural design.",
      distance_landmark="Columbia Point, near UMass Boston"),

    m("Boston Children's Museum", "boston-childrens-museum",
      "Boston", "MA", "308 Congress St, Boston, MA 02210",
      42.3525, -71.0494, "Children", 1913, 8.7, 7400, 22,
      visit_time="2.5 hours", best_for="Children under 10",
      hours_today="10 AM – 5 PM", hours_summary="Wed–Sun 10 AM – 5 PM · closed Mon–Tue",
      tagline="The country's second-oldest children's museum. Best for under-10s.",
      description="Founded 1913, second-oldest children's museum in the US. Hands-on exhibits across science, art, and culture; the Japanese House — a real two-story Kyoto townhouse reassembled inside the building — is the unusual highlight.",
      badges=[{"label": "Family favorite", "tone": "warn"}],
      highlights=[{"location": "Floor 2", "item": "Kyo-no-Machiya, a real Kyoto silk merchant's house"}],
      distance_landmark="Seaport waterfront"),

    m("USS Constitution Museum", "uss-constitution-museum",
      "Boston", "MA", "Building 22, Charlestown Navy Yard, Boston, MA 02129",
      42.3724, -71.0556, "Military", 1972, 8.8, 4900, 0, "suggested donation",
      visit_time="1.5 hours",
      hours_today="10 AM – 5 PM", hours_summary="Daily 10 AM – 5 PM",
      tagline="The world's oldest commissioned warship still afloat. Free, with the ship next door.",
      description="The companion museum to USS Constitution (Old Ironsides), the 1797 frigate that earned its nickname when British cannonballs bounced off its hull during the War of 1812. Both museum and ship are free with suggested donation; the ship is across the street.",
      badges=[{"label": "Suggested donation", "tone": "ok"}],
      affiliate_network="none",
      distance_landmark="Charlestown Navy Yard, across the river from downtown"),

    m("Peabody Museum of Archaeology and Ethnology", "peabody-museum-of-archaeology-and-ethnology",
      "Boston", "MA", "11 Divinity Ave, Cambridge, MA 02138",
      42.3779, -71.1148, "Specialized", 1866, 8.5, 1600, 15,
      visit_time="1.5 hours",
      hours_today="9 AM – 5 PM", hours_summary="Daily 9 AM – 5 PM",
      tagline="Harvard's anthropology museum. Maya, Indigenous American, Pacific collections.",
      description="One of the oldest anthropology museums in the Americas. Strong Mesoamerican (Aztec, Maya) collection, a Pacific Hall, and Indigenous American galleries. Combined ticket with the adjacent Harvard Museum of Natural History.",
      distance_landmark="Harvard Yard, Cambridge"),

    m("MIT Museum", "mit-museum",
      "Boston", "MA", "314 Main St, Cambridge, MA 02141",
      42.3622, -71.0879, "Science", 1971, 8.7, 2300, 18,
      visit_time="1.5 hours", best_for="Engineering, AI history",
      hours_today="10 AM – 5 PM", hours_summary="Tue–Sun 10 AM – 5 PM · closed Mon",
      tagline="MIT's research and engineering museum, reopened 2022 in Kendall Square.",
      description="MIT's official museum, reopened 2022 in a new Kendall Square location. Permanent exhibits include MIT's history with AI, robotics, and the early Web; rotating shows often feature live MIT research.",
      distance_landmark="Kendall Square, Cambridge"),

    m("Mary Baker Eddy Library", "mary-baker-eddy-library",
      "Boston", "MA", "200 Massachusetts Ave, Boston, MA 02115",
      42.3461, -71.0857, "Specialized", 2002, 9.0, 2400, 6,
      visit_time="45 minutes",
      hours_today="10 AM – 4 PM", hours_summary="Tue–Sat 10 AM – 4 PM · closed Sun–Mon",
      tagline="The Mapparium — a stained-glass globe you walk inside.",
      description="The library is the headquarters of the Christian Science Monitor and the Mary Baker Eddy archive, but the reason to visit is the Mapparium: a 30-foot-diameter stained-glass globe of the world (1935) you walk through on a bridge through its center. The acoustics make whispers travel across the inside.",
      review_long="Most visitors come specifically for the Mapparium and stay for the rest. Built in 1935, the globe shows national borders as they were at that exact moment — Persia, the British Raj, the USSR — preserved unchanged. The acoustic effect on the bridge through the middle is genuinely strange: speak normally and you'll hear yourself echo back amplified, while a whisper from across the globe arrives clearly.",
      highlights=[{"location": "Mapparium", "item": "30-foot stained-glass globe, 1935 borders preserved"}],
      distance_landmark="Christian Science Plaza, near Symphony Hall"),
]


# ============================================================
# SAN FRANCISCO (12)
# ============================================================
SAN_FRANCISCO = [
    m("de Young Museum", "de-young-museum",
      "San Francisco", "CA", "50 Hagiwara Tea Garden Dr, San Francisco, CA 94118",
      37.7714, -122.4685, "Art", 1895, 8.9, 18000, 20,
      visit_time="2 hours", best_for="American art, observation tower",
      hours_today="9:30 AM – 5:15 PM", hours_summary="Tue–Sun 9:30 AM – 5:15 PM · closed Mon",
      tagline="Herzog & de Meuron building in Golden Gate Park. American and Oceanic art.",
      description="One of the Fine Arts Museums of San Francisco. The 2005 Herzog & de Meuron building is wrapped in copper that's now oxidized green; the 144-foot observation tower at the top is free to enter. Strong American and Oceanic collections.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "The 9th-floor observation tower is free, even without a ticket."},
            {"tag": "FREE", "tone": "ok", "text": "Free first Tuesdays for Bay Area residents."}],
      highlights=[{"location": "Hamon Tower", "item": "144-foot observation tower, free entry, 360° park views"}],
      distance_landmark="Golden Gate Park, near the Japanese Tea Garden"),

    m("San Francisco Museum of Modern Art", "san-francisco-museum-of-modern-art",
      "San Francisco", "CA", "151 3rd St, San Francisco, CA 94103",
      37.7857, -122.4011, "Art", 1935, 8.8, 20000, 30,
      visit_time="2.5 hours", best_for="Modern and contemporary",
      hours_today="10 AM – 5 PM", hours_summary="Fri–Tue 10 AM – 5 PM · closed Wed–Thu",
      tagline="The first West Coast museum dedicated to 20th-century art. Doubled in size in 2016.",
      description="Founded 1935 — the first West Coast museum exclusively for modern art. The 2016 Snøhetta expansion doubled the gallery space and added one of the largest contemporary collections on the West Coast. The Pritzker Center for Photography is the largest dedicated photography space in any US art museum.",
      badges=[{"label": "Free for under-18s", "tone": "ok"}],
      distance_landmark="Yerba Buena, SoMa"),

    m("California Academy of Sciences", "california-academy-of-sciences",
      "San Francisco", "CA", "55 Music Concourse Dr, San Francisco, CA 94118",
      37.7699, -122.4661, "Natural History", 1853, 9.1, 27000, 45,
      visit_time="3 hours", best_for="Families, four-museums-in-one",
      hours_today="9:30 AM – 5 PM", hours_summary="Mon–Sat 9:30 AM – 5 PM · Sun 11 AM – 5 PM",
      tagline="Aquarium, planetarium, natural history museum, and rainforest under one living roof.",
      description="A natural history museum, a Steinhart Aquarium, the Morrison Planetarium, and a four-story enclosed rainforest, all under a 2.5-acre living roof designed by Renzo Piano. NightLife events on Thursdays are 21+ only and drink-friendly.",
      review_long="Four major institutions under one roof: a natural history museum, an aquarium with the largest coral reef on display in any US museum, a planetarium dome, and a four-story enclosed Costa Rican rainforest with a glass canopy walk and a basement-level Amazon flooded forest. The roof itself, planted with native California species, is open to visitors.\n\nNightLife on Thursdays (21+, ticketed separately) turns the whole museum into an after-hours venue with cocktails.",
      badges=[{"label": "Family favorite", "tone": "warn"}, {"label": "NightLife Thu 21+", "tone": "info"}],
      highlights=[{"location": "Rainforest", "item": "4-story enclosed rainforest with glass canopy walk"},
                  {"location": "Aquarium", "item": "Philippine Coral Reef, largest in any US museum"}],
      distance_landmark="Golden Gate Park, opposite the de Young"),

    m("Legion of Honor", "legion-of-honor",
      "San Francisco", "CA", "100 34th Ave, San Francisco, CA 94121",
      37.7841, -122.5008, "Art", 1924, 9.0, 9200, 20,
      visit_time="2 hours", best_for="European art, Rodin, ocean views",
      hours_today="9:30 AM – 5:15 PM", hours_summary="Tue–Sun 9:30 AM – 5:15 PM · closed Mon",
      tagline="A neoclassical replica of the Paris Légion d'honneur, perched over the Pacific.",
      description="3/4-scale replica of the Hôtel de Salm in Paris, built in 1924 on a clifftop in Lincoln Park overlooking the Pacific. European art (Rembrandt, El Greco, Monet) plus the largest collection of Auguste Rodin sculpture outside Europe.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "Combine with Lands End and the Sutro Bath ruins — they're a short walk away."}],
      highlights=[{"location": "Court of Honor", "item": "An original cast of Rodin's The Thinker"}],
      distance_landmark="Lincoln Park, Outer Richmond"),

    m("Asian Art Museum of San Francisco", "asian-art-museum-of-san-francisco",
      "San Francisco", "CA", "200 Larkin St, San Francisco, CA 94102",
      37.7800, -122.4159, "Art", 1966, 8.8, 9100, 20,
      visit_time="2 hours",
      hours_today="10 AM – 5 PM", hours_summary="Thu–Mon 10 AM – 5 PM (Thu until 9 PM) · closed Tue–Wed",
      tagline="One of the largest Asian art collections in the world. In SF's old Main Library.",
      description="More than 18,000 works from 6,000 years across the Asian continent. The 2003 Gae Aulenti renovation transformed San Francisco's old main library into the museum's home. Free first Sundays.",
      badges=[{"label": "Free first Sundays", "tone": "ok"}],
      distance_landmark="Civic Center, opposite City Hall"),

    m("Exploratorium", "exploratorium",
      "San Francisco", "CA", "Pier 15, San Francisco, CA 94111",
      37.8011, -122.3987, "Science", 1969, 9.2, 22000, 35,
      visit_time="3 hours", best_for="Families, hands-on science",
      hours_today="10 AM – 5 PM", hours_summary="Tue–Sun 10 AM – 5 PM · closed Mon (After Dark Thu 18+)",
      tagline="The original hands-on science museum. Frank Oppenheimer's 1969 founding template.",
      description="The original hands-on science museum, founded by physicist Frank Oppenheimer in 1969. The pier-side location since 2013 is the third home; outdoor exhibits along the Embarcadero are free to anyone walking by. After Dark Thursdays are 18+ and ticketed separately.",
      review_long="Frank Oppenheimer's 1969 Exploratorium was the template that every children's science museum since has copied. Six galleries, more than 600 exhibits, all of them are designed to be touched and operated. The outdoor portion along the Embarcadero — the Wave Organ, the bay bridge sound mirrors — is free to anyone walking by.",
      badges=[{"label": "After Dark Thu (18+)", "tone": "info"}, {"label": "Family favorite", "tone": "warn"}],
      distance_landmark="Embarcadero, Pier 15"),

    m("Contemporary Jewish Museum", "contemporary-jewish-museum",
      "San Francisco", "CA", "736 Mission St, San Francisco, CA 94103",
      37.7857, -122.4040, "Art", 1984, 8.4, 1900, 16,
      visit_time="1 hour",
      hours_today="11 AM – 5 PM", hours_summary="Thu–Tue 11 AM – 5 PM · closed Wed",
      tagline="Daniel Libeskind addition grafted onto a brick power substation.",
      description="A non-collecting museum focused on rotating exhibitions of contemporary Jewish art and culture. The Daniel Libeskind addition — a tilted blue cube — is grafted onto an 1881 brick power substation. Often included on city museum passes.",
      distance_landmark="Yerba Buena, SoMa"),

    m("Museum of the African Diaspora", "museum-of-the-african-diaspora",
      "San Francisco", "CA", "685 Mission St, San Francisco, CA 94105",
      37.7866, -122.4007, "Art", 2005, 8.5, 1300, 12,
      visit_time="1 hour",
      hours_today="11 AM – 6 PM", hours_summary="Wed–Sat 11 AM – 6 PM · Sun 12 PM – 5 PM · closed Mon–Tue",
      tagline="A non-collecting institution focused on contemporary art of the African diaspora.",
      description="Three floors of rotating exhibitions in the lobby of the St. Regis hotel. Programming centers contemporary artists, music, and film of the African diaspora.",
      distance_landmark="Yerba Buena, SoMa"),

    m("Walt Disney Family Museum", "walt-disney-family-museum",
      "San Francisco", "CA", "104 Montgomery St, San Francisco, CA 94129",
      37.7990, -122.4566, "Specialized", 2009, 9.1, 4500, 25,
      visit_time="2 hours", best_for="Disney history, animation",
      hours_today="10 AM – 5:30 PM", hours_summary="Wed–Sun 10 AM – 5:30 PM · closed Mon–Tue",
      tagline="The full personal and professional life of Walt Disney, in the Presidio.",
      description="Founded by Walt's daughter Diane, in a converted Presidio barracks. Tells Walt Disney's life chronologically through original animation cels, his own model trains, and a 12-foot-tall model of Disneyland built to original specs.",
      distance_landmark="Presidio, near the Main Post"),

    m("Cable Car Museum", "cable-car-museum",
      "San Francisco", "CA", "1201 Mason St, San Francisco, CA 94108",
      37.7949, -122.4117, "History", 1974, 9.0, 4000, 0, "always free",
      visit_time="45 minutes",
      hours_today="10 AM – 5 PM", hours_summary="Daily 10 AM – 5 PM",
      tagline="The actual working power station that pulls every cable car in the city.",
      description="A free museum inside the 1907 Washington-Mason powerhouse — the still-operating heart of the cable car system. From the gallery floor you can watch the four motors that pull all of the city's cable lines.",
      badges=[{"label": "Always free", "tone": "ok"}],
      affiliate_network="none",
      tips=[{"tag": "FREE", "tone": "ok", "text": "Free museum, plus an active power plant — the wheels are turning while you watch."}],
      distance_landmark="Nob Hill, on the Powell-Mason cable line"),

    m("Cartoon Art Museum", "cartoon-art-museum",
      "San Francisco", "CA", "781 Beach St, San Francisco, CA 94109",
      37.8068, -122.4226, "Specialized", 1987, 8.6, 1200, 0, "suggested $5",
      visit_time="45 minutes",
      hours_today="11 AM – 5 PM", hours_summary="Tue–Sun 11 AM – 5 PM · closed Mon",
      tagline="A small, suggested-donation museum focused on comics and animation.",
      description="The country's only museum dedicated entirely to cartoon art. Rotating exhibitions of original comic strip art, animation cels, graphic novels, and editorial cartoons. Suggested donation.",
      badges=[{"label": "Suggested $5", "tone": "ok"}],
      affiliate_network="none",
      distance_landmark="Fisherman's Wharf, near Ghirardelli Square"),

    m("GLBT Historical Society Museum", "glbt-historical-society-museum",
      "San Francisco", "CA", "4127 18th St, San Francisco, CA 94114",
      37.7610, -122.4316, "History", 2011, 8.7, 760, 5,
      visit_time="1 hour",
      hours_today="11 AM – 5 PM", hours_summary="Thu–Sun 11 AM – 5 PM · closed Mon–Wed",
      tagline="The country's first LGBTQ history museum, in the heart of the Castro.",
      description="A small, focused history museum in the Castro. Permanent and rotating exhibits on LGBTQ history in San Francisco, from gay-rights pioneer Harvey Milk to the AIDS crisis archives. $5 suggested admission.",
      affiliate_network="none",
      distance_landmark="The Castro, on 18th Street"),
]


# ============================================================
# PHILADELPHIA (12)
# ============================================================
PHILADELPHIA = [
    m("Philadelphia Museum of Art", "philadelphia-museum-of-art",
      "Philadelphia", "PA", "2600 Benjamin Franklin Pkwy, Philadelphia, PA 19130",
      39.9656, -75.1810, "Art", 1876, 9.1, 28000, 30,
      visit_time="3 hours", best_for="European and American art, the steps",
      hours_today="10 AM – 5 PM", hours_summary="Wed–Mon 10 AM – 5 PM · closed Tue",
      tagline="The Rocky steps. Also one of the great American art museums.",
      description="The third-largest art museum in the country by gallery space, in a 1928 Greek revival building topped by the steps Sylvester Stallone made famous. Strong Impressionism, Asian, and American collections; 2021 Frank Gehry renovation reopened the lower-level Forum.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "Free admission Friday after 5 PM. Pay-what-you-wish first Sunday of the month."},
            {"tag": "TIP", "tone": "warn", "text": "Combine with the Rodin Museum and the Barnes — all on the parkway."}],
      highlights=[{"location": "Steps", "item": "The Rocky Steps and the Rocky statue at the bottom"},
                  {"location": "American Wing", "item": "Thomas Eakins, including The Gross Clinic"}],
      distance_landmark="Top of the Benjamin Franklin Parkway"),

    m("Barnes Foundation", "barnes-foundation",
      "Philadelphia", "PA", "2025 Benjamin Franklin Pkwy, Philadelphia, PA 19130",
      39.9655, -75.1727, "Art", 1922, 9.3, 12000, 30,
      visit_time="2.5 hours", best_for="Impressionism, idiosyncratic display",
      hours_today="11 AM – 5 PM", hours_summary="Wed–Mon 11 AM – 5 PM · closed Tue",
      tagline="The largest single Renoir collection in the world. Hung exactly as Albert Barnes arranged it.",
      description="Albert C. Barnes's idiosyncratic 1920s collection — the world's largest Renoir holding, plus dozens of Cézannes, Matisses, Picassos — hung in his original 'ensembles' alongside ironwork and ceramics. The 2012 move from Merion to the Parkway preserved every wall arrangement.",
      review_long="Barnes was a chemist who got rich off an antiseptic in the 1900s and spent the next 40 years assembling the most idiosyncratic art collection in America: 181 Renoirs (the largest single collection anywhere), 69 Cézannes, 59 Matisses, 46 Picassos, plus medieval ironwork, African masks, and Pennsylvania Dutch furniture, all hung in 'ensembles' that he arranged personally and forbade anyone from rearranging in his will.\n\nThe 2012 building on the Parkway preserves every ensemble exactly as Barnes left them in his Merion mansion.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "Reserve in advance — entry is timed and Saturdays sell out."}],
      highlights=[{"location": "Main Room", "item": "Cézanne's The Card Players"},
                  {"location": "Throughout", "item": "181 Renoirs in the original Barnes ensembles"}],
      distance_landmark="On the Parkway, between Logan Square and the Art Museum"),

    m("Franklin Institute", "franklin-institute",
      "Philadelphia", "PA", "222 N 20th St, Philadelphia, PA 19103",
      39.9582, -75.1729, "Science", 1824, 8.9, 21000, 25,
      visit_time="3 hours", best_for="Families",
      hours_today="9:30 AM – 5 PM", hours_summary="Daily 9:30 AM – 5 PM",
      tagline="The Giant Heart you walk through. Old-school hands-on science.",
      description="One of the oldest science museums in the country. The walk-through Giant Heart — a two-story anatomical model with sound effects — has been a fixture since 1954. Plus a planetarium, an IMAX, and a permanent Franklin biographical wing.",
      badges=[{"label": "Family favorite", "tone": "warn"}],
      highlights=[{"location": "Giant Heart", "item": "Two-story heart model, walk-through since 1954"}],
      distance_landmark="Logan Square, on the Parkway"),

    m("National Constitution Center", "national-constitution-center",
      "Philadelphia", "PA", "525 Arch St, Philadelphia, PA 19106",
      39.9518, -75.1494, "History", 2003, 9.0, 7800, 16,
      visit_time="2 hours",
      hours_today="10 AM – 5 PM", hours_summary="Wed–Sun 10 AM – 5 PM · closed Mon–Tue",
      tagline="The only museum dedicated to the U.S. Constitution.",
      description="Across the lawn from Independence Hall. Permanent exhibit traces the Constitution's history; the Signers' Hall has 42 life-size bronze statues of the framers, walkable. Hosts the 'We the People' theatrical experience.",
      highlights=[{"location": "Signers' Hall", "item": "42 life-size bronze statues of the Constitutional framers"}],
      distance_landmark="Independence Mall, opposite Independence Hall"),

    m("Mütter Museum", "mutter-museum",
      "Philadelphia", "PA", "19 S 22nd St, Philadelphia, PA 19103",
      39.9530, -75.1764, "Specialized", 1858, 9.2, 12000, 20,
      visit_time="1.5 hours", best_for="Medical curiosities, dark tourism",
      hours_today="10 AM – 5 PM", hours_summary="Daily 10 AM – 5 PM",
      tagline="Anatomical specimens and medical history. Not for everyone.",
      description="The College of Physicians' museum of medical specimens, since 1858. Holds the Hyrtl Skull Collection, slides of Einstein's brain, the Soap Lady (a saponified corpse), and conjoined-twin skeletons. Photography prohibited inside.",
      review_long="Founded 1858 as a teaching collection for the College of Physicians and now one of the country's strangest museums. Specimens include the Hyrtl Skull Collection (139 craniums for racial anatomy comparisons, an artifact of 19th-century pseudoscience), the Soap Lady (a body that saponified in the soil), tissue samples from Einstein's brain, and a wall of inhaled foreign objects extracted from Philadelphia patients between 1900 and 1930. Photography is prohibited inside.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "Not for the squeamish. Photography is prohibited inside."}],
      distance_landmark="Center City, near Logan Square"),

    m("Independence Seaport Museum", "independence-seaport-museum",
      "Philadelphia", "PA", "211 S Christopher Columbus Blvd, Philadelphia, PA 19106",
      39.9474, -75.1410, "History", 1961, 8.5, 2400, 20,
      visit_time="2 hours",
      hours_today="10 AM – 5 PM", hours_summary="Daily 10 AM – 5 PM",
      tagline="The cruiser Olympia (1892) and submarine Becuna (WWII), with the Seaport Museum.",
      description="At Penn's Landing on the Delaware. Combined ticket includes the museum, the cruiser USS Olympia (Admiral Dewey's flagship at Manila Bay, 1898), and the WWII submarine USS Becuna. Olympia is the oldest steel American warship still afloat.",
      distance_landmark="Penn's Landing, downtown waterfront"),

    m("Rodin Museum", "rodin-museum",
      "Philadelphia", "PA", "2151 Benjamin Franklin Pkwy, Philadelphia, PA 19130",
      39.9633, -75.1750, "Art", 1929, 8.9, 3500, 12,
      visit_time="45 minutes",
      hours_today="10 AM – 5 PM", hours_summary="Wed–Mon 10 AM – 5 PM · closed Tue",
      tagline="The largest collection of Auguste Rodin sculpture outside Paris.",
      description="A small purpose-built 1929 museum on the Parkway with the largest Rodin collection outside the Musée Rodin in Paris. Garden contains a cast of The Thinker; main hall has a cast of The Burghers of Calais.",
      highlights=[{"location": "Garden", "item": "An original cast of The Thinker"},
                  {"location": "Hall", "item": "Burghers of Calais, six full-size figures"}],
      distance_landmark="On the Parkway, between Logan Square and the Art Museum"),

    m("Penn Museum", "penn-museum",
      "Philadelphia", "PA", "3260 South St, Philadelphia, PA 19104",
      39.9494, -75.1916, "Specialized", 1887, 8.8, 5800, 18,
      visit_time="2 hours",
      hours_today="10 AM – 5 PM", hours_summary="Tue–Sun 10 AM – 5 PM · closed Mon",
      tagline="The University of Pennsylvania's archaeology and anthropology museum.",
      description="One of the largest archaeology museums in the country. Strong Egyptian (a 13-ton sphinx of Ramses II), Mesopotamian (Ur royal tombs), and Mayan collections. The Egyptian Galleries reopened in 2024 after a major renovation.",
      highlights=[{"location": "Egypt", "item": "Sphinx of Ramses II, 13 tons of red granite"}],
      distance_landmark="University City, on the Penn campus"),

    m("African American Museum in Philadelphia", "african-american-museum-in-philadelphia",
      "Philadelphia", "PA", "701 Arch St, Philadelphia, PA 19106",
      39.9540, -75.1503, "History", 1976, 8.5, 1700, 14,
      visit_time="1.5 hours",
      hours_today="10 AM – 5 PM", hours_summary="Thu–Sat 10 AM – 5 PM · Sun 12 PM – 5 PM · closed Mon–Wed",
      tagline="The first major US museum dedicated to African American history. Built for the 1976 Bicentennial.",
      description="Founded for the 1976 Bicentennial as the first US museum funded and built specifically for African American history. Permanent exhibit on Black Philadelphia from the colonial era to the present.",
      distance_landmark="Old City, near Independence Mall"),

    m("Weitzman National Museum of American Jewish History", "weitzman-national-museum-of-american-jewish-history",
      "Philadelphia", "PA", "101 S Independence Mall E, Philadelphia, PA 19106",
      39.9494, -75.1499, "History", 1976, 8.6, 2100, 15,
      visit_time="1.5 hours",
      hours_today="10 AM – 5 PM", hours_summary="Wed–Sun 10 AM – 5 PM · closed Mon–Tue",
      tagline="Three centuries of Jewish American history, on Independence Mall.",
      description="The only museum dedicated to the Jewish American experience, in a James Polshek building on Independence Mall. Permanent collection includes Irving Berlin's piano and a section of the original Lower East Side Eldridge Street Synagogue.",
      distance_landmark="Independence Mall, opposite the Liberty Bell"),

    m("Eastern State Penitentiary", "eastern-state-penitentiary",
      "Philadelphia", "PA", "2027 Fairmount Ave, Philadelphia, PA 19130",
      39.9682, -75.1719, "History", 1994, 9.2, 14000, 25,
      visit_time="2 hours", best_for="History, Halloween",
      hours_today="10 AM – 5 PM", hours_summary="Daily 10 AM – 5 PM",
      tagline="A preserved 1829 prison, including Al Capone's cell. Also runs Halloween Nights.",
      description="The world's first true penitentiary, opened 1829, abandoned in 1971, preserved as a 'stabilized ruin' since 1994. Houses Al Capone's preserved cell. Operates Halloween Nights, the country's most-attended Halloween event, in October.",
      review_long="Eastern State was the prototype for the modern penitentiary system: complete solitary confinement was the design principle, and 300+ prisons worldwide copied its radial cellblock layout. Most famous inmate: Al Capone, who served eight months here in 1929–30 (his cell, with rugs, lamps, and a radio, is preserved). The audio tour is narrated by Steve Buscemi.\n\nIn October the entire complex transforms into Halloween Nights, a haunted-house experience that's been running since 1991 and books out far in advance.",
      highlights=[{"location": "Cellblock 8", "item": "Al Capone's preserved cell, 1929"}],
      distance_landmark="Fairmount, on the way to the Art Museum"),

    m("Please Touch Museum", "please-touch-museum",
      "Philadelphia", "PA", "4231 Avenue of the Republic, Philadelphia, PA 19131",
      39.9772, -75.2063, "Children", 1976, 8.7, 7100, 24,
      visit_time="2.5 hours", best_for="Children under 8",
      hours_today="9 AM – 5 PM", hours_summary="Daily 9 AM – 5 PM",
      tagline="Philadelphia's children's museum, in the 1876 Centennial Memorial Hall.",
      description="In Memorial Hall, the only major surviving building from the 1876 Centennial Exhibition. Hands-on exhibits across science, art, and storytelling for children under 8. The 1908 Dentzel carousel is original to the building.",
      badges=[{"label": "Family favorite", "tone": "warn"}],
      distance_landmark="Fairmount Park, west side"),
]


# ============================================================
# ATLANTA (12)
# ============================================================
ATLANTA = [
    m("High Museum of Art", "high-museum-of-art",
      "Atlanta", "GA", "1280 Peachtree St NE, Atlanta, GA 30309",
      33.7901, -84.3858, "Art", 1905, 8.8, 8400, 19,
      visit_time="2.5 hours", best_for="American and folk art",
      hours_today="10 AM – 5 PM", hours_summary="Tue–Sun 10 AM – 5 PM · closed Mon",
      tagline="Richard Meier's white modernist building. Strong American and African collections.",
      description="The leading art museum in the Southeast. Richard Meier's 1983 building (his first museum, before the Getty) was expanded by Renzo Piano in 2005. Strong holdings in American art, decorative arts, folk and self-taught art.",
      highlights=[{"location": "Folk Art Galleries", "item": "Howard Finster, Bill Traylor, Thornton Dial"}],
      distance_landmark="Midtown, in the Woodruff Arts Center"),

    m("Atlanta History Center", "atlanta-history-center",
      "Atlanta", "GA", "130 W Paces Ferry Rd NW, Atlanta, GA 30305",
      33.8430, -84.3879, "History", 1926, 9.0, 5400, 24,
      visit_time="3 hours", best_for="Civil War, Atlanta history",
      hours_today="10 AM – 5:30 PM", hours_summary="Mon–Sat 10 AM – 5:30 PM · Sun 12 PM – 5:30 PM",
      tagline="The Battle of Atlanta cyclorama (1886), one of only two surviving in the US.",
      description="33 acres in Buckhead. The 1886 Battle of Atlanta Cyclorama (a 49-foot-tall, 358-foot-around painted-in-the-round Civil War scene) is the headline; also includes a 1928 Tudor Revival mansion (the Swan House) and an 1840s plantation house.",
      review_long="The Cyclorama is the reason most visitors come: an 1886 hand-painted depiction of the 1864 Battle of Atlanta, 49 feet tall and 358 feet around, viewed from a center platform that rotates. One of only two surviving cycloramas of its type in the US (the other is at Gettysburg). The Swan House gardens and the cyclorama building are themselves architectural pieces.",
      highlights=[{"location": "Cyclorama Building", "item": "Battle of Atlanta cyclorama, 1886, fully restored"},
                  {"location": "Swan House", "item": "1928 Tudor mansion, used as the Capitol in The Hunger Games"}],
      distance_landmark="Buckhead"),

    m("World of Coca-Cola", "world-of-coca-cola",
      "Atlanta", "GA", "121 Baker St NW, Atlanta, GA 30313",
      33.7626, -84.3927, "Specialized", 1990, 8.8, 30000, 19,
      visit_time="1.5 hours", best_for="Families, brand history",
      hours_today="10 AM – 5 PM", hours_summary="Daily 10 AM – 5 PM",
      tagline="The Coca-Cola Company's official brand museum. Tasting room with 100+ flavors.",
      description="A corporate museum, but a comprehensive one — the actual handwritten Coca-Cola formula vault, century-old advertising archives, a 4D theater, and a tasting room with 100+ Coca-Cola products from 60 countries (including Beverly, the famous bitter Italian one).",
      badges=[{"label": "Family favorite", "tone": "warn"}],
      tips=[{"tag": "TIP", "tone": "warn", "text": "Combo with the Georgia Aquarium across the plaza."}],
      highlights=[{"location": "Vault", "item": "The (replica) handwritten Coca-Cola formula"},
                  {"location": "Tasting Room", "item": "100+ Coca-Cola flavors from 60 countries"}],
      distance_landmark="Pemberton Place, downtown"),

    m("National Center for Civil and Human Rights", "national-center-for-civil-and-human-rights",
      "Atlanta", "GA", "100 Ivan Allen Jr Blvd, Atlanta, GA 30313",
      33.7634, -84.3927, "History", 2014, 9.2, 5400, 21,
      visit_time="2 hours",
      hours_today="10 AM – 5 PM", hours_summary="Tue–Sun 10 AM – 5 PM · closed Mon",
      tagline="The American civil rights movement and its global descendants. Sit-in simulator.",
      description="Three floors covering the American civil rights movement, the Martin Luther King Jr. archive, and global human rights work. The lunch-counter sit-in simulator (haptic feedback for the slurs and threats hurled at participants in 1960) is the centerpiece.",
      review_long="The Rolls Down Like Water gallery on the second floor walks through the American civil rights movement chronologically. The lunch-counter simulator — wear headphones, sit at the counter, hold the chair to feel the real haptic feedback of the slurs and threats — is the most demanding two minutes you can spend in any Atlanta museum.\n\nThe MLK Archive on the third floor includes original handwritten drafts of his speeches.",
      highlights=[{"location": "Floor 2", "item": "Lunch counter simulator, 1960 sit-in"},
                  {"location": "Floor 3", "item": "Original Martin Luther King Jr. handwritten drafts"}],
      distance_landmark="Pemberton Place, opposite the Georgia Aquarium"),

    m("Fernbank Museum", "fernbank-museum",
      "Atlanta", "GA", "767 Clifton Rd NE, Atlanta, GA 30307",
      33.7728, -84.3265, "Natural History", 1992, 8.8, 5800, 27,
      visit_time="2.5 hours", best_for="Families, dinosaurs",
      hours_today="10 AM – 5 PM", hours_summary="Daily 10 AM – 5 PM",
      tagline="Argentinosaurus and Giganotosaurus mounts in the Atrium. Plus 75 acres of forest.",
      description="Atlanta's natural history museum. Headline: full-size casts of Argentinosaurus (123 feet long) and the predator Giganotosaurus in the Great Hall. The museum is on a 75-acre old-growth forest preserve with hiking trails included on the ticket.",
      badges=[{"label": "Family favorite", "tone": "warn"}],
      highlights=[{"location": "Great Hall", "item": "Argentinosaurus, 123 ft, full skeletal cast"}],
      distance_landmark="Druid Hills, near Emory University"),

    m("Center for Puppetry Arts", "center-for-puppetry-arts",
      "Atlanta", "GA", "1404 Spring St NW, Atlanta, GA 30309",
      33.7929, -84.3917, "Specialized", 1978, 9.0, 3200, 12,
      visit_time="1 hour (museum) + show",
      hours_today="11 AM – 5 PM", hours_summary="Tue–Sun 11 AM – 5 PM · closed Mon",
      tagline="Jim Henson's archive — Kermit, Big Bird, the Yip Yips. Also a working theater.",
      description="The largest Henson collection anywhere — original Kermit, Big Bird, Bert and Ernie, and the original Labyrinth puppets — donated by Jim Henson and the Henson family. The Global Gallery covers world puppetry traditions. Live shows in the attached theater (separately ticketed).",
      review_long="The largest Jim Henson collection in the world, donated personally by Henson and his family. Original Kermit (the one made from his mother's coat), Big Bird, Yip Yips, and the entire cast of the 1986 Labyrinth (with David Bowie's Goblin King at the center). The Global Gallery shows world puppetry traditions; the on-site theater puts on weekly puppet shows.",
      highlights=[{"location": "Henson Gallery", "item": "Original Kermit, Big Bird, Bert, Ernie"},
                  {"location": "Henson Gallery", "item": "Labyrinth puppets, including David Bowie's Goblin King"}],
      distance_landmark="Midtown"),

    m("Michael C. Carlos Museum", "michael-c-carlos-museum",
      "Atlanta", "GA", "571 S Kilgo Cir NE, Atlanta, GA 30322",
      33.7913, -84.3260, "Art", 1876, 8.7, 1100, 8,
      visit_time="1.5 hours",
      hours_today="10 AM – 5 PM", hours_summary="Tue–Sun 10 AM – 5 PM · closed Mon",
      tagline="Emory's antiquities museum. Strong Egyptian, Greek, Roman collections.",
      description="Emory's encyclopedic antiquities museum, in a 1916 Henry Hornbostel building expanded by Michael Graves in 1993. One of the largest ancient art collections in the Southeast — 17,000+ objects spanning Africa, Asia, and the ancient Mediterranean.",
      distance_landmark="Emory University campus"),

    m("Jimmy Carter Presidential Library and Museum", "jimmy-carter-presidential-library-and-museum",
      "Atlanta", "GA", "441 John Lewis Freedom Pkwy NE, Atlanta, GA 30307",
      33.7676, -84.3536, "History", 1986, 8.7, 3400, 12,
      visit_time="1.5 hours",
      hours_today="9 AM – 4:45 PM", hours_summary="Mon–Sat 9 AM – 4:45 PM · Sun 12 PM – 4:45 PM",
      tagline="The 39th president's archive, on a hilltop east of downtown.",
      description="Permanent exhibit covers the 1976 campaign, Camp David Accords, and the Iran hostage crisis. Includes a full-scale Oval Office replica. The 35-acre Carter Center campus around it includes formal gardens.",
      distance_landmark="Poncey-Highland, on the Carter Center campus"),

    m("Atlanta Contemporary", "atlanta-contemporary",
      "Atlanta", "GA", "535 Means St NW, Atlanta, GA 30318",
      33.7755, -84.4111, "Art", 1973, 8.4, 920, 0, "always free",
      visit_time="45 minutes",
      hours_today="11 AM – 5 PM", hours_summary="Wed–Sun 11 AM – 5 PM · closed Mon–Tue",
      tagline="Free, non-collecting contemporary art. Strong Atlanta-artist focus.",
      description="A non-collecting contemporary art museum focused on living artists, with strong representation of Atlanta and Southeast US artists. Always free.",
      affiliate_network="none",
      badges=[{"label": "Always free", "tone": "ok"}],
      distance_landmark="West Midtown"),

    m("APEX Museum", "apex-museum",
      "Atlanta", "GA", "135 Auburn Ave NE, Atlanta, GA 30303",
      33.7544, -84.3801, "History", 1978, 8.5, 850, 8,
      visit_time="1 hour",
      hours_today="10 AM – 5 PM", hours_summary="Tue–Sat 10 AM – 5 PM · closed Sun–Mon",
      tagline="African American Panoramic Experience. On Auburn Avenue, the historic Sweet Auburn district.",
      description="A small but focused museum on Auburn Avenue — the Sweet Auburn district that was the center of Black Atlanta in the segregation era. Permanent exhibits cover African American achievement from antiquity to civil rights.",
      distance_landmark="Sweet Auburn, near the MLK National Historic Site"),

    m("Museum of Design Atlanta", "museum-of-design-atlanta",
      "Atlanta", "GA", "1315 Peachtree St NE, Atlanta, GA 30309",
      33.7903, -84.3857, "Specialized", 1989, 8.4, 720, 13,
      visit_time="45 minutes",
      hours_today="11 AM – 6 PM", hours_summary="Tue–Sun 11 AM – 6 PM · closed Mon",
      tagline="The only US museum dedicated entirely to design. Across the street from the High.",
      description="A non-collecting museum focused on rotating exhibitions of contemporary design — graphic, industrial, fashion, architectural. Across the street from the High Museum, often combinable on a museum pass.",
      distance_landmark="Midtown, opposite the High Museum"),

    m("Children's Museum of Atlanta", "childrens-museum-of-atlanta",
      "Atlanta", "GA", "275 Centennial Olympic Park Dr NW, Atlanta, GA 30313",
      33.7635, -84.3940, "Children", 2003, 8.6, 4200, 17,
      visit_time="2.5 hours", best_for="Children under 8",
      hours_today="10 AM – 4 PM", hours_summary="Wed–Sun 10 AM – 4 PM · closed Mon–Tue",
      tagline="Hands-on exhibits for children under 8, on Centennial Olympic Park.",
      description="Hands-on play-and-learn galleries for ages 0–8. Adjacent to Centennial Olympic Park, the Aquarium, and World of Coca-Cola — easy to combine.",
      badges=[{"label": "Family favorite", "tone": "warn"}],
      distance_landmark="Centennial Olympic Park, downtown"),
]


# ============================================================
# SEATTLE (12)
# ============================================================
SEATTLE = [
    m("Museum of Pop Culture", "museum-of-pop-culture",
      "Seattle", "WA", "325 5th Ave N, Seattle, WA 98109",
      47.6215, -122.3481, "Specialized", 2000, 8.6, 19000, 35,
      visit_time="2.5 hours", best_for="Music, sci-fi, families",
      hours_today="10 AM – 5 PM", hours_summary="Daily 10 AM – 5 PM",
      tagline="MoPOP. Frank Gehry's crumpled blob at Seattle Center, with Hendrix and Nirvana inside.",
      description="Founded by Paul Allen, in a 2000 Frank Gehry building wrapped in ribbons of stainless steel and aluminum. Permanent galleries on Jimi Hendrix, Nirvana, and Pacific Northwest grunge; rotating sci-fi and horror-film exhibits; an acoustically isolated Sound Lab where you can play instruments.",
      review_long="Frank Gehry's first major Seattle building, modeled on the smashed body of an electric guitar. Inside, the Nirvana and Jimi Hendrix galleries are anchored by the actual instruments — Hendrix's white Stratocaster from Woodstock, the broken neck of Cobain's smashed Fender. The Sky Church atrium hosts free music in the evenings.",
      highlights=[{"location": "Hendrix Gallery", "item": "The white Stratocaster played at Woodstock"},
                  {"location": "Nirvana Gallery", "item": "Cobain's smashed Fender Mustang"}],
      distance_landmark="Seattle Center, at the foot of the Space Needle"),

    m("Seattle Art Museum", "seattle-art-museum",
      "Seattle", "WA", "1300 1st Ave, Seattle, WA 98101",
      47.6075, -122.3380, "Art", 1933, 8.7, 8500, 30,
      visit_time="2 hours",
      hours_today="10 AM – 5 PM", hours_summary="Wed–Sun 10 AM – 5 PM · closed Mon–Tue",
      tagline="Strong African and Pacific Northwest collections. Hammering Man at the entrance.",
      description="The city's main art museum. Permanent collection emphasizes African art (3,500+ objects), Pacific Northwest Native American art, and 20th-century American work. Jonathan Borofsky's 48-foot Hammering Man statue is at the entrance, hammering once every 4.5 seconds.",
      badges=[{"label": "First Thursdays free", "tone": "ok"}],
      tips=[{"tag": "TIP", "tone": "warn", "text": "Same ticket admits the Asian Art Museum in Volunteer Park within a week."}],
      highlights=[{"location": "Entrance", "item": "Hammering Man, Jonathan Borofsky, 48 feet tall"}],
      distance_landmark="Downtown, on 1st Avenue"),

    m("Chihuly Garden and Glass", "chihuly-garden-and-glass",
      "Seattle", "WA", "305 Harrison St, Seattle, WA 98109",
      47.6202, -122.3499, "Art", 2012, 9.3, 32000, 39,
      visit_time="1.5 hours", best_for="Glass art, photography",
      hours_today="10 AM – 8 PM", hours_summary="Daily 10 AM – 8 PM",
      tagline="Dale Chihuly's glass at the foot of the Space Needle. Stunning at sunset.",
      description="A purpose-built museum for Dale Chihuly's blown-glass work, immediately next to the Space Needle. Eight gallery rooms plus a 100-foot Glasshouse and an outdoor garden where glass forms grow out of plant beds. Best near sunset for the lighting transition.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "Combo ticket with the Space Needle saves ~$10."},
            {"tag": "TIP", "tone": "warn", "text": "Last entry an hour before close — go near sunset for the light change."}],
      highlights=[{"location": "Glasshouse", "item": "100-foot suspended glass sculpture"},
                  {"location": "Garden", "item": "Outdoor glass forms among living plants"}],
      distance_landmark="Seattle Center, next to the Space Needle"),

    m("Museum of Flight", "museum-of-flight",
      "Seattle", "WA", "9404 E Marginal Way S, Seattle, WA 98108",
      47.5180, -122.2972, "Science", 1965, 9.2, 18000, 28,
      visit_time="3 hours", best_for="Aviation, families",
      hours_today="10 AM – 5 PM", hours_summary="Daily 10 AM – 5 PM",
      tagline="The largest private air-and-space museum in the world. Concorde and Air Force One.",
      description="At Boeing Field, with 175+ aircraft and spacecraft. Headlines: a Concorde, a Boeing 747 prototype, the original Air Force One that flew Eisenhower, Kennedy, Johnson, and Nixon, an SR-71 Blackbird, and a full-scale F-14 Tomcat. The Boeing-Bertelsen Gallery covers WWI through Korea.",
      review_long="The largest privately-funded air-and-space museum in the world, sitting on Boeing Field where the company assembled airplanes from 1916 onward. Aircraft you can actually walk through include the Concorde (one of three on US display), the original VC-137B Air Force One that carried Kennedy to Dallas, and the very first 747. The outdoor pavilion has the SR-71, the only B-52 at any museum, and a Soviet MiG-21.",
      badges=[{"label": "Family favorite", "tone": "warn"}],
      highlights=[{"location": "Outdoor", "item": "Concorde G-BOAG, Air Force One VC-137B"},
                  {"location": "Pavilion", "item": "SR-71 Blackbird, the fastest jet ever"}],
      distance_landmark="Boeing Field, 15 minutes south of downtown"),

    m("Pacific Science Center", "pacific-science-center",
      "Seattle", "WA", "200 2nd Ave N, Seattle, WA 98109",
      47.6202, -122.3514, "Science", 1962, 8.5, 11000, 30,
      visit_time="2.5 hours", best_for="Families, hands-on",
      hours_today="10 AM – 5 PM", hours_summary="Wed–Sun 10 AM – 5 PM · closed Mon–Tue",
      tagline="A 1962 World's Fair leftover. Tropical butterfly house, planetarium, IMAX.",
      description="One of the few 1962 World's Fair buildings still in use. Houses a butterfly tropical house (500+ live butterflies), the Willard Smith Planetarium, an IMAX theater, and Sound Garden — a working tide-and-wind organ outdoors.",
      badges=[{"label": "Family favorite", "tone": "warn"}],
      distance_landmark="Seattle Center"),

    m("Burke Museum of Natural History and Culture", "burke-museum-of-natural-history-and-culture",
      "Seattle", "WA", "4300 15th Ave NE, Seattle, WA 98105",
      47.6603, -122.3120, "Natural History", 1885, 8.7, 4400, 22,
      visit_time="2 hours",
      hours_today="10 AM – 5 PM", hours_summary="Tue–Sun 10 AM – 5 PM · closed Mon",
      tagline="Washington's official natural history museum. New 2019 building lets you watch fossil prep.",
      description="Washington's state-mandated natural history and culture museum, on the UW campus. The 2019 Olson Kundig building is unusual in that the working laboratories and collections are visible from the public galleries. Strong Pacific Northwest and Pacific Rim Indigenous collections.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "Free first Thursdays. The fossil prep lab is open to the gallery floor."}],
      distance_landmark="University of Washington campus"),

    m("Seattle Asian Art Museum", "seattle-asian-art-museum",
      "Seattle", "WA", "1400 E Prospect St, Seattle, WA 98112",
      47.6307, -122.3146, "Art", 1933, 8.6, 2200, 18,
      visit_time="1.5 hours",
      hours_today="10 AM – 5 PM", hours_summary="Wed–Sun 10 AM – 5 PM · closed Mon–Tue",
      tagline="The Seattle Art Museum's Asian collection, in a 1933 Art Deco building in Volunteer Park.",
      description="The original 1933 home of the Seattle Art Museum, redesigned to house the institution's deep Asian art collection. Renovated 2020. Walking distance to the Volunteer Park Conservatory.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "SAM ticket includes admission here within 7 days."}],
      distance_landmark="Volunteer Park, Capitol Hill"),

    m("Frye Art Museum", "frye-art-museum",
      "Seattle", "WA", "704 Terry Ave, Seattle, WA 98104",
      47.6068, -122.3252, "Art", 1952, 8.5, 1300, 0, "always free",
      visit_time="1 hour",
      hours_today="11 AM – 5 PM", hours_summary="Tue–Sun 11 AM – 5 PM · closed Mon",
      tagline="Free art museum. Strong 19th-century German painting, contemporary rotations.",
      description="A free art museum dedicated to the legacy of meatpacking magnate Charles Frye, whose 19th-century European collection is the historical core. Contemporary rotating exhibits round out the program. Always free, always has been.",
      badges=[{"label": "Always free", "tone": "ok"}],
      affiliate_network="none",
      distance_landmark="First Hill"),

    m("Wing Luke Museum", "wing-luke-museum",
      "Seattle", "WA", "719 S King St, Seattle, WA 98104",
      47.5980, -122.3242, "History", 1967, 8.9, 2400, 19,
      visit_time="1.5 hours",
      hours_today="10 AM – 5 PM", hours_summary="Wed–Sun 10 AM – 5 PM · closed Mon–Tue",
      tagline="Asian Pacific American experience. Smithsonian Affiliate, in the Chinatown-International District.",
      description="A Smithsonian Affiliate in a restored 1910 hotel that once housed Asian immigrant labor. Permanent and rotating exhibits on Asian Pacific American history; the historic preserved hotel rooms upstairs are part of the visit.",
      tips=[{"tag": "TIP", "tone": "warn", "text": "The historic rooms upstairs are tour-only — book at the front desk on arrival."}],
      distance_landmark="Chinatown-International District"),

    m("National Nordic Museum", "national-nordic-museum",
      "Seattle", "WA", "2655 NW Market St, Seattle, WA 98107",
      47.6691, -122.3848, "Specialized", 1980, 8.8, 1700, 18,
      visit_time="1.5 hours",
      hours_today="10 AM – 5 PM", hours_summary="Tue–Sun 10 AM – 5 PM · closed Mon",
      tagline="The only US museum dedicated to Nordic culture. New 2018 Ballard building.",
      description="Federally designated as the National Nordic Museum in 2019. Permanent exhibition traces 12,000 years of Nordic history; rotating shows feature contemporary Scandinavian art and design. The 2018 Mithun building doubled the previous space.",
      distance_landmark="Ballard"),

    m("Klondike Gold Rush National Historical Park", "klondike-gold-rush-national-historical-park",
      "Seattle", "WA", "319 2nd Ave S, Seattle, WA 98104",
      47.6004, -122.3329, "History", 1976, 8.7, 1900, 0, "always free",
      visit_time="1 hour",
      hours_today="10 AM – 5 PM", hours_summary="Daily 10 AM – 5 PM",
      tagline="A National Park Service museum about the 1897 Klondike rush. Free.",
      description="One of the smallest National Park sites: a single museum in Pioneer Square commemorating Seattle's role as the outfitting hub for the 1897 Klondike Gold Rush. Free, run by the NPS.",
      affiliate_network="none",
      badges=[{"label": "Always free", "tone": "ok"}],
      distance_landmark="Pioneer Square"),

    m("Center for Wooden Boats", "center-for-wooden-boats",
      "Seattle", "WA", "1010 Valley St, Seattle, WA 98109",
      47.6280, -122.3370, "Specialized", 1976, 9.0, 1100, 0, "free; rentals priced",
      visit_time="1 hour",
      hours_today="10 AM – 5 PM", hours_summary="Wed–Mon 10 AM – 5 PM · closed Tue",
      tagline="A working museum on Lake Union. Free admission, sailboats and rowboats for rent.",
      description="A free working museum on Lake Union's south end. The collection is more than 100 historic small boats, and most of them can be rented. Free Sunday public sail rides on heritage sailboats from the museum's own dock.",
      affiliate_network="none",
      badges=[{"label": "Always free", "tone": "ok"}],
      tips=[{"tag": "FREE", "tone": "ok", "text": "Free Sunday public sail rides — first-come, first-served at the dock."}],
      distance_landmark="South Lake Union"),
]


# ============================================================
# CITY HUBS
# ============================================================
CITIES = {
    "new-york": {
        "city": "New York", "state": "NY",
        "title": "12 best museums in New York City",
        "intro": "From the Met's encyclopedic galleries to the Frick's preserved Gilded Age mansion, New York holds the densest concentration of major museums anywhere in the country.",
        "read_minutes": 13,
        "museums": NEW_YORK,
        "body": """New York's museum scene divides cleanly into three axes: the Mall of art (Met, MoMA, Whitney, Guggenheim), the Mall of natural and human history (Natural History, Tenement, New-York Historical), and a long tail of specialist institutions that any other city would treat as a centerpiece.

Most are in Manhattan, but the Brooklyn Museum and the Met Cloisters in upper Manhattan are worth their separate trips. NY/NJ/CT residents pay-what-you-wish at the Met, the Natural History Museum, and the Frick — bring ID. Pay-what-you-wish slots elsewhere include MoMA on Friday evenings, the Whitney on Friday evenings, and the New-York Historical on Friday evenings.

If you only have a day, the conventional triangle is the Met, MoMA, and the Natural History Museum — all walkable from the same Central Park entrances. If you have two days, fold in the Cloisters and the Tenement Museum, both of which are different in character from the Manhattan flagships.

The full directory of every New York museum (200+) is at the bottom of this page."""
    },
    "los-angeles": {
        "city": "Los Angeles", "state": "CA",
        "title": "12 best museums in Los Angeles",
        "intro": "The Getty's hilltop campus, The Broad's free contemporary collection, and the Huntington's 120-acre estate make LA's museum scene one of the country's most spread out.",
        "read_minutes": 11,
        "museums": LOS_ANGELES,
        "body": """Los Angeles's museum scene is unusually dispersed. The Getty Center sits in Brentwood, the Huntington in San Marino, the Norton Simon in Pasadena — each demands its own half-day, and they're 30+ minutes apart by car.

That said, three major institutions cluster on Mid-Wilshire's Museum Row (LACMA, the Petersen, La Brea Tar Pits) and three more cluster downtown (The Broad, MOCA, the Bunker Hill area). Either pairing makes a workable day.

Free museums are unusually generous here: Getty Center, Getty Villa, The Broad, California Science Center, MOCA, and the Hammer all charge nothing. Parking, however, often costs $20–25, and most free museums require advance timed reservations.

The full directory of every Los Angeles museum (90+) is at the bottom of this page."""
    },
    "washington": {
        "city": "Washington", "state": "DC",
        "title": "12 best museums in Washington, DC",
        "intro": "The Smithsonian's eleven Mall museums plus the National Gallery of Art make Washington one of the only cities where world-class museums are reliably free.",
        "read_minutes": 12,
        "museums": WASHINGTON_DC,
        "body": """Almost every major museum in Washington is free. The eleven Smithsonian museums on the National Mall, the National Gallery of Art, and the Holocaust Memorial all charge nothing. The exceptions — the International Spy Museum, the Phillips Collection — are private institutions and they charge accordingly.

Plan around the Mall's geography. The Smithsonian museums run east-to-west: the Museum of the American Indian at the east end near the Capitol, then Air and Space, then Hirshhorn, then African American History, then American History, then Natural History, then the National Gallery's two buildings nearer the Capitol. Comfortable walking distance, but a full day's work to do justice to even three of them.

Most popular Smithsonian museums require timed-entry passes that release 30 days in advance. Same-day passes appear at 8:15 AM and disappear within minutes. Reserve.

The full directory of every Washington-area museum (75+) is at the bottom of this page."""
    },
    "boston": {
        "city": "Boston", "state": "MA",
        "title": "12 best museums in Boston",
        "intro": "The MFA's encyclopedic collection, the Gardner's preserved palazzo, and Harvard's free art museums anchor a museum scene weighted toward art and early American history.",
        "read_minutes": 11,
        "museums": BOSTON,
        "body": """Boston's museum scene is concentrated in two zones: the Fenway (MFA, Gardner) and Cambridge (Harvard Art Museums, Peabody, MIT Museum). The Seaport adds the ICA and the Children's Museum; downtown adds the Mary Baker Eddy Library's Mapparium.

For a single day, the MFA-Gardner pairing is the standard recommendation: the two are across the street from each other, the Gardner takes 90 minutes, and the MFA fills the rest of the day. Harvard's free art museums add a strong half-day across the river in Cambridge.

Free museums include Harvard Art Museums (free since 2022) and the USS Constitution Museum (suggested donation). Pay-what-you-wish slots include the Gardner for visitors named Isabella and the ICA on Thursday evenings.

The full directory of every Boston-area museum (60+) is at the bottom of this page."""
    },
    "san-francisco": {
        "city": "San Francisco", "state": "CA",
        "title": "12 best museums in San Francisco",
        "intro": "Free admission, world-class collections, and an unusual concentration of small specialist museums (cable cars, glass, comics) make SF a strong museum city for its size.",
        "read_minutes": 10,
        "museums": SAN_FRANCISCO,
        "body": """San Francisco's museums divide between two main concentrations. Golden Gate Park holds the de Young, the California Academy of Sciences, and the Asian Art Museum's planning office (the museum itself is in Civic Center). The downtown core — SoMa, Yerba Buena, and the Embarcadero — holds SFMOMA, the Contemporary Jewish Museum, the Museum of the African Diaspora, and the Exploratorium.

Bay Area residents get free first-Sundays at most major museums, including the de Young, Legion of Honor, and Asian Art Museum. The Cable Car Museum and the GLBT Historical Society Museum are always free.

The Exploratorium's After Dark on Thursdays (21+) is worth a separate evening — it's the city's best after-hours museum experience.

The full directory of every Bay Area museum (80+) is at the bottom of this page."""
    },
    "philadelphia": {
        "city": "Philadelphia", "state": "PA",
        "title": "12 best museums in Philadelphia",
        "intro": "From the Rocky steps at the Philadelphia Museum of Art to the Mütter Museum's medical specimens, Philadelphia's museum scene mixes art-historical heavyweights with deeply specific specialist collections.",
        "read_minutes": 11,
        "museums": PHILADELPHIA,
        "body": """Philadelphia's museums cluster on two axes. The Benjamin Franklin Parkway — Philadelphia's Champs-Élysées — runs from City Hall to the Art Museum and lines up the Franklin Institute, the Barnes Foundation, the Rodin Museum, and the Philadelphia Museum of Art on a single one-mile walk. The Independence Mall area — Old City and the Constitution Center — houses the National Constitution Center, the Weitzman National Museum of American Jewish History, and the African American Museum.

Two specialist institutions are reasons to visit Philadelphia on their own. The Mütter Museum's medical specimens are unmatched anywhere; Eastern State Penitentiary is the country's best example of preserved 19th-century carceral architecture, and its Halloween Nights program runs October–November.

The full directory of every Philadelphia museum (45+) is at the bottom of this page."""
    },
    "atlanta": {
        "city": "Atlanta", "state": "GA",
        "title": "12 best museums in Atlanta",
        "intro": "Civil rights, Southern history, and an unusually strong puppetry museum anchor Atlanta's collection. The High Museum holds the city's main art institution.",
        "read_minutes": 9,
        "museums": ATLANTA,
        "body": """Atlanta's museum scene is concentrated in three areas. Downtown, the Pemberton Place complex puts the National Center for Civil and Human Rights, World of Coca-Cola, and the Children's Museum next to the Georgia Aquarium on a single plaza. Midtown holds the High Museum, the Center for Puppetry Arts, and the Museum of Design Atlanta. Buckhead and the eastern neighborhoods hold the Atlanta History Center, Fernbank, and the Carter Library.

The National Center for Civil and Human Rights is the museum most distinctive to Atlanta — its lunch-counter sit-in simulator is genuinely demanding and unmatched as a physical-empathy exhibit. The Center for Puppetry Arts holds the world's largest Jim Henson collection, donated by Henson personally.

The full directory of every Atlanta-area museum (35+) is at the bottom of this page."""
    },
    "seattle": {
        "city": "Seattle", "state": "WA",
        "title": "12 best museums in Seattle",
        "intro": "The Museum of Flight is among the country's best aviation museums; MoPOP and Chihuly Garden anchor Seattle Center; and the city's specialist museums (Wooden Boats, Klondike Gold Rush) are unusually deep.",
        "read_minutes": 10,
        "museums": SEATTLE,
        "body": """Seattle's museum scene clusters around Seattle Center — the 1962 World's Fair grounds. MoPOP, Chihuly Garden and Glass, and the Pacific Science Center are all walkable from the Space Needle. South of downtown, the Museum of Flight at Boeing Field is the city's must-see for aviation visitors, with a Concorde and the original Air Force One you can walk through.

Free museums include the Frye Art Museum (always), the Klondike Gold Rush National Historical Park (always, run by the NPS), and the Center for Wooden Boats. First Thursdays brings free entry at SAM, the Burke Museum, and the Seattle Asian Art Museum among others.

If you only have a day, the conventional pairing is MoPOP-and-Chihuly at Seattle Center plus the Museum of Flight; if you have a half-day, MoPOP and Chihuly are 50 yards apart.

The full directory of every Seattle-area museum (35+) is at the bottom of this page."""
    },
}


# ============================================================
# WRITE FILES
# ============================================================
def write_museum(slug, data):
    out = MUSEUMS_DIR / f"{slug}.json"
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def write_city(city_slug, c):
    """Write the .mdx file for a city hub."""
    body = c["body"]
    slugs = [m_slug for m_slug, _ in c["museums"]]
    fm = (
        "---\n"
        f"city: {c['city']}\n"
        f"state: {c['state']}\n"
        f"title: {json.dumps(c['title'])}\n"
        f"intro: {json.dumps(c['intro'])}\n"
        "last_updated: 2026-04-27\n"
        f"read_minutes: {c['read_minutes']}\n"
        "museum_slugs:\n"
        + "".join(f"  - {s}\n" for s in slugs)
        + "---\n\n"
    )
    out = CITIES_DIR / f"{city_slug}.mdx"
    out.write_text(fm + body + "\n")


def main():
    MUSEUMS_DIR.mkdir(parents=True, exist_ok=True)
    CITIES_DIR.mkdir(parents=True, exist_ok=True)

    n_museums = 0
    for city_slug, c in CITIES.items():
        for slug, data in c["museums"]:
            write_museum(slug, data)
            n_museums += 1
        write_city(city_slug, c)

    print(f"Wrote {n_museums} museum JSON files")
    print(f"Wrote {len(CITIES)} city hub MDX files")


if __name__ == "__main__":
    main()
