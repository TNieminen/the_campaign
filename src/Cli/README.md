CLI Runner
==========

This folder contains a simple **command-line interface** for running story content using the core story engine.

## Preconditions

- **.NET SDK**:
  - Install the latest **.NET 10 SDK** (or newer) from the official .NET site.
  - Verify installation:
    ```powershell
    dotnet --version
    ```
- **Working directory**:
  - Commands below assume you are in the **repository root**:
    ```powershell
    cd c:\Users\tuomo\programming\the_campaign
    ```

## How to run

From the repository root:

```powershell
dotnet run
```

This will:

- Build the project defined in `the_campaign.csproj`.
- Start the CLI defined in `src/Cli/Program.cs`.
- Run **Chapter 1** via `Chapter1Entry.CreateEngine()`:
  - Show the current node description.
  - List available choices as numbered options.
  - Let you pick a choice (or type `q` to quit).
  - Continue until no choices remain, then print the final game state (flags and string values).

You can adjust which chapter or story entry is used by changing the engine creation line in `Program.cs`.

