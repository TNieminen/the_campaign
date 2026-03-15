using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;

namespace TheCampaign.StoryEngine
{
    /// <summary>
    /// Imports a Yarn Spinner (.yarn) source string into our story engine format.
    /// Supports: start: NodeName (optional, at top of file), title:, ---, body text, [[Display|TargetNode]], <<jump NodeName>>, ===.
    /// Ignores: position and other metadata. No support yet for &lt;&lt;set&gt;&gt; / conditions.
    /// </summary>
    public static class YarnImporter
    {
        private static readonly Regex StartRegex = new Regex(@"^\s*start:\s*(.+)$", RegexOptions.Compiled);
        private static readonly Regex TitleRegex = new Regex(@"^\s*title:\s*(.+)$", RegexOptions.Compiled);
        private static readonly Regex OptionRegex = new Regex(@"\[\[(.+?)\|(.+?)\]\]", RegexOptions.Compiled);
        private static readonly Regex JumpRegex = new Regex(@"^\s*<<jump\s+(.+?)>>\s*$", RegexOptions.Compiled);

        /// <summary>
        /// Parses Yarn content and returns a list of story nodes and the start node id.
        /// If the file contains a line "start: NodeName" at the top, that node is used as start; otherwise the first node is used.
        /// </summary>
        public static (IReadOnlyList<StoryNode> Nodes, string StartNodeId) Parse(string yarnContent)
        {
            if (string.IsNullOrWhiteSpace(yarnContent))
                throw new ArgumentException("Yarn content cannot be null or empty.", nameof(yarnContent));

            string content = yarnContent.Trim();
            string? explicitStart = null;
            var lines = content.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.None).ToList();
            for (int i = 0; i < lines.Count; i++)
            {
                var m = StartRegex.Match(lines[i]);
                if (m.Success)
                {
                    explicitStart = m.Groups[1].Value.Trim();
                    lines.RemoveAt(i);
                    content = string.Join("\n", lines);
                    break;
                }
                if (lines[i].Trim().StartsWith("title:", StringComparison.OrdinalIgnoreCase))
                    break;
            }

            var nodes = new List<StoryNode>();
            var blocks = SplitBlocks(content);

            foreach (var block in blocks)
            {
                var node = ParseBlock(block);
                if (node != null)
                    nodes.Add(node);
            }

            if (nodes.Count == 0)
                throw new InvalidOperationException("No valid nodes found in Yarn content.");

            string startNodeId = nodes[0].Id;
            if (explicitStart != null)
            {
                if (nodes.Any(n => n.Id == explicitStart))
                    startNodeId = explicitStart;
            }
            return (nodes, startNodeId);
        }

        /// <summary>
        /// Loads all .yarn files from the notes/story directory, merges nodes (by id; duplicate id = last wins),
        /// and creates a StoryEngine. Only .yarn files are read; .md and other files are ignored.
        /// File order is alphabetical so the graph is deterministic. Start node: first file (alphabetically)
        /// that defines "start: NodeName" wins; if none, the first node from the first file is used.
        /// Nodes can reference each other across files.
        /// </summary>
        /// <param name="notesStoryDirectoryPath">Full path to the notes/story folder.</param>
        /// <param name="explicitStartNodeId">Optional. If set, this node id is used as start; must exist in the merged set.</param>
        public static StoryEngine CreateEngineFromDirectory(string notesStoryDirectoryPath, string? explicitStartNodeId = null, GameState? initialState = null)
        {
            if (!Directory.Exists(notesStoryDirectoryPath))
                throw new DirectoryNotFoundException($"Story directory not found: {notesStoryDirectoryPath}");

            var yarnFiles = Directory.GetFiles(notesStoryDirectoryPath, "*.yarn")
                .OrderBy(f => f, StringComparer.OrdinalIgnoreCase)
                .ToList();

            if (yarnFiles.Count == 0)
                throw new InvalidOperationException($"No .yarn files found in {notesStoryDirectoryPath}");

            var allNodes = new Dictionary<string, StoryNode>(StringComparer.OrdinalIgnoreCase);
            string? firstStartNodeId = null;

            foreach (string filePath in yarnFiles)
            {
                string content = File.ReadAllText(filePath);
                var (nodes, fileStartNodeId) = Parse(content);
                if (firstStartNodeId == null)
                    firstStartNodeId = fileStartNodeId;
                foreach (var node in nodes)
                    allNodes[node.Id] = node;
            }

            string startNodeId = explicitStartNodeId ?? firstStartNodeId!;
            if (string.IsNullOrEmpty(startNodeId) || !allNodes.ContainsKey(startNodeId))
                throw new InvalidOperationException($"Start node '{startNodeId}' not found in merged nodes.");

            var state = initialState ?? new GameState();
            return new StoryEngine(allNodes.Values, startNodeId, state);
        }

