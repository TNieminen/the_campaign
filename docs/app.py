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
LOCATIONS = [
    loot.Location(
        name=l["name"], faction=l["faction"], type=l["type"], tier=l["tier"],
        status=l["status"], summary=l["summary"], purpose=l["purpose"], slug=l["slug"],
    )
    for l in DATA.get("locations", [])
]
MONSTER_BODY = {m["slug"]: m["body"] for m in DATA["monsters"]}
ENV_BODY = {h["slug"]: h["body"] for h in DATA["environments"]}
LOC_BODY = {l["slug"]: l["body"] for l in DATA.get("locations", [])}

# Pretty labels for the faction slug stored in location frontmatter.
FACTION_LABELS = {
    "kutur": "Kutur",
    "savol": "Savol",
    "valvela": "Valvela",
    "hollow-ledger": "Hollow Ledger",
}


def faction_label(slug):
    return FACTION_LABELS.get(slug, slug.replace("-", " ").title() if slug else "")


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


def md_inline(text):
    """Render a single line of markdown (no wrapping <p>), for list/result items."""
    return window.marked.parseInline(text)


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


def copy_btn():
    return "<button class='copy-md' type='button' title='Copy as Markdown'>Copy MD</button>"


def md_src(text):
    """Hidden carrier of the raw markdown for the Copy MD button to read."""
    return f"<pre class='md-src' hidden>{esc(text)}</pre>"


def collapsible(title_html, body_md, open_=False):
    """A click-to-expand card that renders markdown and offers a Copy MD button."""
    state = " open" if open_ else ""
    return (
        f"<details class='card' data-md-card{state}>"
        f"<summary><span class='card-title'>{title_html}</span>{copy_btn()}</summary>"
        f"<div class='card-body'>{md(body_md)}{md_src(body_md)}</div>"
        f"</details>"
    )


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


def activate_tab(tab_id):
    """Switch the visible main tab (encounter, loot, bestiary, reference)."""
    for node in document.querySelectorAll(".tab"):
        node.classList.toggle("active", node.dataset.tab == tab_id)
    for node in document.querySelectorAll(".panel"):
        node.classList.toggle("active", node.id == f"panel-{tab_id}")


def bestiary_href(slug):
    return f"#bestiary/{slug}"


def environment_href(slug):
    return f"#environment/{slug}"


def location_href(slug):
    return f"#location/{slug}"


def monster_link(m, qty=None):
    """Clickable monster name that opens the bestiary entry in a new tab."""
    href = esc(bestiary_href(m.slug))
    name = esc(m.name)
    inner = f'<a class="entry-link" href="{href}" target="_blank" rel="noopener">{name}</a>'
    if qty is not None and qty > 1:
        return f"{qty}x {inner}"
    return inner


def hazard_link(h):
    """Clickable hazard name that opens the environments entry in a new tab."""
    href = esc(environment_href(h.slug))
    name = esc(h.name)
    return f'<a class="entry-link" href="{href}" target="_blank" rel="noopener">{name}</a>'


def location_link(loc):
    """Clickable location name that opens the locations entry in a new tab."""
    href = esc(location_href(loc.slug))
    name = esc(loc.name)
    return f'<a class="entry-link" href="{href}" target="_blank" rel="noopener">{name}</a>'


# --------------------------------------------------------------------------- #
# Encounter tab
# --------------------------------------------------------------------------- #
def render_encounter_parts(results, budget):
    rows = []
    for total, parts in results:
        pieces = " + ".join(monster_link(m, qty) for m, qty in parts)
        pct = round(100 * total / budget) if budget else 0
        members = "".join(
            f"<li><strong>{monster_link(m)}</strong> "
            f"<span class='tag'>CR {esc(m.cr)}</span> "
            f"<span class='tag'>{m.xp:,} XP</span> &mdash; {esc(m.summary)}</li>"
            for m, _ in parts
        )
        rows.append(
            f"<details class='result-card' open>"
            f"<summary class='result-head'>{pieces} "
            f"<span class='muted'>&mdash; {total:,} XP ({pct}% of budget)</span></summary>"
            f"<ul class='member-list'>{members}</ul>"
            f"</details>"
        )
    return "".join(rows)


