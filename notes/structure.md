Notes Structure
===============

All non-code information for **The Campaign** lives under the `notes/` folder.  
When in doubt, put it here rather than in `src/`.

### Top-level categories

- `notes/story/`
  - World, factions, characters, plot arcs, quests, and narrative structure.
  - Yarn scripts (`.yarn`) live here; see also `notes/the_campaign.yarnproject` for Yarn Spinner editor/VS Code (see `development/yarn-import.md`).
- `notes/development/`
  - Technical design notes, tasks and TODOs, implementation plans, and experiments.
  - See `running-tests.md` for how to run the unit tests (xUnit, from repo root).
- `notes/unity/`
  - Unity specific notes, how the editor internals works. Low and high level concepts
- `notes/csharp/`
  - C# related notes about coding practices, templates etc
- `notes/ai/`
  - Rules, conventions, and guidance for AI assistants working on this project.
- `notes/art/`
  - Visual art direction, asset lists, budgeting estimates, and audio (music/SFX) planning.
- `notes/dnd/`
  - Tabletop D&D reference and content, organized by region/topic into buckets.
  - `greath-northwood/` — wilderness travel content for the Great Northwood: `mechanic.md` (the d20 travel roll), `encounters.md` (d20 1–10), and the `loot/` folder (d20 11–20).
    - `greath-northwood/monsters/` — one stat block per creature, flat (no difficulty subfolders). Each file starts with YAML frontmatter (`name`, `cr`, `xp`, `size`, `type`, `summary`) followed by the stat block and an `Appearance` paragraph. See its `README.md` for the schema and a CR-sorted roster.
    - `greath-northwood/environments/` — one environmental challenge per file (hazards, terrain, puzzles), flat. Each file starts with YAML frontmatter (`name`, `kind`, `severity`, `dc`, `damage`, `check`, `summary`) followed by a description and resolution. `severity` (low/moderate/high) maps to the tool's difficulty. See its `README.md`.
    - `greath-northwood/loot/` — one file per loot category (`nothing-found.md`, `mundane-treasure.md`, `magic-treasure.md`, `wondrous-discovery.md`), each with YAML frontmatter (`name`, `category`, `die`, `range`, `summary`) and the option list(s). See its `README.md` for the schema and category table.
    - `greath-northwood/tools/encounter.py` — Python CLI (standard library only) that computes 2024 (5.5e) encounter XP budgets from party input and finds matching encounters. Accepts the players' travel d20 via `--roll` (1–10, mapping to a difficulty band; a natural 1 is a "deadly special" above the High budget) or an explicit `--difficulty`. `--filter monster|environmental|both` (default both) chooses whether to draw monster fights from `monsters/`, environmental challenges from `environments/`, or both (never mixed in one encounter). Monster mode supports `mix` and `boss-minions`; run with `--help` for difficulty-band descriptions and examples.
    - `greath-northwood/tools/loot.py` — Python CLI (standard library only) that takes the players' travel d20 `--roll` (11–20) plus party size and level, maps the roll to a loot category in `loot/`, and randomizes the reward. Party level skews magic-item rarity; a natural-20 also rolls a guardian with equal odds of none / a high-severity environmental hazard / a boss-tier monster (sourced from `encounter.py`'s data — see `roll_guardian()`).


### How to use this folder

- Keep this `structure.md` file up to date whenever new major sections or folders are added.
- Prefer short, focused markdown files over very long mixed documents.
- Reference these notes from code comments only when necessary; most details should live here.

### Relationship to code

- All C# scripts and other code live under `src/`.
- Notes can refer to specific files or classes using backticks (for example, `src/SomeSystem.cs`).
