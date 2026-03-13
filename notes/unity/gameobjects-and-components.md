# Unity: GameObjects, Components, Hierarchy, Inspector

## Core concept

- **GameObject**:
  - A named entity in the **Hierarchy** (e.g. `Main Camera`, `Canvas`, `ChoicesContainer`, `StoryController`).
  - Always has a `Transform` (or `RectTransform` for UI) that defines position/rotation/scale or screen-space rect.
  - By itself, does nothing until you attach components.

- **Component**:
  - A piece of behaviour or data attached to a GameObject (shown in the **Inspector** when that GameObject is selected).
  - Examples: `Camera`, `Light`, `Image`, `TextMeshProUGUI`, `Button`, `GridLayoutGroup`, `StorySceneController`.
  - You add/remove them via **Add Component** in the Inspector.

## Hierarchy vs Inspector

- **Hierarchy window**:
  - Shows the **tree of GameObjects** in the current scene.
  - You use it to create, delete, parent, and select objects (e.g. making `ChoicesContainer` a child of `Canvas`).

- **Inspector window**:
  - Shows the **components and properties** for the currently selected GameObject.
  - This is where you:
    - Set references (e.g. drag `DescriptionText` into `StorySceneController.descriptionText`).
    - Add components like `Grid Layout Group` or `Canvas Scaler`.
    - Configure visuals and behaviour (fonts, colors, anchors, scripts, etc.).

In practice: **pick “what object” you’re editing in the Hierarchy, then edit “what it does / how it looks” in the Inspector.**

