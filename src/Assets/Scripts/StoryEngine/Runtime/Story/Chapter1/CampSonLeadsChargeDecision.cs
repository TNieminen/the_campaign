namespace TheCampaign.StoryEngine
{
public static class CampSonLeadsChargeDecision
{
    public const string Id = "camp.son_leads_charge.decision";

    public static StoryNode CreateNode()
    {
        return new StoryNode(
            id: Id,
            text:
            "Your son steps forward, eyes burning with determination.\n" +
            "\"Father, let me lead the charge. Our men will rally if they see me at the front.\"\n" +
            "The war council falls silent, all eyes on you.",
            choices: new[]
            {
                new Choice(
                    id: "allow",
                    text: "Allow your son to lead the charge.",
                    targetNodeId: CampSonLeadsChargeAllowOutcome.Id,
                    effects: new IEffect[]
                    {
                        new DelegateEffect(state =>
                        {
                            state.SetFlag("son_dead", true);
                            state.SetString("battle_outcome", "victory");
                        })
                    }),
                new Choice(
                    id: "deny",
                    text: "Deny your son and lead the charge yourself.",
                    targetNodeId: CampSonLeadsChargeDenyOutcome.Id,
                    effects: new IEffect[]
                    {
                        new DelegateEffect(state =>
                        {
                            state.SetFlag("son_dead", false);
                            state.SetString("battle_outcome", "defeat");
                        })
                    })
            });
    }
}
}
