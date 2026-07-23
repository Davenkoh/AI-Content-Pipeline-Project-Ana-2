# Holicay — Brand Reference

> **Local cache — NOT the source of truth.** Brand knowledge is user-owned on two
> front-ends: the Sheet's **Holicay Brand** tab (features / knowledge) and the **Drive brand
> folder** (assets). Before using the brand (Stage 5), the workflow refreshes from both
> (`engine/sheets/sheets.py brand-list` + `engine/drive/drive_sync.py --brand-list`) and
> rewrites this file. The loop may also **write back** — a new Brand-tab row (`brand-add`)
> or a Drive asset — when it learns something durable. What Holicay is, its assets, and how
> to refer to it (append/correct as we learn):

## What Holicay is
Holicay is a **travel / trip-planner app** — an **itinerary planner**. It builds **day-by-day trip itineraries** with a map view, budget tracking, and flights/transport, and lets users browse and **share trips** (the app feed shows things like "3 days to Vietnam", "5 days in ..."). It's AI-assisted (see the `holi-ai` asset) and works across destinations (mockups show Tokyo / Vietnam / Singapore routes).

One line: **the app you plan your trip itinerary on.**

Reachable at **holicay.com** (and as the **Holicay app**). When promoting, always give viewers a discoverable handle — say "holicay.com" or "the holicay app", never just "holicay" with no signpost (they won't know it's a thing to go find).

## Features (for promo reference — in content, name the USE CASE, not the feature name)
- **Holi-AI** — an AI planner built right into the itinerary planner. It plans the trip for you and lets you rearrange / drag things around in the itinerary on the fly. In content, describe what it *does* (e.g. "the ai plans it for you and you just drag things around"); do NOT say the name "Holi-AI". Screenshot: `App Demos/Plan with HoliAI Viet/1.PNG` (the Chat-with-Holi-AI setup: trip type / budget / interests → "Start Planning with AI"). (First used: `06_VN_SaveThis` slide 4.)
- **Planning Canvas** — the map-based day view inside the app. Shows all of a day's stops as **numbered pins on a live map** (you see the full layout of the day geographically). Navigate days via a day-selector row at the bottom. For each day it surfaces: real weather (temp range + humidity %), and each activity listed in chronological order with a category icon (Food, Place, etc.), the name, time block, and a thumbnail — plus the **walking distance and travel time to the next stop** between items. Designed to help you optimize your day's route: spot if two things are far apart, decide whether to walk or grab, rearrange. Screenshot reference: `App Demos/Planning Canvas Vietnam.png` (Day 4 Hanoi: Phở BÁT ĐÀN → National Museum → Vua Chả Cá, with distances between each). In content, describe what it *does* ("you can see the map, the weather, how far everything is and how to get between each stop"); do NOT say "Planning Canvas" in post copy. Best shown on the **plug slide** — the C1 mockup treatment frames an app screenshot like this one (see `/CONTRACT.md` plug designs).
- **Community Itineraries** — a feed of ready-made trip itineraries created by other travelers / locals that you **copy and customize** instead of planning from scratch. Browse by destination (search + filter chips: Popular destinations / Free / Premium); each card shows a hero photo, a view/save count (e.g. 11.14k), length + place count ("3 days · 14 places"), and the author (e.g. "Minh Khoi"). Open one to see its Overview, route Map, day-by-day Itinerary, and Comments, then tap **"Customize this Trip"** to copy it into your own editable trip (it becomes a Planning Canvas you tweak to your dates / taste). The use case to name in content: **"don't plan from scratch — copy someone's real itinerary and tweak it."** Describe what it *does* ("you just copy someone's trip who already did it and change it to what you like"); do NOT say "Community Itineraries" in post copy. Screenshots: `App Demos/Plan with Community Itin Vietnam/1-3.PNG` (browse feed → itinerary detail with the Customize button → your customized canvas). This is the use case behind C1's comment-keyword plug ("copy people's itinerary on holicay.com" — see `../frameworks/content_frameworks.md` Variant C1).
- _(add more Holicay features here as we learn them)_

## Brand
- **Coral / red-orange:** `#F25142` (primary)
- **Dark navy:** `#133A4A` (secondary)
- **Wordmark:** "Holicay" — *Holi* in coral, *cay* in navy; distinctive cut-out **"H"** mark (reads like binoculars / a stylized H with curved notches).
- **App icon:** coral rounded-square with the white "H" mark.

## Logo assets (this folder)
- `Copy of HOLICAY og logo.png` — full wordmark, coral+navy on white.
- `Copy of HOLICAY logo in white.png` — full wordmark in **white** (for photo / dark backgrounds).
- `Copy of HLC app logo.png` — app icon (coral square + white H).
- `Copy of HLC H logo (white).png` — the white **"H"** mark alone.
- `Copy of HLC app iph mockup.png` — two-iPhone app screenshot (itinerary view + home feed).
- `Copy of holi-ai logos.png` — the "holi-ai" (AI) sub-brand logos.

## App screenshots (App Demos folder)
- `Planning Canvas Vietnam.png` — real in-app screenshot of the Planning Canvas, Day 4 Hanoi itinerary (map pins + day selector + weather + timed activities with distances between stops). Use on a dedicated Holicay slide to ground it in reality.
- `Plan with Community Itin Vietnam/1-3.PNG` — the community-itineraries flow: (1) browse feed for "ho chi minh" (cards with view counts + days/places + author), (2) itinerary detail (Overview / Map / Itinerary / Comment tabs + "Customize this Trip" button), (3) the customized trip as a Canvas ("5 Days in Saigon", day tabs, timed stops, travel time between). Use for the cat 4 community-itineraries soft-demo post.
- `Plan with HoliAI Viet/1-2.PNG` — the Holi-AI flow: (1) Chat-with-Holi-AI setup (trip type / budget / interests → Start Planning with AI), (2) the resulting Canvas (shared with the community-itin end state).

Use the **white** wordmark / H over photos; the coral+navy version on white/light.

## How to refer to it in content
- Name: **Holicay** (capital H). Never "Holiday".
- Function tag when listed: **"Holicay (itinerary)"** or "(trip planner)".
- It earns its place by being genuinely useful in context — the frameworks fix how/when: the plug is slide 4 with that option's verbatim first-person copy (`../frameworks/content_frameworks.md`).

## To expand (TODO — fill as we learn)
- Tagline / one-line positioning
- Key features to name in content (and any we should NOT mention yet)
- App Store / Play Store / website links + social handle
- Wordmark typeface, logo clear-space rules
