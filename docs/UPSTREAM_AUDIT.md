# Upstream audit (before changes)

- Source: https://github.com/dotslashsimran/simcraft
- Commit: `58224d131814572224537fb516b8c5d33dd5fa67` (2026-11-09, "Redesign README, add MIT license, remove preview GIF"); 3 commits, one author.
- Licence: MIT, Copyright (c) 2026 Simran Sachdeva. Manifests: `package.json` (playwright 1.60.0), `package-lock.json`, `.gitignore`.
- Read: README, LICENSE, manifests, all 24 `SKILL.md`, every `reference.md`, and every script was searched for platform
  assumptions and imports. No upstream code was executed before the audit was written; nothing was installed globally.

## Capability inventory

| Skill (upstream path) | Scripts | Setup | Python deps | Other deps | Network |
|---|---|---|---|---|---|
| perspective-illusion (video) | blink_map.py, 3 renderers (.mjs), 5 scene templates | npm in work folder | numpy (checks) | three 0.170, Playwright, ffmpeg | npm only |
| code-loop (video) | render_loop.mjs, check_loop.py, 2 starters | npm in work folder | numpy | Playwright, ffmpeg, three (optional) | npm only |
| reverse-engineer-video (video) | analyze, cuts, motion, audio, ocr, sheets, compare (.py) | setup.sh (OpenCV, optional Whisper) | numpy (+cv2, whisper) | ffmpeg, tesseract (opt.) | model download |
| scripted-screencast (video) | capture, compose, render (.mjs), compositor.html | repo npm | none | Playwright, ffmpeg | target URL |
| repo-timelapse (video) | extract.py, render.mjs, engine | repo npm | none | git, Playwright, ffmpeg | none |
| rough-cut (video) | transcribe, find_cuts, render, verify (.py) | setup.sh (Whisper) | numpy, faster-/mlx-whisper | ffmpeg | model download |
| clean-audio (video) | clean_audio.py | reuses rough-cut venv | numpy, whisper | ffmpeg | model download |
| vox-explainer (video) | build.py, render.mjs, shot.mjs, motion_check.py, engine | repo npm + rough-cut venv | numpy | Playwright, ffmpeg | photo URLs |
| codebase-map (coding) | entrypoints, deps, hotspots, trace_py, check_map | none | stdlib | git | none |
| bisect-anything (coding) | bisect, bisect_list, hunk_minimise, 4 oracles | none | stdlib | git | none |
| flaky-test-killer (coding) | flake_rate, stress, find_polluter, 2 shims | none | stdlib | node (optional) | none |
| benchmark-honestly (coding) | bench, env_report, latency_test | none | stdlib | none | local URL |
| api-design-review (coding) | lint_openapi, breaking_diff, sdk_surface | none | stdlib (+PyYAML opt.) | none | none |
| security-threat-model (coding) | surface, secrets_scan, dataflow | none | stdlib | none | local only |
| dx-audit (coding) | friction.py, snapshot.mjs, svg2png.mjs | repo npm | stdlib | Playwright, ffmpeg (reel) | target docs |
| paper-to-runnable (learning) | fetch_paper, animate + grokking example | setup.sh | numpy, matplotlib, pypdf (+torch) | ffmpeg | arXiv |
| system-design-from-scratch (learning) | loadgen, faultsim + 2 examples | none | stdlib (+matplotlib opt.) | none | none |
| from-scratch (learning) | none (guidance) | none | none | none | none |
| teach-back (learning) | none (guidance) | none | none | none | none |
| image-gen (design) | gen_image.py | none | stdlib | none | Gemini / OpenAI (paid) |
| brand-kit (design) | extract.mjs, propose.py, board.py | repo npm | stdlib | Playwright, ffmpeg | brand site |
| skill-router (planning) | catalog.py | none | stdlib | none | none |
| next-step (planning) | none (guidance) | none | none | none | none |
| video-script (planning) | none (guidance) | none | none | none | none |

## Gap report (what the audit found)

Portability (Windows was not a target upstream):
1. README install is a Bash symlink loop into `~/.claude/skills`; symlinks need developer mode or admin on Windows, and it links everything globally at once.
2. `code-loop/scripts/render_loop.mjs` and all three perspective-illusion renderers launch Chromium with `--use-angle=metal` (macOS only); nothing reports which backend actually ran.
3. `scripted-screencast/scripts/capture.mjs` builds `"file://" + path.resolve(...)`: invalid on Windows (`file://C:\...`), unencoded spaces and Unicode, and its scheme test treats `C:` as a URL scheme. Same string-built URLs in repo-timelapse and vox-explainer renderers.
4. `setup.sh` in rough-cut, reverse-engineer-video and paper-to-runnable: `sh`, `uname`, `.venv/bin/python`; vox-explainer hard-codes `rough-cut/.venv/bin/python`.
5. bisect-anything uses `start_new_session` + `os.killpg` (POSIX); `bench_oracle.py` imports `resource` at top level (crashes on Windows).
6. flaky-test-killer `stress.py` passes `preexec_fn` and uses `RLIMIT_NOFILE` (POSIX).
7. Paths assume macOS or upstream's own layout: `~/simcraft/...` in most SKILL.md files, `~/Movies/edits`, `~/.config/simcraft`, `~/.local/share/simcraft`, `open` / `open -e`; `brand-kit/board.py` and `skill-router/catalog.py` hard-code the category folder depth.
8. The vox engine's default display face, Avenir Next Condensed, exists only on macOS, with no fallback stack.

Overclaims and inherited personal assumptions:
9. vox-explainer is defined by one creator's "style C" and pronouns ("her taste", "she has called that out"); quality equals that look.
10. rough-cut hard-codes "the user's taste" (snappy cuts, no whooshes) as rules, and quotes upstream's real-footage result as general.
11. reverse-engineer-video triggers on "why does this go viral"; motion metrics invite virality inference.
12. check_loop treats any hold over 0.5 s as a failure; there is no way to declare an intentional hold.
13. perspective-illusion names a specific creator's account as the style reference.
14. image-gen makes paid calls with no plan or approval step; model defaults and free-tier claims are stated from memory.
15. repo-timelapse has no review step for commit messages before export; activity can read as success.

Licensing and assets:
16. Twelve template cut-out PNGs (characters, food, products) have no stated provenance; likely generated.
17. dx-audit's example ships screenshots and copied text of a third party's documentation.
18. Geist Mono in vox-explainer ships without its OFL text (repo-timelapse has it). The shader starter embeds MIT simplex noise (credited in-file).

Structure and evidence:
19. No per-skill contract (inputs, deliverables, cost, network, decisions), no validation record, no diagnostic command, no CI.
20. Four guidance-only skills (from-scratch, teach-back, next-step, video-script) have no examples or scenarios.

Each item is resolved, or deliberately left with a reason, in [ORIGINALITY_LEDGER.md](ORIGINALITY_LEDGER.md) and
[../CHANGELOG.md](../CHANGELOG.md).

## Implementation order used

1. Import upstream unmodified (commit `6f0e6ae`) so every later change is a reviewable diff.
2. Flatten layout and fix paths; portability fixes 2-8 with platform-specific branches rather than removals.
3. Generalise 9-15 into configurable, asked-for choices; add the spend gate.
4. Add the expansion skills with fixtures that fail on planted problems and pass on fixed ones.
5. Catalog, contracts, doctor, installer, validator; then run everything that can run here and record it honestly.
