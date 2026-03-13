# Campaign scene setup (Unity)

Step-by-step instructions to create a scene with a full-screen background image and UI (text + buttons) on top.

## 1. New scene

- **File → New Scene** (or duplicate an existing one).
- Save as `Assets/Scenes/CampaignScene.unity` (or your preferred name).

## 2. Canvas (UI root)

- **GameObject → UI → Canvas**.
- On the Canvas:
  - **Render Mode**: Screen Space - Overlay (default).
- Add a **Canvas Scaler** if not present: **Add Component → Canvas Scaler**.
  - **UI Scale Mode**: Scale With Screen Size.
  - **Reference Resolution**: e.g. 1920 × 1080.
  - **Match**: 0.5 (or adjust for your aspect ratio).
- Add **EventSystem** if Unity didn’t create it: **GameObject → UI → Event System**.

## 3. Background image (full screen)

- Under the Canvas: **Right‑click Canvas → UI → Image**.
- Name it e.g. **BackgroundImage**.
- **RectTransform**:
  - Anchor: stretch both horizontally and vertically (bottom‑right anchor preset: hold **Alt**, click the stretch icon so left/right/top/bottom all stretch).
  - **Left, Right, Top, Bottom**: all **0** so it fills the screen.
- **Image** component:
  - **Source Image**: assign your background sprite (e.g. `Assets/Images/campaign` — use the sprite from the campaign image asset).
  - **Color**: white (255,255,255,255) for no tint.
- Optional: set **Raycast Target** off if you don’t need the background to block UI clicks.

## 4. Story text

- Under Canvas: **Right‑click Canvas → UI → Text - TextMeshPro** (recommended).
- Name it e.g. **DescriptionText**.
- **RectTransform**:
  - Anchor to a region (e.g. top-center or bottom-half). Example: anchor top, stretch horizontally; set **Left** / **Right** for margins, **Height** and **Pos Y** as needed.
  - Or anchor bottom and give it a fixed height and Y position so it sits above the buttons.
- **No background**:
  - Make sure the GameObject only has `RectTransform` + `TextMeshProUGUI` (no `Image` component). If there *is* an `Image`, either remove it or set its Color alpha to 0.
- **Text appearance** (red with black outline, tuned for readability):
  - In the `TextMeshProUGUI` component on your `DescriptionText` object (shown in the Inspector as **“TextMeshPro - Text (UI)”**), set **Color** to a slightly darker red (e.g. `R=0.9, G=0.1, B=0.1, A=1`) to avoid over-bright edges.
  - Scroll to the bottom of that **TextMeshPro - Text (UI)** component and locate the **Material** field (it shows the font material that TMP is using).
  - Click the small circle or the material thumbnail to open it, then click **Edit** (or open the material in the Inspector).
  - In the material Inspector (SDF TMP shader), find the **Outline** section:
    - Set **Outline Color** to black (`R=0, G=0, B=0, A=1`).
    - Increase **Outline Width** gradually (e.g. start at `0.3–0.5`) until the text clearly separates from the background.
  - For very busy backgrounds, consider:
    - Slightly darkening the area behind the text with a semi-transparent black panel (low alpha, e.g. `A=0.3–0.4`), or
    - Increasing the **Font Size** and **Line Spacing** a bit for extra legibility.
  - Adjust alignment (e.g. top-left or center) and overflow (Vertical Overflow = Overflow) as desired.

## 5. Choices container (for buttons)

- Under Canvas: **Right‑click Canvas → Create Empty**.
- Name it **ChoicesContainer**.
- **RectTransform**:
  - Anchor to bottom (or above DescriptionText). Stretch horizontally; set **Left**, **Right**, **Top**, **Bottom** to define the strip where choice buttons will appear.
- **Grid layout for 2×3 choices** (up to 6 options, **fill left column first**):
  - Add **Grid Layout Group** component.
  - **Cell Size**: e.g. `Width = 300`, `Height = 80` (tune to your taste).
  - **Spacing**: e.g. `X = 20`, `Y = 10`.
  - **Start Corner**: `Upper Left`.
  - **Start Axis**: `Vertical` (so it fills down a column before moving to the next).
  - **Child Alignment**: `Upper Center` (or `Upper Left` if you prefer).
  - **Constraint**: `Fixed Row Count`.
  - **Constraint Count**: `3` (3 rows per column; with 1–3 choices they all appear in the left column; 4–6 start filling the right column).
  - Make sure **ChoicesContainer has a non‑zero height** in its RectTransform (e.g. anchored to bottom with Top/Bottom giving it a visible band); if its height is 0, all grid cells collapse on top of each other.

### Debugging the grid layout

