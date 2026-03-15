using System;
using System.IO;
using System.Linq;
using TheCampaign.StoryEngine;
using Xunit;

namespace TheCampaign.Tests.StoryEngine.Import
{
    public class YarnImporterTests
    {
        [Fact]
        public void Parse_ThrowsOnNullContent()
        {
            Assert.Throws<ArgumentException>(() => YarnImporter.Parse(null!));
        }

        [Fact]
        public void Parse_ThrowsOnEmptyContent()
        {
            Assert.Throws<ArgumentException>(() => YarnImporter.Parse(""));
            Assert.Throws<ArgumentException>(() => YarnImporter.Parse("   "));
        }

        [Fact]
        public void Parse_ThrowsWhenNoValidNodes()
        {
            // Block has title but no --- so ParseBlock returns null (no body)
            var content = @"
title: NoBody
===
";
            Assert.Throws<InvalidOperationException>(() => YarnImporter.Parse(content));
        }

        [Fact]
        public void Parse_SingleNode_ReturnsOneNodeAndUsesItAsStart()
        {
            var content = @"
title: Solo
---
Hello world.
===
";
            var (nodes, startNodeId) = YarnImporter.Parse(content);

            Assert.Single(nodes);
            Assert.Equal("Solo", startNodeId);
            Assert.Equal("Solo", nodes[0].Id);
            Assert.Equal("Hello world.", nodes[0].Text.Trim());
            Assert.Empty(nodes[0].Choices);
        }

        [Fact]
        public void Parse_SingleNodeWithChoices_ParsesOptionsAndTargets()
        {
            var content = @"
title: WithChoices
---
Some text here.
[[First option|TargetA]]
<<jump TargetA>>
[[Second option|TargetB]]
<<jump TargetB>>
===
";
            var (nodes, startNodeId) = YarnImporter.Parse(content);

            Assert.Single(nodes);
            Assert.Equal("WithChoices", nodes[0].Id);
            Assert.Equal("Some text here.", nodes[0].Text.Trim());
            Assert.Equal(2, nodes[0].Choices.Count);
            Assert.Equal("First option", nodes[0].Choices[0].Text);
            Assert.Equal("TargetA", nodes[0].Choices[0].TargetNodeId);
            Assert.Equal("Second option", nodes[0].Choices[1].Text);
            Assert.Equal("TargetB", nodes[0].Choices[1].TargetNodeId);
        }

        [Fact]
        public void Parse_StartDirective_SetsStartNodeId()
        {
            var content = @"
start: Second

title: First
---
First node body.
===

title: Second
---
Second node body.
===
";
            var (nodes, startNodeId) = YarnImporter.Parse(content);

            Assert.Equal(2, nodes.Count);
            Assert.Equal("Second", startNodeId);
            Assert.Equal("First", nodes[0].Id);
            Assert.Equal("Second", nodes[1].Id);
        }

        [Fact]
        public void Parse_StartDirectiveWithInvalidNode_FallsBackToFirstNode()
        {
            var content = @"
start: NonExistent

title: RealNode
---
Only node.
===
";
            var (nodes, startNodeId) = YarnImporter.Parse(content);

            Assert.Single(nodes);
            Assert.Equal("RealNode", startNodeId);
        }

        [Fact]
        public void Parse_MultipleNodes_AllParsedInOrder()
        {
            var content = @"
title: A
---
Body A.
[[Go to B|B]]
===

title: B
---
Body B.
===
";
            var (nodes, startNodeId) = YarnImporter.Parse(content);

            Assert.Equal(2, nodes.Count);
            Assert.Equal("A", startNodeId);
            Assert.Equal("A", nodes[0].Id);
            Assert.Equal("Body A.", nodes[0].Text.Trim());
            Assert.Single(nodes[0].Choices);
            Assert.Equal("Go to B", nodes[0].Choices[0].Text);
            Assert.Equal("B", nodes[0].Choices[0].TargetNodeId);
            Assert.Equal("B", nodes[1].Id);
            Assert.Equal("Body B.", nodes[1].Text.Trim());
            Assert.Empty(nodes[1].Choices);
        }

        [Fact]
        public void Parse_IgnoresPositionMetadata()
        {
            var content = @"
title: Meta
position: 100,-200
---
Body only.
===
";
            var (nodes, _) = YarnImporter.Parse(content);

            Assert.Single(nodes);
            Assert.Equal("Meta", nodes[0].Id);
            Assert.Contains("Body only", nodes[0].Text);
        }

        [Fact]
        public void Parse_JumpLines_NotAddedAsChoices()
        {
            var content = @"
title: OneChoice
---
Text.
[[Only option|Target]]
<<jump Target>>
===
";
            var (nodes, _) = YarnImporter.Parse(content);

            Assert.Single(nodes[0].Choices);
            Assert.Equal("Only option", nodes[0].Choices[0].Text);
            Assert.Equal("Target", nodes[0].Choices[0].TargetNodeId);
        }

