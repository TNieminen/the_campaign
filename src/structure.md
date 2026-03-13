Source Structure
================

All C# code for **The Campaign** lives under `src/`. The story engine is implemented as a **framework-agnostic C# state machine**, with Unity acting as an integration layer.

Unity opens the project at `src/`, which contains the standard Unity folders:

- `src/Assets/`
  - Unity project content:
    - Scenes, prefabs, images, audio, materials, etc.
    - Unity-facing C# scripts (e.g. MonoBehaviours and ScriptableObjects) under `Assets/Scripts/` and related folders.
  - These scripts reference the story engine runtime and drive the in-game presentation.
- `src/ProjectSettings/`, `src/Packages/`, `src/UserSettings/`
  - Unity configuration, package manifests, and editor preferences.
- `src/Library/`
  - Unity’s local cache and build artefacts (generated; ignored in git).

## High-level C# layout

- `src/StoryEngine/Runtime/`
  - Pure C# story engine (no Unity dependencies).
  - Contains the state machine, data types (nodes, choices, game state), and core interfaces.
- `src/StoryEngine/Unity/` (planned)
  - Unity-specific adapters for ScriptableObjects and MonoBehaviours.
  - Loads data from assets, constructs the core engine, and connects it to UI.
- Future:
  - `src/StoryUI/` for generic story UI components.
  - `src/Game/` (or `Gameplay/`) for game-specific orchestration and systems.

## Current contents

- `StoryEngine/Runtime/StoryCore.cs`
  - Core story engine types:
    - `GameState`
    - `ICondition`, `IEffect`
    - `StoryNode`, `Choice`
    - `StoryEngine`
  - This file is Unity-agnostic and can be unit tested independently.

- `StoryEngine/Runtime/Story/Chapter1/…`
  - Individual files for Chapter 1 nodes, e.g.:
    - `CampPreludeCommandersReport.cs`
    - `CampPreludeScoutReport.cs`
    - `CampSonLeadsChargeDecision.cs`
    - `CampSonLeadsChargeAllowOutcome.cs`
    - `CampSonLeadsChargeDenyOutcome.cs`
  - `Chapter1Entry.cs` composes these into a `StoryEngine` instance and defines the starting node.

- `tools/Cli/Program.cs`
  - Simple command-line runner for the story engine.
  - Currently runs **Chapter 1** via `Chapter1Entry.CreateEngine()`:
    - Prints the current node description.
    - Lists available choices and lets the user pick by number.
    - Moves through the story until there are no more choices or the user quits.
    - Prints the final game state (flags and string values) at the end.
  - See `tools/Cli/README.md` for details on prerequisites and how to run it.

As the project grows, this document should be updated to reflect new namespaces, folders, and responsibilities.

