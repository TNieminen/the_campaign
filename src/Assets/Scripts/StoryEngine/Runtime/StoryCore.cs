using System;
using System.Collections.Generic;
using System.Linq;

namespace TheCampaign.StoryEngine
{
public sealed class GameState
{
    public const int MoraleMin = 0;
    public const int MoraleMax = 100;
    public const int MoraleDefault = 50;

    private readonly Dictionary<string, bool> _flags = new();
    private readonly Dictionary<string, string> _strings = new();
    private int _morale = MoraleDefault;

    public IReadOnlyDictionary<string, bool> Flags => _flags;

    public IReadOnlyDictionary<string, string> Strings => _strings;

    public int Morale => _morale;

    public bool GetFlag(string key) => _flags.TryGetValue(key, out var value) && value;

    public void SetFlag(string key, bool value) => _flags[key] = value;

    public string? GetString(string key) => _strings.TryGetValue(key, out var value) ? value : null;

    public void SetString(string key, string value) => _strings[key] = value;

    public void SetMorale(int value) => _morale = ClampMorale(value);

    public void AddMorale(int delta) => _morale = ClampMorale(_morale + delta);

    private static int ClampMorale(int value)
    {
        if (value < MoraleMin) return MoraleMin;
        if (value > MoraleMax) return MoraleMax;
        return value;
    }
}

public interface ICondition
{
    bool IsMet(GameState state);
}

public interface IEffect
{
    void Apply(GameState state);
}

public sealed class StoryNode
{
    public string Id { get; }
    public string Text { get; }
    public IReadOnlyList<Choice> Choices { get; }
    public IReadOnlyList<ICondition> EntryConditions { get; }

    public StoryNode(
        string id,
        string text,
        IEnumerable<Choice>? choices = null,
        IEnumerable<ICondition>? entryConditions = null)
    {
        Id = id ?? throw new ArgumentNullException(nameof(id));
        Text = text ?? throw new ArgumentNullException(nameof(text));
        Choices = (choices ?? Array.Empty<Choice>()).ToArray();
        EntryConditions = (entryConditions ?? Array.Empty<ICondition>()).ToArray();
    }
}

public sealed class Choice
{
    public string Id { get; }
    public string Text { get; }
    public string TargetNodeId { get; }
    public IReadOnlyList<ICondition> Conditions { get; }
    public IReadOnlyList<IEffect> Effects { get; }

    public Choice(
        string id,
        string text,
        string targetNodeId,
        IEnumerable<ICondition>? conditions = null,
        IEnumerable<IEffect>? effects = null)
    {
        Id = id ?? throw new ArgumentNullException(nameof(id));
        Text = text ?? throw new ArgumentNullException(nameof(text));
        TargetNodeId = targetNodeId ?? throw new ArgumentNullException(nameof(targetNodeId));
        Conditions = (conditions ?? Array.Empty<ICondition>()).ToArray();
        Effects = (effects ?? Array.Empty<IEffect>()).ToArray();
    }
}

public sealed class StoryEngine
{
    private readonly Dictionary<string, StoryNode> _nodes;

    public string CurrentNodeId { get; private set; }
    public GameState State { get; }

    public event Action<StoryNode>? NodeChanged;

    public StoryEngine(IEnumerable<StoryNode> nodes, string startNodeId, GameState? initialState = null)
    {
        if (nodes == null) throw new ArgumentNullException(nameof(nodes));

        _nodes = nodes.ToDictionary(n => n.Id, n => n);

        if (!_nodes.ContainsKey(startNodeId))
        {
            throw new ArgumentException($"Start node '{startNodeId}' not found.", nameof(startNodeId));
        }

        CurrentNodeId = startNodeId;
        State = initialState ?? new GameState();

        var current = GetCurrentNode();
        if (!AreEntryConditionsMet(current))
        {
            throw new InvalidOperationException($"Entry conditions not met for start node '{startNodeId}'.");
        }
    }

    public StoryNode GetCurrentNode() => _nodes[CurrentNodeId];

    public IEnumerable<Choice> GetAvailableChoices()
    {
        var node = GetCurrentNode();
        return node.Choices.Where(c => c.Conditions.All(cond => cond.IsMet(State)));
    }

    public void Choose(string choiceId)
    {
        if (choiceId == null) throw new ArgumentNullException(nameof(choiceId));

        var available = GetAvailableChoices().ToList();
        var choice = available.FirstOrDefault(c => c.Id == choiceId);
        if (choice == null)
        {
            throw new InvalidOperationException($"Choice '{choiceId}' is not available in node '{CurrentNodeId}'.");
        }

        foreach (var effect in choice.Effects)
        {
            effect.Apply(State);
        }

        if (!_nodes.ContainsKey(choice.TargetNodeId))
        {
            throw new InvalidOperationException($"Target node '{choice.TargetNodeId}' not found.");
        }

        CurrentNodeId = choice.TargetNodeId;
        var newNode = GetCurrentNode();

        if (!AreEntryConditionsMet(newNode))
        {
            throw new InvalidOperationException($"Entry conditions not met for node '{newNode.Id}' after transition.");
        }

        NodeChanged?.Invoke(newNode);
    }

    private bool AreEntryConditionsMet(StoryNode node) =>
        node.EntryConditions.All(cond => cond.IsMet(State));
}

public sealed class DelegateEffect : IEffect
{
    private readonly Action<GameState> _action;

    public DelegateEffect(Action<GameState> action)
    {
        _action = action ?? throw new ArgumentNullException(nameof(action));
    }

    public void Apply(GameState state) => _action(state);
}
}