        [Fact]
        public void Parse_TrimsContent()
        {
            var content = "  \n  title: Trimmed\n---\n  Hi.\n  ===  \n";
            var (nodes, startNodeId) = YarnImporter.Parse(content);

            Assert.Single(nodes);
            Assert.Equal("Trimmed", startNodeId);
            Assert.Contains("Hi", nodes[0].Text);
        }

        [Fact]
        public void CreateEngine_ReturnsEngineWithCorrectStartNode()
        {
            var content = @"
title: Start
---
Start text.
[[Next|Next]]
===

title: Next
---
Next text.
===
";
            var engine = YarnImporter.CreateEngine(content);

            Assert.NotNull(engine);
            Assert.Equal("Start", engine.CurrentNodeId);
            Assert.NotNull(engine.State);
        }

        [Fact]
        public void CreateEngine_WithInitialState_PreservesState()
        {
            var content = @"
title: One
---
Body.
===
";
            var state = new GameState();
            state.SetFlag("custom", true);
            state.SetMorale(75);

            var engine = YarnImporter.CreateEngine(content, state);

            Assert.Same(state, engine.State);
            Assert.True(engine.State.GetFlag("custom"));
            Assert.Equal(75, engine.State.Morale);
        }

        [Fact]
        public void CreateEngine_WithNullInitialState_CreatesNewState()
        {
            var content = @"
title: One
---
Body.
===
";
            var engine = YarnImporter.CreateEngine(content, null);

            Assert.NotNull(engine.State);
            Assert.Equal(GameState.MoraleDefault, engine.State.Morale);
        }

        [Fact]
        public void CreateEngineFromFile_WhenFileMissing_ThrowsFileNotFoundException()
        {
            var dir = Path.Combine(Path.GetTempPath(), "YarnImporterTests_" + Guid.NewGuid().ToString("N"));
            try
            {
                Directory.CreateDirectory(dir);
                Assert.Throws<FileNotFoundException>(() =>
                    YarnImporter.CreateEngineFromFile(dir, "nonexistent"));
            }
            finally
            {
                if (Directory.Exists(dir))
                    Directory.Delete(dir);
            }
        }

