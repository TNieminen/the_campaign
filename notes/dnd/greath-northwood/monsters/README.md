Great Northwood — Monster Stat Blocks
=====================================

One file per creature, flat (no difficulty subfolders). Each file begins with a
YAML frontmatter block so the encounter tool can read it without parsing prose,
followed by the human-readable stat block including an **Appearance** paragraph.

Difficulty is no longer encoded by folders — it is computed per party by
`../tools/encounter.py` using the 2024 (5.5e) XP budget rules. Statistics use
standard 5e (SRD) values.

## Frontmatter schema

```
---
name: Wolf            # display name
cr: "1/4"             # challenge rating (string; fractions allowed)
xp: 50                # integer XP the tool spends from the budget
size: Medium          # Tiny / Small / Medium / Large / Huge / Gargantuan
type: beast           # creature type
summary: A lean grey-furred pack predator built for endurance and the hunt.
---
```

## Finding monsters for an encounter

From this folder's parent, run the tool (see `../tools/encounter.py --help`):

```
python ../tools/encounter.py --party-size 4 --level 6 --difficulty high --count 3
```

## Roster (sorted by CR)

| Monster | CR | XP | File |
| --- | --- | --- | --- |
| Wolf | 1/4 | 50 | `wolf.md` |
| Scout | 1/2 | 100 | `scout.md` |
| Dire Wolf | 1 | 200 | `dire-wolf.md` |
| Giant Spider | 1 | 200 | `giant-spider.md` |
| Harpy | 1 | 200 | `harpy.md` |
| Ankheg | 2 | 450 | `ankheg.md` |
| Bandit Captain | 2 | 450 | `bandit-captain.md` |
| Gargoyle | 2 | 450 | `gargoyle.md` |
| Ogre | 2 | 450 | `ogre.md` |
| Swarm of Poisonous Snakes | 2 | 450 | `swarm-of-poisonous-snakes.md` |
| Displacer Beast | 3 | 700 | `displacer-beast.md` |
| Manticore | 3 | 700 | `manticore.md` |
| Owlbear | 3 | 700 | `owlbear.md` |
| Bulette | 5 | 1,800 | `bulette.md` |
| Troll | 5 | 1,800 | `troll.md` |
| Chimera | 6 | 2,300 | `chimera.md` |
| Wyvern | 6 | 2,300 | `wyvern.md` |
| Stone Giant | 7 | 2,900 | `stone-giant.md` |
| Young Green Dragon | 8 | 3,900 | `young-green-dragon.md` |
| Fire Giant | 9 | 5,000 | `fire-giant.md` |
| Behir | 11 | 7,200 | `behir.md` |
| Roc | 11 | 7,200 | `roc.md` |
| Adult White Dragon | 13 | 10,000 | `adult-white-dragon.md` |
