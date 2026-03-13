AI Rules for The Campaign
=========================

- **Documentation updates**:
  - When the user asks for a clarification about a document that the AI has created (for example, a note under `notes/`), and the outcome is that the document should be changed or clarified, the AI must update that document accordingly instead of only explaining the change in chat.
  - The AI should mention briefly in its reply that the corresponding note/doc was updated.

- **Color values in Unity notes**:
  - When giving color examples for Unity UI or TextMeshPro, the AI should express RGBA values in the **0–255 format** (e.g. `R=230, G=25, B=25, A=255`) to match the default Inspector presentation, and may optionally mention the 0–1 equivalents in parentheses if useful.
