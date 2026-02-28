The Campaign
============

This repository contains a Unity game project implemented in **C#**.

### Project layout

- **`src/`**: All runtime and editor C# scripts for the Unity project.
- **`notes/`**: All documentation, design notes, story material, AI guidance, and development planning.
  - When in doubt, any non-code information should be written under `notes/`.

### Notes and documentation

- See `notes/structure.md` for an overview of how information is organized under `notes/`.
- Existing subfolders include:
  - `notes/story/` for world, characters, plot, and quest design.
  - `notes/development/` for technical notes, tasks, and implementation plans.
  - `notes/ai/` for rules and instructions for AI assistants.

### Code

- Place all gameplay and tooling code in **C#** under `src/`.
- Unity components (MonoBehaviours, ScriptableObjects, etc.) should live here and be referenced from the Unity project.

This file should be updated as the project structure evolves.
