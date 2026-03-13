namespace TheCampaign.StoryEngine
{
public static class CampPreludeScoutReport
{
    public const string Id = "camp.prelude.scout_report";

    public static StoryNode CreateNode()
    {
        return new StoryNode(
            id: Id,
            text:
            "Mud-streaked scouts burst into the tent, breathless.\n" +
            "\"Their main force is forming up on the ridge,\" one gasps.\n" +
            "\"If we strike before dawn, we might catch them unprepared.\"",
            choices: new[]
            {
                new Choice(
                    id: "return_to_council",
                    text: "Return to the war council and decide who will lead the attack.",
                    targetNodeId: CampSonLeadsChargeDecision.Id)
            });
    }
}
}
