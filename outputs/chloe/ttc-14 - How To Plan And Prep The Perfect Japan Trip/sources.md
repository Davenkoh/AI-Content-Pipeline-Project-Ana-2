# Photo sources — ttc-14 · Framework D · Japan

Row format per `media/PHOTO_SOURCES.md`: `NN slug — KEPT|REPLACED — platform — author — source_url — note`.

Gate 9 (real-visitor handheld framing) was applied to every **body** photo; the cover scenic, the ending
scenic and the plug `bg_photo` are the specced postcard exemptions.

| NN | slug | status | platform | author | source_url | note |
|---|---|---|---|---|---|---|
| 01 | jp_fuji_torii | KEPT | google_images | Third Eye Traveller | https://thirdeyetraveller.com/chureito-pagoda-best-view-mount-fuji/ | cover scenic (nohuman variant); also the real background plate the human cover was generated into. Gate-9 exempt |
| 02 | spring_cherry_blossom | KEPT | google_images | fooddiversity.today | https://fooddiversity.today/en/article_85799.html | "Spring" season cell |
| 02 | summer_festival | KEPT | google_images | The Japan Times | https://www.japantimes.co.jp/life/2026/07/14/travel/uchiwa-festival-kumagaya-heat-matsuri/ | "Summer" season cell |
| 02 | autumn_leaves | KEPT | repo-graded | Chloe / ttc-06 pool | outputs/06 - Japan Travel Tips That Matter | "Autumn" season cell |
| 02 | winter_snow | KEPT | google_images | Delta News Hub | https://news.delta.com/snow-slopes-and-serenity-exploring-japans-skiing-resorts | "Winter" season cell |
| 03 | route_map_jp2 | KEPT | google-maps-embed | Google Maps | https://www.google.com/maps/embed/v1/directions | pinned open-jaw Osaka → Kyoto → Hakone → Tokyo route at 1080x1920. Re-rendered twice: once to crop the embed's directions panel, once re-centred north so the route line sits clear of the text band. Google attribution retained in-frame |
| 04 | oishi_park_fuji | **REPLACED** | google_places_user_photo | LYNN HUNG | https://maps.google.com/maps/contrib/109521811029768267426 | plug `bg_photo`. **Replaced `hakone_lake_ashi`** after the §8 contact-sheet review: that frame is a dusk shot and went muddy under the plug scrim, against DESIGN.md's "full-bleed picturesque scenic". Gate-9 exempt |
| 05 | arashiyama_bamboo | KEPT | google_images | Sprayedout.com | https://www.sprayedout.com/bamboo-grove-in-arashiyama-kyoto/ | favorites hero |
| 06 | cramped_hotel_room | KEPT | google_images | YouTube | https://www.youtube.com/watch?v=tg5lz_zIAao | accommodation slide. A genuinely tiny business-hotel room, which is the point of the copy |
| 07 | ghibli_museum_mitaka | KEPT | google_places_user_photo | Quang Huynh | https://maps.google.com/maps/contrib/107345633974102014829 | book-activities-early slide. Handheld, overcast, real visitors |
| 08 | jp_ticket_machine | KEPT | google_images | Coto Academy | https://cotoacademy.com/how-to-use-japan-ramen-vending-machines/ | language slide. A real Japanese-only ramen ticket machine, dark enough for the white sticker boxes to hold contrast |
| 08 | app_google-translate | KEPT | app-store | Google | https://apps.apple.com/app/google-translate/id414706506 | real app icon via `app_icons.py` |
| 08 | app_deepl | KEPT | app-store | DeepL SE | https://apps.apple.com/app/deepl/id1552407475 | real app icon |
| 09 | jp_station_shinkansen | KEPT | google_images | Japan Bullet Train | https://www.japan-bullettrain.com/articles/blog/tokyo-shinkansen-boarding | internal-transport slide. Tokyo Station concourse with real Shinkansen signage and commuters |
| 10 | dotonbori_neon_night | KEPT | google_places_user_photo | John Snow | https://maps.google.com/maps/contrib/110521069195680098831 | mobile-data slide |
| 11 | golden_gai | KEPT | repo-graded (pre-existing) | n/a | n/a | save scenic (nohuman variant); also the real background plate the human ending was generated into. Gate-9 exempt |

## Rejected during curation

- `subway_ticket_machine` (already in `media/graded`) — it is a **Seoul Metro** kiosk, wrong country for a
  Japan deck. Replaced with `jp_ticket_machine`.
- `jr_pass_ticket` (already in `media/graded`) — a real JR Pass, but a **14 day pass at the pre-2023
  ¥47,250 price**, which visibly contradicts this deck's ¥50,000 / ¥53,000 line. Replaced with
  `jp_station_shinkansen`.
- `japan-shinkansen/1a6f1a0e` — Alamy watermark.
- `japan-shibuya/2f87fd9b` — Alamy watermark, and too dense a crowd to place a subject in; the ending
  scene moved to Golden Gai instead.
- `japan-fuji/1dce8fec` — a strong Chureito frame, but it already has a woman in a red dress centre-frame,
  which fights a character gen.
- `japan-ghiblimuseum/3e6c918e` — a stone cube sculpture; not recognisable as the museum.
- `japan-shokkenki/c51cdb4e` — a good Matsuya machine, but brighter and busier than the pick.

## Character scene photos (not manifest media)

- `chars/chloe_ttc-14_cover.png` — new per-post gen, the Arakurayama torii with Fuji through the gate in
  autumn; burgundy halter + red scarf tie + baggy light-wash jeans + burgundy boots.
- `chars/chloe_ttc-14_ending.png` — new per-post gen, a Golden Gai alley at night; white ribbed henley +
  baggy jeans + tan backpack.
- Both use real sourced background plates (`chars/_gen/chloe_scene/bg_ttc-14_*.jpg`), identity locked to
  `character/Chloe/Base References/`. Different setting **and** wardrobe from ttc-12 (Miyajima / Kanazawa)
  and ttc-13 (Yasaka Pagoda / Dotonbori). The two scenes share an autumn season, which matches the deck's
  "autumn is the quietly correct answer" line.
