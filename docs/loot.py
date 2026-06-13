#!/usr/bin/env python3
"""Great Northwood Loot & Discovery Tool.

Rolls a random result from one of the travel loot categories (the d20 11-20
half of the travel roll; see ``../mechanic.md``). Reads the category option
lists from the sibling ``../loot/`` folder so the data stays human-editable.

Inputs are the party size, the party level, and the discovery category. Party
level (and, slightly, party size) skews the magic-treasure rarity tier. A
wondrous discovery additionally rolls a scaled boss-tier **guardian** that
watches over the find. The higher the loot's value, the more likely it was
found inside a faction **location** (see ../locations/).

Pure standard library, no third-party dependencies. See ``loot.py --help``.
"""

from __future__ import annotations

import argparse
import os
import random
import re
import sys
from dataclasses import dataclass

# Category slug -> (display name, loot file). Mirrors the d20 11-20 ranges in
# ../mechanic.md and the per-category files in ../loot/.
CATEGORIES = {
    "nothing": ("Nothing Found", "nothing-found.md", "11-13"),
    "mundane": ("Mundane Treasure", "mundane-treasure.md", "14-16"),
    "magic": ("Magic Treasure", "magic-treasure.md", "17-19"),
    "wondrous": ("Wondrous Discovery", "wondrous-discovery.md", "20"),
}

# Magic-treasure rarity tiers as they appear under "## <Tier>" headings.
MAGIC_TIERS = ("Common", "Uncommon", "Rare")

# The loot half of the travel roll. Rolls 1-10 are encounters (../encounters.md).
LOOT_ROLL_MIN = 11
LOOT_ROLL_MAX = 20

# How likely a find was made *inside a location*, by loot category. The higher
# the value of the loot, the more likely (and the grander the site). See
# ../locations/README.md.
LOCATION_CHANCE = {
    "nothing": 0.0,
    "mundane": 0.25,
    "magic": 0.60,
    "wondrous": 1.0,
}

# Which location value tier each loot category pulls from.
CATEGORY_TIER = {
    "mundane": "modest",
    "magic": "notable",
    "wondrous": "grand",
}


def category_for_roll(roll):
    """Map a travel d20 result to its loot category slug, or ``None``."""
    for slug, (_, _, drange) in CATEGORIES.items():
        lo, _, hi = drange.partition("-")
        lo = int(lo)
        hi = int(hi) if hi else lo
        if lo <= roll <= hi:
            return slug
    return None

LIST_ITEM_RE = re.compile(r"^\s*(?:\d+[.)]|[-*])\s+(.*\S)\s*$")
HEADING_RE = re.compile(r"^\s*#{1,6}\s+(.*\S)\s*$")

# Gold amounts inside an item string: dice ("4d10 gp", "2d10 x 10 gp") or a flat
# value ("25 gp"). The dice branch is listed first so it wins over the flat one.
GOLD_RE = re.compile(
    r"(\d+)d(\d+)(?:\s*[x\u00d7*]\s*(\d+))?\s*gp\b|(\d+)\s*gp\b",
    re.IGNORECASE,
)


# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #
def default_loot_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "loot"))


def strip_frontmatter(text):
    """Drop a leading ``---`` delimited YAML block, returning the body."""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1:])
    return text


def parse_sections(text):
    """Parse a loot file body into ``{heading: [options...]}``.

    List items are collected under the most recent ``##``/``###`` heading. The
    document title (the first heading, usually an ``H1`` echoing the file name)
    is ignored as a section so its items - if any - are not double counted.
    Items that appear before any sub-heading are stored under the key ``""``.
    """
    body = strip_frontmatter(text)
    sections = {}
    current = ""
    seen_subheading = False
    for line in body.splitlines():
        heading = HEADING_RE.match(line)
        if heading:
            # Count the leading '#' run to know the heading depth.
            depth = len(line) - len(line.lstrip("#"))
            title = heading.group(1).strip()
            if depth >= 2:
                current = title
                seen_subheading = True
                sections.setdefault(current, [])
            # H1 (depth 1) is the doc title; leave ``current`` as the pre-heading bucket.
            continue
        item = LIST_ITEM_RE.match(line)
        if item:
            sections.setdefault(current, []).append(item.group(1).strip())
    return sections


