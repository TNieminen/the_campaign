namespace TheCampaign.StoryEngine;

public static class CampSonLeadsChargeDenyOutcome
{
    public const string Id = "camp.son_leads_charge.deny_outcome";

    public static StoryNode CreateNode()
    {
        return new StoryNode(
            id: Id,
            text:
                "You place a hand on his shoulder. \"No. I will lead them.\"\n" +
                "His jaw tightens, but he steps back as you ride out.\n" +
                "The men hesitate; the charge falters. By dusk, the field is lost and your banners burn on the horizon.");
    }
}