        [Fact]
        public void CreateEngineFromFile_LoadsAndParsesFile()
        {
            var dir = Path.Combine(Path.GetTempPath(), "YarnImporterTests_" + Guid.NewGuid().ToString("N"));
            try
            {
                Directory.CreateDirectory(dir);
                var path = Path.Combine(dir, "test.yarn");
                File.WriteAllText(path, @"
title: FromFile
---
Content from file.
===
");
                var engine = YarnImporter.CreateEngineFromFile(dir, "test");

                Assert.NotNull(engine);
                Assert.Equal("FromFile", engine.CurrentNodeId);
                Assert.Contains("Content from file", engine.GetCurrentNode().Text);
            }
            finally
            {
                if (Directory.Exists(dir))
                {
                    foreach (var f in Directory.GetFiles(dir))
                        File.Delete(f);
                    Directory.Delete(dir);
                }
            }
        }

        [Fact]
        public void Parse_ChoiceIds_AreUniquePerNode()
        {
            var content = @"
title: Multi
---
[[A|X]]
[[B|X]]
[[C|X]]
===
";
            var (nodes, _) = YarnImporter.Parse(content);

            var ids = nodes[0].Choices.Select(c => c.Id).ToList();
            Assert.Equal(3, ids.Count);
            Assert.Equal(ids.Distinct().Count(), ids.Count);
        }

        [Fact]
        public void Parse_MultilineBody_PreservesLineBreaks()
        {
            var content = @"
title: Lines
---
First line.
Second line.
Third.
===
";
            var (nodes, _) = YarnImporter.Parse(content);

            Assert.Single(nodes);
            Assert.Contains("First line", nodes[0].Text);
            Assert.Contains("Second line", nodes[0].Text);
            Assert.Contains("Third", nodes[0].Text);
        }

        [Fact]
        public void Parse_HandlesCrLfLineEndings()
        {
            var content = "title: CrLf\r\n---\r\nHello.\r\n===\r\n";
            var (nodes, startNodeId) = YarnImporter.Parse(content);

            Assert.Single(nodes);
            Assert.Equal("CrLf", startNodeId);
            Assert.Contains("Hello", nodes[0].Text);
        }

        [Fact]
        public void CreateEngineFromFile_DefaultFileName_LoadsChapter1()
        {
            var dir = Path.Combine(Path.GetTempPath(), "YarnImporterTests_" + Guid.NewGuid().ToString("N"));
            try
            {
                Directory.CreateDirectory(dir);
                File.WriteAllText(Path.Combine(dir, "chapter1.yarn"), @"
title: Chapter1Start
---
Default chapter.
===
");
                var engine = YarnImporter.CreateEngineFromFile(dir); // default fileName = chapter1

                Assert.Equal("Chapter1Start", engine.CurrentNodeId);
            }
            finally
            {
                if (Directory.Exists(dir))
                {
                    foreach (var f in Directory.GetFiles(dir))
                        File.Delete(f);
                    Directory.Delete(dir);
                }
            }
        }

        [Fact]
        public void CreateEngineFromDirectory_LoadsOnlyYarnFiles_IgnoresMd()
        {
            var dir = Path.Combine(Path.GetTempPath(), "YarnImporterTests_" + Guid.NewGuid().ToString("N"));
            try
            {
                Directory.CreateDirectory(dir);
                File.WriteAllText(Path.Combine(dir, "readme.md"), "# Ignored\n");
                File.WriteAllText(Path.Combine(dir, "story.yarn"), @"
title: FromYarn
---
Only .yarn is read.
===
");
                var engine = YarnImporter.CreateEngineFromDirectory(dir);

                Assert.Equal("FromYarn", engine.CurrentNodeId);
                Assert.Contains("Only .yarn", engine.GetCurrentNode().Text);
            }
            finally
            {
                if (Directory.Exists(dir))
                {
                    foreach (var f in Directory.GetFiles(dir))
                        File.Delete(f);
                    Directory.Delete(dir);
                }
            }
        }

        [Fact]
        public void CreateEngineFromDirectory_NodesCanReferenceAcrossFiles()
        {
            var dir = Path.Combine(Path.GetTempPath(), "YarnImporterTests_" + Guid.NewGuid().ToString("N"));
            try
            {
                Directory.CreateDirectory(dir);
                File.WriteAllText(Path.Combine(dir, "a.yarn"), @"
title: Start
---
In file A.
[[Go to B|InB]]
===
");
                File.WriteAllText(Path.Combine(dir, "b.yarn"), @"
title: InB
---
In file B.
===
");
                var engine = YarnImporter.CreateEngineFromDirectory(dir);

                Assert.Equal("Start", engine.CurrentNodeId);
                var choices = engine.GetAvailableChoices().ToList();
                Assert.Single(choices);
                Assert.Equal("Go to B", choices[0].Text);
                Assert.Equal("InB", choices[0].TargetNodeId);
                engine.Choose(choices[0].Id);
                Assert.Equal("InB", engine.CurrentNodeId);
                Assert.Contains("In file B", engine.GetCurrentNode().Text);
            }
            finally
            {
                if (Directory.Exists(dir))
                {
                    foreach (var f in Directory.GetFiles(dir))
                        File.Delete(f);
                    Directory.Delete(dir);
                }
            }
        }

        [Fact]
        public void CreateEngineFromDirectory_FirstFileAlphabetically_ProvidesStart()
        {
            var dir = Path.Combine(Path.GetTempPath(), "YarnImporterTests_" + Guid.NewGuid().ToString("N"));
            try
            {
                Directory.CreateDirectory(dir);
                File.WriteAllText(Path.Combine(dir, "z.yarn"), @"
start: ZStart
title: ZStart
---
In z.
===
");
                File.WriteAllText(Path.Combine(dir, "a.yarn"), @"
start: AStart
title: AStart
---
In a.
===
");
                var engine = YarnImporter.CreateEngineFromDirectory(dir);

                Assert.Equal("AStart", engine.CurrentNodeId);
            }
            finally
            {
                if (Directory.Exists(dir))
                {
                    foreach (var f in Directory.GetFiles(dir))
                        File.Delete(f);
                    Directory.Delete(dir);
                }
            }
        }

        [Fact]
        public void CreateEngineFromDirectory_ExplicitStartNodeId_OverridesFileStart()
        {
            var dir = Path.Combine(Path.GetTempPath(), "YarnImporterTests_" + Guid.NewGuid().ToString("N"));
            try
            {
                Directory.CreateDirectory(dir);
                File.WriteAllText(Path.Combine(dir, "one.yarn"), @"
start: First
title: First
---
First.
===
title: Second
---
Second.
===
");
                var engine = YarnImporter.CreateEngineFromDirectory(dir, "Second");

                Assert.Equal("Second", engine.CurrentNodeId);
            }
            finally
            {
                if (Directory.Exists(dir))
                {
                    foreach (var f in Directory.GetFiles(dir))
                        File.Delete(f);
                    Directory.Delete(dir);
                }
            }
        }

        [Fact]
        public void CreateEngineFromDirectory_WhenDirectoryMissing_Throws()
        {
            var dir = Path.Combine(Path.GetTempPath(), "YarnImporterTests_" + Guid.NewGuid().ToString("N"));
            Assert.Throws<DirectoryNotFoundException>(() => YarnImporter.CreateEngineFromDirectory(dir));
        }

        [Fact]
        public void CreateEngineFromDirectory_WhenNoYarnFiles_Throws()
        {
            var dir = Path.Combine(Path.GetTempPath(), "YarnImporterTests_" + Guid.NewGuid().ToString("N"));
            try
            {
                Directory.CreateDirectory(dir);
                File.WriteAllText(Path.Combine(dir, "notes.md"), "Only .md here.");
                Assert.Throws<InvalidOperationException>(() => YarnImporter.CreateEngineFromDirectory(dir));
            }
            finally
            {
                if (Directory.Exists(dir))
                {
                    foreach (var f in Directory.GetFiles(dir))
                        File.Delete(f);
                    Directory.Delete(dir);
                }
            }
        }
    }
}