def encounter_markdown(levels, difficulty, budget, results, hazards, band=None, roll=None,
                       location=None):
    if band is not None:
        deadly = " x deadly" if band["deadly"] else ""
        title = f"# Encounter \u2014 roll {roll}: {band['label']} ({difficulty.title()}{deadly})"
    else:
        title = f"# Encounter \u2014 {difficulty.title()}"
    lines = [
        title,
        f"Party: {party_line(levels)}  |  Budget: {budget:,} XP",
    ]
    if location is not None:
        living = ", inhabited" if location.status == "inhabited" else ""
        lines.append(
            f"Encounter site: [{location.name}]({location_href(location.slug)}) "
            f"({faction_label(location.faction)}, {location.tier} site{living}) "
            f"\u2014 {location.summary}"
        )
    lines.append("")
    if results:
        for total, parts in results:
            pieces = " + ".join(f"{qty}x {m.name}" for m, qty in parts)
            pct = round(100 * total / budget) if budget else 0
            lines.append(f"- **{pieces}** \u2014 {total:,} XP ({pct}% of budget)")
            for m, _ in parts:
                lines.append(
                    f"  - [{m.name}]({bestiary_href(m.slug)}) "
                    f"(CR {m.cr}, {m.xp:,} XP): {m.summary}"
                )
    else:
        lines.append("- No monster encounters matched.")
    if hazards:
        lines.append("")
        lines.append(f"## Environmental challenges ({difficulty} severity)")
        for h in hazards:
            lines.append(
                f"- [{h.name}]({environment_href(h.slug)}) "
                f"(DC {h.dc}, {h.severity}): {h.summary}"
            )
    return "\n".join(lines)


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

    # Optional travel d20 roll (1-10) overrides the difficulty dropdown.
    band = None
    roll = None
    roll_str = el("#enc-roll").value.strip()
    if roll_str:
        try:
            roll = int(roll_str)
        except ValueError:
            set_html("#enc-out", "<p class='error'>Enter the travel d20 roll (1-10).</p>")
            return
        if not 1 <= roll <= 20:
            set_html("#enc-out", "<p class='error'>Roll must be a d20 result (1-20).</p>")
            return
        if roll > encounter.ENCOUNTER_ROLL_MAX:
            set_html(
                "#enc-out",
                f"<p class='warn'>A roll of {roll} is <strong>loot</strong> "
                "(d20 11-20), not an encounter. Use the Loot &amp; Discovery tab.</p>",
            )
            return
        band = encounter.band_for_roll(roll)
        difficulty = band["difficulty"]

    budgets = {d: encounter.budget_for(levels, d) for d in encounter.DIFFICULTIES}
    budget = encounter.budget_for_band(levels, band) if band else budgets[difficulty]

    if mode == "boss-minions":
        if count < 2:
            set_html("#enc-out", "<p class='error'>Boss + minions needs a count of at least 2.</p>")
            return
        results = encounter.find_boss_minions(
            MONSTERS, budget, count, min_fill, 0.4, 0.7, limit
        )
    else:
        results = encounter.find_mix(MONSTERS, budget, count, max_types, min_fill, limit)

    if band is not None:
        deadly = " &times; deadly" if band["deadly"] else ""
        selected_line = (
            f"<div>Travel roll: <strong>{roll}</strong> &rarr; "
            f"{esc(band['label'])} ({difficulty.upper()}{deadly}) "
            f"&rarr; budget {budget:,} XP</div>"
        )
    else:
        selected_line = (
            f"<div>Selected: <strong>{difficulty.upper()}</strong> "
            f"&rarr; budget {budget:,} XP</div>"
        )
    header = (
        f"<div class='out-header'>"
        f"<div>Party: <strong>{esc(party_line(levels))}</strong></div>"
        f"<div class='muted'>Budgets: Low {budgets['low']:,} | "
        f"Moderate {budgets['moderate']:,} | High {budgets['high']:,}</div>"
        f"{selected_line}"
        f"</div>"
    )

    # The encounter may take place at a faction location; chance and grandeur
    # scale with how dangerous the encounter is.
    severity = encounter.encounter_severity(difficulty, bool(band and band["deadly"]))
    location = encounter.roll_encounter_location(severity, random.Random(), LOCATIONS)
    location_html = ""
    if location is not None:
        l_html, _ = format_location(location)
        location_html = f"<div class='loot-location'>Encounter site: {l_html}</div>"

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
            f"<li><strong>{hazard_link(h)}</strong> "
            f"<span class='tag'>DC {esc(h.dc)}</span> "
            f"<span class='tag'>{esc(h.severity)}</span> &mdash; {esc(h.summary)}</li>"
            for h in hazards
        )
        body += (
            f"<details class='result-card'><summary class='result-head'>"
            f"Environmental challenges ({difficulty} severity)</summary>"
            f"<ul class='member-list'>{haz}</ul></details>"
        )

    md_text = encounter_markdown(levels, difficulty, budget, results, hazards, band, roll,
                                 location)
    top = f"<div class='out-top'>{copy_btn()}</div>"
    set_html("#enc-out", top + header + location_html + body + md_src(md_text))


