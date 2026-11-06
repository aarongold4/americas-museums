import { defineCollection, z } from 'astro:content';

// ---- Museum schema ----
// One JSON file per museum in src/content/museums/
// Slug = filename minus .json (e.g. art-institute-of-chicago.json)
const museums = defineCollection({
  type: 'data',
  schema: z.object({
    name: z.string(),
    short_name: z.string().optional(),
    city: z.string(),
    state: z.string().length(2),
    address: z.string(),
    lat: z.number(),
    lng: z.number(),
    discipline: z.enum([
      'Art',
      'History',
      'Natural History',
      'Science',
      'Children',
      'Military',
      'Specialized',
      'General',
    ]),
    founded: z.number().int().optional(),
    // Photos: hero is shown solo on the museum page hero strip;
    // gallery is a small thumbnail set used on the museum page collage.
    // When absent, components fall back to a discipline-colored swatch.
    hero_image: z.string().url().optional(),
    gallery_images: z.array(z.string().url()).default([]),
    photo_credit: z.string().optional(),
    rating: z.number().min(0).max(10).optional(),
    review_count: z.number().int().optional(),
    review_label: z.string().optional(),     // "Wonderful", "Excellent", etc.
    admission_from: z.number().optional(),    // USD
    admission_text: z.string().optional(),    // "general admission"
    hours_summary: z.string().optional(),     // human-readable string
    hours_today: z.string().optional(),       // "11 AM – 5 PM"
    visit_time: z.string().optional(),        // "3–5 hours"
    best_for: z.string().optional(),          // "Art lovers"
    tagline: z.string(),                      // 1-line hook for cards
    description: z.string(),                  // 2-3 sentence about
    review_long: z.string().optional(),       // editorial review (markdown ok)
    badges: z
      .array(
        z.object({
          label: z.string(),
          tone: z.enum(['ok', 'warn', 'info', 'neutral']).default('neutral'),
        })
      )
      .default([]),
    tips: z
      .array(
        z.object({
          tag: z.string(),  // "FREE", "TIP", "WARNING"
          tone: z.enum(['ok', 'warn', 'info', 'neutral']).default('neutral'),
          text: z.string(),
        })
      )
      .default([]),
    highlights: z
      .array(
        z.object({
          location: z.string(),  // "Gallery 262"
          item: z.string(),      // "Nighthawks, Edward Hopper, 1942"
        })
      )
      .default([]),
    affiliate: z
      .object({
        network: z.enum(['getyourguide', 'tiqets', 'viator', 'gocity', 'none']),
        deep_link: z.string().url().optional(),
        product_name: z.string().optional(),
      })
      .optional(),
    distance_landmark: z.string().optional(), // "0.4 mi from Millennium Park"
    // Google Places sync
    google_place_id: z.string().optional(),
    rating_google: z.number().optional(),
    review_count_google: z.number().int().optional(),
    business_status: z.string().optional(), // 'OPERATIONAL', 'CLOSED_TEMPORARILY', 'CLOSED_PERMANENTLY'
  }),
});

// ---- City hub schema ----
// One MDX file per city in src/content/cities/
const cities = defineCollection({
  type: 'content',
  schema: z.object({
    city: z.string(),
    state: z.string().length(2),
    title: z.string(),                // "10 best museums in Chicago"
    intro: z.string(),                // hero subhead
    museum_slugs: z.array(z.string()), // ordered list — the ranking
    last_updated: z.coerce.date(),
    read_minutes: z.number().int(),
  }),
});

export const collections = { museums, cities };
