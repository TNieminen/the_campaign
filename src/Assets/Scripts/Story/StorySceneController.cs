using System.Linq;
using StoryRuntime = TheCampaign.StoryEngine;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

namespace TheCampaign.Unity
{
    /// <summary>
    /// Simple Unity driver that:
    /// - Displays the campaign image in the scene (via a referenced UI Image).
    /// - Uses the StoryEngine Chapter 1 entry point.
    /// - Renders the current node's text and available choices as UI buttons.
    /// </summary>
    public sealed class StorySceneController : MonoBehaviour
    {
        [Header("Visuals")]
        [SerializeField] private Image campaignImage;

        [Header("Story UI")]
        [SerializeField] private TMP_Text descriptionText;
        [SerializeField] private Transform choicesContainer;
        [SerializeField] private Button choiceButtonPrefab;

        private StoryRuntime.StoryEngine _engine;

        private void Start()
        {
            // Construct the Chapter 1 story engine from the framework-agnostic runtime.
            _engine = StoryRuntime.Chapter1Entry.CreateEngine();
            _engine.NodeChanged += OnNodeChanged;

            // Render the initial node immediately.
            RenderCurrentNode(_engine.GetCurrentNode());
        }

        private void OnDestroy()
        {
            if (_engine != null)
            {
                _engine.NodeChanged -= OnNodeChanged;
            }
        }

        private void OnNodeChanged(StoryRuntime.StoryNode node)
        {
            RenderCurrentNode(node);
        }

        private void RenderCurrentNode(StoryRuntime.StoryNode node)
        {
            if (_engine == null)
            {
                return;
            }

            if (descriptionText != null)
            {
                descriptionText.text = node.Text;
            }

            // Clear old choice buttons.
            if (choicesContainer != null)
            {
                for (var i = choicesContainer.childCount - 1; i >= 0; i--)
                {
                    var child = choicesContainer.GetChild(i);
                    if (Application.isPlaying)
                    {
                        Destroy(child.gameObject);
                    }
                    else
                    {
                        DestroyImmediate(child.gameObject);
                    }
                }
            }

            if (choiceButtonPrefab == null || choicesContainer == null)
            {
                return;
            }

            var choices = _engine.GetAvailableChoices().ToList();
            if (choices.Count == 0)
            {
                // No further choices; story branch has ended.
                var endText = "(No further choices. This branch has ended.)";
                if (descriptionText != null)
                {
                    descriptionText.text += $"\n\n{endText}";
                }

                return;
            }

            foreach (var choice in choices)
            {
                var button = Instantiate(choiceButtonPrefab, choicesContainer);

                // Set button label.
                var label = button.GetComponentInChildren<TMP_Text>();
                if (label != null)
                {
                    label.text = choice.Text;
                }

                var choiceId = choice.Id; // capture for closure
                button.onClick.AddListener(() =>
                {
                    _engine.Choose(choiceId);
                });
            }
        }
    }
}

