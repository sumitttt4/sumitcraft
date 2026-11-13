# Changelog

SumitCraft's changes on top of simcraft. Upstream work is not listed here as ours; see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Commit `6f0e6ae` is the unmodified upstream import, so
`git diff 6f0e6ae` shows every change below.

## 0.1.0 (2026-11-13)

### Foundation (upstream simcraft 58224d1), kept
- All 24 skills, under their upstream names, with their scripts, references and examples, minus assets of unclear
  provenance (perspective-illusion cut-out PNGs; dx-audit uv screenshots, snapshots and video).

### Changed in foundation skills
- Layout flattened to `skills/<name>/`; all SKILL.md paths relative to the skill (`<skill>`, `<skill>/../<sibling>`).
- Windows portability: per-platform WebGL backend with readback and override (code-loop, perspective-illusion);
  `pathToFileURL` for every local page URL (scripted-screencast, repo-timelapse, vox-explainer); process-group start
  and kill on Windows (bisect-anything); no top-level POSIX `resource` import; `preexec_fn` and `RLIMIT_NOFILE` guarded
  (flaky-test-killer); venv paths for `Scripts/python.exe`; per-OS key and data folders (image-gen, brand-kit,
  vox-explainer); Windows path basename (repo-timelapse); font fallbacks for the macOS-only display face (vox-explainer).
- `setup.sh` replaced by cross-platform `setup.py` that prints a plan with sizes and installs only with `--yes`
  (rough-cut, reverse-engineer-video, paper-to-runnable); `.sh` and `.ps1` wrappers.
- code-loop: run manifest (settings, versions, backend actually used); `check_loop.py --holds` for intentional holds.
- image-gen: spend gate (`--dry-run`, refuses without `--approve-spend`, exit 3, before any request); sidecar marks
  images as generated; no free-tier or model claims from memory.
- vox-explainer: "style C" is now the credited `editorial-collage` preset; presets expose palette, typography,
  spacing, composition, texture and motion; two provisional presets; creator pronouns removed.
- rough-cut and clean-audio: creator taste becomes recorded, asked-for preferences; workspace location asked; model
  sizes stated before download; mixed Hindi/English guidance; honest limits on overlapping sources.
- reverse-engineer-video: virality trigger removed; estimates and manual corrections recorded.
- repo-timelapse: commit-message review file and `--redact-messages`; activity is not success.
- perspective-illusion: credits a genre rather than one artist's account; portable work-folder setup.
- brand-kit and skill-router: sibling and catalog paths fixed after flattening.
- OFL licence text added next to the Geist Mono copy in vox-explainer.

### Added
- Skills: design-to-code-inspection, design-critique, design-system-build, interaction-motion-study,
  visual-reference-analysis, learn-a-domain, work-to-explanation.
- from-scratch worked example (content-addressed store checked against `git hash-object`).
- `catalog/skills.mjs` and generated `contract.md` for every skill; docs: upstream audit, catalog, originality
  ledger, validation matrix, setup (Windows-first), chains.
- Tools: doctor (read-only diagnostics, per-skill readiness, next step), installer (copy-based, selective, marker-
  guarded, `--yes` for the global folder), static validator, docs generator; PowerShell wrappers.
- Tests: functional runner with evidence, path unit test, scenarios for guidance-only skills; inactive CI definitions.
- Claude Code plugin and marketplace manifests (`sumitcraft:<name>` namespacing).

### Added after 0.1.0 review
- design-hub: discovers every installed design skill on the machine (global, plugin, project, cloud image), classifies
  them by stage, reports overlaps and merges them into one plan with SumitCraft evidence checks. References other skills
  by name only (most installed design skills ship no licence file, so none are copied). Known-answer fixture test.
- Test logs and inventories now redact account and organisation IDs found in folder names.

- glyph: bundled from Glyph-Skill (MIT, Glyph Contributors) at `00d2bad`, unchanged apart from a contract link;
  registered in design-hub. SumitCraft measured its 13 starter-kit presets in Chromium: 11 pass, and the `bold` (3.28:1)
  and `retro` (4.30:1) button colours fall below 4.5:1 (fixes suggested in evidence/glyph, not applied).

### Vendored gap skills
Twenty-one third-party skills, one per gap the workshop did not already cover. Existing skill folders were not
edited. Sources, licences, and the skills that were left out are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
None of the new skills has a recorded run; the validation matrix lists them as not run. The installer accepts
`--category docs` and lists vendor skills under their category.

### Known gaps
- No native Windows or macOS run yet. clean-audio and the transcription parts of rough-cut and vox-explainer are blocked
  until the speech-model download is approved. No live image-gen provider call has been made. See the validation matrix.
