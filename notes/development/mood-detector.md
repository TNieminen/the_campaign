# Implementation plan: automatic D&D music importer

Implement an importer that accepts a list of audio files, analyzes their audio using a pretrained music-focused CLAP model, and suggests tags for a D&D soundboard.

Use the existing application's architecture where possible. The importer must work without user-provided training data.

## 1. Scope and approach

Use:
- A Python worker for decoding audio and running CLAP inference.
- A music-focused checkpoint from the official LAION CLAP project.
- FFmpeg for decoding supported audio formats.
- The existing application database for tracks, analysis results, and review state.

Run analysis locally by default. Download model weights once and cache them. Do not upload audio to external services.

Start with CLAP alone. Keep the analyzer modular so Essentia can be added later if testing shows that intensity classification needs improvement.

The output is a set of suggested tags, not a claim of objective classification.

Do not train or fine-tune a model in the initial implementation.

## 2. Import interface

Accept multiple files through the application's file picker or drag and drop.

Expose a corresponding worker/API entry point that accepts a list of accessible file references:

    import_tracks(files, options) -> job_id

Possible options:
- Analyze automatically: default true.
- Reanalyze previously processed files: default false.
- Auto-apply suggestions: default false.
- Model configuration.
- Sampling configuration.

For a browser application, file objects must be ingested into durable storage or a local companion service before the Python worker can read them. Do not assume browser-provided filenames are usable filesystem paths.

Support the common formats supported by the installed decoder, including MP3, WAV, FLAC, M4A, and OGG where available.

Validate each file independently. A corrupt or unsupported file must not fail the entire batch.

## 3. Tag taxonomy

### Purpose
Multiple suggestions permitted:
- Exploration
- Social
- Combat
- Chase
- Reveal

### Mood
Multiple suggestions permitted:
- Peaceful
- Warm
- Wondrous
- Mysterious
- Ominous
- Terrifying
- Melancholic
- Tragic
- Playful
- Heroic

### Intensity
One suggestion or unset:
- Low
- Medium
- High

### Setting / flavour
Optional; multiple suggestions permitted:
- Wilderness
- Settlement
- Dungeon
- Courtly
- Sacred
- Arcane
- Otherworldly
- Nautical

Do not force a mood or setting onto every track.
Allow any category to remain unresolved when evidence is weak.

## 4. Prompt configuration

Store tag descriptions in an editable, versioned configuration file.

Use several descriptions per tag, including different musical realizations. Avoid making percussion, particular instruments, or tempo mandatory for a tag.

Initial examples:

### Purpose prompts

Exploration:
- "Instrumental background music for exploring, with a sustained atmosphere and little urgency."
- "An atmospheric instrumental underscore for travel and discovery."

Social:
- "Unobtrusive instrumental music accompanying conversation or a social gathering."
- "Background music for dialogue, negotiation, or a tavern scene."

Combat:
- "Instrumental battle music with sustained rhythmic drive, tension, and confrontation."
- "Tense action music accompanying a fight."
- "Restrained but rhythmically tense music for a dangerous skirmish."

Chase:
- "Urgent instrumental pursuit music with rapid movement and relentless momentum."
- "Suspenseful action music for running, escaping, or being chased."

Reveal:
- "A dramatic musical revelation with a striking entrance or swelling discovery."
- "Instrumental music that builds toward a moment of awe or surprise."

### Mood prompts

Peaceful:
- "Calm, tranquil instrumental music with a feeling of safety and rest."

Warm:
- "Comforting, friendly instrumental music with a sense of companionship."

Wondrous:
- "Instrumental music expressing awe, enchantment, beauty, and discovery."

Mysterious:
- "Intriguing, enigmatic instrumental music suggesting curiosity and unanswered questions."

Ominous:
- "Unsettling instrumental music suggesting lurking danger and impending trouble."

Terrifying:
- "Frightening horror music with a strong sense of menace and terror."
- "Quiet but deeply disturbing music with an atmosphere of intense horror."

Melancholic:
- "Reflective, wistful instrumental music expressing loneliness or restrained sadness."

Tragic:
- "Heartbreaking instrumental music expressing grief, devastation, or profound loss."

Playful:
- "Lighthearted, mischievous instrumental music with a humorous or whimsical character."

Heroic:
- "Courageous, noble instrumental music expressing determination or triumph."

