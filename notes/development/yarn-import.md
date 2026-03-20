# Importing Yarn Spinner into the C# story engine

## Overview

The story engine **always loads from the repo's `notes/story` folder**. All **`.yarn`** files in that folder are loaded and merged into one graph; **`.md`** and other files are **ignored**. File names and count are arbitrary. Nodes can reference each other across files (e.g. a choice in `chapter1.yarn` can jump to a node in `chapter2.yarn`). The order in which files are read is **alphabetical by filename** so the result is deterministic.

## Where files live

- **Source of truth:** `notes/story/` in the repo. Any number of `.yarn` files, any names (e.g. `chapter1.yarn`, `chapter2.yarn`, `sidequests.yarn`).
- **Only `.yarn` files are read.** `.md` and other extensions are ignored.
- **Unity** resolves the path at runtime as `Application.dataPath/../../notes/story` (when the project is at `src/`). No need to copy Yarn into `Assets/` for the editor.

### Yarn Spinner project file (editors / VS Code)

For the **Yarn Spinner VS Code extension** and other official tooling, the project file must be named with the **`.yarnproject`** extension (not a plain `yarn_project` file). This repo has **`notes/the_campaign.yarnproject`**.

- **`sourceFiles`** globs are **relative to the folder that contains the `.yarnproject` file** (here, `notes/`). We use `story/**/*.yarn` so every `.yarn` under `notes/story/` is included (cross-file node links resolve in the graph).
- The C# game still loads only via `YarnImporter` from `notes/story/`; the `.yarnproject` is for **authoring** (validation, graph preview), not required at runtime.

## Node naming standard

**Use the `ChapterX` prefix for node titles** so it's clear which file a node belongs to and cross-file links stay readable.

- **Format:** `Chapter` + chapter/file number + descriptive name (e.g. `Chapter2CommandersReport`, `Chapter3Start`, `Chapter2ScoutReport`).
- **Apply to all nodes in a file:** Every node in `chapter2.yarn` should have a `Chapter2` prefix; every node in `chapter3.yarn` a `Chapter3` prefix; and so on.
- **Cross-file links:** When a node in one file links to a node in another, the target id makes the source file obvious (e.g. `Chapter2ScoutReport` from chapter3).

## Start node

- **In .yarn:** The **first file alphabetically** that contains a `start: NodeName` line defines the global start node. If no file has `start:`, the first node of the first file (alphabetically) is used.
- **In code/Unity:** You can pass an explicit start node id to `CreateEngineFromDirectory(..., explicitStartNodeId)` or set the **Start Node Id** field on the Story Scene Controller to override.

## How it works

- **`YarnImporter.CreateEngineFromDirectory(notesStoryPath, explicitStartNodeId?)`**:
  - Enumerates only **`*.yarn`** in the directory (ignores `.md` and others).
  - Sorts files by name and parses each; nodes are merged by **node id** (duplicate id = last file wins).
  - Picks start node: explicit argument, or first file's `start:`, or first node of first file.
- **`YarnImporter.CreateEngineFromFile(notesStoryPath, fileNameWithoutExtension)`** still exists for loading a **single** file (e.g. tests).
- Supported in .yarn:
  - `start: NodeName` (optional, at top of a file)
  - `title: NodeName` and `---` / `===`
  - `[[Display text|TargetNode]]` for options (TargetNode can be in any loaded file)
  - `<<jump NodeName>>` is ignored (links come from `[[...|...]]`).
- **Not supported yet:** `<<set>>`, `<<if>>`; only nodes and options.

## Using it in Unity

1. **Story Scene Controller** loads **all** `.yarn` files from `notes/story`. Optional **Start Node Id** overrides the start node.
2. No need to assign a TextAsset; files are read from disk when the scene runs.
3. For **builds**, you may need to copy the needed `.yarn` files into `StreamingAssets` or `Resources` and adjust loading; in-editor always uses `notes/story`.

## Creating an engine in code

```csharp
using TheCampaign.StoryEngine;

// Load all .yarn from directory (ignores .md)
string notesStoryPath = @"C:\path\to\repo\notes\story";
var engine = YarnImporter.CreateEngineFromDirectory(notesStoryPath);

// Optional: force a specific start node
var engine = YarnImporter.CreateEngineFromDirectory(notesStoryPath, explicitStartNodeId: "Chapter2CommandersReport");

// Single file (e.g. tests)
var engine = YarnImporter.CreateEngineFromFile(notesStoryPath, "chapter1");

// From string
var engine = YarnImporter.CreateEngine(yarnContent);
```

## File format reference

- **Start (optional):** `start: NodeName` at the top, then `---` or a blank line.
- **Node:** `title: NodeName` then `---`, then body, then `===`.
- **Option:** `[[Display text|TargetNode]]` on its own line.