def load_category(loot_dir, slug):
    name, filename, _ = CATEGORIES[slug]
    path = os.path.join(loot_dir, filename)
    if not os.path.isfile(path):
        sys.exit(f"error: loot file not found: {path}")
    with open(path, encoding="utf-8") as fh:
        return parse_sections(fh.read())


# --------------------------------------------------------------------------- #
# Party input
# --------------------------------------------------------------------------- #
def resolve_party(args):
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


# --------------------------------------------------------------------------- #
# Selection logic
# --------------------------------------------------------------------------- #
def magic_tier_weights(avg_level, party_size):
    """Relative weights for (Common, Uncommon, Rare) given the party.

    Higher average level shifts the odds toward rarer items; a larger-than-
    baseline party (4) nudges the Rare weight up a little on top of that.
    """
    if avg_level <= 4:
        common, uncommon, rare = 6.0, 3.0, 1.0
    elif avg_level <= 7:
        common, uncommon, rare = 3.0, 5.0, 2.0
    elif avg_level <= 10:
        common, uncommon, rare = 2.0, 5.0, 3.0
    elif avg_level <= 13:
        common, uncommon, rare = 1.0, 4.0, 5.0
    else:
        common, uncommon, rare = 1.0, 3.0, 6.0
    rare += max(0, party_size - 4) * 0.5
    return {"Common": common, "Uncommon": uncommon, "Rare": rare}


def pick_magic(sections, avg_level, party_size, rng):
    weights = magic_tier_weights(avg_level, party_size)
    tiers = [t for t in MAGIC_TIERS if sections.get(t)]
    if not tiers:
        sys.exit("error: magic-treasure file has no Common/Uncommon/Rare items")
    chosen_tier = rng.choices(tiers, weights=[weights[t] for t in tiers])[0]
    item = rng.choice(sections[chosen_tier])
    return chosen_tier, item


def all_items(sections):
    items = []
    for opts in sections.values():
        items.extend(opts)
    return items


# --------------------------------------------------------------------------- #
# Gold scaling
# --------------------------------------------------------------------------- #
def gold_multiplier(levels):
    """How much to scale coin/value rewards for this party.

    Table gold is tuned for a baseline party of four at low level (tier 1).
    Bigger parties scale linearly (party_size / 4); higher level scales by
    rough 5e treasure tier (x1 at 1-4, x2 at 5-10, x4 at 11-16, x8 at 17-20).
    """
    party_scale = len(levels) / 4.0
    avg_level = sum(levels) / len(levels)
    if avg_level <= 4:
        tier = 1.0
    elif avg_level <= 10:
        tier = 2.0
    elif avg_level <= 16:
        tier = 4.0
    else:
        tier = 8.0
    return party_scale * tier


def _avg_gp(match):
    """Average gp value of a single GOLD_RE match."""
    if match.group(4):  # flat "N gp"
        return float(int(match.group(4)))
    dice, faces = int(match.group(1)), int(match.group(2))
    factor = int(match.group(3)) if match.group(3) else 1
    return dice * (faces + 1) / 2 * factor


def _fmt_factor(factor):
    return f"{factor:g}"


def scale_gold(text, factor):
    """Apply ``factor`` to every gp amount in ``text``.

    Flat values are rewritten to the scaled amount ("25 gp" -> "75 gp"). Dice
    expressions stay rollable and are annotated with the multiplier and an
    average ("4d10 gp" -> "4d10 gp x3 (~66 gp)"). Returns ``(new_text, changed)``.
    """
    if factor == 1:
        return text, False
    changed = False

    def repl(match):
        nonlocal changed
        changed = True
        scaled = max(1, int(round(_avg_gp(match) * factor)))
        if match.group(4):  # flat amount
            return f"{scaled} gp"
        return f"{match.group(0)} \u00d7{_fmt_factor(factor)} (\u2248{scaled} gp)"

    return GOLD_RE.sub(repl, text), changed


# --------------------------------------------------------------------------- #
# Locations (faction ruins / camps discovered alongside loot)
# --------------------------------------------------------------------------- #
@dataclass
class Location:
    name: str
    faction: str
    type: str
    tier: str
    status: str
    summary: str
    purpose: str
    slug: str


