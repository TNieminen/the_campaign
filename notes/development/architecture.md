Story Engine Architecture
=========================

This document describes the architecture of the **story engine** as a testable C# state machine, and how it connects to Unity and ScriptableObject data.

## 1. High-level design goals

- **Engine is framework-agnostic**
  - Implement the story engine as a pure C# library (no `UnityEngine` types).
  - Make it possible to unit test all branching and state changes outside Unity.

- **Unity is an integration layer**
  - Unity is responsible for:
    - Loading story data (from ScriptableObjects).
    - Creating and configuring the engine.
    - Displaying the current node and choices via UI.
    - Forwarding player input (choice selection) to the engine.

- **Story content is data**
  - Individual nodes, choices, and chapters are data (ScriptableObjects), not separate C# classes.
  - The same engine code should work for any set of nodes/chapters.

## 2. Core engine (pure C#)

The core engine lives under `src/StoryEngine/Runtime/` as plain C# classes and interfaces.

- **Key types**
  - `StoryEngine`
    - Holds:
      - `string CurrentNodeId`
      - `GameState State` (flags, variables, quest states, etc.)
      - `IDictionary<string, StoryNode> Nodes`
    - Responsibilities:
      - Initialize from a list/dictionary of `StoryNode` definitions and an initial node ID.
      - Return the current node and available choices.
      - Apply a choice:
        - Validate that it is available.
        - Apply its effects to `GameState`.
        - Move to the target node.
      - Optionally expose events/callbacks (e.g. `OnNodeChanged`).

  - `StoryNode`
    - `string Id`
    - `string Text`
    - `IReadOnlyList<Choice> Choices`
    - Optional:
      - Entry conditions (node-level `ICondition` list).

  - `Choice`
    - `string Id` (unique within the node).
    - `string Text`
    - `string TargetNodeId`
    - `IReadOnlyList<ICondition>` Conditions
    - `IReadOnlyList<IEffect>` Effects

  - `GameState`
    - Stores flags, numeric variables, quest states, etc.
    - Exposed via a simple API that conditions/effects can query and mutate.

  - `ICondition` / `IEffect`
    - Interfaces or abstract base classes that operate on `GameState`.
    - Examples:
      - `FlagIsTrueCondition`, `VariableAtLeastCondition`
      - `SetFlagEffect`, `IncrementVariableEffect`, `SetQuestStateEffect`

- **Engine operations (example API)**
  - `StoryNode GetCurrentNode()`
  - `IEnumerable<Choice> GetAvailableChoices()`
  - `void Choose(string choiceId)`
  - Events:
    - `event Action<StoryNode> OnNodeChanged`

The core engine must not know about ScriptableObjects, scenes, UI, or any Unity-specific classes.

## 3. Unity integration layer

The Unity-facing part lives under `src/StoryEngine/Unity/` (or another Unity-specific namespace).

- **ScriptableObject data**
  - `StoryNodeAsset : ScriptableObject`
    - Fields mirroring the core `StoryNode` data:
      - `string id`
      - `string text`
      - `List<ChoiceAsset> choices`
      - Optional: conditions/effects configuration.
  - `ChoiceAsset`
    - `string id`
    - `string text`
    - Reference or ID for target node (e.g. `StoryNodeAsset targetNode` or `string targetNodeId`).
    - Serialized condition/effect setup.
  - Optional `StoryGraphAsset`
    - Contains a list of `StoryNodeAsset` instances and metadata for a chapter/region.

- **Adapter / factory**
  - A converter that builds core engine data from ScriptableObjects:
    - E.g. `StoryEngineFactory` with a method:
      - `StoryEngine Create(StoryGraphAsset graph, GameState initialState)`
    - Responsibilities:
      - Scan `StoryGraphAsset` (or a folder of `StoryNodeAsset`s).
      - Build a dictionary of `StoryNode` objects for the core engine.
      - Resolve ScriptableObject references into `TargetNodeId` strings or vice versa.

- **Runtime MonoBehaviour**
  - `StoryRunner : MonoBehaviour`
    - Holds a reference to:
      - A `StoryGraphAsset` to load at start.
      - UI components that render text and choices.
    - On `Start()`:
      - Uses `StoryEngineFactory` to create a `StoryEngine` instance.
      - Subscribes to `OnNodeChanged`.
      - Renders the initial node.
    - When the player selects a choice:
      - Calls `StoryEngine.Choose(choiceId)`.
      - UI updates via `OnNodeChanged`.

## 4. Unit testing strategy

- **Test the core engine in isolation**
  - Write tests that instantiate `GameState`, a collection of `StoryNode` objects, and `StoryEngine` directly (no ScriptableObjects).
  - Cover:
    - Visible/hidden choices based on conditions.
    - Flags and variables being set correctly by effects.
    - Correct node transitions for various paths.
    - Handling of invalid choice IDs or misconfigured nodes.

- **Keep conditions and effects small and composable**
  - Each `ICondition` and `IEffect` implementation should be testable individually with simple `GameState` instances.
  - This avoids complex logic being hidden inside the Unity layer.

- **Minimal Unity-dependent tests**
  - Unity-side tests (e.g. PlayMode/Editor tests) focus on:
    - Verifying ScriptableObjects can be converted into engine data.
    - Ensuring UI reacts properly to engine events.
  - Most logic should remain in the pure C# layer.

## 5. Story data organization (ScriptableObjects)

- **Chapters and regions as graphs**
  - In Unity, organize ScriptableObject assets by chapter/region:
    - `Assets/Story/Chapters/Chapter1/Intro/...`
    - `Assets/Story/Chapters/Chapter2/...`
  - Each chapter can have its own `StoryGraphAsset` listing its nodes.

- **Stable IDs and modular graphs**
  - Use the ID conventions and modular guidelines from `story-engine.md`:
    - Hierarchical IDs (`camp.intro.001`, `city.market.003`, etc.).
    - Clear entry/exit nodes per graph.
  - The engine itself only cares about IDs and connectivity; Unity assets are simply a source of those definitions.

## 6. Benefits of this architecture

- **Highly testable**: core logic is independent of Unity and easy to exercise with unit tests.
- **Flexible**: the same engine can be reused in other contexts or tools (e.g. command-line simulation, editor tooling).
- **Maintainable**: clear boundary between:
  - Story rules and state transitions (core engine).
  - Data representation (ScriptableObjects).
  - Presentation and input (Unity scene/UI).

