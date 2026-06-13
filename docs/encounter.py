#!/usr/bin/env python3
"""Great Northwood Encounter Tool (D&D 2024 / 5.5e).

Computes 2024 Dungeon Master's Guide encounter XP budgets for a party and finds
encounters built from the monster stat-block files in the sibling ``monsters/``
folder. Pure standard library, no third-party dependencies.

See ``encounter.py --help`` for usage and the difficulty-band descriptions.
"""

from __future__ import annotations

import argparse
import os
import random
import sys
from dataclasses import dataclass

# 2024 DMG "XP Budget per Character" table: level -> (low, moderate, high).
# Budget = sum of each character's per-level value for the chosen difficulty.
# The 2024 rules have NO monster-count multiplier: monster XP is summed directly.
XP_BUDGET_PER_CHARACTER = {
    1: (50, 75, 100),
    2: (100, 150, 200),
    3: (150, 225, 400),
    4: (250, 375, 500),
    5: (500, 750, 1100),
    6: (600, 1000, 1400),
    7: (750, 1300, 1700),
    8: (1000, 1700, 2100),
    9: (1300, 2000, 2600),
    10: (1600, 2300, 3100),
    11: (1900, 2900, 4100),
    12: (2200, 3700, 4700),
    13: (2600, 4200, 5400),
    14: (2900, 4900, 6200),
    15: (3300, 5400, 7800),
    16: (3800, 6100, 9800),
    17: (4500, 7200, 11700),
    18: (5000, 8700, 14200),
    19: (5500, 10700, 17200),
    20: (6400, 13200, 22000),
}

DIFFICULTIES = ("low", "moderate", "high")
DIFFICULTY_INDEX = {"low": 0, "moderate": 1, "high": 2}

DIFFICULTY_DESCRIPTIONS = {
    "low": (
        "A warm-up. The party should win without spending many resources, "
        "though a careless or unlucky character can still get hurt."
    ),
    "moderate": (
        "A real fight. Expect the party to spend resources (spell slots, hit "
        "points, abilities). It can turn lethal if they are already depleted."
    ),
    "high": (
        "A tough, potentially deadly fight. Even a fresh party risks one or "
        "more deaths with poor tactics or bad luck."
    ),
}


@dataclass
class Monster:
    name: str
    cr: str
    xp: int
    size: str
    type: str
    summary: str
    slug: str


@dataclass
class Hazard:
    name: str
    severity: str
    dc: str
    damage: str
    check: str
    summary: str
    slug: str


# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #
def parse_frontmatter(text):
    """Parse a minimal flat ``key: value`` YAML frontmatter block.

    Only the simple form delimited by ``---`` lines is supported, which is all
    the monster files use. Returns a dict of string keys to string values.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        data[key] = value
    return data


def default_monsters_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "monsters"))


def default_environments_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "environments"))


def load_monsters(monsters_dir):
    if not os.path.isdir(monsters_dir):
        sys.exit(f"error: monsters directory not found: {monsters_dir}")
    monsters = []
    for entry in sorted(os.listdir(monsters_dir)):
        if not entry.endswith(".md") or entry.lower() == "readme.md":
            continue
        with open(os.path.join(monsters_dir, entry), encoding="utf-8") as fh:
            fm = parse_frontmatter(fh.read())
        if "name" not in fm or "xp" not in fm:
            continue
        try:
            xp = int(fm["xp"])
        except ValueError:
            continue
        monsters.append(
            Monster(
                name=fm.get("name", entry[:-3]),
                cr=fm.get("cr", "?"),
                xp=xp,
                size=fm.get("size", ""),
                type=fm.get("type", ""),
                summary=fm.get("summary", ""),
                slug=entry[:-3],
            )
        )
    if not monsters:
        sys.exit(f"error: no parseable monster files found in {monsters_dir}")
    return monsters


def load_environments(environments_dir):
    if not os.path.isdir(environments_dir):
        sys.exit(f"error: environments directory not found: {environments_dir}")
    hazards = []
    for entry in sorted(os.listdir(environments_dir)):
        if not entry.endswith(".md") or entry.lower() == "readme.md":
            continue
        with open(os.path.join(environments_dir, entry), encoding="utf-8") as fh:
            fm = parse_frontmatter(fh.read())
        if "name" not in fm or "severity" not in fm:
            continue
        hazards.append(
            Hazard(
                name=fm.get("name", entry[:-3]),
                severity=fm.get("severity", "").lower(),
                dc=fm.get("dc", "?"),
                damage=fm.get("damage", ""),
                check=fm.get("check", ""),
                summary=fm.get("summary", ""),
                slug=entry[:-3],
            )
        )
    if not hazards:
        sys.exit(f"error: no parseable environment files found in {environments_dir}")
    return hazards


# --------------------------------------------------------------------------- #
# Budget math
# --------------------------------------------------------------------------- #
def resolve_levels(args):
    if args.levels:
        try:
            levels = [int(x) for x in args.levels.split(",") if x.strip()]
        except ValueError:
            sys.exit("error: --levels must be comma-separated integers, e.g. 4,6,6,7")
    elif args.party_size is not None and args.level is not None:
        levels = [args.level] * args.party_size
    else:
        sys.exit("error: provide either --levels, or both --party-size and --level")
    if not levels:
        sys.exit("error: party is empty")
    for lv in levels:
        if not 1 <= lv <= 20:
            sys.exit(f"error: character level out of range (1-20): {lv}")
    return levels


def budget_for(levels, difficulty):
    idx = DIFFICULTY_INDEX[difficulty]
    return sum(XP_BUDGET_PER_CHARACTER[lv][idx] for lv in levels)


# Travel d20 results 1-10 are encounters (11-20 are loot; see loot.py). Each
# band maps to a 2024 difficulty; a natural 1 is a "deadly special" that pushes
# the budget above High.
ENCOUNTER_ROLL_MIN = 1
ENCOUNTER_ROLL_MAX = 10
DEADLY_BUDGET_MULTIPLIER = 1.75

# (low, high, label, difficulty, deadly)
TRAVEL_BANDS = (
    (1, 1, "Deadly special", "high", True),
    (2, 3, "Dangerous", "high", False),
    (4, 6, "Medium", "moderate", False),
    (7, 10, "Minor", "low", False),
)


def band_for_roll(roll):
    """Map a travel d20 result (1-10) to its encounter band, or ``None``."""
    for lo, hi, label, difficulty, deadly in TRAVEL_BANDS:
        if lo <= roll <= hi:
            return {"label": label, "difficulty": difficulty, "deadly": deadly}
    return None


def budget_for_band(levels, band):
    """XP budget for a travel band, inflating a natural-1 'deadly special'."""
    budget = budget_for(levels, band["difficulty"])
    if band.get("deadly"):
        budget = int(round(budget * DEADLY_BUDGET_MULTIPLIER))
    return budget


# --------------------------------------------------------------------------- #
# Locations (faction ruins / camps an encounter takes place at)
# --------------------------------------------------------------------------- #
# How likely an encounter happens at a faction location, by severity. Mirrors
# the loot location curve (see loot.py): the more dangerous the encounter, the
# more likely it guards (or lurks at) a place, and the grander that place. A
# natural-1 "deadly special" always has a grand setting.
ENCOUNTER_LOCATION_CHANCE = {
    "low": 0.25,
    "moderate": 0.50,
    "high": 0.75,
    "deadly": 1.0,
}

# Which location value tier each encounter severity pulls from.
ENCOUNTER_LOCATION_TIER = {
    "low": "modest",
    "moderate": "notable",
    "high": "grand",
    "deadly": "grand",
}


def encounter_severity(difficulty, deadly=False):
    """The location-scaling key for an encounter: its difficulty, or 'deadly'."""
    return "deadly" if deadly else difficulty


def _loot_module():
    """Import the sibling ``loot.py`` tool (lazy) for its location data."""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    import loot  # noqa: E402  (sibling tool in the same folder)
    return loot


def roll_encounter_location(severity, rng, locations=None):
    """Maybe pick a location the encounter takes place at, scaled to severity.

    The chance scales with the encounter severity (``ENCOUNTER_LOCATION_CHANCE``);
    on a hit the site is drawn uniformly from the matching tier
    (``ENCOUNTER_LOCATION_TIER``), falling back to any tier if that pool is
    empty. Returns a ``loot.Location`` or ``None``.
    """
    chance = ENCOUNTER_LOCATION_CHANCE.get(severity, 0.0)
    if locations is None:
        lt = _loot_module()
        locations = lt.load_locations(lt.default_locations_dir())
    if not locations or rng.random() >= chance:
        return None
    tier = ENCOUNTER_LOCATION_TIER.get(severity)
    pool = [loc for loc in locations if loc.tier == tier] or list(locations)
    return rng.choice(pool)


# --------------------------------------------------------------------------- #
# Encounter search
# --------------------------------------------------------------------------- #
def find_mix(monsters, budget, count, max_types, min_fill, limit):
    """Find encounters of exactly ``count`` monsters, at most ``max_types``
    distinct kinds, whose total XP lands in ``[min_fill*budget, budget]``."""
    ms = sorted(monsters, key=lambda m: m.xp)
    n = len(ms)
    max_xp = ms[-1].xp
    min_total = min_fill * budget
    results = []

    def dfs(i, slots_left, budget_left, types_left, chosen, total):
        if slots_left == 0:
            if total >= min_total:
                results.append((total, tuple(chosen)))
            return
        if i >= n or types_left == 0:
            return
        # Prune (high): cheapest remaining can't even fill the open slots.
        if ms[i].xp * slots_left > budget_left:
            return
        # Prune (low): most expensive possible fill can't reach the minimum.
        if total + max_xp * slots_left < min_total:
            return
        m = ms[i]
        max_k = slots_left
        if m.xp > 0:
            max_k = min(max_k, budget_left // m.xp)
        for k in range(1, max_k + 1):
            chosen.append((m, k))
            dfs(i + 1, slots_left - k, budget_left - k * m.xp,
                types_left - 1, chosen, total + k * m.xp)
            chosen.pop()
        # Skip this monster entirely.
        dfs(i + 1, slots_left, budget_left, types_left, chosen, total)

    dfs(0, count, budget, max_types, [], 0)
    results.sort(key=lambda r: r[0], reverse=True)
    return results[:limit]


def find_boss_minions(monsters, budget, count, min_fill, boss_min, boss_max, limit):
    """One boss (XP within ``[boss_min, boss_max] * budget``) plus ``count-1``
    identical minions of the most expensive type that still fits the budget."""
    if count < 2:
        sys.exit("error: boss-minions mode needs --count of at least 2 (boss + 1 minion)")
    min_total = min_fill * budget
    minion_slots = count - 1
    boss_lo, boss_hi = boss_min * budget, boss_max * budget
    by_xp_desc = sorted(monsters, key=lambda m: m.xp, reverse=True)
    results = []
    for boss in monsters:
        if not boss_lo <= boss.xp <= boss_hi:
            continue
        remaining = budget - boss.xp
        if remaining <= 0:
            continue
        for minion in by_xp_desc:
            if minion.slug == boss.slug or minion.xp <= 0:
                continue
            if minion.xp * minion_slots <= remaining:
                total = boss.xp + minion.xp * minion_slots
                if total >= min_total:
                    results.append((total, ((boss, 1), (minion, minion_slots))))
                break  # most expensive minion that fits; cheaper ones only score lower
    results.sort(key=lambda r: r[0], reverse=True)
    return results[:limit]


def select_environments(hazards, difficulty, limit):
    """Environmental challenges whose severity matches the chosen difficulty.

    Severity uses the same low/moderate/high vocabulary as difficulty, so the
    selected --difficulty maps straight onto hazard severity.
    """
    matches = [h for h in hazards if h.severity == difficulty]
    matches.sort(key=lambda h: h.name)
    return matches[:limit]


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #
def print_header(difficulty, levels, band=None, roll=None):
    if band is not None:
        deadly = " x deadly" if band["deadly"] else ""
        print(f"Travel roll: {roll}  ->  {band['label']} ({difficulty.upper()}{deadly})")
    else:
        print(f"Selected difficulty: {difficulty.upper()}")
    if levels is not None:
        budgets = {d: budget_for(levels, d) for d in DIFFICULTIES}
        levels_desc = ", ".join(str(lv) for lv in levels)
        print(f"Party: {len(levels)} character(s) (levels {levels_desc})")
        print(
            "Difficulty budgets (2024):  "
            f"Low {budgets['low']:,} | Moderate {budgets['moderate']:,} | High {budgets['high']:,}"
        )


def print_location_section(location):
    print("\n=== ENCOUNTER SITE ===")
    living = " - inhabited" if location.status == "inhabited" else ""
    print(f"  {location.name} ({location.faction}, {location.tier} site{living})")
    if location.summary:
        print(f"       {location.summary}")


def print_monster_section(args, results, budget):
    print("\n=== MONSTER ENCOUNTERS ===")
    print(f"Budget: {budget:,} XP  (no monster-count multiplier in 2024)")
    if args.mode == "mix":
        print(
            f"Mode: mix (exactly {args.count} monster(s), up to {args.max_types} "
            f"distinct kind(s), filling {int(args.min_fill * 100)}-100% of budget)"
        )
    else:
        print(
            f"Mode: boss + minions (1 boss at {int(args.boss_min * 100)}-"
            f"{int(args.boss_max * 100)}% of budget + {args.count - 1} minion(s), "
            f"filling {int(args.min_fill * 100)}-100% of budget)"
        )

    if not results:
        print("\nNo monster encounters matched. Try a different --count, --difficulty,")
        print("a lower --min-fill, or (mix mode) a higher --max-types.")
        return

    print(f"\nFound {len(results)} encounter(s):\n")
    for total, parts in results:
        pieces = " + ".join(f"{qty}x {m.name}" for m, qty in parts)
        pct = round(100 * total / budget) if budget else 0
        print(f"  {pieces} - {total:,} XP ({pct}% of budget)")
        name_w = max(len(m.name) for m, _ in parts)
        cr_w = max(len(str(m.cr)) for m, _ in parts)
        for m, _ in parts:
            print(
                f"       {m.name:<{name_w}}  CR {str(m.cr):<{cr_w}}  "
                f"{m.xp:>6,} XP  - {m.summary}"
            )
        print()


def print_environment_section(difficulty, hazards):
    print("\n=== ENVIRONMENTAL CHALLENGES ===")
    print(f"Severity: {difficulty} (matches selected difficulty)")

    if not hazards:
        print(f"\nNo environmental challenges with '{difficulty}' severity were found.")
        return

    print(f"\nFound {len(hazards)} challenge(s):\n")
    name_w = max(len(h.name) for h in hazards)
    for h in hazards:
        dc = f"DC {h.dc}" if h.dc else ""
        print(f"  {h.name:<{name_w}}  {dc}  - {h.summary}")
        detail = h.check or ""
        if h.damage and h.damage.lower() != "none":
            detail = f"{detail}; damage {h.damage}" if detail else f"damage {h.damage}"
        if detail:
            print(f"       {' ' * name_w}  {detail}")
        print()


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser():
    epilog = f"""\
