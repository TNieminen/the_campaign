namespace TheCampaign.StoryEngine;

public static class CampSonLeadsChargeAllowOutcome
{
    public const string Id = "camp.son_leads_charge.allow_outcome";

    public static StoryNode CreateNode()
    {
        return new StoryNode(
            id: Id,
            text:
                "The banners rise and your son rides at the front.\n" +
                "The charge shatters the enemy line, but when the dust settles, his banner lies torn in the mud.\n" +
                "Your son is dead, and victory tastes like ash.");
    }
}