# --------------------------------------------------------------------------- #
# Loot tab
# --------------------------------------------------------------------------- #
def roll_d20(event=None):
    el("#loot-roll").value = str(random.randint(11, 20))


def roll_d20_encounter(event=None):
    el("#enc-roll").value = str(random.randint(1, 10))


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
    factor = loot.gold_multiplier(levels)

    parts = [
        f"<div class='out-top'>{copy_btn()}</div>",
        f"<div class='out-header'>"
        f"<div>Party: <strong>{esc(party_line(levels))}</strong></div>"
        f"<div>Travel roll: <strong>{roll}</strong> &rarr; "
        f"{esc(cat['name'])} <span class='muted'>(d20 {esc(cat['range'])})</span></div>"
        f"</div>"
    ]
    md_lines = [
        f"**Travel roll {roll} \u2014 {cat['name']} (d20 {cat['range']})**",
        f"Party: {party_line(levels)}",
        "",
    ]

    if slug == "magic":
        tier, item = loot.pick_magic(sections, avg_level, party_size, rng)
        item, _ = loot.scale_gold(item, factor)
        parts.append(
            f"<div class='loot-result'><span class='tag tier-{tier.lower()}'>{esc(tier)}</span> "
            f"{md_inline(item)}</div>"
        )
        md_lines.append(f"- Magic item [{tier}]: {item}")
    else:
        item = rng.choice(loot.all_items(sections))
        item, scaled = loot.scale_gold(item, factor)
        parts.append(f"<div class='loot-result'>{md_inline(item)}</div>")
        md_lines.append(f"- {item}")
        if scaled:
            parts.append(
                f"<p class='muted'>Gold scaled &times;{factor:g} for a party of "
                f"{party_size} at avg level {avg_level:g}.</p>"
            )
            md_lines.append(
                f"- Gold scaled x{factor:g} for a party of {party_size} at "
                f"avg level {avg_level:g}"
            )

    location = loot.roll_location(slug, rng, LOCATIONS)
    if location is not None:
        l_html, l_md = format_location(location)
        parts.append(f"<div class='loot-location'>Found at: {l_html}</div>")
        md_lines.append(f"- Found at: {l_md}")

    if slug == "wondrous":
        guardian = roll_guardian_web(levels, rng)
        if guardian is None:
            parts.append(
                "<div class='guardian none'>Guardian: none this time &mdash; "
                "the discovery lies unguarded.</div>"
            )
            md_lines.append("- Guardian: none this time")
        else:
            g_html, g_md = format_guardian(guardian)
            parts.append(f"<div class='guardian'>Guardian: {g_html}</div>")
            md_lines.append(f"- Guardian: {g_md}")

    parts.append(md_src("\n".join(md_lines)))
    set_html("#loot-out", "".join(parts))


