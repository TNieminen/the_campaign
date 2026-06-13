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
   - **Encounters** (`encounters.md`): run the combat, hazard, or skill challenge. Environmental challenges may grant advantage on the next travel check, inspiration, or reveal a shortcut on success.
   - **Loot & discoveries** (`loot/`): hand out treasure, or use the alternative discovery option on a Nat 20 for a more memorable, story-driven reward.

## Content files

- `encounters.md` — d20 **1–10**: dangerous, medium, and minor encounters, each mixing monsters and environmental obstacles. Stat blocks in `monsters/`, hazards in `environments/`.
- `loot/` — d20 **11–20**: nothing found, mundane treasure, magic treasure, wondrous discoveries (one file per category).

## Tooling

- `tools/encounter.py` — build encounters (d20 **1–10**) for a given party, drawing monster fights from `monsters/` and/or environmental obstacles from `environments/` (`--filter monster|environmental|both`). Pass the players' travel d20 with `--roll` (1–10) to pick the difficulty band automatically (a natural 1 is a "deadly special" above the High budget), or set `--difficulty` directly.
- `tools/loot.py` — roll a random loot/discovery result. Takes the players' travel d20 `--roll` (**11–20**) plus party size and level; it maps the roll to a category, level skews magic-item rarity, and a natural-20 also rolls a guardian (equal odds: none, a high-severity environmental hazard, or a boss-tier monster).
