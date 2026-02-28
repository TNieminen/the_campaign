namespace TheCampaign.StoryEngine;

/// <summary>
/// Entry point and composition for Chapter 1 story nodes.
/// </summary>
public static class Chapter1Entry
{
    public static StoryEngine CreateEngine()
    {
        var nodes = new[]
        {
            CampPreludeCommandersReport.CreateNode(),
            CampPreludeScoutReport.CreateNode(),
            CampSonLeadsChargeDecision.CreateNode(),
            CampSonLeadsChargeAllowOutcome.CreateNode(),
            CampSonLeadsChargeDenyOutcome.CreateNode()
        };

        var state = new GameState();
        return new StoryEngine(nodes, startNodeId: CampPreludeCommandersReport.Id, initialState: state);
    }
}

