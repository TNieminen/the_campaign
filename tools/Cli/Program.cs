using System;
using System.IO;
using System.Linq;
using TheCampaign.StoryEngine;

namespace TheCampaign.Cli;

internal static class Program
{
    private static void Main(string[] args)
    {
        // For now we always run Chapter 1, loading from notes/story (relative to current directory).
        var notesStoryPath = Path.Combine(Directory.GetCurrentDirectory(), "notes", "story");
        var engine = Chapter1Entry.CreateEngineFromDirectory(notesStoryPath);
        engine.NodeChanged += node => RenderNode(engine, node);

        RenderNode(engine, engine.GetCurrentNode());

        while (true)
        {
            var choices = engine.GetAvailableChoices().ToList();
            if (choices.Count == 0)
            {
                Console.WriteLine();
                Console.WriteLine("No more choices available. Scenario ended.");
                break;
            }

            Console.WriteLine();
            Console.WriteLine("Choose an option (or 'q' to quit):");

            for (var i = 0; i < choices.Count; i++)
            {
                Console.WriteLine($"  {i + 1}) {choices[i].Text}");
            }

            Console.Write("> ");
            var input = Console.ReadLine();

            if (string.Equals(input, "q", StringComparison.OrdinalIgnoreCase))
            {
                break;
            }

            if (!int.TryParse(input, out var index) || index < 1 || index > choices.Count)
            {
                Console.WriteLine("Invalid selection, please try again.");
                continue;
            }

            var choice = choices[index - 1];

            try
            {
                engine.Choose(choice.Id);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error applying choice: {ex.Message}");
                break;
            }
        }

        PrintFinalState(engine);
    }

    private static void RenderNode(StoryEngine.StoryEngine engine, StoryNode node)
    {
        Console.WriteLine();
        Console.WriteLine("========================================");
        Console.WriteLine(node.Text);
        Console.WriteLine("========================================");
    }

    private static void PrintFinalState(StoryEngine.StoryEngine engine)
    {
        Console.WriteLine();
        Console.WriteLine("Final game state:");

        if (engine.State.Flags.Count == 0 && engine.State.Strings.Count == 0)
        {
            Console.WriteLine("  (no flags or string values set)");
            return;
        }

        if (engine.State.Flags.Count > 0)
        {
            Console.WriteLine("  Flags:");
            foreach (var pair in engine.State.Flags)
            {
                Console.WriteLine($"    {pair.Key} = {pair.Value}");
            }
        }

        if (engine.State.Strings.Count > 0)
        {
            Console.WriteLine("  String values:");
            foreach (var pair in engine.State.Strings)
            {
                Console.WriteLine($"    {pair.Key} = \"{pair.Value}\"");
            }
        }
    }
}

