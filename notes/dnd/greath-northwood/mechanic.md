Great Northwood — Travel Roll Mechanic
======================================

The core mechanic that drives travel through the Great Northwood. On each travel
beat roll twice a **d20** and the result is looked up on the table below.

> **Scaling:** This table is tuned for a **party of 4 at 6th level**. Adjust
> encounter difficulty and loot rarity up or down for parties of different size
> or level.

## The roll

Roll a single **d20** and consult the matching range:

| d20 | Result | Where to look |
| --- | --- | --- |
| 1-3 | Dangerous Encounter | `encounters.md` |
| 4-6 | Medium Encounter | `encounters.md` |
| 7-10 | Minor Encounter | `encounters.md` |
| 11-13 | Nothing Found | `loot/nothing-found.md` |
| 14-16 | Mundane Treasure | `loot/mundane-treasure.md` |
| 17-19 | Magic Treasure | `loot/magic-treasure.md` |
| 20 | Wondrous Discovery | `loot/wondrous-discovery.md` |

In short: **1–10 is an encounter**, **11–20 is loot or a discovery**. Each
encounter band mixes **monster** fights and **environmental** obstacles, and a
**natural 1** escalates to a deadly special encounter (see `encounters.md`).

## Resolving the result

1. Roll the d20 and find the range above.
2. Open the referenced file and roll the inner sub-table (d6/d8/d10/d12/d20 as noted there), or use the tooling below.
3. Apply the outcome:
   - **Encounters** (`encounters.md`): run the combat, hazard, or skill challenge. Environmental challenges may grant advantage on the next travel check, inspiration, or reveal a shortcut on success. The more dangerous the encounter, the more likely it takes place at a faction location (`locations/`) — 25% Minor, 50% Medium, 75% Dangerous, 100% on a natural-1 deadly special — and the grander that site.
   - **Loot & discoveries** (`loot/`): hand out treasure, or use the alternative discovery option on a Nat 20 for a more memorable, story-driven reward.
   - **Locations** (`locations/`): the higher the value of the loot, the more likely the find was made inside a faction ruin (or one of Valvela's rare living camps) — ~25% on mundane, ~60% on magic, always on a Nat 20. The grander the site, the higher the value.

## Content files

- `encounters.md` — d20 **1–10**: dangerous, medium, and minor encounters, each mixing monsters and environmental obstacles. Stat blocks in `monsters/`, hazards in `environments/`.
- `loot/` — d20 **11–20**: nothing found, mundane treasure, magic treasure, wondrous discoveries (one file per category).
- `locations/` — faction ruins and rare living camps that can be discovered alongside a loot result, scaled to the loot's value (see `locations/README.md`).

## Tooling

- `tools/encounter.py` — build encounters (d20 **1–10**) for a given party, drawing monster fights from `monsters/` and/or environmental obstacles from `environments/` (`--filter monster|environmental|both`). Pass the players' travel d20 with `--roll` (1–10) to pick the difficulty band automatically (a natural 1 is a "deadly special" above the High budget), or set `--difficulty` directly. The encounter may be sited at a `locations/` ruin or camp, with the chance and tier scaling with its danger (see `roll_encounter_location()`); `--seed` makes the pick reproducible.
- `tools/loot.py` — roll a random loot/discovery result. Takes the players' travel d20 `--roll` (**11–20**) plus party size and level; it maps the roll to a category, level skews magic-item rarity, **coin/value rewards auto-scale by party size and average level**, may attach a **location** from `locations/` (chance and grandeur scale with the loot value), and a natural-20 also rolls a guardian (equal odds: none, a high-severity environmental hazard, or a boss-tier monster).
