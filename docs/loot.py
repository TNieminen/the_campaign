#!/usr/bin/env python3
"""Great Northwood Loot & Discovery Tool.

Rolls a random result from one of the travel loot categories (the d20 11-20
half of the travel roll; see ``../mechanic.md``). Reads the category option
lists from the sibling ``../loot/`` folder so the data stays human-editable.

Inputs are the party size, the party level, and the discovery category. Party
level (and, slightly, party size) skews the magic-treasure rarity tier. A
wondrous discovery additionally rolls a scaled boss-tier **guardian** that
watches over the find.

Pure standard library, no third-party dependencies. See ``loot.py --help``.
"""

from __future__ import annotations

import argparse
import os
import random
import re
import sys

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
def print_result(slug, roll, levels, sections, rng):
    name, _, drange = CATEGORIES[slug]
    avg_level = sum(levels) / len(levels)
    party_size = len(levels)

    levels_desc = ", ".join(str(lv) for lv in levels)
    print(f"Party: {party_size} character(s) (levels {levels_desc})")
    print(f"Travel roll: {roll}  ->  {name}  (d20 {drange})\n")

    if slug == "magic":
        tier, item = pick_magic(sections, avg_level, party_size, rng)
        print(f"  Magic item [{tier}]: {item}")
    else:
        item = rng.choice(all_items(sections))
        print(f"  Result: {item}")
        if slug == "mundane" and party_size != 4:
            mult = party_size / 4
            print(f"  (suggested coin/value scale for a party of {party_size}: x{mult:.2f})")

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
rolled. A wondrous discovery also rolls a scaled boss-tier guardian.

examples
--------
  # The party rolled a 17 (magic treasure) - four level-6 PCs
  loot.py --party-size 4 --level 6 --roll 17

  # The party rolled a natural 20 (rolls a guardian), mixed-level party
  loot.py --levels 5,6,6,7 --roll 20

  # The party rolled a 15 (mundane) with a big party (prints a value hint)
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
    print_result(slug, roll, levels, sections, rng)


if __name__ == "__main__":
    main()
