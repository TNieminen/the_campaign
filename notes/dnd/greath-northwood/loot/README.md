Great Northwood — Loot & Discoveries
====================================

The loot/discovery half of the travel roll (d20 **11-20**; see `../mechanic.md`).
One file per category, each with YAML frontmatter followed by the option list(s)
so `../tools/loot.py` can read them while they stay easy to hand-edit.

Encounters (d20 **1-10**) live in `../encounters.md` and `../monsters/`.

## How it fits the travel roll

On each travel beat the **players roll the d20**. Results **11-20** land here and
map to one of four categories. You can resolve a result by rolling the inner die
by hand, or pass the players' roll to `../tools/loot.py`, which maps it to a
category and randomizes the reward inside it (scaled to the party).

| Travel d20 (`--roll`) | Category | File | Inner die | Notes |
| --- | --- | --- | --- | --- |
| 11-13 | Nothing Found | `nothing-found.md` | d12 | Flavour only, no treasure. |
| 14-16 | Mundane Treasure | `mundane-treasure.md` | d24 | Coins, goods, valuables (gold auto-scales to the party). |
| 17-19 | Magic Treasure | `magic-treasure.md` | tiered | Items grouped into `## Common`/`## Uncommon`/`## Rare`. |
| 20 | Wondrous Discovery | `wondrous-discovery.md` | d24 | Rare find or story discovery, **plus a randomized guardian** (monster, hazard, or none). |

Rolls **1-10** are encounters — see `../encounters.md` and `../tools/encounter.py`.

## File format

Each category is a standalone markdown file: a YAML frontmatter block, then the
option list(s) as ordinary numbered/bulleted lists. The tool reads the lists; the
frontmatter is metadata for humans and tooling.

```
---
name: Magic Treasure   # display name
category: magic         # category slug (metadata; the tool maps the d20 roll to this)
die: d20                # the inner die you would roll by hand
range: 17-19            # the travel d20 range this category covers
summary: One-line description.
---
```

`magic-treasure.md` additionally splits its options under `## Common`,
`## Uncommon`, and `## Rare` headings — those tier headings are meaningful to the
tool (see below). `wondrous-discovery.md` splits into `## Treasures` and
`## Discoveries`, which the tool merges into a single pool.

## Rolling loot

From this folder's parent, run the tool with the players' d20 result (see
`../tools/loot.py --help`):

```
python3 tools/loot.py --party-size 4 --level 6 --roll 17   # rolled 17 -> magic
python3 tools/loot.py --levels 5,6,6,7 --roll 20            # natural 20 -> wondrous
python3 tools/loot.py --party-size 6 --level 5 --roll 15 --seed 12
```

Pass the travel `--roll` (11-20), plus the party as either `--party-size`+`--level`
for a uniform party or `--levels a,b,c` for mixed levels. `--seed` makes a roll
reproducible. A natural-20 also rolls a guardian (monster, hazard, or none).

## Design description

The system is intentionally **data-driven**: all options live in editable
markdown, and `loot.py` only handles dice and scaling. Adding or rewording an
option never requires touching code — the tool re-parses the lists each run.

**Why party size and level are inputs.** The campaign content is tuned for the
baseline party (4 characters at 6th level; see `../mechanic.md`). Rather than
maintain separate loot tables per level, the tool reads the party and scales a
single set of tables:

- **Level drives magic-item rarity.** Instead of every magic roll being a flat
  pick, level chooses *which rarity tier* is likely, then a random item is taken
  from that tier. Low-level parties mostly see Common items; high-level parties
  mostly see Rare. The tier weights (Common / Uncommon / Rare) are:

  | Avg. level | Common | Uncommon | Rare |
  | --- | --- | --- | --- |
  | 1-4 | 6 | 3 | 1 |
  | 5-7 | 3 | 5 | 2 |
  | 8-10 | 2 | 5 | 3 |
  | 11-13 | 1 | 4 | 5 |
  | 14+ | 1 | 3 | 6 |

  These are relative weights, not percentages — a tier is only eligible if its
  list has items. This keeps the curve smooth and avoids hard "you must be level
  X" gates.

- **Party size is a secondary nudge.** Each character above the baseline of 4
  adds `+0.5` to the Rare weight (a bigger party finds a bit more, and earns
  slightly better odds at the top tier).

**Gold is auto-scaled, not just hinted.** Every coin/value amount in a rolled
result is multiplied automatically by `gold_multiplier(levels)`:

- **Party size** scales linearly (`party_size / 4`).
- **Average level** scales by rough 5e treasure tier: `x1` at levels 1-4, `x2`
  at 5-10, `x4` at 11-16, `x8` at 17-20.

Flat values are rewritten in place (`25 gp` → `75 gp`), and dice amounts stay
rollable with the multiplier and an average appended (`4d10 gp` →
`4d10 gp x3 (~66 gp)`). The source tables hold the un-scaled baseline, so the
markdown never needs rewriting per party. Nothing-found is pure flavour and is
picked uniformly with no scaling.

**Items and monsters link to their source.** Every magic/wondrous item name (and
each monster stat block) carries a clickable **D&D Beyond** link, so a card's
full rules text is one click away. Item links are embedded in these markdown
tables; monster links are generated by `../../../../docs/build_data.py` from the
creature name.

**Wondrous discoveries may come guarded.** A natural 20 is a marquee moment, so
on top of the reward the tool rolls a **guardian** with three equally likely
outcomes:

- **none** — the find lies unguarded this time;
- **environmental** — a high-severity hazard from `../environments/` watches over it; or
- **monster** — a boss-tier creature from `../monsters/`, picked between the
  party's High XP budget and twice that, so it reads as a genuine threat rather
  than a fair fight.

Both encounter kinds are sourced from the sibling `../tools/encounter.py` tool's
data, so guardians stay consistent with the rest of the travel content. The
treasure itself is drawn from the merged `Treasures` + `Discoveries` pool, so a
roll may yield a powerful item *or* a story discovery (a fey crossing, a shrine
boon, etc.). The randomized guardian lives in `roll_guardian()` in
`../tools/loot.py`.

## Editing the tables

- Add, remove, or reword list items freely — the tool re-reads them each run.
- To add a magic item, drop it under the appropriate `## Common`/`## Uncommon`/
  `## Rare` heading.
- To retune the rarity curve or the party-size nudge, edit `magic_tier_weights()`
  in `../tools/loot.py`.
- Keep frontmatter (`name`, `category`, `die`, `range`, `summary`) in sync if you
  rename or repurpose a file, and update the category table above and
  `../mechanic.md`.
