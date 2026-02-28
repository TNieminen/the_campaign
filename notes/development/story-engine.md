Story Engine
============

The game uses a **prompt-based story system**. At each step, the player sees:

- A **situation description** (what is happening now).
- A **list of text prompts** (choices) to pick from.
- Each choice leads to another node in the story tree and may apply side effects (flags, stats, inventory, etc.).

## Core concepts

- **Story Node**
  - Unique ID (e.g. `camp_intro_001`).
  - Text shown to the player (narration, dialogue, description).
  - Optional conditions for entering this node (flags, quest state).
  - List of **Choices**.

- **Choice**
  - Text prompt the player selects.
  - Target node ID (where this choice leads).
  - Optional conditions (only show if condition is true).
  - Optional effects (set flags, change variables, give items, start quests).

- **Flags / Variables**
  - Booleans or numeric values controlling branches.
  - Used for:
    - Locking/unlocking choices.
    - Tracking long-term consequences.
    - Changing text (optional).

## Engine responsibilities

- Load all story data into memory from ScriptableObjects.
- Track the **current node** and the **current game state** (flags, variables).
- For the current node:
  - Evaluate conditions to determine which choices are visible.
  - Present the list of valid prompts.
- When a choice is selected:
  - Apply effects (update flags, variables, quests).
  - Transition to the target node.
  - Repeat.

## Storage decision

- **Decision**: Story data will be stored primarily in **ScriptableObjects**.
- We will:
  - Represent nodes and (optionally) graphs as ScriptableObject assets.
  - Build a dictionary at runtime mapping node IDs to ScriptableObject instances.
  - Use IDs and/or direct references to connect choices to target nodes.
- This keeps the system Unity-native and inspector-friendly, while still allowing future tools (e.g. custom node editor).

## Guidelines for managing complexity

- **Think in modules, not one giant graph**
  - Split the story into separate graphs by chapter, region, or quest (e.g. `camp_*`, `city_*`, `dungeon_*`).
  - Each module should have a small set of well-defined entry and exit nodes.

- **Use strong, hierarchical IDs**
  - Encode structure into IDs (e.g. `camp.intro.001`, `city.market.003`, `quest.bandits.010`).
  - Use consistent prefixes/suffixes (`CAMP_`, `CITY_`, `*_ENTRY`, `*_EXIT`, `*_HUB`, `*_FAILURE`) to make relationships obvious.

- **Separate navigation nodes from content nodes**
  - Use hub-style nodes for navigation (e.g. “What do you do now?”).
  - Let content nodes (dialogue, descriptions, small scenes) often return back to a hub node instead of endlessly branching.

- **Rejoin branches with flags instead of endless splits**
  - Use flags/variables to remember choices, then converge branches back into shared nodes that react differently based on state.
  - Prefer shallow graphs with rich conditional logic over deeply nested trees.

- **Validate and visualize the graph**
  - Maintain tools or scripts that can:
    - Detect missing target nodes, dead ends, and unreachable nodes.
    - Export the node/edge structure for visualization in an external graph viewer if needed.

- **Adopt a scalable authoring workflow**
  - Start with a mostly linear spine, then branch only where choices are meaningful.
  - Keep a soft limit on the number of choices per node (e.g. 3–4) to avoid combinatorial explosion.
  - Document the entry/exit nodes of each module in notes so connections stay clear.

- **Debug from the player’s path**
  - During testing, record the sequence of node IDs the player traverses.
  - Use these paths to debug and refine specific flows instead of trying to reason about the entire graph at once.

## Next design steps

- Decide how to represent the **tree/graph** structure in C# (IDs, references, adjacency) using ScriptableObjects.
- Define a minimal runtime API, for example:
  - `GetCurrentNode()`
  - `GetAvailableChoices()`
  - `Choose(choiceId)`
  - `OnNodeChanged` event for the UI.

Implementation details will live in `src/` as C# code, while this document captures the **design** and **rules** of the story system.

