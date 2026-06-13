Great Northwood — Encounters
============================

Wilderness travel encounters for the Great Northwood. The party rolls a **d20**
on each travel beat; results **1–10** are encounters (this file). Results
**11–20** are handled in `loot-and-discoveries.md`.

Each encounter may be a **monster** fight or an **environmental** obstacle —
both are mixed into every difficulty band below. Stat blocks live in `monsters/`,
environmental challenges in `environments/`, and `tools/encounter.py` can roll
up either kind (see its `--filter` and `--difficulty` options).

> **Scaling:** Tuned for a **party of 4 at 6th level**. The bands map to the
> 2024 (5.5e) difficulty tiers the tool uses:
> Minor = Low · Medium = Moderate · Dangerous = High · Nat 1 = beyond High.

| d20 | Band | 2024 difficulty |
| --- | --- | --- |
| Nat 1 | **Deadly special** (can drop PCs / TPK) | beyond High |
| 2-3 | Dangerous | High |
| 4-6 | Medium | Moderate |
| 7-10 | Minor | Low |

---

## Natural 1 — Deadly Encounter (special)

A natural 1 on the travel die is the worst-case roll: the party stumbles onto an
apex threat or a catastrophe far beyond a fair fight. These are **meant to be
deadly** — capable of dropping a couple of characters, and a TPK if the party is
reckless or very unlucky.

**DM guidance:** Telegraph these (tracks, carcasses, distant rumbling, ruined
terrain) and always leave an out — fleeing, hiding, parley, or sacrificing loot
should be viable. The threat is the point; a stand-up fight should feel like a mistake.

Roll d8:

1. **Adult White Dragon** on the hunt (CR 13) — claims the whole valley.
2. **Fire Giant** raid party: 1 Fire Giant (CR 9) + 2 Ogres (CR 2).
3. **Roc** (CR 11) — snatches a PC or mount and tries to carry it off.
4. **Behir** (CR 11) — drops from a cliff cave, lightning breath down a line.
5. **Young Green Dragon + brood** (CR 8 + 2 Ankhegs) defending a lair.
6. **Troll warband**: 4 Trolls (CR 5 each) — regeneration turns it into a grind.
7. *(Environment)* **Avalanche** — a wall of snow and rock buries the trail (high severity).
8. *(Environment)* **Glacial flash flood** — an ice dam bursts and floods the ravine (high severity).

---

## 2-3 Dangerous Encounter

Challenging beats, balanced toward **High** difficulty. Roll d10:

1. **Young Green Dragon** hunting the area (CR 8) — poison breath, hit-and-run flight.
2. **Bulette** erupts from beneath the party (1–2 × CR 5) — use 2 for a deadly spike.
3. **Chimera** defending a kill (1–2 × CR 6) — fire breath + flight.
4. **Stone Giant** in its hunting grounds (CR 7) — boulders at range, prone on hit.
5. **Manticore** flight stalking from above (3 × CR 3) — tail-spike volleys.
6. **Troll(s)** emerging from a cave (2 × CR 5) — fire/acid to stop regeneration.
7. **Wyvern(s)** nesting nearby (1–2 × CR 6) — poison stinger, swooping attacks.
8. **Displacer beast** ambush (3 × CR 3) — displacement makes them hard to hit.
9. *(Environment)* **Rockslide** on a steep pass (high severity) — falling stone, then a blocked route.
10. *(Environment)* **Crumbling rope bridge** over a deep ravine (collapse risks a long fall).

---

## 4-6 Medium Encounter

Mid-weight beats, balanced toward **Moderate** difficulty. Roll d10:

1. **Dire wolves** — 2d4 Dire Wolves (CR 1) hunting as a pack with Pack Tactics.
2. **Giant spiders** — 4 Giant Spiders (CR 1) in a webbed ravine (restraining terrain).
3. **Harpies** — 4 Harpies (CR 1) on a cliffside, leading with Luring Song.
4. **Ankhegs** — 2–3 Ankhegs (CR 2) in a burrow field, acid spray + grapple.
5. **Bandit scouts** — 1 Bandit Captain (CR 2) + 4 Scouts (CR 1/2), ranged ambush.
6. **Venomous swarm** — 2 Swarms of Poisonous Snakes (CR 2) in undergrowth.
7. **Territorial beast** — 1 Owlbear (CR 3) defending its range (or a mated pair for a harder fight).
8. **Minor elemental** — 2 Gargoyles (CR 2) animated by an elemental disturbance.
9. *(Environment)* **Fast-flowing river crossing** (moderate severity) — strong current, cold water.
10. *(Environment)* **Quicksand field** or a **deep crevasse** barring the way (moderate severity).

---

## 7-10 Minor Encounter

Light beats, balanced toward **Low** difficulty — often an obstacle rather than a
fight. Roll d8:

1. *(Environment)* **Dense thorn maze** (low severity) — navigate or get snagged and lost.
2. *(Environment)* **Disorienting fog** (low severity) — risk losing a day's travel.
3. *(Environment)* **Steep cliff** to climb (low severity).
4. *(Environment)* **Ancient puzzle gate** (low severity) — a sealed way that yields to wit.
5. **Wolves** — 1d4 Wolves (CR 1/4) trailing and testing the party.
6. **Lone dire wolf** (CR 1) — a solitary hunter, wary and hungry.
7. **Lone scout** (CR 1/2) — a lost hunter or a bandit lookout who may talk or flee.
8. **Giant spider** (CR 1) — a single ambusher in an old web across the trail.

---

Environmental obstacles may be resolved as skill challenges; see each file in
`environments/` for its DC, consequences, and suggested checks. Success on any
encounter may grant advantage on the next travel check, inspiration, or reveal a
shortcut.