### Intensity prompts

Low:
- "Restrained, spacious background music with little rhythmic drive or dramatic activity."

Medium:
- "Moderately energetic instrumental music with noticeable movement and controlled dramatic tension."

High:
- "Forceful, urgent, highly energetic music with strong dramatic activity."

### Setting prompts

Wilderness:
- "Pastoral instrumental music evoking natural landscapes and woodland travel."

Settlement:
- "Instrumental music evoking a bustling village, town, or tavern."

Dungeon:
- "Claustrophobic, shadowy instrumental music evoking underground ruins or a crypt."

Courtly:
- "Formal, stately instrumental music evoking a royal court."

Sacred:
- "Reverent, ceremonial music with a devotional or liturgical character."

Arcane:
- "Instrumental music with an uncanny, magical, spellbinding character."

Otherworldly:
- "Alien, surreal instrumental music evoking an unfamiliar supernatural realm."

Nautical:
- "Seafaring instrumental music with a maritime or sailing character."

Expand these seeds with a small number of useful paraphrases.

Treat setting prompts as weak thematic associations, not literal location detection. They must be easy to reject or leave unresolved.

## 5. Audio preprocessing and sampling

For each file:

1. Read title, artist, album, duration, and available embedded metadata.
2. Compute a content hash for duplicate detection.
3. Decode the audio.
4. Select several excerpts distributed across the track.
5. Convert each excerpt to the sample rate, channel format, and input duration required by the selected checkpoint.
6. Compute one audio embedding per excerpt.

Suggested default:
- Five excerpts distributed across the usable duration.
- Use the checkpoint's supported input length.
- For short tracks, use fewer excerpts and the model's supported padding behaviour.
- Avoid mostly silent excerpts when possible.
- Preserve temporal diversity; do not select only the loudest sections.

Do not analyze only the introduction.

Keep preprocessing identical between imports. Record sampling timestamps and preprocessing version.

Filenames and metadata may populate display fields, but must not determine audio classifications.

## 6. Scoring and aggregation

Precompute and cache text embeddings for all prompt descriptions.

For each excerpt:
1. Compute cosine similarity with each prompt embedding.
2. Aggregate paraphrase scores into a score for each tag.
3. Retain per-excerpt tag scores.

For each track:
- Aggregate tag scores across excerpts.
- Retain score dispersion and per-excerpt top matches.
- Rank candidates separately within each category.

Use a documented aggregation method, such as the mean of prompt similarities followed by the median across excerpts. Keep it configurable for later evaluation.

Important:
- Similarity scores are not probabilities.
- Do not display "90% confidence" from raw similarity or softmax values.
- Raw scores may have different baselines across tags.
- Do not assume a universal threshold works for all tags.
- Do not force exactly one winning tag in every category.

Suggestion policy:
- Purpose: up to two plausible suggestions.
- Mood: up to two plausible suggestions.
- Intensity: one suggestion, or unresolved.
- Setting: optional and conservative.

Make selection rules configurable. Use score margins and agreement across excerpts as review heuristics, not guarantees of accuracy.

Until the selection rules have been evaluated, treat results as provisional suggestions requiring review. Automatic application remains opt-in.

For intensity, allow a middle excerpt to disagree without immediately marking the entire track variable. Flag variation when several excerpts show a meaningful, persistent difference.

## 7. Review flags

Generate understandable flags where appropriate:

- "Purpose unclear"
- "Mood unclear"
- "Intensity varies"
- "Possible atmosphere change"
- "Limited usable audio"
- "Analysis failed"

Base flags on recorded scores, segment disagreement, or processing failures.

Do not invent explanations about instruments or musical structure from similarity scores alone.

Provide representative excerpt timestamps so the user can quickly listen and review.

## 8. Data model

Keep confirmed metadata separate from machine suggestions.

Suggested analysis record:

    {
      "track_id": "...",
      "content_hash": "...",
      "analysis_status": "completed",
      "model_id": "...",
      "model_version": "...",
      "prompt_version": "...",
      "preprocessing_version": "...",
      "selection_policy_version": "...",
      "analyzed_at": "...",
      "sample_timestamps": [12.0, 48.0, 84.0],
      "suggested_tags": {
        "purpose": ["Combat"],
        "mood": ["Ominous", "Terrifying"],
        "intensity": "High",
        "setting": []
      },
      "tag_scores": {},
      "segment_scores": [],
      "review_flags": [],
      "review_status": "pending"
    }