def roll_guardian_web(levels, rng):
    """Browser port of loot.roll_guardian using the preloaded data.

    Equal odds of: no guardian, a high-severity environmental hazard, or a
    boss-tier monster (via the shared loot._pick_boss_monster).

    Returns ``None`` or a dict with ``type`` ``environment`` or ``monster``.
    """
    outcome = rng.choice(("none", "environment", "monster"))
    if outcome == "none":
        return None
    if outcome == "environment":
        pool = [h for h in HAZARDS if h.severity == "high"] or HAZARDS
        h = rng.choice(pool)
        return {"type": "environment", "hazard": h}
    m = loot._pick_boss_monster(encounter, MONSTERS, levels, rng)
    return {"type": "monster", "monster": m}


def format_guardian(guardian):
    """HTML and markdown lines for a wondrous-discovery guardian."""
    if guardian["type"] == "environment":
        h = guardian["hazard"]
        html = (
            f"Environmental &mdash; {hazard_link(h)} "
            f"({esc(h.severity)} severity): {esc(h.summary)}"
        )
        md = (
            f"Environmental — [{h.name}]({environment_href(h.slug)}) "
            f"({h.severity} severity): {h.summary}"
        )
        return html, md
    m = guardian["monster"]
    html = (
        f"Monster &mdash; {monster_link(m)} "
        f"(CR {esc(m.cr)}, {m.xp:,} XP): {esc(m.summary)}"
    )
    md = (
        f"Monster — [{m.name}]({bestiary_href(m.slug)}) "
        f"(CR {m.cr}, {m.xp:,} XP): {m.summary}"
    )
    return html, md


def format_location(loc):
    """HTML and markdown lines for a location a loot result was found at."""
    living = " &middot; inhabited" if loc.status == "inhabited" else ""
    meta = f"{esc(faction_label(loc.faction))} &middot; {esc(loc.tier)} site{living}"
    html = (
        f"{location_link(loc)} "
        f"<span class='muted'>({meta})</span> &mdash; {esc(loc.summary)}"
    )
    living_md = ", inhabited" if loc.status == "inhabited" else ""
    md = (
        f"[{loc.name}]({location_href(loc.slug)}) "
        f"({faction_label(loc.faction)}, {loc.tier} site{living_md}): {loc.summary}"
    )
    return html, md


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


def show_monster(slug, *, update_hash=True):
    body = MONSTER_BODY.get(slug)
    if body is None:
        return False
    set_html(
        "#mon-detail",
        f"<div class='out-top'>{copy_btn()}</div>"
        f"<article class='statblock'>{md(body)}</article>"
        f"{md_src(body)}",
    )
    for node in document.querySelectorAll("#mon-list .list-item"):
        node.classList.toggle("active", node.dataset.slug == slug)
    if update_hash:
        window.location.hash = f"bestiary/{slug}"
    return True


def apply_route_from_hash():
    """Open a deep-linked entry from #bestiary/<slug>, #environment/<slug>, or #location/<slug>."""
    raw = (window.location.hash or "").lstrip("#")
    if raw.startswith("bestiary/"):
        slug = raw.split("/", 1)[1]
        if slug in MONSTER_BODY:
            activate_tab("bestiary")
            show_monster(slug, update_hash=False)
            return True
    if raw.startswith("environment/"):
        slug = raw.split("/", 1)[1]
        if slug in ENV_BODY:
            activate_tab("environment")
            show_environment(slug, update_hash=False)
            return True
    if raw.startswith("location/"):
        slug = raw.split("/", 1)[1]
        if slug in LOC_BODY:
            activate_tab("location")
            show_location(slug, update_hash=False)
            return True
    return False


def on_hash_change(event=None):
    apply_route_from_hash()


def on_bestiary_search(event):
    render_bestiary(el("#mon-search").value)


def on_bestiary_click(event):
    btn = event.target.closest(".list-item")
    if btn is not None:
        show_monster(btn.dataset.slug)


