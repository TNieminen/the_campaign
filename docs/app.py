"""Great Northwood DM Toolkit - PyScript front-end.

Runs entirely in the browser. It imports the real ``encounter.py`` and
``loot.py`` tool modules (copied alongside this file by ``build_data.py``) and
feeds them data from ``data.json``, so the web UI uses exactly the same
selection logic as the command-line tools.
"""

import json
import random

from pyscript import document, window
from pyscript.ffi import create_proxy

import encounter
import loot

# --------------------------------------------------------------------------- #
# Data
# --------------------------------------------------------------------------- #
with open("data.json", encoding="utf-8") as _fh:
    DATA = json.load(_fh)

MONSTERS = [
    encounter.Monster(
        name=m["name"], cr=m["cr"], xp=m["xp"], size=m["size"],
        type=m["type"], summary=m["summary"], slug=m["slug"],
    )
    for m in DATA["monsters"]
]
HAZARDS = [
    encounter.Hazard(
        name=h["name"], severity=h["severity"], dc=h["dc"], damage=h["damage"],
        check=h["check"], summary=h["summary"], slug=h["slug"],
    )
    for h in DATA["environments"]
]
MONSTER_BODY = {m["slug"]: m["body"] for m in DATA["monsters"]}
ENV_BODY = {h["slug"]: h["body"] for h in DATA["environments"]}


# --------------------------------------------------------------------------- #
# Small DOM helpers
# --------------------------------------------------------------------------- #
def el(selector):
    return document.querySelector(selector)


def set_html(selector, html):
    el(selector).innerHTML = html


def md(text):
    """Render markdown to HTML using marked.js (loaded in the page)."""
    return window.marked.parse(text)