Store separately:
- User-confirmed tags.
- Whether a category is manually locked.
- Accepted and rejected suggestions.
- Source of applied tags: manual or automatic.

Reanalysis must never overwrite confirmed or locked categories.

Save corrections for future evaluation. Do not claim the model learns from corrections unless an explicit learning mechanism is implemented.

## 9. Import jobs and resilience

Track progress through:
- Queued
- Reading metadata
- Decoding
- Analyzing
- Awaiting review
- Completed
- Failed
- Cancelled

Show:
- Files processed / total.
- Current file.
- Per-file failures.
- Counts awaiting review and completed.
- Cancel and retry controls.

Load the model once per worker.
Use bounded concurrency to avoid exhausting memory.
Checkpoint progress after each file.
Resume incomplete jobs without reprocessing successful files.
Make cancellation cooperative between processing stages or batches.

Deduplication:
- Detect identical file content using hashes.
- Reuse cached analysis when model, prompts, and preprocessing match.
- Cache audio embeddings separately so prompt changes can be evaluated without decoding audio again.
- Do not silently merge files based only on title or filename.

## 10. Review UI

After analysis, show a reviewable list containing:
- Track title and duration.
- Suggested purpose, mood, intensity, and setting.
- Review flags.
- Play and excerpt-preview controls.
- Accept, edit, and reject actions.

Support:
- Accept selected tracks.
- Accept one category across selected tracks.
- Bulk correction.
- Filtering to unresolved or flagged tracks.
- Keeping a track imported even if all suggestions are rejected.

Rejected suggestions must not immediately reappear as new pending suggestions unless the analysis configuration changes or the user explicitly requests reanalysis.

## 11. Integration with the soundboard

Accepted tags feed the existing library filters and saved session shortcuts immediately.

Analysis must run in the background without interrupting music playback.

Manual playback and browsing should remain responsive while importing.

Suggested tags must be visually distinguishable from confirmed tags. Default scene filters should use applied tags, not unaccepted suggestions.

Preserve cached audio embeddings so natural-language music search can be added later. Natural-language search is optional and not required for this first implementation.

## 12. Evaluation

No labelled examples are required to start importing.

Provide an optional evaluation workflow:
1. The user confirms tags for a small representative collection.
2. Compare automatic suggestions with these confirmed tags.
3. Inspect common confusions, especially:
   - Exploration versus Combat.
   - Combat versus Chase.
   - Mysterious versus Ominous.
   - Ominous versus Terrifying.
   - Melancholic versus Tragic.
4. Adjust prompt descriptions and selection rules.
5. Check adjustments against additional tracks.

Treat this as evaluation and calibration, not model training.

Do not claim a target accuracy without measuring it on representative music.

## 13. Delivery phases

### Phase 1: working batch analyzer
- File-list input.
- Metadata extraction and decoding.
- CLAP model loading.
- Distributed excerpt analysis.
- Versioned prompt configuration.
- Ranked scores and provisional suggestions.
- Structured output and per-file errors.

### Phase 2: application integration
- Background import jobs.
- Persistence and caching.
- Review interface.
- Accepting and correcting tags.
- Integration with existing filters and shortcuts.

### Phase 3: refinement
- Evaluate on user-reviewed tracks.
- Improve prompt descriptions and selection rules.
- Tune variable-track flags.
- Add Essentia only if it resolves a demonstrated weakness.
- Optionally add natural-language search using cached embeddings.

## 14. Acceptance criteria

- A list of files can be imported and analyzed without labelled training data.
- Classification uses the actual audio.
- Multiple sections of each track contribute to results.
- Categories are scored independently.
- Ambiguous categories can remain unresolved.
- Raw similarity is not presented as probability.
- One corrupt file does not stop a batch.
- Interrupted jobs can resume.
- Duplicate files reuse compatible analysis.
- Prompt changes can reuse cached audio embeddings.
- Manual corrections survive reanalysis.
- Suggested tags can be reviewed and accepted in bulk.
- Existing playback continues during analysis.
- No audio is uploaded externally by default.

Before implementation, verify the chosen checkpoint's current installation requirements, input format, and licence. Document the model and dependency versions used.
