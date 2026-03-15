# Running tests

Unit tests use **xUnit** and live in **`tests/TheCampaign.Tests`**. The test project references the main `the_campaign.csproj`. From the repo root, use the solution **`the_campaign.slnx`** so that tests are built and run.

## From the repo root

Run all tests:

```bash
dotnet test the_campaign.slnx
```

Run only the test project:

```bash
dotnet test tests/TheCampaign.Tests/TheCampaign.Tests.csproj
```

## See which tests passed or failed

By default you only get a summary. To list **each test** and whether it passed or failed, use the **console logger** (not MSBuild verbosity):

```bash
dotnet test the_campaign.slnx --logger "console;verbosity=detailed"
```

Or slightly less output:

```bash
dotnet test the_campaign.slnx --logger "console;verbosity=normal"
```

`-v n` / `-v normal` control **build** verbosity only; they do not show per-test results.

## Filtering tests

Run tests whose full name contains a string:

```bash
dotnet test the_campaign.slnx --filter "FullyQualifiedName~YarnImporter"
```

Run a single test by name:

```bash
dotnet test the_campaign.slnx --filter "FullyQualifiedName~Parse_SingleNode_ReturnsOneNodeAndUsesItAsStart"
```

## Requirements

- **.NET SDK** (same major as the project; the project targets `net10.0`).
- Run from the **repository root** (where `the_campaign.csproj` and `the_campaign.slnx` are).