def esc(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def on(selector, event, handler):
    node = el(selector)
    if node is not None:
        node.addEventListener(event, create_proxy(handler))


# --------------------------------------------------------------------------- #
# Party parsing (mirrors resolve_party / resolve_levels without argparse)
# --------------------------------------------------------------------------- #
def parse_levels(levels_str, party_size_str, level_str):
    """Return (levels, error_message). Prefers an explicit --levels string."""
    levels_str = (levels_str or "").strip()
    if levels_str:
        try:
            levels = [int(x) for x in levels_str.split(",") if x.strip()]
        except ValueError:
            return None, "Levels must be comma-separated integers, e.g. 4,6,6,7"
    else:
        try:
            party_size = int(party_size_str)
            level = int(level_str)
        except (TypeError, ValueError):
            return None, "Enter a party size and level (or a Levels list)."
        levels = [level] * party_size
    if not levels:
        return None, "The party is empty."
    for lv in levels:
        if not 1 <= lv <= 20:
            return None, f"Character level out of range (1-20): {lv}"
    return levels, None


def party_line(levels):
    return f"{len(levels)} character(s) - levels {', '.join(str(l) for l in levels)}"


# --------------------------------------------------------------------------- #
# Encounter tab
# --------------------------------------------------------------------------- #
def render_encounter_parts(results, budget):
    rows = []
    for total, parts in results:
        pieces = " + ".join(f"{qty}x {esc(m.name)}" for m, qty in parts)
        pct = round(100 * total / budget) if budget else 0
        members = "".join(
            f"<li><strong>{esc(m.name)}</strong> "
            f"<span class='tag'>CR {esc(m.cr)}</span> "
            f"<span class='tag'>{m.xp:,} XP</span> &mdash; {esc(m.summary)}</li>"
            for m, _ in parts
        )
        rows.append(
            f"<div class='result-card'>"
            f"<div class='result-head'>{pieces} "
            f"<span class='muted'>&mdash; {total:,} XP ({pct}% of budget)</span></div>"
            f"<ul class='member-list'>{members}</ul>"
            f"</div>"
        )
    return "".join(rows)


def run_encounter(event=None):
    levels, err = parse_levels(
        el("#enc-levels").value, el("#enc-party-size").value, el("#enc-level").value
    )
    if err:
        set_html("#enc-out", f"<p class='error'>{esc(err)}</p>")
        return

    difficulty = el("#enc-difficulty").value
    mode = el("#enc-mode").value
    try:
        count = int(el("#enc-count").value)
        max_types = int(el("#enc-max-types").value)
        min_fill = float(el("#enc-min-fill").value)
        limit = int(el("#enc-limit").value)
    except ValueError:
        set_html("#enc-out", "<p class='error'>Check the numeric tuning fields.</p>")
        return
    if count < 1:
        set_html("#enc-out", "<p class='error'>Count must be at least 1.</p>")
        return
    if not 0 < min_fill <= 1:
        set_html("#enc-out", "<p class='error'>Min fill must be between 0 and 1.</p>")
        return

    budgets = {d: encounter.budget_for(levels, d) for d in encounter.DIFFICULTIES}
    budget = budgets[difficulty]

    if mode == "boss-minions":
        if count < 2:
            set_html("#enc-out", "<p class='error'>Boss + minions needs a count of at least 2.</p>")
            return
        results = encounter.find_boss_minions(
            MONSTERS, budget, count, min_fill, 0.4, 0.7, limit
        )
    else:
        results = encounter.find_mix(MONSTERS, budget, count, max_types, min_fill, limit)

    header = (
        f"<div class='out-header'>"
        f"<div>Party: <strong>{esc(party_line(levels))}</strong></div>"
        f"<div class='muted'>Budgets: Low {budgets['low']:,} | "
        f"Moderate {budgets['moderate']:,} | High {budgets['high']:,}</div>"
        f"<div>Selected: <strong>{difficulty.upper()}</strong> "
        f"&rarr; budget {budget:,} XP</div>"
        f"</div>"
    )

    if results:
        body = (
            f"<p class='muted'>Found {len(results)} encounter(s):</p>"
            + render_encounter_parts(results, budget)
        )
    else:
        body = (
            "<p class='warn'>No monster encounters matched. Try a different count, "
            "difficulty, a lower min-fill, or a higher max-types.</p>"
        )

    # Environmental challenges at this difficulty (severity == difficulty).
    hazards = encounter.select_environments(HAZARDS, difficulty, limit)
    if hazards:
        haz = "".join(
            f"<li><strong>{esc(h.name)}</strong> "
            f"<span class='tag'>DC {esc(h.dc)}</span> "
            f"<span class='tag'>{esc(h.severity)}</span> &mdash; {esc(h.summary)}</li>"
            for h in hazards
        )
        body += (
            f"<div class='result-card'><div class='result-head'>"
            f"Environmental challenges ({difficulty} severity)</div>"
            f"<ul class='member-list'>{haz}</ul></div>"
        )

    set_html("#enc-out", header + body)


# --------------------------------------------------------------------------- #
# Loot tab
# --------------------------------------------------------------------------- #
def roll_d20(event=None):
    el("#loot-roll").value = str(random.randint(11, 20))


def run_loot(event=None):
    try:
        roll = int(el("#loot-roll").value)
    except (TypeError, ValueError):
        set_html("#loot-out", "<p class='error'>Enter the travel d20 roll (11-20).</p>")
        return
    if not 1 <= roll <= 20:
        set_html("#loot-out", "<p class='error'>Roll must be a d20 result (1-20).</p>")
        return
    if roll < loot.LOOT_ROLL_MIN:
        set_html(
            "#loot-out",
            "<p class='warn'>A roll of "
            f"{roll} is an <strong>encounter</strong> (d20 1-10), not loot. "
            "Use the Encounter Builder tab.</p>",
        )
        return

    slug = loot.category_for_roll(roll)
    levels, err = parse_levels(
        el("#loot-levels").value, el("#loot-party-size").value, el("#loot-level").value
    )
    if err:
        set_html("#loot-out", f"<p class='error'>{esc(err)}</p>")
        return

    seed_str = el("#loot-seed").value.strip()
    rng = random.Random(int(seed_str)) if seed_str else random.Random()

    cat = DATA["loot"][slug]
    sections = cat["sections"]
    avg_level = sum(levels) / len(levels)
    party_size = len(levels)

    parts = [
        f"<div class='out-header'>"
        f"<div>Party: <strong>{esc(party_line(levels))}</strong></div>"
        f"<div>Travel roll: <strong>{roll}</strong> &rarr; "
        f"{esc(cat['name'])} <span class='muted'>(d20 {esc(cat['range'])})</span></div>"
        f"</div>"
    ]

    if slug == "magic":
        tier, item = loot.pick_magic(sections, avg_level, party_size, rng)
        parts.append(
            f"<div class='loot-result'><span class='tag tier-{tier.lower()}'>{esc(tier)}</span> "
            f"{esc(item)}</div>"
        )
    else:
        item = rng.choice(loot.all_items(sections))
        parts.append(f"<div class='loot-result'>{esc(item)}</div>")
        if slug == "mundane" and party_size != 4:
            mult = party_size / 4
            parts.append(
                f"<p class='muted'>Suggested coin/value scale for a party of "
                f"{party_size}: &times;{mult:.2f}</p>"
            )

    if slug == "wondrous":
        guardian = roll_guardian_web(levels, rng)
        if guardian is None:
            parts.append(
                "<div class='guardian none'>Guardian: none this time &mdash; "
                "the discovery lies unguarded.</div>"
            )
        else:
            parts.append(f"<div class='guardian'>Guardian: {esc(guardian)}</div>")

    set_html("#loot-out", "".join(parts))


def roll_guardian_web(levels, rng):
    """Browser port of loot.roll_guardian using the preloaded data.

    Equal odds of: no guardian, a high-severity environmental hazard, or a
    boss-tier monster (via the shared loot._pick_boss_monster).
    """
    outcome = rng.choice(("none", "environment", "monster"))
    if outcome == "none":
        return None
    if outcome == "environment":
        pool = [h for h in HAZARDS if h.severity == "high"] or HAZARDS
        h = rng.choice(pool)
        return f"Environmental \u2014 {h.name} ({h.severity} severity): {h.summary}"
    m = loot._pick_boss_monster(encounter, MONSTERS, levels, rng)
    return f"Monster \u2014 {m.name} (CR {m.cr}, {m.xp:,} XP): {m.summary}"


# --------------------------------------------------------------------------- #
# Bestiary tab
# --------------------------------------------------------------------------- #
def render_bestiary(filter_text=""):
    filter_text = filter_text.strip().lower()
    items = []
    for m in MONSTERS:
        hay = f"{m.name} {m.type} {m.cr}".lower()
        if filter_text and filter_text not in hay:
            continue
        items.append(
            f"<button class='list-item' data-slug='{esc(m.slug)}'>"
            f"<span class='li-name'>{esc(m.name)}</span>"
            f"<span class='li-meta'>CR {esc(m.cr)} &middot; {m.xp:,} XP</span>"
            f"</button>"
        )
    set_html("#mon-list", "".join(items) or "<p class='muted'>No matches.</p>")


def show_monster(slug):
    body = MONSTER_BODY.get(slug)
    if body is None:
        return
    set_html("#mon-detail", f"<article class='statblock'>{md(body)}</article>")


def on_bestiary_search(event):
    render_bestiary(el("#mon-search").value)


def on_bestiary_click(event):
    btn = event.target.closest(".list-item")
    if btn is not None:
        show_monster(btn.dataset.slug)


# --------------------------------------------------------------------------- #
# Reference tab (loot tables + environmental hazards)
# --------------------------------------------------------------------------- #
def render_reference():
    blocks = ["<h2 class='ref-title'>Loot &amp; discovery tables</h2>"]
    for slug in ("nothing", "mundane", "magic", "wondrous"):
        cat = DATA["loot"][slug]
        blocks.append(
            f"<details class='ref-block' open><summary>{esc(cat['name'])} "
            f"<span class='muted'>(d20 {esc(cat['range'])})</span></summary>"
            f"<div class='ref-body'>{md(cat['body'])}</div></details>"
        )
    blocks.append("<h2 class='ref-title'>Environmental hazards</h2>")
    for h in HAZARDS:
        blocks.append(
            f"<details class='ref-block'><summary>{esc(h.name)} "
            f"<span class='muted'>({esc(h.severity)} severity)</span></summary>"
            f"<div class='ref-body'>{md(ENV_BODY[h.slug])}</div></details>"
        )
    set_html("#ref-out", "".join(blocks))


# --------------------------------------------------------------------------- #
# Wire up
# --------------------------------------------------------------------------- #
def setup():
    on("#enc-run", "click", run_encounter)
    on("#loot-run", "click", run_loot)
    on("#loot-rolld20", "click", roll_d20)
    on("#mon-search", "input", on_bestiary_search)
    on("#mon-list", "click", on_bestiary_click)

    render_bestiary()
    render_reference()
    if MONSTERS:
        show_monster(MONSTERS[0].slug)

    # Tell the page Python is ready (hides the loading splash).
    document.body.classList.add("py-ready")


setup()
