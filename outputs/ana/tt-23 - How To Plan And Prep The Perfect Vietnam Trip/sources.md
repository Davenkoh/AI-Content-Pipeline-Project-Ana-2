# Photo sources — tt-23 · Framework D · Vietnam

Row format per `media/PHOTO_SOURCES.md`: `NN slug — KEPT|REPLACED — platform — author — source_url — note`.

11 of 16 slugs are Google Places **user** photos (the prioritized UGC source). Gate 9 (real-visitor
handheld framing) was applied to every **body** photo; the cover scenic, the ending scenic and the plug
`bg_photo` are the specced postcard exemptions.

| NN | slug | status | platform | author | source_url | note |
|---|---|---|---|---|---|---|
| 01 | danang_goldenbridge | KEPT | google_places_user_photo | H.C Wei | https://maps.google.com/maps/contrib/112660515389503253308 | cover scenic (nohuman variant), matches the human cover location. Gate-9 exempt |
| 02 | sapa_town | KEPT | google_images | LillaGreen | https://lillagreen.com/is-sapa-worth-visiting-travel-guide-to-vietnams-city-in-the-fog/ | "North" season cell. Real handheld town square in the cool misty season |
| 02 | hoian_lanterns | KEPT | google_places_user_photo | Ngoc Diep | https://maps.google.com/maps/contrib/106900348685778550008 | "Central" season cell |
| 02 | mekong_daytour | KEPT | google_images | GetYourGuide | https://www.getyourguide.com/ho-chi-minh-city-l272/explore-non-touristy-mekong-delta-day-tour/ | "South" season cell |
| 02 | vn_tet_hangma | KEPT | google_places_user_photo | N.Đ.C | https://maps.google.com/maps/contrib/101729007070537868291 | "Avoid Tet" cell. Hang Ma street, Hanoi, at Tet. Picked over two brighter frames that carried visible watermarks |
| 03 | route_map_vn | KEPT | google-maps-embed | Google Maps | https://www.google.com/maps/embed/v1/directions | pinned Hanoi → Ha Long → Ninh Binh → Hoi An → Saigon route, captured at 1080x1920. Re-rendered once to crop the embed's directions panel; Google attribution retained in-frame |
| 04 | vn_trangan_scenic | KEPT | google_places_user_photo | Gintaras Čekanavičius | https://maps.google.com/maps/contrib/115247436984601290117 | plug `bg_photo`. Gate-9 exempt, and distinct from this deck's cover + save scenics |
| 05 | vn_trangan_boats | KEPT | google_places_user_photo | Hiệp Phạm Thế | https://maps.google.com/maps/contrib/113410386158268153548 | favorites hero. Real sampans + visitors, overcast rather than postcard |
| 06 | hanoi_oldquarter | KEPT | google_places_user_photo | Quý Nguyễn | https://maps.google.com/maps/contrib/114533195548532842088 | accommodation slide. Handheld Old Quarter shopfront street |
| 07 | vn_halong_cruise | KEPT | google_places_user_photo | Fatma Dahlawi | https://maps.google.com/maps/contrib/100481807999728427744 | book-activities-early slide. Handheld from a boat deck, native portrait |
| 08 | vn_bun_cha_stools | **REPLACED** | google_places_user_photo | Tiger LEE | https://maps.google.com/maps/contrib/111917957897096399585 | language slide. **Replaced `vn_menu_board`** (a real Bun Cha Huong Lien menu board) after the §8 contact-sheet review: white sticker boxes over a near-white menu lost contrast. Graded file + manifest row for `vn_menu_board` were pruned |
| 08 | app_google-translate | KEPT | app-store | Google | https://apps.apple.com/app/google-translate/id414706506 | real app icon via `app_icons.py` |
| 08 | app_deepl | KEPT | app-store | DeepL SE | https://apps.apple.com/app/deepl/id1552407475 | real app icon. DeepL added Vietnamese in June 2025, so the pairing is honest for this country |
| 09 | vn_grab_ride | KEPT | google_images | Báo Thanh Niên | https://thanhnien.vn/tai-xe-grabbike-ke-chuyen-chay-xe-mua-nha-ganh-ca-uoc-mo-cua-con.htm | internal-transport slide. Real GrabBike rider in a Hanoi side street |
| 10 | saigon_buivien | KEPT | google_places_user_photo | Peter Holroyd | https://maps.google.com/maps/contrib/114220226898873699275 | mobile-data slide. Bui Vien at dusk, handheld |
| 11 | vn_hoankiem_tower | KEPT | google_places_user_photo | Didier Omnes | https://maps.google.com/maps/contrib/110120631703688660994 | save scenic (nohuman variant), matches the human ending location (Hoan Kiem). Gate-9 exempt |

## Rejected during curation

- `vietnam-north/2229ba86` (Mu Cang Chai rice terraces) — **drone/aerial**, an outright Gate 9 reject.
- `vietnam-north/a91e1218` (terraced fields with villagers) — real, but an HDR-postcard grade; `sapa_town` reads more like a visitor's phone.
- `vietnam-tet/f0513b6c` and `.../fad43619` — clean subjects but both carry stock/agency watermarks.
- `vietnam-signs/a06b6c9c`, `.../fc847edb` — Alamy-watermarked; one was also a US Vietnamese-diaspora sign board, not Vietnam.
- `vietnam-saigon/08a22d78` — reads AI-generated (impossibly clean rooftop, symmetric furniture).
- `vietnam-halong/109c3bda` — a cruise-ship infinity pool; too resort-brochure for a body slide.

## Character scene photos (not manifest media)

- `chars/ana_tt-23_cover.png` — new per-post gen, Golden Bridge at Ba Na Hills, white halter crop + baggy jeans.
- `chars/ana_tt-23_ending.png` — new per-post gen, the Huc Bridge at Hoan Kiem in golden hour, brown off-shoulder top + cream cargos.
- Both use real sourced background plates (kept at `chars/_gen/ana_scene/bg_tt-23_*.jpg`), identity locked to `character/Ana/Base References/`. Different setting **and** different wardrobe from tt-20, tt-21 and tt-22.
