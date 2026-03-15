using TheCampaign.StoryEngine;
using Xunit;

namespace TheCampaign.Tests.StoryEngine
{
    public class GameStateTests
    {
        [Fact]
        public void Default_MoraleIsDefault()
        {
            var state = new GameState();
            Assert.Equal(GameState.MoraleDefault, state.Morale);
        }

        [Fact]
        public void SetMorale_UpdatesValue()
        {
            var state = new GameState();
            state.SetMorale(75);
            Assert.Equal(75, state.Morale);
        }

        [Fact]
        public void SetMorale_ClampsToMin()
        {
            var state = new GameState();
            state.SetMorale(-10);
            Assert.Equal(GameState.MoraleMin, state.Morale);
        }

        [Fact]
        public void SetMorale_ClampsToMax()
        {
            var state = new GameState();
            state.SetMorale(200);
            Assert.Equal(GameState.MoraleMax, state.Morale);
        }

        [Fact]
        public void AddMorale_IncreasesValue()
        {
            var state = new GameState();
            state.SetMorale(50);
            state.AddMorale(20);
            Assert.Equal(70, state.Morale);
        }

        [Fact]
        public void AddMorale_ClampsWhenExceedingMax()
        {
            var state = new GameState();
            state.SetMorale(95);
            state.AddMorale(20);
            Assert.Equal(GameState.MoraleMax, state.Morale);
        }

        [Fact]
        public void AddMorale_ClampsWhenBelowMin()
        {
            var state = new GameState();
            state.SetMorale(10);
            state.AddMorale(-50);
            Assert.Equal(GameState.MoraleMin, state.Morale);
        }

        [Fact]
        public void GetFlag_ReturnsFalseWhenNotSet()
        {
            var state = new GameState();
            Assert.False(state.GetFlag("missing"));
        }

        [Fact]
        public void SetFlag_GetFlag_RoundTrip()
        {
            var state = new GameState();
            state.SetFlag("key", true);
            Assert.True(state.GetFlag("key"));
            state.SetFlag("key", false);
            Assert.False(state.GetFlag("key"));
        }

        [Fact]
        public void GetString_ReturnsNullWhenNotSet()
        {
            var state = new GameState();
            Assert.Null(state.GetString("missing"));
        }

        [Fact]
        public void SetString_GetString_RoundTrip()
        {
            var state = new GameState();
            state.SetString("name", "value");
            Assert.Equal("value", state.GetString("name"));
        }

        [Fact]
        public void Flags_ExposesReadOnlyDictionary()
        {
            var state = new GameState();
            state.SetFlag("a", true);
            Assert.True(state.Flags["a"]);
            Assert.Single(state.Flags);
        }

        [Fact]
        public void Strings_ExposesReadOnlyDictionary()
        {
            var state = new GameState();
            state.SetString("k", "v");
            Assert.Equal("v", state.Strings["k"]);
            Assert.Single(state.Strings);
        }
    }
}
