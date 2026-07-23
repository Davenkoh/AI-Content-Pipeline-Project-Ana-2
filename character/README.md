# character/ — the creator personas (visual identity only)

Each subfolder here is **one creator persona** the pipeline can post as. **Ana** (Vietnam),
**Chloe** (Japan), **Hannah** (USA), and **Mia** (Japan, **faceless**) are the roster — parallel TikTok
pipelines, each with its own account. This is an **active, multi-persona** area.

A character is deliberately lightweight — there are **no personality or makeup text files**. A
character is just:
1. a **registry entry** in [`../state.json`](../state.json) → `characters` (name, `id_prefix`, default `country`), and
2. a locked **visual identity** = the images in `character/<Name>/Base References/`, with her signature
   look **baked into the hero reference** so every downstream gen inherits it.

The content is open — she is a general **digital influencer**; the `country` is only the *default
subject* for her posts.

> **Faceless variant (Mia).** A character can be **faceless** (`"faceless": true` in the registry) —
> no persona, no face, and **no `Base References/`**. Her identity is the *design system + a location /
> food photo library* instead of a locked look, and her posts are built entirely from real photography
> + text overlay modelled on Ana's `tt-03` — she **never** touches the persona / cover-gen path (the
> absent `Base References/` is the failsafe). See [`Mia/README.md`](Mia/README.md).

## Add a character
Run the **`new-character` skill** ([`../.claude/skills/new-character/SKILL.md`](../.claude/skills/new-character/SKILL.md)) — it registers her,
walks the identity image-gen (hero gate → face-closeup + half-front, makeup baked in), and wires her
Drive folder + Sheet tab. (e.g. *"create a profile, call it Hannah, USA content."*)

## Where things live (the storage rule)
The **`.gitignore` boundary** the whole system uses — git carries code/config, Drive carries media:

| What | Lives in |
|---|---|
| Character **config** (name, id_prefix, country) | `state.json` → `characters` (**git**) |
| **Per-character reference images** — `Base References/`, `Profile Pictures/` | **Drive** → `<Name>/…` (one folder per character; gitignored locally) |
| **Shared references** — `Wardrobe References/`, `Profile Pic References/` | **Drive** → `_shared/…` (gitignored) |
| Finished **posts** | **Drive** → `<Name>/Tiktok/NN - Title/` |

> **Drive layout = one folder per character.** `<root>/Ana/{Base References, Profile Pictures, Tiktok/NN}`
> (same for `Chloe/`), shared refs under `<root>/_shared/`. The post library (`Tiktok/`) is
> NOT pulled by the ref sync (large; browse on Drive or pull on demand).

Sync a character's gitignored media to Drive:
```bash
python3 engine/drive/drive_sync.py --mirror "character/<Name>" --dest "<Name>"   # up
python3 engine/drive/drive_sync.py --pull   "<Name>" --to "character/<Name>"     # down (skips post libs)
```
`git clone` gives you the code + `state.json`; `bootstrap` (or `--pull`) fills in the images.

> **Building a post AS a character** — pass `--character <key>` to the Sheet/Drive commands and
> `--persona <Name>` to `prep_cover_refs.py`, and export `MASQ_PERSONA=<Name>` so the cover scripts read
> her Base References + name `<persona>_cover_*`. See [`../WORKFLOW.md`](../WORKFLOW.md) (character scene-photo stage).
