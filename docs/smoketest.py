"""CPython smoke test for the PyScript app (docs/app.py).

Stubs the browser-only ``pyscript`` modules so ``app.py`` can be imported and
exercised under plain CPython. Verifies the data bundle loads and that the
location features (loot finds + encounters happening at a location) behave:
correct discovery rates, tier matching, and markdown deep links.

Run from the repo root or the docs folder:

    python docs/smoketest.py
"""
import os
import random
import sys
import types

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")


# --------------------------------------------------------------------------- #
# Minimal PyScript / DOM stubs
# --------------------------------------------------------------------------- #
class Node:
    def __init__(self):
        self.innerHTML = ""
        self.value = ""
        self.classList = types.SimpleNamespace(
            toggle=lambda *a, **k: None, add=lambda *a, **k: None,
            remove=lambda *a, **k: None,
        )
        self.dataset = types.SimpleNamespace(slug="", tab="")

    def addEventListener(self, *a, **k):
        pass

    def querySelectorAll(self, *a, **k):
        return []


class Doc:
    body = Node()

    def querySelector(self, *a, **k):
        return Node()

    def querySelectorAll(self, *a, **k):
        return []


class Win:
    class location:
        hash = ""

    console = types.SimpleNamespace(error=lambda *a, **k: print("console.error", *a))
    marked = types.SimpleNamespace(parse=lambda s: s, parseInline=lambda s: s)

    def addEventListener(self, *a, **k):
        pass


def _install_stubs():
    pyscript = types.ModuleType("pyscript")
    pyscript.document = Doc()
    pyscript.window = Win()
    ffi = types.ModuleType("pyscript.ffi")
    ffi.create_proxy = lambda f: f
    pyscript.ffi = ffi
    sys.modules["pyscript"] = pyscript
    sys.modules["pyscript.ffi"] = ffi


def _rate(fn, sev_or_slug, locations, expected_tier, n=4000):
    """Return (hit fraction, all-tiers-matched) for a location roller."""
    hits, ok, rng = 0, True, random.Random(1)
    for _ in range(n):
        loc = fn(sev_or_slug, rng, locations)
        if loc is not None:
            hits += 1
            ok = ok and loc.tier == expected_tier
    return hits / n, ok


def main():
    _install_stubs()
    import app  # noqa: E402  (runs setup() with the stubs in place)

    assert app.LOCATIONS, "no locations loaded from data.json"
    assert len(app.LOCATIONS) == len(app.LOC_BODY)
    print(f"locations loaded: {len(app.LOCATIONS)}")

    # Locations tab functions render without error.
    app.render_locations()
    app.render_locations("valvela")
    assert app.show_location(app.LOCATIONS[0].slug) is True

    # Loot finds: scaling discovery chance + tier match (see loot.roll_location).
    print("\n[loot] category -> (rate, tier_ok)")
    for slug, tier in (("mundane", "modest"), ("magic", "notable"), ("wondrous", "grand")):
        rate, ok = _rate(app.loot.roll_location, slug, app.LOCATIONS, tier)
        print(f"  {slug:9} {rate:.3f}  tier_ok={ok}")
        assert ok
    assert app.loot.roll_location("nothing", random.Random(0), app.LOCATIONS) is None

    # Encounters: scaling site chance + tier match (see encounter.roll_encounter_location).
    print("\n[encounter] severity -> (rate, tier_ok)")
    for sev, tier in (("low", "modest"), ("moderate", "notable"),
                      ("high", "grand"), ("deadly", "grand")):
        rate, ok = _rate(app.encounter.roll_encounter_location, sev, app.LOCATIONS, tier)
        print(f"  {sev:9} {rate:.3f}  tier_ok={ok}")
        assert ok
    assert app.encounter.encounter_severity("high", deadly=True) == "deadly"
    assert app.encounter.encounter_severity("low") == "low"

    # Markdown carries clickable deep links for both flows.
    loc = app.LOCATIONS[0]
    _, loot_md = app.format_location(loc)
    assert app.location_href(loc.slug) in loot_md
    enc_md = app.encounter_markdown(
        [6, 6, 6, 6], "high", 9800, [], [],
        band={"label": "Dangerous", "difficulty": "high", "deadly": False},
        roll=2, location=loc,
    )
    assert "Encounter site:" in enc_md and app.location_href(loc.slug) in enc_md

    print("\nOK")


if __name__ == "__main__":
    main()
