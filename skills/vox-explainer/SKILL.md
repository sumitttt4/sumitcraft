---
name: vox-explainer
description: Make voice-led editorial explainer graphics or a full faceless explainer video: big type, quotes, stats, charts, photos and cut-outs, with every beat, highlight and list item timed to the exact word in the voiceover. The look comes from an inspectable preset (palette, typography, spacing, composition, texture, motion): the upstream editorial-collage preset by default, two provisional alternatives, or a brand kit. Use when asked for a Vox-style or editorial explainer, explainer graphics, animated quotes or stats over a voiceover, or word-timed motion graphics. Not for screen recordings (scripted-screencast) or generative loops (code-loop).
---

# Vox explainer

Setup, once: `run `npm install` once in the SumitCraft folder (Playwright)`. It also needs rough-cut's Python env (`sh <skill>/../rough-cut/setup.sh`) for word timings, and ffmpeg.

## Steps

0. **Look first.** If the video is for, with or about a company (a sponsor, a client), run the **brand-kit** skill for that company first (check the brand's official guidelines and usage rights), show the user its board, then put `"brand": "<slug>"` in the scene. Otherwise pick a preset with `"preset": "<name>"`: `editorial-collage` (default; the upstream look, credited), or the provisional `quiet-paper` and `night-signal`. Each file in `presets/` spells out palette, typography, spacing, composition, texture and motion, so the choice can be inspected and changed. If the look is a taste decision the user has not made, render one still per preset (step 4) and let them choose; do not pick a personal style on their behalf.
1. **Voice first.** Get the voiceover before designing anything. It can be the creator's recorded take (run rough-cut and clean-audio on it first) or a narration file. The picture is timed to the voice, never the other way round.
2. **Beat map.** Read the transcript and write one beat per idea, about 2.5–3.5 s each. For each beat, name its point in one clause. If you can't, the beat is filler. Show the beat list to the user before building.
3. **Write the scene file** (format below), next to the voiceover.
4. **Check layouts with stills** at a few seconds, and look at them:
   `python3 scripts/build.py scene.json --stills 2,6.5,11`
5. **Preview** (half size, fast). It ends with a motion check that fails if anything sits still for 0.5 s or more:
   `python3 scripts/build.py scene.json --preview`
6. After the user approves, render the **final** at full size: `python3 scripts/build.py scene.json`

Add `--words <file>` to reuse word timings you already have, such as rough-cut's `audio/words.json` or verify's `cuts/verify_vN_words.json` for a cut. Otherwise the voiceover is transcribed.

## Scene file

```json
{ "audio": "vo.mp4", "format": "16:9",
  "beats": [
    {"at": "Did", "device": "big", "bg": "red", "text": "$0", "sub": "What startups spent on SOC 2", "submark": "SOC 2", "submark_at": "SOC2"},
    {"at": "today", "device": "photo", "url": "https://example.com", "caption": "example.com, today",
     "tags": [{"text": "Same product", "at": "selling", "yellow": true, "x": 62, "y": 78}]},
    {"at": "Then", "device": "card", "label": "Their security team", "quote": true, "text": "Where's the SOC 2 report?", "mark": "SOC 2 report", "mark_at": "SOC"}
  ] }
```

- `at` is the word (or a few words) in the voiceover where the beat starts. Each beat searches after the previous one. A number means seconds.
- `mark`, `headmark` and `submark` are the phrase to highlight. It sweeps in when its first word is spoken; use `*_at` if the transcript spells it differently ("SOC2"). **Only one highlight per beat.**
- `preset` is a preset name from `presets/` or a path to your own preset JSON. `brand` is a brand-kit slug (or folder) and overrides the preset.
- `bg` is `a`, `b`, `paper` or `accent` (`navy`/`red` still work as aliases for `a`/`b`). Alternate them. The diagonal split changes on its own each beat. Use `"flat": true` for a single colour.
- `format` is `16:9` or `9:16`. `"twos": false` turns off the 12 fps stepped motion.
- `tags` are black mono label strips (`yellow: true` for the accent). `x` and `y` are in % of the frame, and `at` is the word that brings the tag in.

| Device | Use for | Fields |
|---|---|---|
| `big` | One huge statement or number | `text`, `sub`, `mark`/`submark` |
| `card` | Torn paper card: a quote, a question, a claim | `label`, `head`, `text`, `quote`, `mark`/`headmark`, `width`, `tilt` |
| `stat` | A number counting up | `value`, `prefix`, `suffix`, `sub` |
| `photo` | Real evidence: a screenshot, document or photo, pinned like a print with a slow push-in | `img` or `url` (captured automatically), `caption`, `width`, `ratio`, `tilt` |
| `cutout` | An object dropped onto the colour blocks | `img` (transparent PNG; make one with the image-gen skill using `--cutout`), `size`, `x`, `tilt` |
| `list` | Numbered points, each landing on its word | `items`, `items_at`, `label` |
| `chart` | A line that draws itself | `points`, `label`, `end_label`, `draw_ms` |

## Rules

These apply to every preset and brand. Palette, typography, edges and motion style come from the preset or brand kit, not from this file.

- **One idea per frame, type big enough to read on a phone.** Use only the preset's palette; one accent for highlights.
- **Mix in pictures.** All-text reads as a slideshow. Use a `photo` with a real screenshot or document every few beats. For things that can't be screenshotted, make cut-outs with image-gen. Generated images never contain text; all type is set in code.
- **Real evidence must be real.** Never present a generated image as a document, a screenshot or a quote.
- **Nothing freezes.** Every beat slowly pushes in, and the motion check enforces it.
- Sound effects are a creator preference; ask before adding any.
- The motion check flags holds of 0.5 s or more. A deliberate hold is allowed: say so, and have a person watch the preview. The check is a diagnostic, not a substitute for watching.

Research, design reasoning and what each choice fixes: [reference.md](reference.md).

Contract, prerequisites and validation status: [contract.md](contract.md).