# --------------------------------------------------------------------------- #
# Environments tab
# --------------------------------------------------------------------------- #
_SEV_ORDER = {"low": 0, "moderate": 1, "high": 2}


def render_environments(filter_text=""):
    filter_text = filter_text.strip().lower()
    items = []
    sorted_hazards = sorted(
        HAZARDS,
        key=lambda h: (_SEV_ORDER.get(h.severity, 9), h.name),
    )
    for h in sorted_hazards:
        hay = f"{h.name} {h.severity} {h.dc}".lower()
        if filter_text and filter_text not in hay:
            continue
        items.append(
            f"<button class='list-item' data-slug='{esc(h.slug)}'>"
            f"<span class='li-name'>{esc(h.name)}</span>"
            f"<span class='li-meta'>{esc(h.severity.title())} &middot; DC {esc(h.dc)}</span>"
            f"</button>"
        )
    set_html("#env-list", "".join(items) or "<p class='muted'>No matches.</p>")


def show_environment(slug, *, update_hash=True):
    body = ENV_BODY.get(slug)
    if body is None:
        return False
    set_html(
        "#env-detail",
        f"<div class='out-top'>{copy_btn()}</div>"
        f"<article class='statblock'>{md(body)}</article>"
        f"{md_src(body)}",
    )
    for node in document.querySelectorAll("#env-list .list-item"):
        node.classList.toggle("active", node.dataset.slug == slug)
    if update_hash:
        window.location.hash = f"environment/{slug}"
    return True


def on_environment_search(event):
    render_environments(el("#env-search").value)


def on_environment_click(event):
    btn = event.target.closest(".list-item")
    if btn is not None:
        show_environment(btn.dataset.slug)


# --------------------------------------------------------------------------- #
# Locations tab
# --------------------------------------------------------------------------- #
_TIER_ORDER = {"modest": 0, "notable": 1, "grand": 2}


def render_locations(filter_text=""):
    filter_text = filter_text.strip().lower()
    items = []
    sorted_locations = sorted(
        LOCATIONS,
        key=lambda loc: (
            faction_label(loc.faction),
            _TIER_ORDER.get(loc.tier, 9),
            loc.name,
        ),
    )
    for loc in sorted_locations:
        hay = f"{loc.name} {faction_label(loc.faction)} {loc.tier} {loc.type} {loc.status}".lower()
        if filter_text and filter_text not in hay:
            continue
        living = " &middot; inhabited" if loc.status == "inhabited" else ""
        items.append(
            f"<button class='list-item' data-slug='{esc(loc.slug)}'>"
            f"<span class='li-name'>{esc(loc.name)}</span>"
            f"<span class='li-meta'>{esc(faction_label(loc.faction))} &middot; "
            f"{esc(loc.tier.title())} site{living}</span>"
            f"</button>"
        )
    set_html("#loc-list", "".join(items) or "<p class='muted'>No matches.</p>")


def show_location(slug, *, update_hash=True):
    body = LOC_BODY.get(slug)
    if body is None:
        return False
    set_html(
        "#loc-detail",
        f"<div class='out-top'>{copy_btn()}</div>"
        f"<article class='statblock'>{md(body)}</article>"
        f"{md_src(body)}",
    )
    for node in document.querySelectorAll("#loc-list .list-item"):
        node.classList.toggle("active", node.dataset.slug == slug)
    if update_hash:
        window.location.hash = f"location/{slug}"
    return True


def on_location_search(event):
    render_locations(el("#loc-search").value)


def on_location_click(event):
    btn = event.target.closest(".list-item")
    if btn is not None:
        show_location(btn.dataset.slug)


