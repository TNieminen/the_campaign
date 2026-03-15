namespace TheCampaign.StoryEngine
{
    /// <summary>
    /// Chapter 1 story: loads all .yarn files from notes/story (nodes can cross files).
    /// </summary>
    public static class Chapter1Entry
    {
        /// <summary>
        /// Creates a StoryEngine by loading all .yarn files from the given notes/story directory.
        /// Start node comes from the first file (alphabetically) that defines "start:", or the first node in that file.
        /// </summary>
        public static StoryEngine CreateEngineFromDirectory(string notesStoryDirectoryPath, GameState? initialState = null)
        {
            return YarnImporter.CreateEngineFromDirectory(notesStoryDirectoryPath, null, initialState);
        }
    }
}