        /// <summary>
        /// Loads a single .yarn file and creates a StoryEngine. Use for one-file stories or tests.
        /// </summary>
        /// <param name="notesStoryDirectoryPath">Directory containing the file.</param>
        /// <param name="fileNameWithoutExtension">File name without .yarn (e.g. "chapter1").</param>
        public static StoryEngine CreateEngineFromFile(string notesStoryDirectoryPath, string fileNameWithoutExtension = "chapter1", GameState? initialState = null)
        {
            string path = Path.Combine(notesStoryDirectoryPath, fileNameWithoutExtension + ".yarn");
            if (!File.Exists(path))
                throw new FileNotFoundException($"Yarn file not found: {path}");
            string content = File.ReadAllText(path);
            return CreateEngine(content, initialState);
        }

        /// <summary>
        /// Creates a StoryEngine instance from parsed Yarn content, using the first node as start.
        /// </summary>
        public static StoryEngine CreateEngine(string yarnContent, GameState? initialState = null)
        {
            var (nodes, startNodeId) = Parse(yarnContent);
            var state = initialState ?? new GameState();
            return new StoryEngine(nodes, startNodeId, state);
        }

        private static List<string> SplitBlocks(string content)
        {
            var blocks = new List<string>();
            var current = new List<string>();
            foreach (var line in content.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.None))
            {
                if (line.Trim() == "===")
                {
                    if (current.Count > 0)
                    {
                        blocks.Add(string.Join("\n", current));
                        current.Clear();
                    }
                }
                else
                {
                    current.Add(line);
                }
            }
            if (current.Count > 0)
                blocks.Add(string.Join("\n", current));
            return blocks;
        }

        private static StoryNode? ParseBlock(string block)
        {
            var lines = block.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.None).ToList();
            string? title = null;
            int bodyStart = -1;

            for (int i = 0; i < lines.Count; i++)
            {
                var m = TitleRegex.Match(lines[i]);
                if (m.Success)
                {
                    title = m.Groups[1].Value.Trim();
                    continue;
                }
                if (lines[i].Trim() == "---")
                {
                    bodyStart = i + 1;
                    break;
                }
            }

            if (string.IsNullOrEmpty(title) || bodyStart < 0 || bodyStart >= lines.Count)
                return null;

            var bodyLines = lines.Skip(bodyStart).ToList();
            var textLines = new List<string>();
            var choices = new List<Choice>();
            int choiceIndex = 0;

            foreach (var line in bodyLines)
            {
                var optionMatch = OptionRegex.Match(line);
                if (optionMatch.Success)
                {
                    string displayText = optionMatch.Groups[1].Value.Trim();
                    string targetId = optionMatch.Groups[2].Value.Trim();
                    string choiceId = $"{targetId}_{choiceIndex}";
                    choiceIndex++;
                    choices.Add(new Choice(choiceId, displayText, targetId));
                    continue;
                }
                if (JumpRegex.IsMatch(line))
                    continue;
                textLines.Add(line);
            }

            string text = string.Join("\n", textLines).Trim();
            return new StoryNode(title, text, choices);
        }
    }
}
