# SumitCraft

A local-first workshop of Claude Code skills for making, investigating, learning and explaining things: video,
engineering, learning, design and planning.

SumitCraft is built on **[simcraft](https://github.com/dotslashsimran/simcraft) by Simran Sachdeva** (MIT). All 24 of
simcraft's skills are kept under their original names as the foundation; SumitCraft adds portability (Windows as a
first-class target), a contract and validation record for every skill, configurable presets in place of one creator's
personal taste, and seven new skills. What came from upstream and what changed is listed skill by skill in
[docs/ORIGINALITY_LEDGER.md](docs/ORIGINALITY_LEDGER.md). Most of the foundation's methods and scripts are upstream's
work, and this README does not claim otherwise.

> **Status: a working local toolkit, not a finished or launch-ready product.** Every recorded run is on Linux in a
> cloud container with software WebGL. Native Windows and macOS have not been run yet. Two video skills that need a
> speech model are blocked until that download is approved. The honest per-skill picture is in
> [docs/VALIDATION_MATRIX.md](docs/VALIDATION_MATRIX.md).

## What is in it

| Area | Foundation skills (from simcraft) | SumitCraft additions |
|---|---|---|
| Video | perspective-illusion, code-loop, reverse-engineer-video, scripted-screencast, repo-timelapse, rough-cut, clean-audio, vox-explainer | |
| Engineering | codebase-map, bisect-anything, flaky-test-killer, benchmark-honestly, api-design-review, security-threat-model, dx-audit | |
| Learning | paper-to-runnable, system-design-from-scratch, from-scratch, teach-back | learn-a-domain |
| Design | image-gen, brand-kit | **design-hub**, **glyph** (from Glyph-Skill), design-critique, design-to-code-inspection, design-system-build, interaction-motion-study, visual-reference-analysis |
| Planning | skill-router, next-step, video-script | work-to-explanation |
| Docs | | **pdf**, **docx**, **pptx**, **xlsx** (Apache-2.0, from anthropics/skills) |

**Vendored gap skills** sit in the same `skills/` tree and install with the rest (`node tools/install.mjs install --category docs`, or `--category video` for the new video skills). One skill per gap. Existing SumitCraft skills were not rewritten.

| Gap | Skill |
|---|---|
| Mixed clips, plus a quiet music mix | vlog-auto-edit |
| Burned-in captions | burned-in-captions |
| Thumbnail options | thumbnail-ab |
| Upload packaging (aspect ratio and encode) | platform-video-export |
| Long-form script and shot list | long-form-storyboard |
| Commits, pull-request text, git operations | git-authoring |
| Root-cause debugging | systematic-debugging |
| Test-first implementation | test-driven-development |
| Implementation plan | writing-plans |
| Prove a "done" claim | verification-before-completion |
| Diff review (standards and spec) | code-review |
| Local Compose stack | docker-compose-patterns |
| React and Next.js performance | react-best-practices |
| Session handoff | handoff |
| Meeting notes to owned tasks | meeting-notes-to-tasks |
| Primary-source research notes | primary-source-research |
| Web interface guidelines audit | web-design-guidelines |
| PDF, Word, slides, spreadsheets | pdf, docx, pptx, xlsx |

Skills that were not vendored, and how to install them yourself, are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

