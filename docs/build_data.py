#!/usr/bin/env python3
"""Build the static data bundle for the Great Northwood web app.

Reads the canonical markdown under ``notes/dnd/greath-northwood/`` (monsters,
environments, loot) and emits a single ``docs/data.json`` that the PyScript app
consumes in the browser. It also copies the two tool modules (``encounter.py``
and ``loot.py``) next to this script so PyScript can import the *real* selection
logic instead of a fork.

The markdown stays the single source of truth: re-run this whenever the notes
change.

    python3 docs/build_data.py

Standard library only.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from urllib.parse import quote_plus

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GN = os.path.join(ROOT, "notes", "dnd", "greath-northwood")
TOOLS = os.path.join(GN, "tools")
MONSTERS_DIR = os.path.join(GN, "monsters")
ENVIRONMENTS_DIR = os.path.join(GN, "environments")
LOOT_DIR = os.path.join(GN, "loot")

# Import the real tools so the build and the app share one implementation.
sys.path.insert(0, TOOLS)
import encounter  # noqa: E402
import loot  # noqa: E402


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def body_of(text):
    """Markdown body with the YAML frontmatter stripped."""
    return loot.strip_frontmatter(text).strip()


def dndbeyond_url(name, category):
    """A clickable D&D Beyond search link for a creature or item by name."""
    return f"https://www.dndbeyond.com/search?q={quote_plus(name)}&f={category}"


def build_monsters():
    out = []
    for m in encounter.load_monsters(MONSTERS_DIR):
        text = read(os.path.join(MONSTERS_DIR, m.slug + ".md"))
        url = dndbeyond_url(m.name, "monsters")
        body = body_of(text) + f"\n\n**Source:** [{m.name} on D&D Beyond]({url})"
        out.append({
            "name": m.name,
            "cr": m.cr,
            "xp": m.xp,
            "size": m.size,
            "type": m.type,
            "summary": m.summary,
            "slug": m.slug,
            "source": url,
            "body": body,
        })
    out.sort(key=lambda d: (d["xp"], d["name"]))
    return out


def build_environments():
    out = []
    for h in encounter.load_environments(ENVIRONMENTS_DIR):
        text = read(os.path.join(ENVIRONMENTS_DIR, h.slug + ".md"))
        out.append({
            "name": h.name,
            "severity": h.severity,
            "dc": h.dc,
            "damage": h.damage,
            "check": h.check,
            "summary": h.summary,
            "slug": h.slug,
            "body": body_of(text),
        })
    severity_order = {"low": 0, "moderate": 1, "high": 2}
    out.sort(key=lambda d: (severity_order.get(d["severity"], 9), d["name"]))
    return out


def build_loot():
    out = {}
    for slug, (name, filename, drange) in loot.CATEGORIES.items():
        text = read(os.path.join(LOOT_DIR, filename))
        fm = encounter.parse_frontmatter(text)
        out[slug] = {
            "name": name,
            "die": fm.get("die", ""),
            "range": drange,
            "summary": fm.get("summary", ""),
            "sections": loot.parse_sections(text),
            "body": body_of(text),
        }
    return out


def copy_tools():
    for name in ("encounter.py", "loot.py"):
        shutil.copyfile(os.path.join(TOOLS, name), os.path.join(HERE, name))


def main():
    data = {
        "generated_by": "docs/build_data.py",
        "source": "notes/dnd/greath-northwood",
        "monsters": build_monsters(),
        "environments": build_environments(),
        "loot": build_loot(),
        "xp_budget_per_character": encounter.XP_BUDGET_PER_CHARACTER,
        "difficulties": list(encounter.DIFFICULTIES),
    }
    with open(os.path.join(HERE, "data.json"), "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    copy_tools()
    print(f"Wrote data.json: {len(data['monsters'])} monsters, "
          f"{len(data['environments'])} environments, {len(data['loot'])} loot tables.")
    print("Copied encounter.py and loot.py into docs/.")


if __name__ == "__main__":
    main()
