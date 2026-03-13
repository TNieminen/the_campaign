The Campaign
============

This repository contains a Unity game project implemented in **C#**.

### Project layout

- **`src/`**: Unity project root (opened directly in the Unity editor).
  - Unity project folders:
    - `src/Assets/` – Unity scenes, prefabs, art/audio assets, and Unity-facing scripts.
    - `src/ProjectSettings/`, `src/Packages/`, `src/UserSettings/` – Unity configuration and package data.
    - `src/Library/` – Unity’s local cache (generated, ignored by git).
  - C# code layout (see `src/structure.md` for details):
    - `src/StoryEngine/Runtime/` – framework-agnostic story engine (no Unity dependencies).
    - Planned/Unity integration namespaces under `src/StoryEngine/Unity/`, `src/StoryUI/`, `src/Game/`, etc.
- **`tools/`**: Supporting tools such as the CLI runner for the story engine.
- **`notes/`**: All documentation, design notes, story material, AI guidance, and development planning.
  - When in doubt, any non-code information should be written under `notes/`.

### Notes and documentation

- See `notes/structure.md` for an overview of how information is organized under `notes/`.
- Existing subfolders include:
  - `notes/story/` for world, characters, plot, and quest design.
  - `notes/development/` for technical notes, tasks, and implementation plans.
  - `notes/ai/` for rules and instructions for AI assistants.
   - `notes/art/` for art direction, asset lists, and art/audio budgeting.

### Code

- Place all gameplay and tooling code in **C#** under `src/`.
- The **core story engine** is in `src/StoryEngine/Runtime/` and is independent of Unity.
- Unity components (MonoBehaviours, ScriptableObjects, etc.) live under `src/Assets/` in standard Unity folders (e.g. `Assets/Scripts/`) and reference the story engine where needed.

This file should be updated as the project structure evolves.