def default_locations_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "locations"))


def load_locations(locations_dir):
    """Load location records from a folder of markdown files.

    Missing folders return an empty list so locations stay an optional feature.
    The slug is the filename without ``.md``. Frontmatter is parsed with the
    sibling ``encounter.py`` parser to avoid duplicating it here.
    """
    if not os.path.isdir(locations_dir):
        return []
    enc = _encounter_module()
    locations = []
    for entry in sorted(os.listdir(locations_dir)):
        if not entry.endswith(".md") or entry.lower() == "readme.md":
            continue
        with open(os.path.join(locations_dir, entry), encoding="utf-8") as fh:
            fm = enc.parse_frontmatter(fh.read())
        if "name" not in fm or "tier" not in fm:
            continue
        locations.append(
            Location(
                name=fm.get("name", entry[:-3]),
                faction=fm.get("faction", ""),
                type=fm.get("type", "ruin"),
                tier=fm.get("tier", "").lower(),
                status=fm.get("status", "ruined").lower(),
                summary=fm.get("summary", ""),
                purpose=fm.get("purpose", ""),
                slug=entry[:-3],
            )
        )
    return locations


def roll_location(slug, rng, locations):
    """Maybe pick a location the loot was found in, scaled to the loot value.

    The chance scales with the loot category (``LOCATION_CHANCE``); on a hit the
    site is drawn uniformly from the matching tier (``CATEGORY_TIER``), falling
    back to any tier if that pool is empty. Returns a ``Location`` or ``None``.
    """
    chance = LOCATION_CHANCE.get(slug, 0.0)
    if not locations or rng.random() >= chance:
        return None
    tier = CATEGORY_TIER.get(slug)
    pool = [loc for loc in locations if loc.tier == tier] or list(locations)
    return rng.choice(pool)


# --------------------------------------------------------------------------- #
# Guardian (boss monster / environmental) integration
# --------------------------------------------------------------------------- #
def _encounter_module():
    """Import the sibling ``encounter.py`` tool as a module (lazy)."""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    import encounter  # noqa: E402  (sibling tool in the same folder)
    return encounter


def _pick_boss_monster(enc, monsters, levels, rng):
    """Pick a single boss-tier creature for the guardian.

    Aims for a monster between the party's High budget and twice that, so the
    guardian reads as a genuine threat rather than a fair fight. Falls back to
    the toughest monster available if nothing lands in that band.
    """
    high = enc.budget_for(levels, "high")
    band = [m for m in monsters if high <= m.xp <= high * 2]
    if not band:
        band = [m for m in monsters if m.xp >= high] or [max(monsters, key=lambda m: m.xp)]
    return rng.choice(band)


