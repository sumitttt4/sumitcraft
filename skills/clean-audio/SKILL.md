---
name: clean-audio
description: Clean up voice audio in a video: rumble, electrical hum, background noise and hiss, muddy or harsh tone, sharp S sounds, uneven volume, and loudness for YouTube/Instagram/TikTok. Measures the audio first, picks the strongest cleanup that doesn't make the words less clear, and keeps lip sync exact. Use when the user says "clean up the audio", "fix the sound", "remove background noise", "remove hum", "my audio is too quiet/loud", "make it sound better", or after a rough cut.
---

# Clean audio

Run with the rough-cut skill's Python (`PY` below): `<skill>/../rough-cut/.venv/Scripts/python.exe` on Windows, `<skill>/../rough-cut/.venv/bin/python` elsewhere. If it doesn't exist, run `python <skill>/../rough-cut/setup.py` to see the plan, then with `--yes`. It shares rough-cut's helpers and uses Whisper (the `small` model, about 0.5 GB, downloads on first use) for the clarity check.

## Steps

1. **Listen test first.** Make a 10-second before/after of the busiest talking moment. Both are set to the same loudness, so the comparison is about quality, not volume:
   ```
   $PY scripts/clean_audio.py <video> --sample
   ```
   Give the user the paths of both wav files to play (do not launch a player for them) and the report. The numbers are diagnostics: the decision is made by listening.

2. **Apply.** There are two ways to run it:
   - In a rough-cut workspace, before rendering. It cleans each raw clip into `audio/<clip>.clean.wav`, and rough-cut's `render.py` uses those automatically:
     ```
     $PY scripts/clean_audio.py <workspace>
     ```
     Then render and verify as usual. The report is saved to `audio/cleanup.md`.
   - On a single video. It writes `<name>_clean.<ext>` next to the original, with the video copied untouched:
     ```
     $PY scripts/clean_audio.py <video>
     ```

3. **Report** in plain words:
   - the speech-vs-background gap before and after,
   - the final loudness,
   - what was found (hum, clipping),
   - which strength the clarity check settled on.

   If the report says leftover noise is voices or music, tell the user that these filters cannot remove overlapping voices or music, and that a dedicated voice-isolation tool is the next option (it may be a hosted service: say so before sending audio anywhere).

## Options

- `--strength strong|medium|light` sets the strongest denoise to try. The default is medium, and the clarity check steps it down on its own.
- `--target -14` sets the loudness in LUFS. -14 is right for YouTube, Instagram and TikTok; use -16 for podcasts.
- `--no-eq` skips the tone shaping, if the user likes their voice as it is.

## Rules

- **Clean the raw clips before cutting, not after.** The noise is learned from a pause, and the rough cut removes the pauses.
- Never touch the original files.
- Never trade clarity for quiet. The clarity check enforces this: no lost words, and confidence within 0.015 of the original.
- Don't push audio to digital silence between words. A little room sound is kept on purpose.

What each step does, why it's built this way, and the test numbers: [reference.md](reference.md).

Contract, prerequisites and validation status: [contract.md](contract.md).