# --------------------------------------------------------------------------- #
# Reference tab (loot tables + environmental hazards)
# --------------------------------------------------------------------------- #
def render_reference():
    blocks = ["<h2 class='ref-title'>Loot &amp; discovery tables</h2>"]
    for slug in ("nothing", "mundane", "magic", "wondrous"):
        cat = DATA["loot"][slug]
        title = f"{esc(cat['name'])} <span class='muted'>(d20 {esc(cat['range'])})</span>"
        blocks.append(collapsible(title, cat["body"]))
    blocks.append("<h2 class='ref-title'>Environmental hazards</h2>")
    for h in HAZARDS:
        title = f"{esc(h.name)} <span class='muted'>({esc(h.severity)} severity)</span>"
        blocks.append(collapsible(title, ENV_BODY[h.slug]))
    set_html("#ref-out", "".join(blocks))


# --------------------------------------------------------------------------- #
# Scaling guide tab
# --------------------------------------------------------------------------- #
def _pct(weight, total):
    return round(100 * weight / total) if total else 0


def scaling_party_example_md(levels):
    """Worked numbers for the party currently entered on the Scaling tab."""
    avg_level = sum(levels) / len(levels)
    party_size = len(levels)
    budgets = {d: encounter.budget_for(levels, d) for d in encounter.DIFFICULTIES}
    deadly = int(round(budgets["high"] * encounter.DEADLY_BUDGET_MULTIPLIER))
    gold_mult = loot.gold_multiplier(levels)
    party_scale = party_size / 4.0
    if avg_level <= 4:
        tier_mult = 1.0
        tier_label = "1 (levels 1–4)"
    elif avg_level <= 10:
        tier_mult = 2.0
        tier_label = "2 (levels 5–10)"
    elif avg_level <= 16:
        tier_mult = 4.0
        tier_label = "4 (levels 11–16)"
    else:
        tier_mult = 8.0
        tier_label = "8 (levels 17–20)"
    weights = loot.magic_tier_weights(avg_level, party_size)
    total_w = sum(weights.values())
    guardian_lo = budgets["high"]
    guardian_hi = budgets["high"] * 2
    per_char = []
    for lv in levels:
        low, mod, high = encounter.XP_BUDGET_PER_CHARACTER[lv]
        per_char.append(f"| {lv} | {low:,} | {mod:,} | {high:,} |")
    per_char_table = "\n".join(per_char)
    return f"""## Your party — worked example

**Party:** {party_line(levels)} (average level **{avg_level:g}**)

### Encounter XP budgets (2024 DMG)

Each character contributes a row from the table below; the party budget is the **sum**. There is **no monster-count multiplier** in 2024 — monster XP values are added directly.

| Level | Low | Moderate | High |
| --- | --- | --- | --- |
{per_char_table}
| **Total ({party_size} PCs)** | **{budgets['low']:,}** | **{budgets['moderate']:,}** | **{budgets['high']:,}** |

- **Travel roll 7–10 (Minor)** uses the **Low** budget ({budgets['low']:,} XP).
- **Travel roll 4–6 (Medium)** uses **Moderate** ({budgets['moderate']:,} XP).
- **Travel roll 2–3 (Dangerous)** uses **High** ({budgets['high']:,} XP).
- **Natural 1 (Deadly special)** uses High × {encounter.DEADLY_BUDGET_MULTIPLIER:g} = **{deadly:,} XP**.

The encounter builder finds monster mixes whose total XP is between **75% and 100%** of the chosen budget (adjustable via *Min fill*).

### Loot gold scaling

Baseline tables assume **4 characters at low level**. Your multiplier:

`({party_size} ÷ 4) × {tier_mult:g} ({tier_label}) = **×{gold_mult:g}**`

- Flat coin values are rewritten (e.g. 25 gp → {max(1, int(round(25 * gold_mult)))} gp).
- Dice amounts stay rollable and show the multiplier plus an average (e.g. 4d10 gp ×{gold_mult:g}).

### Magic treasure tier odds

When the travel roll is **17–19**, the tool picks a rarity tier before rolling the item:

| Tier | Weight | ≈ Chance |
| --- | --- | --- |
| Common | {weights['Common']:g} | {_pct(weights['Common'], total_w)}% |
| Uncommon | {weights['Uncommon']:g} | {_pct(weights['Uncommon'], total_w)}% |
| Rare | {weights['Rare']:g} | {_pct(weights['Rare'], total_w)}% |

Party size above 4 adds **+0.5** to the Rare weight per extra character (currently **+{max(0, party_size - 4) * 0.5:g}**).

### Wondrous guardian (natural 20)

If a guardian monster is rolled, it is chosen from creatures with XP between **{guardian_lo:,}** and **{guardian_hi:,}** (High budget to double High) — a boss-tier threat, not a fair fight.
"""


