# YarnImporter

Imports Yarn Spinner (`.yarn`) content into the campaign story engine (`StoryNode`, `Choice`, `StoryEngine`). Supports multiple files, cross-file node links, and optional start node override.

## How to run / use it

### Load all story files from the repo (typical)

Story files live in **`notes/story`**. Only **`.yarn`** files are read; `.md` is ignored. Files are merged by node id (alphabetical file order).

```csharp
using TheCampaign.StoryEngine;

// Path to notes/story (e.g. from repo root, or Unity: Application.dataPath + "/../../notes/story")
string notesStoryPath = Path.Combine(ProjectRoot, "notes", "story");
var engine = YarnImporter.CreateEngineFromDirectory(notesStoryPath);

// Optional: start at a specific node (e.g. "Chapter2CommandersReport")
var engine = YarnImporter.CreateEngineFromDirectory(notesStoryPath, explicitStartNodeId: "Chapter2CommandersReport");
```

- **Unity:** `StorySceneController` calls `CreateEngineFromDirectory(notesStoryPath, startNodeId)` in `Start()`. Set the optional **Start Node Id** in the Inspector to override.
- **CLI:** `Chapter1Entry.CreateEngineFromDirectory(notesStoryPath)` uses the same API; path is resolved from the current directory (e.g. `notes/story` when run from repo root).

### Load a single file (e.g. tests)

```csharp
var engine = YarnImporter.CreateEngineFromFile(notesStoryPath, fileNameWithoutExtension: "chapter2");
```

### Parse a string (no file)

```csharp
var engine = YarnImporter.CreateEngine(yarnContent);
// Or just get nodes + start id:
var (nodes, startNodeId) = YarnImporter.Parse(yarnContent);
```

## Story file location

| Context   | Path to `notes/story` |
|----------|------------------------|
| Repo root / CLI | `notes/story` (relative to current directory) |
| Unity editor    | `Path.GetFullPath(Path.Combine(Application.dataPath, "..", "..", "notes", "story"))` |

## Node naming

Use the **ChapterX** prefix for node titles (e.g. `Chapter2CommandersReport`, `Chapter3Start`) so cross-file links are obvious. See the full doc below.

## Tests

**`YarnImporterTests.cs`** in **`tests/TheCampaign.Tests/StoryEngine/Import/`** tests the importer. Run with:

```bash
dotnet test the_campaign.slnx --filter "FullyQualifiedName~YarnImporter"
```

See **`notes/development/running-tests.md`** for more.

## Full documentation

Full format reference, start-node rules, and Unity setup: **`notes/development/yarn-import.md`**.
