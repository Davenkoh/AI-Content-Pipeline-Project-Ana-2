# Flags — tt-23 · Framework D · Vietnam · human · iteration 1

First Framework D deck ever shipped in this repo (D had only the unposted `fixtures/D.json` Japan
exemplar at iteration 0), so the slide-by-slide mapping below is worth an extra look.

## Verbatim vs drafted

| Element | Status |
|---|---|
| Slide 1 hook title + subtitle | **verbatim** from `CREATIVE.md` §D (`How to plan & prep the perfect {country} trip for first timers` / `everything you need to know`) |
| Slide 4 plug copy | **verbatim** Framework B plug, transformed only by the DESIGN.md §plug-paragraph-grammar type rules (sentence-final periods dropped, brand written `HOLICAY.COM`). "alot" and "revisted" kept as-is |
| Slide 11 SAVE THIS + subtitle | **verbatim** (`just incase you need it ❤️`) |
| Hashtags | **formula** (`#{country}travel #{country}tips #travel{country} #{country}trip #{country}`) |
| Every step pill + body line | **drafted** for Vietnam |
| Caption essay | **drafted**, one paragraph per slide |

## Verified against primary / current sources

| Claim on the deck | Source | Status |
|---|---|---|
| Tet 2027 falls 6 Feb 2027, country shuts ~a week | PublicHolidays.vn + Tet 2027 guides | verified |
| North best Oct to Apr; Central Feb to May, typhoons Aug to Nov; South Dec to Apr, wet May to Nov | Rough Guides / Intrepid / Oxalis climate guides | verified (consistent across sources) |
| Son Doong booked out through 2027, 2028 reservations open | Oxalis Adventure + Son Doong booking guides | verified |
| Hang En = 8,800,000 VND (~US$333), 2 days, capped 16 guests | **oxalisadventure.com** (operator's own page) | verified, primary source |
| Hanoi to Da Nang flight ~80 min vs 16h+ train | route/operator comparisons (VN Airlines, VietJet, Bamboo; Reunification Express) | verified |
| Viettel eSIM ~US$10 to $15 for 10 to 20GB; airport kiosks 20 to 30% more | Vietnam eSIM comparison guides | **see unverified below** |
| Google Translate and DeepL both support Vietnamese | DeepL launch announcement (Vietnamese added June 2025) | verified |

## Unverified / soft numbers — flagged, not buried

1. **Hanoi to Da Nang "$40 to $60"** is a *booked-ahead* range, not a fixed fare. Live fares swing to
   $120 to $150 last minute and around Tet. The slide says "for $40 to $60", which reads as typical, not
   guaranteed.
2. **eSIM "$10 to $15 for 10 to 20gb"** and the **"20 to 30% more"** airport-kiosk markup come from eSIM
   comparison guides, **not** from Viettel's own site (Viettel does not publish a stable tourist-eSIM
   price page). Directionally right, but it is the softest number on the deck.
3. **"$333" for Hang En** is Oxalis's own VND price (8,800,000₫) converted at a mid-2026 rate. The VND
   figure is fixed; the dollar figure moves with FX.
4. **"crossing a vietnamese city eats an hour"** is judgment anchored on real Hanoi/Saigon traffic, not a
   measured figure.
5. **Ninh Binh "earns a night, not a day trip"** and the whole day-split (3/1/1/3/2) are itinerary
   opinion, not fetched facts. They are internally consistent and never backtrack.

## Notes for the human

- **`engine/source/route_map_shot.js` is hardcoded to the Tokyo → Osaka corridor** and exposes no
  origin/destination flags, so it cannot render a non-Japan route. Because `engine/` is not to be edited
  as a side effect of a post, this deck's map was rendered by a scratchpad twin of that script (same
  Maps Embed API call, same 1080x1920 capture) into `media/graded/route_map_vn.png` with a matching
  manifest row. **Parameterising the real script is a proper follow-up** so D can run for any country.
- Slide 2 flexes the D spec's "4 seasons" grid into **3 climate regions + a Tet warning**, per the
  spec's own instruction to flex the cell count to the country's real seasons. Vietnam genuinely has no
  four-season model.