def roll_guardian(levels, rng):
    """Decide whether a wondrous discovery is guarded, and by what.

    Randomly picks one of three outcomes with equal odds:

      * ``None``        - unguarded this time.
      * an environment  - a high-severity hazard watching the find.
      * a monster       - a boss-tier creature scaled to the party.

    Encounters are sourced from the sibling ``encounter.py`` tool's data so the
    guardian stays consistent with the rest of the travel content.
    """
    outcome = rng.choice(("none", "environment", "monster"))
    if outcome == "none":
        return None

    enc = _encounter_module()
    if outcome == "environment":
        hazards = enc.load_environments(enc.default_environments_dir())
        pool = [h for h in hazards if h.severity == "high"] or hazards
        h = rng.choice(pool)
        return f"Environmental - {h.name} ({h.severity} severity): {h.summary}"

    monsters = enc.load_monsters(enc.default_monsters_dir())
    m = _pick_boss_monster(enc, monsters, levels, rng)
    return f"Monster - {m.name} (CR {m.cr}, {m.xp:,} XP): {m.summary}"


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #
def print_result(slug, roll, levels, sections, rng, locations=None):
    name, _, drange = CATEGORIES[slug]
    avg_level = sum(levels) / len(levels)
    party_size = len(levels)

    levels_desc = ", ".join(str(lv) for lv in levels)
    print(f"Party: {party_size} character(s) (levels {levels_desc})")
    print(f"Travel roll: {roll}  ->  {name}  (d20 {drange})\n")

    factor = gold_multiplier(levels)
    if slug == "magic":
        tier, item = pick_magic(sections, avg_level, party_size, rng)
        item, _ = scale_gold(item, factor)
        print(f"  Magic item [{tier}]: {item}")
    else:
        item = rng.choice(all_items(sections))
        item, scaled = scale_gold(item, factor)
        print(f"  Result: {item}")
        if scaled:
            print(
                f"  (gold scaled x{factor:g} for {party_size} PC(s) at "
                f"avg level {avg_level:g})"
            )

    if locations is None:
        locations = load_locations(default_locations_dir())
    location = roll_location(slug, rng, locations)
    if location is not None:
        living = " - inhabited" if location.status == "inhabited" else ""
        print(
            f"\n  Found at: {location.name} "
            f"({location.faction}, {location.tier} site{living}): {location.summary}"
        )

    if slug == "wondrous":
        guardian = roll_guardian(levels, rng)
        if guardian is None:
            print("\n  Guardian: none this time - the discovery lies unguarded.")
        else:
            print(f"\n  Guardian: {guardian}")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def build_parser():
    epilog = """\
how it works
------------
The players roll the travel d20; pass that result as --roll. This tool covers
the loot/discovery half (results 11-20; see ../mechanic.md) and maps the roll to
a category, then randomizes the actual reward inside it:

  --roll 11-13  Nothing Found - flavour only.
  --roll 14-16  Mundane Treasure - coins, goods, valuables.
  --roll 17-19  Magic Treasure - tier weighted by party level/size.
  --roll 20     Wondrous Discovery - rare find PLUS a boss guardian.

Rolls 1-10 are encounters - use ../encounters.md and tools/encounter.py instead.

Party level (and, a little, party size) skews which magic-item rarity tier is
rolled. Coin and value rewards are auto-scaled by party size and average level
(see gold_multiplier). A wondrous discovery also rolls a scaled boss guardian.

The higher the loot category, the more likely the find was made inside a
faction location (modest/notable/grand site): 0% nothing, ~25% mundane, ~60%
magic, 100% wondrous. Sites live in ../locations/.

examples
--------
  # The party rolled a 17 (magic treasure) - four level-6 PCs
  loot.py --party-size 4 --level 6 --roll 17

  # The party rolled a natural 20 (rolls a guardian), mixed-level party
  loot.py --levels 5,6,6,7 --roll 20

  # The party rolled a 15 (mundane); coin values auto-scale for a big party
  loot.py --party-size 6 --level 5 --roll 15
"""
    parser = argparse.ArgumentParser(
        prog="loot.py",
        description="Roll a random Great Northwood loot/discovery result for a party.",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    party = parser.add_argument_group("party (use --levels, OR --party-size with --level)")
    party.add_argument("--party-size", type=int, help="number of characters (uniform level)")
    party.add_argument("--level", type=int, help="level shared by all characters")
    party.add_argument("--levels", help="comma-separated per-character levels, e.g. 4,6,6,7")

    parser.add_argument("--roll", type=int, required=True,
                        help="the players' travel d20 result (11-20; 1-10 are encounters)")
    parser.add_argument("--seed", type=int, default=None,
                        help="optional RNG seed for reproducible rolls")
    parser.add_argument("--loot-dir", default=None,
                        help="path to the loot folder (default: sibling ../loot)")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    roll = args.roll
    if not 1 <= roll <= 20:
        sys.exit(f"error: --roll must be a d20 result (1-20): {roll}")
    if roll < LOOT_ROLL_MIN:
        sys.exit(
            f"error: a roll of {roll} is an encounter (d20 1-10), not loot. "
            "See ../encounters.md and tools/encounter.py."
        )
    slug = category_for_roll(roll)
    if slug is None:
        sys.exit(f"error: no loot category covers a roll of {roll}")

    levels = resolve_party(args)
    loot_dir = args.loot_dir or default_loot_dir()
    sections = load_category(loot_dir, slug)
    if not all_items(sections):
        sys.exit(f"error: no options found in the {slug} loot file")
    rng = random.Random(args.seed)
    locations = load_locations(default_locations_dir())
    print_result(slug, roll, levels, sections, rng, locations)


if __name__ == "__main__":
    main()