how it works
------------
This tool uses the 2024 (5.5e) Dungeon Master's Guide encounter model:

  1. Each character has an XP budget based on their level and the target
     difficulty (Low, Moderate, High).
  2. The party budget is the sum of every character's budget.
  3. Monsters are chosen so their XP values sum to AT or UNDER that budget.
     There is NO monster-count multiplier in 2024 - you just add up monster XP.
     (2024 advises rounding difficulty UP when you land between two bands.)

travel roll (1-10)
------------------
Instead of naming a difficulty, pass the players' travel d20 with --roll. The
encounter half of the table (1-10) maps to a band:

  1      Deadly special (High budget x{DEADLY_BUDGET_MULTIPLIER:g}, can drop PCs / TPK)
  2-3    Dangerous       (High)
  4-6    Medium          (Moderate)
  7-10   Minor           (Low)

Rolls 11-20 are loot - use loot.py instead.

encounter location
------------------
The more dangerous the encounter, the more likely it takes place at a faction
location (a ruin, or one of Valvela's rare camps), and the grander that site:
25% Low (modest), 50% Moderate (notable), 75% High (grand), 100% deadly special
(grand). Sites live in ../locations/; pass --seed for a reproducible pick.

difficulty levels
-----------------
  low       {DIFFICULTY_DESCRIPTIONS['low']}
  moderate  {DIFFICULTY_DESCRIPTIONS['moderate']}
  high      {DIFFICULTY_DESCRIPTIONS['high']}

filter (encounter kind)
-----------------------
  monster        Only monster encounters (XP-budget based; needs --count).
  environmental  Only environmental challenges, chosen by matching the
                 selected --difficulty to each hazard's severity.
  both           Both of the above as separate sections (default).
  Monsters and environmental challenges are never mixed into one encounter.

modes (monster encounters only)
-------------------------------
  mix           Encounters of exactly --count monsters: N of the same kind, or
                a mix of up to --max-types different kinds.
  boss-minions  One tougher "boss" plus --count-1 identical weaker "minions".

examples
--------
  # The party rolled a 2 (Dangerous) on travel - 3 creatures for four level-6 PCs
  encounter.py --party-size 4 --level 6 --roll 2 --count 3

  # A natural 1 deadly special, boss + 4 minions
  encounter.py --party-size 4 --level 6 --roll 1 --mode boss-minions --count 5

  # A hard fight of 3 creatures for four level-6 PCs
  encounter.py --party-size 4 --level 6 --difficulty high --count 3

  # Only high-severity environmental challenges (no party needed)
  encounter.py --difficulty high --filter environmental

  # Both kinds: a moderate 5-monster fight plus moderate hazards
  encounter.py --levels 4,6,6,7 --difficulty moderate --count 5

  # A boss with 5 minions, monsters only
  encounter.py --party-size 4 --level 6 --difficulty high --filter monster --mode boss-minions --count 6
"""
    parser = argparse.ArgumentParser(
        prog="encounter.py",
        description="Compute 2024 (5.5e) encounter XP budgets and find matching "
                    "encounters from the Great Northwood monster files.",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    party = parser.add_argument_group("party (use --levels, OR --party-size with --level)")
    party.add_argument("--party-size", type=int, help="number of characters (uniform level)")
    party.add_argument("--level", type=int, help="level shared by all characters")
    party.add_argument("--levels", help="comma-separated per-character levels, e.g. 4,6,6,7")

    parser.add_argument("--roll", type=int, default=None,
                        help="the players' travel d20 result (1-10); picks the "
                             "difficulty band (11-20 is loot, see loot.py)")
    parser.add_argument("--difficulty", choices=DIFFICULTIES, default=None,
                        help="target encounter difficulty (omit if using --roll)")
    parser.add_argument("--filter", choices=("monster", "environmental", "both"),
                        default="both",
                        help="which encounter kinds to show (default: both)")
    parser.add_argument("--count", type=int, default=None,
                        help="exact number of monsters in the fight (required for "
                             "monster/both filters)")
    parser.add_argument("--mode", choices=("mix", "boss-minions"), default="mix",
                        help="monster encounter style (default: mix)")

    knobs = parser.add_argument_group("tuning")
    knobs.add_argument("--max-types", type=int, default=3,
                       help="max distinct monster kinds in a mix (default: 3)")
    knobs.add_argument("--min-fill", type=float, default=0.75,
                       help="minimum fraction of budget to use, 0-1 (default: 0.75)")
    knobs.add_argument("--limit", type=int, default=15,
                       help="max encounters to show (default: 15)")
    knobs.add_argument("--boss-min", type=float, default=0.4,
                       help="boss min share of budget, boss-minions mode (default: 0.4)")
    knobs.add_argument("--boss-max", type=float, default=0.7,
                       help="boss max share of budget, boss-minions mode (default: 0.7)")
    knobs.add_argument("--monsters-dir", default=None,
                       help="path to the monsters folder (default: sibling ../monsters)")
    knobs.add_argument("--environments-dir", default=None,
                       help="path to the environments folder (default: sibling ../environments)")
    knobs.add_argument("--locations-dir", default=None,
                       help="path to the locations folder (default: sibling ../locations)")
    knobs.add_argument("--seed", type=int, default=None,
                       help="optional RNG seed for a reproducible encounter location")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    want_monsters = args.filter in ("monster", "both")
    want_environment = args.filter in ("environmental", "both")

    if args.max_types < 1:
        sys.exit("error: --max-types must be at least 1")
    if not 0 < args.min_fill <= 1:
        sys.exit("error: --min-fill must be between 0 (exclusive) and 1 (inclusive)")

    # Resolve the difficulty band, optionally from a travel d20 roll (1-10).
    band = None
    if args.roll is not None:
        if not 1 <= args.roll <= 20:
            sys.exit("error: --roll must be a d20 result (1-20)")
        if args.roll > ENCOUNTER_ROLL_MAX:
            sys.exit(f"error: a roll of {args.roll} is loot (d20 11-20), not an "
                     "encounter. See loot.py.")
        band = band_for_roll(args.roll)
        difficulty = band["difficulty"]
    elif args.difficulty:
        difficulty = args.difficulty
    else:
        sys.exit("error: provide either --roll (1-10), or --difficulty")

    levels = None
    monster_results = None
    budget = 0
    if want_monsters:
        if args.count is None:
            sys.exit("error: --count is required for monster encounters "
                     "(use --filter environmental to skip monsters)")
        if args.count < 1:
            sys.exit("error: --count must be at least 1")
        levels = resolve_levels(args)
        monsters = load_monsters(args.monsters_dir or default_monsters_dir())
        budget = budget_for_band(levels, band) if band else budget_for(levels, difficulty)
        if args.mode == "mix":
            monster_results = find_mix(monsters, budget, args.count, args.max_types,
                                       args.min_fill, args.limit)
        else:
            monster_results = find_boss_minions(monsters, budget, args.count,
                                                args.min_fill, args.boss_min,
                                                args.boss_max, args.limit)

    env_results = None
    if want_environment:
        hazards = load_environments(args.environments_dir or default_environments_dir())
        env_results = select_environments(hazards, difficulty, args.limit)

    # The encounter may take place at a faction location; chance and grandeur
    # scale with how dangerous the encounter is.
    severity = encounter_severity(difficulty, bool(band and band["deadly"]))
    lt = _loot_module()
    locations = lt.load_locations(args.locations_dir or lt.default_locations_dir())
    location = roll_encounter_location(severity, random.Random(args.seed), locations)

    print_header(difficulty, levels, band=band, roll=args.roll)
    if location is not None:
        print_location_section(location)
    if want_monsters:
        print_monster_section(args, monster_results, budget)
    if want_environment:
        print_environment_section(difficulty, env_results)


if __name__ == "__main__":
    main()
