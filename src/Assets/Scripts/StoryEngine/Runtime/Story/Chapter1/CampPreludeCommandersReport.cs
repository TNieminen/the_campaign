namespace TheCampaign.StoryEngine
{
public static class CampPreludeCommandersReport
{
    public const string Id = "camp.prelude.commanders_report";

    public static StoryNode CreateNode()
    {
        return new StoryNode(
            id: Id,
            text:
            "Night hangs over the camp as commanders crowd around the war table.\n" +
            "Reports of enemy movements pile up, each more urgent than the last.\n" +
            "You can wait for the scouts to return, or make your decision now.",
            choices: new[]
            {
                new Choice(
                    id: "wait_for_scouts",
                    text: "Wait for the scouts' report before committing to an attack.",
                    targetNodeId: CampPreludeScoutReport.Id),
                new Choice(
                    id: "decide_now",
                    text: "Decide now, without waiting for more information.",
                    targetNodeId: CampSonLeadsChargeDecision.Id)
            });
    }
}
}