- At edit time you won’t see the runtime‑spawned buttons, so to debug the grid:
  - Temporarily create a **dummy Button** as a child of **ChoicesContainer** (right‑click ChoicesContainer → UI → Button).
  - You should immediately see how the Grid Layout Group positions that dummy button; adjust **Cell Size**, **Spacing**, and the **ChoicesContainer RectTransform** until it sits where you want.
  - When the layout looks good, you can delete the dummy button (your prefab‑spawned buttons will use the same layout at runtime).

## 6. Choice button (prefab)

- Under **ChoicesContainer**: **Right‑click ChoicesContainer → UI → Button** (so the button is a child and uses the grid layout).
- Name it **ChoiceButton**.
- Resize and style the button (RectTransform, Image, etc.).
- Replace the default `Text` child with **TextMeshPro**:
  - Delete the built-in `Text` child if present.
  - Right-click the button → **UI → Text - TextMeshPro** to add a `TextMeshProUGUI` child.
  - Name it e.g. **Label**.
- **Choice text appearance** (no extra background, red text with black outline):
  - Ensure the label child has only `RectTransform` + `TextMeshProUGUI` (no `Image`).
  - In `TextMeshProUGUI`, set **Color** to red (e.g. `R=1, G=0, B=0, A=1`).
  - Scroll to the bottom of the TMP component, find the **Material** field, and open that material in the Inspector.
  - In the TMP SDF material Inspector:
    - Set **Outline Color** to black (`R=0, G=0, B=0, A=1`).
    - Set **Outline Width** to a small value (e.g. `0.2–0.4`) and tweak.
  - Set placeholder text (e.g. “Choice”); `StorySceneController` will replace this at runtime.
- **Button and label sizing**:
  - The visible text is constrained by the **button’s RectTransform**; if the font is large and the button is too small, text will wrap or be clipped.
  - When the button lives inside a **Grid Layout Group**, the actual on‑screen size is controlled by the grid’s **Cell Size**. It is normal for a prefab with stretch anchors to show `Width = 0, Height = 0` in the RectTransform — at runtime, the cell size will give it real dimensions.
  - Pick a readable **Font Size** (e.g. 24–32 for labels at 1080p), then adjust the grid’s **Cell Size** so there is comfortable padding around the text.
  - Avoid “Best Fit” for now; instead, pick a clear font size and adjust the grid cell size to match so readability stays consistent across choices.
- When you’re happy with the look, drag **ChoiceButton** from the Hierarchy into `Assets/` (or a subfolder like `Assets/Prefabs`) to create a **prefab**.
- Optionally delete the instance from the scene if you only want buttons spawned by script.

## 7. Hook up StorySceneController

- **Create Empty** in the scene (not under Canvas). Name it **StoryController**.
- **Add Component → Scripts → Story Scene Controller** (your `StorySceneController` script).
- Assign in the Inspector:
  - **Campaign Image**: the BackgroundImage (`Image` component on that GameObject).
  - **Description Text**: the DescriptionText (`TextMeshPro - Text (UI)` / `TextMeshProUGUI` component).
  - **Choices Container**: the ChoicesContainer (the `RectTransform` / `Transform` of that GameObject).
  - **Choice Button Prefab**: the ChoiceButton prefab.

> When assigning fields in the Inspector, **drag the GameObject from the Hierarchy**, not the individual component from the Inspector. Unity will automatically pick the correct component type (e.g. `TextMeshProUGUI` or `RectTransform`) from that GameObject if it matches the field type.

## 8. Background music (audio)

- Place your audio file (e.g. `*.mp3`, `*.wav`, `*.ogg`) under `Assets/Audio/` in the Unity project.
- In your scene:
  - **Right‑click Hierarchy → Create Empty** and name it `MusicPlayer`.
  - With `MusicPlayer` selected, click **Add Component → Audio → Audio Source**.
  - Drag your imported audio clip from the Project window into the **AudioClip** field of the `Audio Source`.
  - Enable **Loop** if you want continuous background music.
  - Enable **Play On Awake** so it starts automatically when the scene loads.
- Ensure your **Main Camera** still has an **Audio Listener** component so you can hear the audio.

## 9. Quick reference

| Element            | Purpose                                      |
|--------------------|----------------------------------------------|
| Canvas             | Root for all UI; use Canvas Scaler for scaling. |
| BackgroundImage    | Full-screen image (stretch anchor, margins 0).  |
| DescriptionText    | Story node text.                            |
| ChoicesContainer   | Parent for dynamically created choice buttons. |
| ChoiceButton prefab| Button prefab with a Text child for label.   |
| StoryController    | GameObject with `StorySceneController` and references. |
| MusicPlayer        | GameObject with `AudioSource` that plays background music. |

After this, entering Play mode should show the background image, background music, the first node’s text in DescriptionText, and clickable choice buttons in ChoicesContainer.
