Great Northwood — Environmental Challenges
==========================================

One file per environmental obstacle (hazards, terrain, puzzles), flat. Each file
begins with a YAML frontmatter block so the encounter tool can read it without
parsing prose, followed by a description and a resolution.

These are selected by `../tools/encounter.py` when `--filter` is `environmental`
or `both`: a hazard is offered when its `severity` matches the chosen
`--difficulty` (both use the same low/moderate/high vocabulary). Hazards are
never mixed into a monster encounter — they are presented as their own section.

## Frontmatter schema

```
---
name: Rockslide          # display name
kind: environmental      # constant marker
severity: high           # low | moderate | high  (maps to --difficulty)
dc: 16                   # primary save/check DC
damage: 4d6 bludgeoning  # or "none"
check: Dexterity saving throw (Athletics/Acrobatics to scramble clear)
summary: A sudden cascade of stone down a steep pass.
---
```

## Roster (by severity)

| Challenge | Severity | DC | File |
| --- | --- | --- | --- |
| Dense Thorn Maze | low | 13 | `thorn-maze.md` |
| Disorienting Fog | low | 13 | `disorienting-fog.md` |
| Steep Cliff | low | 13 | `steep-cliff.md` |
| Ancient Puzzle Gate | low | 13 | `ancient-puzzle-gate.md` |
| Tangled Deadfall | low | 12 | `tangled-deadfall.md` |
| Whining Midge Bog | low | 12 | `whining-midge-bog.md` |
| Icy Stepping-Stones | low | 13 | `icy-stepping-stones.md` |
| Weathered Boundary Stones | low | 13 | `weathered-boundary-stones.md` |
| Fast-Flowing River Crossing | moderate | 14 | `river-crossing.md` |
| Quicksand Field | moderate | 13 | `quicksand.md` |
| Crumbling Rope Bridge | moderate | 15 | `crumbling-rope-bridge.md` |
| Deep Crevasse | moderate | 14 | `deep-crevasse.md` |
| Snowdrift Field | moderate | 14 | `snowdrift-field.md` |
| Thin Ice Lake Crossing | moderate | 14 | `thin-ice-lake.md` |
| Bramble-Choked Ravine | moderate | 14 | `bramble-choked-ravine.md` |
| Freezing Sleet Storm | moderate | 14 | `freezing-sleet-storm.md` |
| Rockslide | high | 16 | `rockslide.md` |
| Glacial Flash Flood | high | 16 | `glacial-flash-flood.md` |
| Avalanche | high | 17 | `avalanche.md` |
| Whiteout Blizzard | high | 16 | `whiteout-blizzard.md` |
| Scalding Geyser Field | high | 16 | `scalding-geyser-field.md` |
| Collapsing Ice Cavern | high | 16 | `collapsing-ice-cavern.md` |
