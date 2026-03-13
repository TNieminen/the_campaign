from pathlib import Path

try:
    from mido import Message, MidiFile, MidiTrack, MetaMessage, bpm2tempo
except ImportError:  # pragma: no cover - guidance for the user
    raise SystemExit(
        "This script now uses the 'mido' library to generate a standards-compliant "
        "MIDI file.\n\n"
        "Install it once with:\n"
        "    pip install mido\n\n"
        "Then run this script again."
    )


TICKS_PER_BEAT = 480  # standard PPQN


def build_midi_file() -> MidiFile:
    """
    Build a single-track MIDI file for the 'sunset medieval camp' theme.

    - Tempo: 75 BPM
    - Key: D minor
    - 8 bars of chords, loopable
    """
    mid = MidiFile(type=1)  # format 1 is very widely supported
    mid.ticks_per_beat = TICKS_PER_BEAT

    track = MidiTrack()
    mid.tracks.append(track)

    # Set tempo
    bpm = 75
    track.append(MetaMessage("set_tempo", tempo=bpm2tempo(bpm), time=0))

    # Chord progression: Dm, Bb, F, C, Dm, Gm, Bb, A
    chords = [
        # (bar_index, [MIDI note numbers])
        (0, [50, 53, 57]),  # D3 F3 A3 (Dm)
        (1, [46, 50, 53]),  # Bb2 D3 F3
        (2, [41, 45, 48]),  # F2 A2 C3
        (3, [48, 52, 55]),  # C3 E3 G3
        (4, [50, 53, 57]),  # D3 F3 A3
        (5, [43, 46, 50]),  # G2 Bb2 D3
        (6, [46, 50, 53]),  # Bb2 D3 F3
        (7, [45, 49, 52]),  # A2 C#3 E3
    ]

    whole_note_ticks = 4 * TICKS_PER_BEAT

    # Build chord notes with proper delta times
    current_time = 0
    for bar_index, notes in chords:
        # Time from last event to this bar start
        target_time = bar_index * whole_note_ticks
        delta_to_bar = target_time - current_time

        # Note-ons at bar start
        for i, note in enumerate(notes):
            time = delta_to_bar if i == 0 else 0
            track.append(Message("note_on", note=note, velocity=80, time=time))

        # Note-offs after one bar
        for i, note in enumerate(notes):
            time = whole_note_ticks if i == 0 else 0
            track.append(Message("note_off", note=note, velocity=0, time=time))

        current_time = target_time + whole_note_ticks

    # End of track
    track.append(MetaMessage("end_of_track", time=0))

    return mid


def main() -> None:
    out_path = Path("campaign_theme.mid")
    mid = build_midi_file()
    mid.save(out_path)
    print(f"Wrote {out_path} (format={mid.type}, ticks_per_beat={mid.ticks_per_beat}).")
    print("You can now import this MIDI file into Sonar / other DAWs.")


if __name__ == "__main__":
    main()


