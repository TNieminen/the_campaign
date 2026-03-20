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


### How to use this folder

- Keep this `structure.md` file up to date whenever new major sections or folders are added.
- Prefer short, focused markdown files over very long mixed documents.
- Reference these notes from code comments only when necessary; most details should live here.

### Relationship to code

- All C# scripts and other code live under `src/`.
- Notes can refer to specific files or classes using backticks (for example, `src/SomeSystem.cs`).
