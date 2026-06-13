Great Northwood — Locations
===========================

Discoverable sites — faction ruins (and a couple of rare living Valvela camps)
that can turn up alongside a loot result, or serve as the setting of an
encounter. One file per location, each with YAML frontmatter followed by the
themed description, so `../tools/loot.py`, `../tools/encounter.py`, and the web
app can read them while they stay easy to hand-edit.

The factions themselves are described in `../factions.md`; these are the marks
they left on the Northwood.

## How locations fit the loot roll

When a travel loot roll (d20 **11-20**) produces a result, the tool then rolls
to see whether the find was made **inside a location**. The higher the value of
the loot, the more likely it came from a site, and the grander that site tends
to be:

| Travel d20 | Loot category | Location chance | Site tier |
| --- | --- | --- | --- |
| 11-13 | Nothing Found | 0% (never) | — |
| 14-16 | Mundane Treasure | ~25% | `modest` |
| 17-19 | Magic Treasure | ~60% | `notable` |
| 20 | Wondrous Discovery | 100% (always) | `grand` |

If the roll calls for a location, the tool picks one **uniformly at random from
the sites whose `tier` matches** (falling back to any tier if that pool is
empty). The faction is incidental flavour. On a natural 20 the wondrous
guardian then reads naturally as the guardian *of* the grand location.

The chances live in `LOCATION_CHANCE` and the tier mapping in `CATEGORY_TIER`,
both in `../tools/loot.py`.

## How locations fit encounters

Encounters (the d20 **1-10** half) use the same idea: the more dangerous the
encounter, the more likely it takes place at a location, and the grander that
site. Here the scaling key is the encounter's difficulty (a natural-1 "deadly
special" being its own top step):

| Encounter | Severity | Location chance | Site tier |
| --- | --- | --- | --- |
| Minor (roll 7-10) | low | ~25% | `modest` |
| Medium (roll 4-6) | moderate | ~50% | `notable` |
| Dangerous (roll 2-3) | high | ~75% | `grand` |
| Deadly special (roll 1) | deadly | 100% | `grand` |

The monsters then read as guarding (or lurking at) the site, and any
environmental challenge as part of it. These live in
`ENCOUNTER_LOCATION_CHANCE` / `ENCOUNTER_LOCATION_TIER` and
`roll_encounter_location()` in `../tools/encounter.py`.

## Frontmatter schema

```
---
name: The Oathbroken Bastion   # display name
faction: kutur                 # kutur | savol | valvela | hollow-ledger
type: ruin                     # ruin | camp
tier: notable                  # modest | notable | grand  (maps to loot category)
status: ruined                 # ruined | inhabited  (inhabited = the rare Valvela camps)
summary: One-line hook.
purpose: Why the place was built / why it exists.
---
```

The body holds a themed **Description**, the site's **Purpose**, and a short
**Now** paragraph on its present (ruined or inhabited) state.

## Tiers

- **modest** — small caches, posts, and minor ruins. Mundane finds.
- **notable** — significant ruins: halls, vaults, forges, dens. Magic finds.
- **grand** — marquee sites: citadels, sepulchres, power-vaults. Wondrous finds.

## Roster (40 — 10 per faction)

### ⚔️ Kutur (chivalric, anti-magic kingdom)

| Location | Tier | File |
| --- | --- | --- |
| Wayfarer's Oathpost | modest | `kutur-wayfarers-oathpost.md` |
| The Pale Picket | modest | `kutur-pale-picket.md` |
| Greycloak Barrow | modest | `kutur-greycloak-barrow.md` |
| Stable of the White Mare | modest | `kutur-stable-white-mare.md` |
| The Oathbroken Bastion | notable | `kutur-oathbroken-bastion.md` |
| Hall of the Iron Crown | notable | `kutur-hall-iron-crown.md` |
| The Wardstone Chapter | notable | `kutur-wardstone-chapter.md` |
| Tomb of the Hundred Lances | notable | `kutur-tomb-hundred-lances.md` |
| The Cataphract Citadel | grand | `kutur-cataphract-citadel.md` |
| The White Horse Sepulcher | grand | `kutur-white-horse-sepulcher.md` |

### 💰 Savol (merchant republic)

| Location | Tier | File |
| --- | --- | --- |
| The Brokenscale Tollhouse | modest | `savol-brokenscale-tollhouse.md` |
| Caravan Rest of the Green Mile | modest | `savol-green-mile-rest.md` |
| The Sunken Weighhouse | modest | `savol-sunken-weighhouse.md` |
| Pedlar's Hollow Cache | modest | `savol-pedlars-hollow-cache.md` |
| The Balance Exchange | notable | `savol-balance-exchange.md` |
| Coinbridge | notable | `savol-coinbridge.md` |
| The Amber Caravanserai | notable | `savol-amber-caravanserai.md` |
| Vault of Interlocking Routes | notable | `savol-vault-interlocking-routes.md` |
| The Grand Counting-House | grand | `savol-grand-counting-house.md` |
| The Drowned Bourse | grand | `savol-drowned-bourse.md` |

### 🔮 Valvela (arcane-progress civilisation; 8 ruins + 2 rare living camps)

| Location | Tier | Status | File |
| --- | --- | --- | --- |
| The Flickering Waystation | modest | ruined | `valvela-flickering-waystation.md` |
| Sigil-Scribe's Outpost | modest | ruined | `valvela-sigil-scribes-outpost.md` |
| The Dead Conduit | modest | ruined | `valvela-dead-conduit.md` |
| The Glassburn Field Lab | modest | ruined | `valvela-glassburn-field-lab.md` |
| Academy Annex of Refracted Light | notable | ruined | `valvela-refracted-light-annex.md` |
| The Shattered Lattice Spire | notable | ruined | `valvela-shattered-lattice-spire.md` |
| Forge of Spell-Forged Steel | notable | ruined | `valvela-spellforge.md` |
| Hearthlight Camp | notable | inhabited | `valvela-hearthlight-camp.md` |
| The Crystal Engine Vault | grand | ruined | `valvela-crystal-engine-vault.md` |
| The Last Sanctum of Mevarre | grand | inhabited | `valvela-last-sanctum-mevarre.md` |

### 🕯️ The Hollow Ledger (information brokers)

| Location | Tier | File |
| --- | --- | --- |
| The Erased Dead-Drop | modest | `hollow-erased-dead-drop.md` |
| Pawnbroker's Backroom | modest | `hollow-pawnbrokers-backroom.md` |
| The Inkwell Stash | modest | `hollow-inkwell-stash.md` |
| Cardsharp's Hideaway | modest | `hollow-cardsharps-hideaway.md` |
| The Hollow Counting-Front | notable | `hollow-counting-front.md` |
| The Masked Gambling Hall | notable | `hollow-masked-gambling-hall.md` |
| Archive of Dissolving Ink | notable | `hollow-dissolving-ink-archive.md` |
| The Debtor's Pit | notable | `hollow-debtors-pit.md` |
| The Sealed Ledger Vault | grand | `hollow-sealed-ledger-vault.md` |
| The Blank-Face Sanctum | grand | `hollow-blankface-sanctum.md` |

## Editing

- Add, remove, or reword files freely — the tool re-reads them each run.
- The `slug` is the filename without `.md`; keep it lowercase and hyphenated.
- Keep `faction`, `type`, `tier`, and `status` in sync with the roster above.
- To retune discovery odds or the tier mapping, edit `LOCATION_CHANCE` and
  `CATEGORY_TIER` in `../tools/loot.py`.
