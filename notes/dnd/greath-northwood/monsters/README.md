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
| Kobold | 1/8 | 25 | `kobold.md` |
| Boar | 1/4 | 50 | `boar.md` |
| Giant Owl | 1/4 | 50 | `giant-owl.md` |
| Wolf | 1/4 | 50 | `wolf.md` |
| Black Bear | 1/2 | 100 | `black-bear.md` |
| Scout | 1/2 | 100 | `scout.md` |
| Worg | 1/2 | 100 | `worg.md` |
| Brown Bear | 1 | 200 | `brown-bear.md` |
| Dire Wolf | 1 | 200 | `dire-wolf.md` |
| Dryad | 1 | 200 | `dryad.md` |
| Giant Eagle | 1 | 200 | `giant-eagle.md` |
| Giant Spider | 1 | 200 | `giant-spider.md` |
| Harpy | 1 | 200 | `harpy.md` |
| Ankheg | 2 | 450 | `ankheg.md` |
| Bandit Captain | 2 | 450 | `bandit-captain.md` |
| Berserker | 2 | 450 | `berserker.md` |
| Gargoyle | 2 | 450 | `gargoyle.md` |
| Giant Elk | 2 | 450 | `giant-elk.md` |
| Ogre | 2 | 450 | `ogre.md` |
| Polar Bear | 2 | 450 | `polar-bear.md` |
| Swarm of Poisonous Snakes | 2 | 450 | `swarm-of-poisonous-snakes.md` |
| Will-o'-Wisp | 2 | 450 | `will-o-wisp.md` |
| Displacer Beast | 3 | 700 | `displacer-beast.md` |
| Manticore | 3 | 700 | `manticore.md` |
| Owlbear | 3 | 700 | `owlbear.md` |
| Veteran | 3 | 700 | `veteran.md` |
| Winter Wolf | 3 | 700 | `winter-wolf.md` |
| Yeti | 3 | 700 | `yeti.md` |
| Ettin | 4 | 1,100 | `ettin.md` |
| Bulette | 5 | 1,800 | `bulette.md` |
| Hill Giant | 5 | 1,800 | `hill-giant.md` |
| Troll | 5 | 1,800 | `troll.md` |
| Werebear | 5 | 1,800 | `werebear.md` |
| Chimera | 6 | 2,300 | `chimera.md` |
| Mammoth | 6 | 2,300 | `mammoth.md` |
| Wyvern | 6 | 2,300 | `wyvern.md` |
| Giant Ape | 7 | 2,900 | `giant-ape.md` |
| Stone Giant | 7 | 2,900 | `stone-giant.md` |
| Frost Giant | 8 | 3,900 | `frost-giant.md` |
| Young Green Dragon | 8 | 3,900 | `young-green-dragon.md` |
| Abominable Yeti | 9 | 5,000 | `abominable-yeti.md` |
| Fire Giant | 9 | 5,000 | `fire-giant.md` |
| Treant | 9 | 5,000 | `treant.md` |
| Behir | 11 | 7,200 | `behir.md` |
| Roc | 11 | 7,200 | `roc.md` |
| Adult White Dragon | 13 | 10,000 | `adult-white-dragon.md` |