def scaling_reference_md():
    """Static explanation of the scaling rules (does not depend on party input)."""
    xp_rows = []
    for lv in range(1, 21):
        low, mod, high = encounter.XP_BUDGET_PER_CHARACTER[lv]
        xp_rows.append(f"| {lv} | {low:,} | {mod:,} | {high:,} |")
    xp_table = "\n".join(xp_rows)
    band_rows = []
    for lo, hi, label, diff, deadly in encounter.TRAVEL_BANDS:
        deadly_note = f" (High × {encounter.DEADLY_BUDGET_MULTIPLIER:g})" if deadly else ""
        roll = str(lo) if lo == hi else f"{lo}–{hi}"
        band_rows.append(f"| {roll} | {label} | {diff.title()}{deadly_note} |")
    band_table = "\n".join(band_rows)
    return {
        "overview": """## Overview

The Great Northwood travel tables are tuned for a **baseline party of 4 at 6th level**. Instead of maintaining separate tables per party, both tools read your **party size** and **character levels** and scale the results.

- **Encounters** use the 2024 DMG *XP budget per character* table. Budget = sum of each PC's value for the chosen difficulty. Monster mixes must fit inside that budget.
- **Loot** auto-scales coin and value amounts by party size and average level, and skews magic-item rarity toward higher tiers as the party levels up.

Enter your party above and press **Update examples** to see the exact numbers.""",
        "encounters": f"""## Encounter budgets — full reference

### Per-character XP budget (2024 DMG)

| Level | Low | Moderate | High |
| --- | --- | --- | --- |
{xp_table}

**Formula:** `party budget = sum of each character's value for the difficulty`

Example: four 6th-level characters at Moderate → 1,000 + 1,000 + 1,000 + 1,000 = **4,000 XP**.

### 2024 rules reminder

- Monster XP is **summed directly** — there is no 2014-style multiplier for multiple monsters.
- The tool targets encounters using **75–100%** of the budget by default (*Min fill* = 0.75).
- **Mix mode:** exactly *N* monsters, up to *M* different kinds.
- **Boss + minions:** one creature at 40–70% of budget, the rest identical minions.

Environmental challenges are separate: hazards match the encounter **severity** (low / moderate / high) and are never mixed into a monster XP total.""",
        "travel": f"""## Travel d20 — encounter half (1–10)

| d20 | Band | Difficulty used |
| --- | --- | --- |
{band_table}

Rolls **11–20** are loot — see the Loot tab and sections below.""",
        "loot_gold": """## Loot — gold and mundane values

Table text is written for **4 PCs at low level**. At roll time:

```
gold multiplier = (party_size ÷ 4) × treasure tier
```

| Average level | Treasure tier |
| --- | --- |
| 1–4 | ×1 |
| 5–10 | ×2 |
| 11–16 | ×4 |
| 17–20 | ×8 |

**Examples**

| Party | Calculation | Multiplier |
| --- | --- | --- |
| 4 PCs, level 6 | (4÷4) × 2 | ×2 |
| 6 PCs, level 6 | (6÷4) × 2 | ×3 |
| 4 PCs, level 12 | (4÷4) × 4 | ×4 |
| 5 PCs, level 12 | (5÷4) × 4 | ×5 |

Flat gp amounts are replaced with the scaled value. Dice expressions (e.g. `4d10 gp`) stay rollable; the output adds `×N` and an approximate total.

**Nothing found** (rolls 11–13) is flavour only — no scaling.""",
        "loot_magic": """## Loot — magic treasure (rolls 17–19)

The tool first picks a **rarity tier**, then a random item from that tier's list.

### Tier weights by average level

| Avg. level | Common | Uncommon | Rare |
| --- | --- | --- | --- |
| 1–4 | 6 | 3 | 1 |
| 5–7 | 3 | 5 | 2 |
| 8–10 | 2 | 5 | 3 |
| 11–13 | 1 | 4 | 5 |
| 14+ | 1 | 3 | 6 |

These are **relative weights**, not percentages. A tier is only eligible if its list has items.

### Party-size nudge

Each character **above 4** adds **+0.5** to the Rare weight (e.g. a party of 6 gets +1 Rare).

Magic items are not re-priced by level — only the **tier odds** change.""",
        "wondrous": """## Loot — wondrous discovery (natural 20)

The reward is drawn from the merged Treasures + Discoveries pool. Additionally, a **guardian** is rolled with equal odds:

1. **None** — unguarded this time.
2. **Environmental** — a random **high-severity** hazard from the environments list.
3. **Monster** — a **boss-tier** creature whose XP falls between the party's **High budget** and **twice** that High budget.

The guardian monster rule uses the same XP budget math as encounters, but picks a single threatening creature rather than a balanced mix.""",
    }


