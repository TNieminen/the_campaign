using System;
using System.Collections.Generic;
using System.Linq;
using TheCampaign.StoryEngine;
using Xunit;
using Engine = TheCampaign.StoryEngine.StoryEngine;

namespace TheCampaign.Tests.StoryEngine
{
    public class StoryEngineTests
    {
        private static StoryNode Node(string id, string text, List<Choice>? choices = null) =>
            new StoryNode(id, text, choices ?? new List<Choice>());

        private static Choice ChoiceTo(string id, string displayText, string targetNodeId) =>
            new Choice($"{targetNodeId}_{id}", displayText, targetNodeId);

        [Fact]
        public void Constructor_ThrowsWhenNodesNull()
        {
            Assert.Throws<ArgumentNullException>(() =>
                new Engine(null!, "A", null));
        }

        [Fact]
        public void Constructor_ThrowsWhenStartNodeNotFound()
        {
            var nodes = new[] { Node("A", "Text") };
            Assert.Throws<ArgumentException>(() =>
                new Engine(nodes, "Missing", null));
        }

        [Fact]
        public void Constructor_SetsCurrentNodeAndState()
        {
            var nodes = new[] { Node("Start", "Hello") };
            var engine = new Engine(nodes, "Start", null);

            Assert.Equal("Start", engine.CurrentNodeId);
            Assert.NotNull(engine.State);
            Assert.Equal("Hello", engine.GetCurrentNode().Text);
        }

        [Fact]
        public void GetCurrentNode_ReturnsNodeForKey()
        {
            var nodes = new[]
            {
                Node("A", "Text A"),
                Node("B", "Text B")
            };
            var engine = new Engine(nodes, "B", null);

            var current = engine.GetCurrentNode();
            Assert.Equal("B", current.Id);
            Assert.Equal("Text B", current.Text);
        }

        [Fact]
        public void GetAvailableChoices_ReturnsAllChoicesWhenNoConditions()
        {
            var nodes = new[]
            {
                Node("A", "Choose", new List<Choice>
                {
                    ChoiceTo("0", "To B", "B"),
                    ChoiceTo("1", "To C", "C")
                }),
                Node("B", "B"),
                Node("C", "C")
            };
            var engine = new Engine(nodes, "A", null);

            var choices = engine.GetAvailableChoices().ToList();
            Assert.Equal(2, choices.Count);
            Assert.Contains(choices, c => c.TargetNodeId == "B");
            Assert.Contains(choices, c => c.TargetNodeId == "C");
        }

        [Fact]
        public void Choose_UpdatesCurrentNodeAndInvokesNodeChanged()
        {
            var nodes = new[]
            {
                Node("A", "Start", new List<Choice> { ChoiceTo("0", "Go", "B") }),
                Node("B", "End")
            };
            StoryNode? changedNode = null;
            var engine = new Engine(nodes, "A", null);
            engine.NodeChanged += n => changedNode = n;

            var choices = engine.GetAvailableChoices().ToList();
            Assert.Single(choices);
            engine.Choose(choices[0].Id);

            Assert.Equal("B", engine.CurrentNodeId);
            Assert.NotNull(changedNode);
            Assert.Equal("B", changedNode.Id);
            Assert.Equal("End", changedNode.Text);
        }

        [Fact]
        public void Choose_ThrowsWhenChoiceNotAvailable()
        {
            var nodes = new[]
            {
                Node("A", "Text", new List<Choice> { ChoiceTo("0", "To B", "B") }),
                Node("B", "B")
            };
            var engine = new Engine(nodes, "A", null);

            Assert.Throws<InvalidOperationException>(() => engine.Choose("wrong_id"));
        }

        [Fact]
        public void Choose_ThrowsWhenChoiceIdNull()
        {
            var nodes = new[] { Node("A", "Text") };
            var engine = new Engine(nodes, "A", null);

            Assert.Throws<ArgumentNullException>(() => engine.Choose(null!));
        }

        [Fact]
        public void Choose_ThrowsWhenTargetNodeMissing()
        {
            var nodes = new[]
            {
                Node("A", "Text", new List<Choice> { new Choice("c1", "Go", "Missing") }),
                Node("B", "B")
            };
            var engine = new Engine(nodes, "A", null);

            Assert.Throws<InvalidOperationException>(() => engine.Choose("c1"));
        }

        [Fact]
        public void Constructor_WithEntryConditionNotMet_Throws()
        {
            var condition = new FailingCondition();
            var nodes = new[] { new StoryNode("A", "Text", null, new[] { condition }) };
            Assert.Throws<InvalidOperationException>(() => new Engine(nodes, "A", null));
        }

        [Fact]
        public void GetAvailableChoices_FiltersByCondition()
        {
            var state = new GameState();
            var visible = new Choice("c1", "Visible", "B", conditions: new[] { new TrueCondition() });
            var hidden = new Choice("c2", "Hidden", "C", conditions: new[] { new FailingCondition() });
            var nodes = new[]
            {
                Node("A", "Text", new List<Choice> { visible, hidden }),
                Node("B", "B"),
                Node("C", "C")
            };
            var engine = new Engine(nodes, "A", state);

            var choices = engine.GetAvailableChoices().ToList();
            Assert.Single(choices);
            Assert.Equal("Visible", choices[0].Text);
        }

        [Fact]
        public void Choose_AppliesEffect()
        {
            var state = new GameState();
            var effect = new DelegateEffect(s => s.SetFlag("done", true));
            var choice = new Choice("c1", "Go", "B", effects: new[] { effect });
            var nodes = new[]
            {
                Node("A", "Text", new List<Choice> { choice }),
                Node("B", "B")
            };
            var engine = new Engine(nodes, "A", state);

            engine.Choose("c1");
            Assert.True(engine.State.GetFlag("done"));
        }

        private sealed class TrueCondition : ICondition
        {
            public bool IsMet(GameState state) => true;
        }

        private sealed class FailingCondition : ICondition
        {
            public bool IsMet(GameState state) => false;
        }
    }
}