**design-hub** is the design category's front door. On whatever machine SumitCraft is installed, it finds every design
skill present (a design plugin, frontend-taste packs, GSAP, Figma, art skills, SumitCraft's own), sorts them into
stages, flags overlaps, and merges them into one plan, pairing each step with a SumitCraft check that measures the
result. It calls other skills by name and never copies them. **Glyph**, the frontend design-judgement skill from the
owner's [Glyph-Skill](https://github.com/sumitttt4/Glyph-Skill) repo, is bundled as-is and is design-hub's first choice for
direction and building when it is installed. Try: `python skills/design-hub/scripts/find_design_skills.py --task "polish my landing page and make it accessible"`.

One line per skill, with prerequisites and status: [docs/CATALOG.md](docs/CATALOG.md). Each skill folder has a
`SKILL.md` (the method) and a `contract.md` (inputs, deliverables, prerequisites, network and cost behaviour, human
decisions, checks, failure cases, limits, example, validation status).

## Install

You need Node.js 18.19+ for the tools. Most skills also need Python 3.9+; video skills need ffmpeg. Check everything
with the doctor first. It is read-only, prints no secrets, and ends with the exact next step.

```powershell
# Windows (PowerShell)
git clone https://github.com/sumitttt4/sumitcraft
cd sumitcraft
npm install                                                    # the Playwright package only
powershell -ExecutionPolicy Bypass -File tools\doctor.ps1      # what is missing, and what to run next
```

```bash
# macOS / Linux
git clone https://github.com/sumitttt4/sumitcraft && cd sumitcraft
npm install
node tools/doctor.mjs
```

Then choose **one** way to give Claude Code the skills:

1. **As a plugin (recommended).** In Claude Code: `/plugin marketplace add sumitttt4/sumitcraft`, then
   `/plugin install sumitcraft@sumitcraft`. Skills load as `sumitcraft:<name>`, so they cannot collide with skills you
   already have. Remove them with `/plugin uninstall sumitcraft@sumitcraft`.
2. **Copy selected skills into one project** (no global changes):
   ```
   node tools/install.mjs list
   node tools/install.mjs install code-loop design-critique --scope project --dry-run
   node tools/install.mjs install code-loop design-critique --scope project
   ```
3. **Copy into your global skills folder** (`~/.claude/skills`, every project): the installer refuses until you add
   `--yes`. It copies (no symlinks, so it works on Windows), never overwrites a skill it did not install, and
   `uninstall` removes only folders carrying its own marker.

Heavier extras are opt-in, per skill, and always show a plan before doing anything:
`python skills/rough-cut/setup.py` (speech model, 0.5-1.5 GB on first use), `python skills/reverse-engineer-video/setup.py`
(OpenCV), `python skills/paper-to-runnable/setup.py` (matplotlib, pypdf, optional PyTorch). Add `--yes` to install.
Browser binaries are separate from the npm package: `npx playwright install chromium` (about 150-200 MB).
Full guide, including supported Windows versions: [docs/SETUP.md](docs/SETUP.md).

## Using it

You do not call skills by name; describe the task and Claude Code picks the skill whose description fits. Some things to try:

- "Render this shader as a seamless 8-second loop and check the seam."
- "Does my pricing page match this spec at phone and desktop widths?"
- "Critique this sign-up form against the brief and make the smallest fix."
- "Find which commit made the export test fail."
- "I want to learn to read rhythm notation in a month."
- "Write up the bug we just fixed as a case study, with the evidence."

Skills that work well together, and which chains have actually been run: [docs/CHAINS.md](docs/CHAINS.md).

## Costs, data and permissions

- Almost everything runs locally and needs no API key.
- **image-gen** is the only skill that calls a paid provider. It prints a plan (provider, model, number of paid calls,
  what data is sent) and refuses to send anything without `--approve-spend`. Prices are not known to the script.
- Keys live in environment variables or a per-user `keys.env` outside the repo (`%APPDATA%\SumitCraft` on Windows,
  `~/.config/sumitcraft` elsewhere). They are never asked for in chat, logged or written to sidecars.
- Speech models download once, locally, and only after you approve the size.
- Fixtures are synthetic and use made-up brands. Brand kits of real companies stay in your private data folder; extracting
  a brand is not permission to redistribute its fonts or logos.
- No skill posts, publishes, emails, signs in or deploys. Security skills run only against code you own, locally.

## Checking the collection

```
node tools/validate.mjs          # static: discovery, metadata, contracts, links, parsing, licence, secrets, platform lint
node tests/unit_paths.mjs        # file-URL handling for spaces, Unicode and Windows drive letters
python tests/run_checks.py       # functional checks per skill, writes evidence/
node tools/gen-docs.mjs          # regenerate contracts, catalog, ledger and matrix from catalog/ and evidence/
```

CI definitions for offline checks on Linux and Windows are in [ci/](ci/README.md). They are stored outside
`.github/workflows` on purpose, so nothing runs remotely until you choose to enable them.

## Layout

```
skills/<name>/          SKILL.md, contract.md, scripts/, examples/, reference.md (one folder per skill)
catalog/skills.mjs      the single source for contracts, catalog, ledger and doctor readiness
tools/                  doctor, install, validate, gen-docs (+ PowerShell wrappers)
tests/                  run_checks.py, unit_paths.mjs, scenarios for guidance-only skills
evidence/               small committed outputs of recorded runs (heavy outputs go to evidence/runs/, ignored)
docs/                   UPSTREAM_AUDIT, CATALOG, ORIGINALITY_LEDGER, VALIDATION_MATRIX, SETUP, CHAINS
.claude-plugin/         plugin and marketplace manifests
```

## Credits and licence

- Foundation: simcraft by Simran Sachdeva, MIT, imported at commit `58224d1` (see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)).
  simcraft itself credits adamd9/skill-image-gen and Charlie Hills' vox-animation skill as inspirations.
- Fonts: Geist and Geist Mono, SIL Open Font License 1.1.
- Some upstream assets of unclear provenance (template cut-out images, third-party documentation screenshots) are not
  included; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
- Licence: [MIT](LICENSE), keeping the upstream copyright notice alongside SumitCraft's. Changes: [CHANGELOG.md](CHANGELOG.md).
