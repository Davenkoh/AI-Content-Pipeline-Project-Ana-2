# TikTok platform notes — voice + strategy

> **Framework posts are governed by [`../frameworks/`](../frameworks/) + [`../../CONTRACT.md`](../../CONTRACT.md).**
> Those own the A/B/C1/C2 blueprints, the on-slide design system, the type system, and the Holicay
> plug. This file keeps only the **platform voice + strategy notes that still apply** across any
> TikTok post; the shared build mechanics (canvas + safe zone, photo sourcing, character/wardrobe
> identity, the render engine, OODA checkpoints) live in the engine + `knowledge/frameworks/`.

## 1. Platform snapshot

- The whole point: it reads as a **real person's phone, not a brand.** Two rules above everything: pick **messy real frames**, and **never let anything look polished or designed.** When in doubt, make it rougher.
- A TikTok carousel = swipeable static images; the **cover hook + first slide** carry the swipe. Caption is short and casual.
- The active character sets the subject default: **Ana** is based in Vietnam (subject defaults to **Vietnam**); **Chloe** is based in Japan (subject defaults to **Japan**). The character is a general digital influencer — content can be anything that works for the format; the **country** (from `state.json` → `characters`) is only the default subject.

## 2. Strategy

- **Subject defaults to the active character's country** (Ana → Vietnam, Chloe → Japan) — localize a foreign-country inspo to that country (content, backdrops, app list) unless the user explicitly asks for another country. Speak as a local ("from someone who lives here").
- **Real brand/app logos**, never emoji stand-ins (iTunes Search API; `engine/source/app_icons.py`; eyeball the verify sheet, a keyword miss grabs the wrong app).
- **Don't assert unverifiable facts** in copy (no invented posting cadence, prices, or dates).
- **Research list content with parallel subagents** (**Reddit-primary** = the source of truth; blog/Google confirm-only; flag traps + tourist-trap-vs-better swaps) — that consensus is what makes a guide save-worthy.
