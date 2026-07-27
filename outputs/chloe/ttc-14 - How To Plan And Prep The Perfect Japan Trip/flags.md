# Flags — ttc-14 · Framework D · Japan · human · iteration 1

Iteration 1 for Japan x D. Iteration 0 is the **unposted** `fixtures/D.json` exemplar, so the freshness
rule applies against it: every step below carries a different angle, and the favorites list shares no
spot with the fixture.

## Freshness vs `fixtures/D.json` (Japan x D, iteration 0)

| Step | Fixture (it. 0) | This pack (it. 1) |
|---|---|---|
| 1 When to go | "each season is SO different"; avoid Golden Week | "pick the season first, everything else prices off it"; bloom is ~2 weeks, book 6 months out, leaves peak late Nov, typhoons in Sep |
| 2 Route | Tokyo 4 → Hakone 1 → Kyoto 3 → Osaka 2 | **reversed and open jaw**: in to Kansai, out of Haneda. Osaka 2 → Kyoto 3 → Hakone 1 → Tokyo 4 |
| 3 Accommodation | book near a main train station | book 6 months ahead for sakura/koyo; rooms are tiny, pay for location |
| 4 Book early | Ghibli **Park** (Nagoya); Shibuya Sky night slot | Ghibli **Museum** (Mitaka): 10am JST on the 10th, month ahead only, ¥1000, never at the door |
| 5 Language | "locals may not speak English" | the real friction point: Japanese-only **ticket machines**, camera-translate before queueing |
| 6 Transport | add Suica to Apple Wallet, top up ¥1000 | **JR Pass maths**: ¥29,470 point to point vs a ¥50,000 pass on the golden route |
| 7 Mobile data | eSIM vs pocket wifi | eSIM with real 2026 pricing; public wifi wants a signup form every time |
| Favorites | Tokyo/Osaka/Kyoto/Nara/Nagoya/Hakone, teamLab, Sensoji, Shibuya Sky, Fushimi Inari… | Osaka/Kyoto/Nara/Hakone/Tokyo, **zero overlapping spots** (Kuromon, Shinsekai, Philosopher's Path, Kasuga Taisha, Open Air Museum, Tsukiji Outer, Yanaka Ginza, Shimokitazawa) |

## Verbatim vs drafted

| Element | Status |
|---|---|
| Slide 1 hook title + subtitle | **verbatim** from `CREATIVE.md` §D |
| Slide 4 plug copy | **verbatim** Framework B plug, transformed only by the DESIGN.md type rules (no sentence-final periods, brand as `HOLICAY.COM`). "alot" and "revisted" kept |
| Slide 11 SAVE THIS + subtitle | **verbatim** |
| Hashtags | **formula** |
| Every step pill + body line | **drafted** |
| Caption essay | **drafted**, one paragraph per slide |

## Verified against primary / official sources

| Claim on the deck | Source | Status |
|---|---|---|
| Ghibli Museum tickets released 10am JST on the 10th, for the following month; ¥1,000 adult; **none sold at the door** | **ghibli-museum.jp** (the museum's own tickets page) | verified, primary source |
| 7 day ordinary JR Pass ¥50,000, rising to ¥53,000 on 1 Oct 2026 | **japan.travel** (JNTO, Japan's official tourism organisation) | verified, official source |
| Tokyo → Kyoto → Osaka → Tokyo ≈ ¥29,470 point to point | JR Pass fare calculators / comparison tools | **see unverified below** |
| Autumn leaves peak late Nov; sakura bloom ~2 weeks; Sep typhoons | standard Japan seasonal guides | verified (consistent across sources) |
| Google Translate and DeepL both support Japanese | both vendors | verified (Japanese is a launch language for DeepL) |
| eSIM ~$14 to $17 for 10GB | Japan eSIM comparison guides (Airalo / Ubigi) | **see unverified below** |

## Unverified / soft numbers — flagged, not buried

1. **¥29,470** for the Tokyo/Kyoto/Osaka loop comes from JR Pass fare calculators, not from a JR
   operator's own fare table. The comparison (point to point beats the pass on the golden route) is
   robust and widely agreed; the exact yen figure is indicative and moves with reserved-seat choices.
2. **The 1 Oct 2026 price rise is time-sensitive.** It is correct as of 27 July 2026, and JNTO notes the
   official site may honour pre-October prices for a limited window. If this post ships after
   1 October 2026 the tip line reads stale and should be re-cut to "the 7 day JR pass is ¥53,000".
3. **eSIM "$14 to $17 for 10gb"** is from comparison guides, not a carrier's own page, and Japan eSIM
   pricing moved noticeably in early 2026. Softest number on the deck.
4. **"rooms here are tiny"**, **"kyoto sells out first"**, and the 2/3/1/4 day split are judgment, not
   fetched facts. The split is internally consistent and never backtracks.
5. **"good dates go in minutes"** for the Ghibli Museum is reported behaviour, not an official statement.
   The official facts around it (release time, no door sales, price) are all primary-source verified.

## Notes for the human

- **`engine/source/route_map_shot.js` is still hardcoded to Tokyo → Osaka** with no origin/destination
  flags. Both D decks this run needed a different route, so the maps were rendered by a parameterised
  scratchpad twin (identical Maps Embed call and 1080x1920 capture) into `media/graded/route_map_jp2.png`
  and `media/graded/route_map_vn.png`, each with a manifest row. **Worth parameterising the real script.**
- Two graded slugs were rejected during build after a look at the actual files: `subway_ticket_machine`
  is a **Seoul Metro** kiosk (wrong country for a Japan deck) and `jr_pass_ticket` shows a **14 day pass
  at the pre-2023 ¥47,250 price**, which would visibly contradict this deck's ¥50,000 line. Both were
  replaced with freshly sourced Japan photos.
