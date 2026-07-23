# Photo provenance — UGC re-curation pass (2026-07-22; user-photo upgrade sweep 2026-07-23)

Every slug referenced by `copy/{A,B,C1,C2}.json` photo fields (`scenic_photo`, `top_photo`,
`bottom_photo`, `photo`, `cells`, `icons`), audited against **CONTRACT.md QC gate 9**
(UGC-framing: reject drone/aerial, tripod long-exposure, editorial symmetry/perfectly-timed
shots, HDR postcard grades, anything professionally staged). Grouped by deck, in slide order.
`NN` = slide position in that deck's own `copy/<X>.json`.

Format: `NN slug — KEPT|REPLACED — platform — author — source_url — framing note`

Untouchable assets (`fuji_lake.jpg`, `route_map.png`, `app_deepl.png`, `app_google-translate.png`,
`cramped_hotel_room.jpg`, `chars/*`) are listed where they appear in a deck for completeness,
marked KEPT, not re-audited.

**2026-07-23 upgrade sweep note:** the human flagged "photo selection is better now, but try to
use user photos" — so every venue-ish slug still sourced via `google_images` (plus a few
`repo-graded`/untraceable stand-ins the human's worklist also named) was re-checked against
fresh-or-already-banked **Google Places** user photos, one venue at a time, simulating each
candidate's actual render crop (half/cell/full geometry) before judging against gate 9 and the
slide's specific message. This was an **upgrade pass, not churn**: a Places photo only replaced
the incumbent when it passed gate 9 AND fit the slot's geometry/message at least as well. Owner
uploads (uploader name = the venue's own account) were auto-skipped as ineligible. 20 venues were
checked; 10 swapped, 10 kept their prior pick because no Places alternative actually beat it (most
often because the Places result showed an empty/crowd-less view when the slide's message needed a
crowd, or because it visually read as more "editorial/staged" than the incumbent despite the
platform label). The KEPT/REPLACED verdict below reflects each row's outcome across BOTH passes
cumulatively (unchanged from the 07-22 doc except the 10 rows this sweep actually swapped, which
now read REPLACED with the new photo's details).

---

## Deck A (10 slides)

01 fuji_lake — KEPT — google_images — Trip.com — https://sg.trip.com/moments/detail/fujikawaguchiko-60548-129960833/ — untouchable, approved candid sunset
02 no_trash_cans_street — REPLACED — google_images — WHEN IN TOKYO — https://whenin.tokyo/Yanaka-Area-Guide — blue-hour Yanaka alley corner
02 carry_bag_trash — KEPT — google_images — ANABA JAPAN — https://anaba-japan.net/en/manners/m_trash_how-en/ — candid rear POV walking
03 cherry_blossom_crowds — KEPT — repo-graded (untracked, pre-existing) — n/a — n/a — crowd phones-up night blossoms
03 tokyo_offseason_quiet — KEPT — google_images — Travely Notes — https://www.travelynotes.com/blog-japan/autumn-walk-around-jindai-ji-discover-tokyos-hidden-gem-for-fall-foliage — quiet autumn alley pedestrians
05 food_queue — KEPT — google_images — Reddit — https://www.reddit.com/r/sushi/comments/o5avst/which_conveyor_belt_sushi_do_you_like_best/ — Kura Sushi table POV (2026-07-23: re-checked vs banked Kura Sushi Places photos, incumbent's candid tablet/gacha-machine POV still wins)
05 golden_gai — KEPT — repo-graded (untracked, pre-existing) — n/a — n/a — handheld night alley lanterns
06 cramped_hotel_room — REPLACED — google_images — YouTube — https://www.youtube.com/watch?v=tg5lz_zIAao — fisheye vlog selfie tiny-room
06 local_neighbourhood — REPLACED — google_images — Trot Op! — https://www.trotop.be/en/tokyo-ueno-yanaka-sights/ — daytime alley cafe signage
07 flight_expensive — KEPT — google_images — Drava Shop — https://drava.shop/blogs/airlines/how-to-choose-your-seat-on-a-long-haul-flight — candid cabin window seat
07 flight_layover_asia — REPLACED — google_places_user_photo — SeungJun Kim — https://maps.google.com/maps/contrib/100958975977925692266 — travelers waiting cactus seating
08 jr_pass_ticket — KEPT — google_images — Wikipedia — https://en.wikipedia.org/wiki/Japan_Rail_Pass — flat-lay used physical ticket
08 suica_card_tap — KEPT — google_images — Trip.com — https://us.trip.com/guide/transport/suica-card.html — hand tapping card reader
09 narita_airport — REPLACED (2026-07-23) — google_places_user_photo — Kazuk Hiros — https://maps.google.com/maps/contrib/117996966271017479971 — candid travelers, Narita+Train signage
09 haneda_airport — REPLACED — google_places_user_photo — のりこ — https://maps.google.com/maps/contrib/116216329288578781287 — railing foreground plane-spotting tarmac
10 tokyo_skyline — REPLACED — google_places_user_photo — たろきち — https://maps.google.com/maps/contrib/115497063726678117311 — deck net glass escalator

## Deck B (8 slides)

01 tokyo_skyline — REPLACED — google_places_user_photo — たろきち — (shared install, see A#10) — deck net glass escalator
02 shibuya_sky — KEPT — google_images — Travel Caffeine — https://www.travelcaffeine.com/shibuya-sky-review-best-observation-tokyo-japan/ — packed sunset deck crowd (2026-07-23: re-checked vs 3 unused banked Places photos of the deck, all empty-of-crowd — incumbent uniquely sells "packed shoulder to shoulder", kept)
02 tokyo_gov_building — REPLACED — google_places_user_photo — Frederic K — https://maps.google.com/maps/contrib/105211076524162208846 — through-glass reflection hazy Shinjuku
03 shibuya_crossing — REPLACED — google_images — Japan A to Z (Substack) — https://tani.substack.com/p/55-shibuya-crossing — accessible walkway angle, no blur
03 shimokitazawa — KEPT — repo-graded — Chloe / ttc-01 (Tokyo Worth It or Overrated) — outputs/01 - Tokyo Worth It or Overrated — grainy vintage storefront crop
05 takeshita — REPLACED (2026-07-23) — google_places_user_photo — Alex Giles — https://maps.google.com/maps/contrib/109318730940402039565 — immersed crowd POV, phone filming
05 cat_street — REPLACED (2026-07-23) — google_places_user_photo — F M — https://maps.google.com/maps/contrib/109932753407941539927 — real Cat Street, fashion crowd (incumbent was a Mia/ttm-01 Harajuku stand-in, not actually this street)
06 skytree — REPLACED (2026-07-23) — google_places_user_photo — Riccardo Widera — https://maps.google.com/maps/contrib/107192220437452611381 — near-identical low-angle, now attributed
06 roppongi_hills — REPLACED — google_places_user_photo — TRIP STAR — https://maps.google.com/maps/contrib/112646953105542800877 — night Tokyo Tower deck view
07 ichiran_queue — KEPT — google_images — 守口・門真つーしん — https://www.morikado2.jp/photo/ichiran-20241205.html — night queue, faces blurred (2026-07-23: 2 unused banked Places photos exist but both show the ramen bowl, not the line — message needs the queue, kept)
07 omoide_yokocho — KEPT — google_images — Hello! Tokyo Tours — https://hellotokyotours.com/blog/tokyo-places-to-eat-shinjuku-omoide-yokocho — lantern alley moody handheld (2026-07-23: 4 banked Places photos checked, none show the lantern-alley subject, kept)
08 fuji_lake — KEPT — google_images — Trip.com — (shared, see A#1) — untouchable, approved candid sunset

## Deck C1 (14 slides)

01 fuji_lake — KEPT — google_images — Trip.com — (shared, see A#1) — untouchable, approved candid sunset
02 shibuya_crossing (divider tokyo, cell 1) — REPLACED — google_images — Japan A to Z (Substack) — (shared, see B#3) — accessible walkway angle, no blur
02 temples (cell 2) — REPLACED — google_images — Genki Mobile — https://www.genkimobile.com/meiji-shrine-yoyogi-forest/ — Meiji torii approach, real tourists (2026-07-23: checked vs 4 banked Sensoji Places photos — the strongest was a dead-empty, perfectly symmetric Kaminarimon gate, an even worse gate-9 fit despite real attribution; incumbent's real pedestrian crowd kept)
02 food_queue (cell 3) — KEPT — google_images — Reddit — (shared, see A#5) — Kura Sushi table POV
02 golden_gai (cell 4) — KEPT — repo-graded (untracked) — n/a — (shared, see A#5) — handheld night alley lanterns
06 kyoto_arashiyama (cell 1) — REPLACED — google_places_user_photo — Miquel Lapuente Marquès — https://maps.google.com/maps/contrib/111855457621476804308 — real crowd, bamboo path
06 kyoto_fushimi_inari (cell 2) — REPLACED (2026-07-23) — google_places_user_photo — Rahil Agrawal — https://maps.google.com/maps/contrib/115439389244360929764 — oblique angle, real visitor glimpse
06 kyoto_botanical_gardens (cell 3) — KEPT — google_images — Wikipedia — https://en.wikipedia.org/wiki/Kyoto_Botanical_Garden — schoolchildren crossing bridge candid
06 kyoto_street (cell 4) — KEPT — repo-graded — Chloe / ttc-06 (Japan Travel Tips That Matter) — outputs/06 - Japan Travel Tips That Matter — muted filter, quiet backstreet
08 osaka_dotonbori (cell 1) — KEPT — google_images — Snow Monkey Resorts — https://www.snowmonkeyresorts.com/activities/the-glico-man-sign-in-osaka/ — night canal, candid crowd (2026-07-23: 4 banked Places photos were all elevated/wrong-landmark shots, kept)
08 osaka_universal_studios (cell 2) — REPLACED (2026-07-23) — google_places_user_photo — Tama Chang (たまちゃん) — https://maps.google.com/maps/contrib/103339197892598787171 — archway distance, crowd barriers visible
08 osaka_amerikamura (cell 3) — REPLACED (2026-07-23) — google_places_user_photo — R — https://maps.google.com/maps/contrib/105736855936668713202 — portrait-blur mural, cyclists passing
08 osaka_street_food (cell 4) — KEPT — google_images — YouTube — https://www.youtube.com/watch?v=kh-yNMGl2tA — takoyaki stall, kimono customer
10 nara_deer_park (cell 1) — KEPT — google_images — BBC — https://www.bbc.co.uk/programmes/articles/ZhDnsVPGqg84KgcbvNz98L/the-marvellous-nara-deer — woman feeding deer crosswalk (2026-07-23: best banked Places alternative was a lone deer with no crowd-interaction moment, kept)
10 nara_todaiji (cell 2) — REPLACED (2026-07-23) — google_places_user_photo — Raven kisses — https://maps.google.com/maps/contrib/104234940698931303596 — wider altar view, barrier rope
10 nara_wakakusayama (cell 3) — REPLACED — google_images — LensTokyo — https://www.lenstokyo.com/locations/wakakusayama-hill — deer, hazy natural hilltop (2026-07-23: best banked Places alt was a dramatic god-ray golden-hour shot that read as more processed/staged than this one, kept)
10 nara_street (cell 4) — KEPT — google_images — Thailande et Asie — https://thailande-et-asie.com/en/balade-vieille-ville-nara-ancienne-capitale — overcast old-town shopfront
12 hakone (cell 1) — REPLACED (2026-07-23) — google_places_user_photo — Natchakorn M. — https://maps.google.com/maps/contrib/116711223853249344106 — couple wading, torii gate close
12 hakone_owakudani (cell 2) — KEPT — google_images — Wikipedia — https://en.wikipedia.org/wiki/%C5%8Cwakudani — ropeway gondola window, valley (2026-07-23: incumbent shows readable "HAKONE ROPEWAY" cabin branding + live steam vents, beats all 4 banked Places alternatives, kept)
12 hakone_glass_museum (cell 3) — REPLACED — google_places_user_photo — shigeru kawanishi — https://maps.google.com/maps/contrib/105435231794808096907 — rowboat visitors, pond, tower
12 hakone_lake_ashi (cell 4) — REPLACED — google_places_user_photo — Annie Vanoverbeke — https://maps.google.com/maps/contrib/114097642364750983294 — dusk pirate-ship, railing, passengers
14 tokyo_skyline — REPLACED — google_places_user_photo — たろきち — (shared, see A#10) — deck net glass escalator

## Deck C2 (11 slides)

01 fuji_lake — KEPT — google_images — Trip.com — (shared, see A#1) — untouchable, approved candid sunset
02 spring_cherry_blossom (cell 1) — KEPT — google_images — fooddiversity.today — https://fooddiversity.today/en/article_85799.html — street banners, pedestrians, bloom
02 summer_festival (cell 2) — REPLACED — google_images — The Japan Times — https://www.japantimes.co.jp/life/2026/07/14/travel/uchiwa-festival-kumagaya-heat-matsuri-traditional-culture/ — ground-level crowd, lantern floats
02 autumn_leaves (cell 3) — KEPT — repo-graded — Chloe / ttc-06 (Japan Travel Tips That Matter) — outputs/06 - Japan Travel Tips That Matter — ginkgo avenue, single walker
02 winter_snow (cell 4) — KEPT — google_images — Delta News Hub — https://news.delta.com/snow-slopes-and-serenity-exploring-japans-skiing-resorts — skiers group, rear-view mountain
03 route_map — KEPT — google_images (pre-selected, japan-route pool) — n/a — n/a — untouchable, real map screenshot
05 tokyo_skyline (favorites) — REPLACED — google_places_user_photo — たろきち — (shared, see A#10) — deck net glass escalator
06 station_pov — REPLACED (2026-07-23) — google_places_user_photo — Shichao Zhang — https://maps.google.com/maps/contrib/105049472035051034972 — huge Shinjuku exterior, JR signage (incumbent was an unlabeled Osaka-area Hankyu platform, not even Tokyo)
07 ghibli_park — KEPT — google_images — Japan Cheapo — https://japancheapo.com/entertainment/ghibli-park-guide/ — Totoro building, visitors for scale (2026-07-23: 4 banked Places photos were gorgeous interior details but none read as instantly "Ghibli Park" the way the Totoro statue does, kept)
08 neighbourhoods — KEPT — repo-graded (untracked, pre-existing) — n/a — n/a — faded alley, morning-glory vines
08 app_deepl (icon) — KEPT — n/a (app icon asset) — n/a — n/a — untouchable, icon asset
08 app_google-translate (icon) — KEPT — n/a (app icon asset) — n/a — n/a — untouchable, icon asset
09 suica_tap_train — KEPT — google_images — Real Japan Guide — https://real-japan-guide.com/japan-suica-pasmo-icoca-guide-2026/ — phone tap, motion-blur train
10 golden_gai — KEPT — repo-graded (untracked) — n/a — (shared, see A#5) — handheld night alley lanterns
11 tokyo_skyline — REPLACED — google_places_user_photo — たろきち — (shared, see A#10) — deck net glass escalator

---

## Per-deck source counts

Counts are per row above (a shared slug reused across multiple slides in the same deck, e.g.
`golden_gai` on A#5 and again as a C1 divider cell, counts once per deck it appears in).

| Deck | instagram | google_places_user_photo | google_images | repo-graded | kept-other (untraceable) | Rows |
|---|---|---|---|---|---|---|
| A  | 0 | 4 | 10 | 0 | 2 | 16 |
| B  | 0 | 6 | 5  | 1 | 0 | 12 |
| C1 | 0 | 9 | 11 | 1 | 1 | 22 |
| C2 | 0 | 3 | 7  | 1 | 4 | 15 |
| **Total** | **0** | **22** | **33** | **3** | **7** | **65** |

**2026-07-23 sweep result:** 10 of 65 rows (10 distinct venues — `skytree`, `takeshita`,
`cat_street`, `osaka_universal_studios`, `osaka_amerikamura`, `kyoto_fushimi_inari`,
`nara_todaiji`, `hakone`, `narita_airport`, `station_pov`) moved from `google_images` /
untraceable-repo-graded to `google_places_user_photo`. `google_places_user_photo` rose from
12→22 rows and `google_images` fell from 40→33; two of the ten (`skytree`, `takeshita`) also
retired the doc's own "untraceable" flag by replacing a byte-identical-looking but unattributable
asset with a real, sourced equivalent. 10 more venues were actively re-checked against banked or
freshly-sourced Places photos and kept their incumbent, each for a documented reason (message
needs a crowd/queue the Places photo lacks, the Places photo is the wrong landmark entirely, or
the Places photo visually reads as more staged/processed than gate 9 wants despite the platform
label). Every swap was installed to `media/graded/<slug>.jpg`, visually confirmed against gate 9
and the slot's actual render crop, and logged in `media/manifest.json` (`used_in` moved from the
old incumbent's manifest row, where one existed, onto the new photo's row).

**"kept-other (untraceable)"** = pre-existing sandbox assets (`cherry_blossom_crowds`,
`golden_gai`, `neighbourhoods`, plus the two app icons) that predate this pass's manifest logging
— no `media/manifest.json` row and no byte-identical file anywhere in `media/library/` was found
for them. They passed gate 9 on direct visual inspection and were kept, but their attribution
chain cannot be reconstructed from current data. (`takeshita` and `skytree` were in this bucket
as of the 2026-07-22 doc; the 2026-07-23 sweep resolved both to real attributed Places photos,
so they no longer appear here.) Worth a follow-up to either re-source `cherry_blossom_crowds` /
`golden_gai` / `neighbourhoods` properly or hand-log an attribution row.

**Note on Instagram:** the IG/Apify backend was exercised twice this pass (a fresh `#amemura` pull
for `osaka_amerikamura`, per SOURCING_STATUS.md's existing verified pulls for Ichiran/Shibuya
Sky/Shimokitazawa). Every IG result actually usable against gate 9 ended up not being the final
pick — the `#amemura` pull returned only business-account promo/collage content (rejected), and
the pre-existing Ichiran/Shibuya Sky/Shimokitazawa IG pulls in the library were not the exact
frames selected (Google Places user photos or Google Images candidates won those slots instead
on image quality). This is a real, not accidental, zero — Places and Images simply won the
head-to-head comparisons this round. The 2026-07-23 sweep did not touch Instagram sourcing.