def render_scaling(levels=None):
    if levels is None:
        levels = [6, 6, 6, 6]
    sections = scaling_reference_md()
    blocks = [
        "<h2 class='ref-title'>Party scaling</h2>",
        f"<div class='scaling-example'>{md(scaling_party_example_md(levels))}</div>",
        collapsible("Overview", sections["overview"], open_=True),
        collapsible("Encounter budgets", sections["encounters"]),
        collapsible("Travel roll bands", sections["travel"]),
        collapsible("Loot — gold scaling", sections["loot_gold"]),
        collapsible("Loot — magic tier weights", sections["loot_magic"]),
        collapsible("Wondrous guardians", sections["wondrous"]),
    ]
    set_html("#scaling-out", "".join(blocks))


def run_scaling_preview(event=None):
    levels, err = parse_levels(
        el("#sc-levels").value, el("#sc-party-size").value, el("#sc-level").value
    )
    if err:
        set_html("#scaling-out", f"<p class='error'>{esc(err)}</p>")
        return
    render_scaling(levels)


# --------------------------------------------------------------------------- #
# Wire up
# --------------------------------------------------------------------------- #
def _guard(label, fn, *args, **kwargs):
    """Run a setup step, surfacing any error to the console instead of aborting
    the whole setup (one failing tab must never silently break the others)."""
    try:
        fn(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001 - report, don't crash the app
        import traceback
        traceback.print_exc()
        window.console.error(f"[{label}] {exc}")


def setup():
    on("#enc-run", "click", run_encounter)
    on("#enc-rolld20", "click", roll_d20_encounter)
    on("#loot-run", "click", run_loot)
    on("#loot-rolld20", "click", roll_d20)
    on("#sc-run", "click", run_scaling_preview)
    on("#mon-search", "input", on_bestiary_search)
    on("#mon-list", "click", on_bestiary_click)
    on("#env-search", "input", on_environment_search)
    on("#env-list", "click", on_environment_click)
    on("#loc-search", "input", on_location_search)
    on("#loc-list", "click", on_location_click)
    window.addEventListener("hashchange", create_proxy(on_hash_change))

    _guard("bestiary", render_bestiary)
    _guard("environments", render_environments)
    _guard("locations", render_locations)
    _guard("reference", render_reference)
    _guard("scaling", render_scaling)
    if not apply_route_from_hash():
        if MONSTERS:
            _guard("monster-default", show_monster, MONSTERS[0].slug, update_hash=False)
        if HAZARDS:
            _guard("hazard-default", show_environment, HAZARDS[0].slug, update_hash=False)
        if LOCATIONS:
            _guard("location-default", show_location, LOCATIONS[0].slug, update_hash=False)

    # Tell the page Python is ready (hides the loading splash).
    document.body.classList.add("py-ready")


setup()
