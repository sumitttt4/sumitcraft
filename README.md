# SumitCraft

**Made by Sumit. Describe the work. The right skill steps in.**

SumitCraft is Sumit's own kit: 55 skills for the interface, the video, the fix, and the document. Install it once. You do not memorise names. Each skill announces when it applies, and the agent loads that one.

## House tools

These two are Sumit's. Reach for them first when the job is a product interface.

- **[Glyph](skills/glyph/SKILL.md)** decides the direction, the composition, and the build, then checks the result. Use it when the page still needs a point of view.
- **[Glaze](skills/glaze/SKILL.md)** is the component library: 93 free React components for interfaces, AI chat, and voice, each in four finishes. Install one at a time. Use it when the interface should be assembled from those components instead of written from scratch.

Glyph chooses. Glaze supplies the pieces.

It runs on your machine. Recorded checks are on Linux; native Windows and macOS have not been run yet. The per-skill record is [docs/VALIDATION_MATRIX.md](docs/VALIDATION_MATRIX.md).

## What you get

- **Video**, from a shader loop or a talking-head rough cut through captions, thumbnails, and a file you can upload.
- **Coding**, from "I'm new to this repo" through the bug, the test, the review, and the commit.
- **Design**, from a direction to a measured check: contrast, spec, motion, and a guidelines pass.
- **Learning and notes**, from a paper or a question to a plan, a quiz, or a cited note in the repo.
- **Documents**: PDF, Word, slides, and spreadsheets.
- **A router** for the vague request that needs two or three skills in order.

## Install

You need Node.js 18.19+. Most skills also want Python 3.9+. Video skills want ffmpeg. Start with the doctor. It only reads the machine and prints the next command.

```bash
git clone https://github.com/sumitttt4/sumitcraft && cd sumitcraft
npm install
node tools/doctor.mjs
node tools/install.mjs install --all --scope project
```

```powershell
git clone https://github.com/sumitttt4/sumitcraft; cd sumitcraft
npm install
powershell -ExecutionPolicy Bypass -File tools\doctor.ps1
powershell -ExecutionPolicy Bypass -File tools\install.ps1 install --all --scope project
```

That copy lands in `./.claude/skills` for the current project. `--scope user --yes` copies into `~/.claude/skills` for every project. The installer will not touch a skill it did not install.

**Claude Code.** `/plugin marketplace add sumitttt4/sumitcraft`, then `/plugin install sumitcraft@sumitcraft`. Skills show up as `sumitcraft:<name>`. Remove them with `/plugin uninstall sumitcraft@sumitcraft`.

**Cursor or Codex.** The installer has no separate destination for those apps. Pass the folder that app already reads:

```bash
node tools/install.mjs install --all --target /path/to/that/skills/folder
```

A smaller set:

```bash
node tools/install.mjs list
node tools/install.mjs install --category video
node tools/install.mjs install code-loop design-critique --dry-run
```

Categories: `video`, `engineering`, `learning`, `design`, `planning`, `docs`.

Speech models, OpenCV, and the paper-skill extras each print a plan first: `python skills/rough-cut/setup.py`, `python skills/reverse-engineer-video/setup.py`, `python skills/paper-to-runnable/setup.py`. Add `--yes` to install. The browser binary is separate: `npx playwright install chromium`. Windows versions and the full list: [docs/SETUP.md](docs/SETUP.md).

## Use it day to day

Say what you want. The agent matches the request to a skill description and follows that skill. A few that map cleanly:

| You say | The skill that fits |
|---|---|
| "Render this shader as a seamless 8-second loop and check the seam." | code-loop |
| "Rough cut this talking-head take. Drop the ums." | rough-cut |
| "I have a folder of clips. Cut them into one video." | vlog-auto-edit |
| "Burn captions into this cut, then export 9:16 and 1:1." | burned-in-captions, then platform-video-export |
| "Turn this transcript into a long script and a shot list." | long-form-storyboard |
| "Write a 60-second script in my voice." | video-script |
| "I'm new to this repo. Map it." | codebase-map |
| "Which commit broke the export test?" | bisect-anything |
| "This test fails sometimes. Find out why." | flaky-test-killer |
| "Debug this before you change anything." | systematic-debugging |
| "Write the failing test first." | test-driven-development |
| "Review this branch against the spec." | code-review |
| "Write the commit message and the pull request." | git-authoring |
| "Don't say it's done until the tests have actually run." | verification-before-completion |
| "Does this page match the spec on a phone and on a desktop?" | design-to-code-inspection |
| "Critique this screen and make the smallest fix." | design-critique |
| "Check this UI code against the web guidelines." | web-design-guidelines |
| "Give this product a real visual direction and build it." | glyph |
| "Build this AI chat with Glaze. Glass finish." | glaze |
| "Design the page, then make it accessible." | design-hub |
| "Turn these meeting notes into owners and dates." | meeting-notes-to-tasks |
| "Research this against the official docs and save a note." | primary-source-research |
| "Make this a Word doc." / "Fill this PDF." / "Build the deck." | docx, pdf, pptx |
| "Write up the bug we just fixed, with the evidence." | work-to-explanation |

When the ask is fuzzy or needs two stages, [skill-router](skills/skill-router/SKILL.md) reads what is installed and proposes the order. Chains that have been run: [docs/CHAINS.md](docs/CHAINS.md).

## Catalog

One line each, from the skill's own description. Needs and status: [docs/CATALOG.md](docs/CATALOG.md).

### Video

| Skill | Use it when |
|---|---|
| [perspective-illusion](skills/perspective-illusion/SKILL.md) | You want a looping illustrated 3D scene that reads flat, then opens into depth. |
| [code-loop](skills/code-loop/SKILL.md) | You want a seamless generative loop from three.js or a shader, checked for a seam. |
| [reverse-engineer-video](skills/reverse-engineer-video/SKILL.md) | You want a reference clip broken into shots so it can be remade. |
| [scripted-screencast](skills/scripted-screencast/SKILL.md) | You want a scripted browser demo recorded with cursor, zoom, and captions. |
| [repo-timelapse](skills/repo-timelapse/SKILL.md) | You want a video of a repository growing from its git history. |
| [rough-cut](skills/rough-cut/SKILL.md) | You want the pauses, fillers, and retakes cut from talking footage. |
| [clean-audio](skills/clean-audio/SKILL.md) | You want rumble, hum, hiss, and uneven loudness taken off a voice. |
| [vox-explainer](skills/vox-explainer/SKILL.md) | You want type, stats, and quotes timed to a voiceover. |
| [vlog-auto-edit](skills/vlog-auto-edit/SKILL.md) | You have many short clips and want one cut, with music under the speech. |
| [burned-in-captions](skills/burned-in-captions/SKILL.md) | You want SRT or ASS captions burned into a finished video. |
| [thumbnail-ab](skills/thumbnail-ab/SKILL.md) | You want several covers and titles so you can pick a thumbnail. |
| [platform-video-export](skills/platform-video-export/SKILL.md) | You want one master re-encoded to 9:16, 3:4, 1:1, or 16:9. |
| [long-form-storyboard](skills/long-form-storyboard/SKILL.md) | You want a long narration and a shot list before anyone records. |

### Engineering

| Skill | Use it when |
|---|---|
| [codebase-map](skills/codebase-map/SKILL.md) | You are new to a repo and want a map of how it fits together. |
| [bisect-anything](skills/bisect-anything/SKILL.md) | Something used to work and you want the commit or input that broke it. |
| [flaky-test-killer](skills/flaky-test-killer/SKILL.md) | A test fails only sometimes and retries are not a fix. |
| [benchmark-honestly](skills/benchmark-honestly/SKILL.md) | You want to know if a change is actually faster. |
| [api-design-review](skills/api-design-review/SKILL.md) | You want an API, SDK, or CLI reviewed, including breaking changes. |
| [security-threat-model](skills/security-threat-model/SKILL.md) | You want a threat model of an app you own, from its real code. |
| [dx-audit](skills/dx-audit/SKILL.md) | You want a tool tried the way a new user would, from the docs only. |
| [git-authoring](skills/git-authoring/SKILL.md) | You want a commit message, a pull request, or help with a git operation. |
| [systematic-debugging](skills/systematic-debugging/SKILL.md) | Something is broken and you want the cause before a fix. |
| [test-driven-development](skills/test-driven-development/SKILL.md) | You want the failing test written before the code. |
| [verification-before-completion](skills/verification-before-completion/SKILL.md) | You are about to say it passes, and the check has not been run. |
| [code-review](skills/code-review/SKILL.md) | You want a diff reviewed against the repo's standards and the spec. |
| [docker-compose-patterns](skills/docker-compose-patterns/SKILL.md) | You are wiring local containers, health checks, and a dev override. |
| [react-best-practices](skills/react-best-practices/SKILL.md) | You are writing or refactoring React or Next.js and want the performance rules applied. |

### Learning

| Skill | Use it when |
|---|---|
| [paper-to-runnable](skills/paper-to-runnable/SKILL.md) | You want a paper's idea as a small program you can run. |
| [system-design-from-scratch](skills/system-design-from-scratch/SKILL.md) | You want a tiny working system with load tests and faults, then a design doc. |
| [from-scratch](skills/from-scratch/SKILL.md) | You want to learn a mechanism by building the smallest version of it. |
| [teach-back](skills/teach-back/SKILL.md) | You want to find out what you actually understand by explaining it. |
| [learn-a-domain](skills/learn-a-domain/SKILL.md) | You want a plan to learn a field, with exercises and a source for every fact. |
| [primary-source-research](skills/primary-source-research/SKILL.md) | You want a question answered from primary sources and saved as a cited note. |

### Design

| Skill | Use it when |
|---|---|
| [design-hub](skills/design-hub/SKILL.md) | The design work spans several stages and you want one plan. |
| [glyph](skills/glyph/SKILL.md) | You want a product-specific frontend: direction, build, and a check. |
| [glaze](skills/glaze/SKILL.md) | You are building React or Next.js UI and want a Glaze component installed before writing one. |
| [design-critique](skills/design-critique/SKILL.md) | You want a rendered screen critiqued against its brief, then a before/after. |
| [design-to-code-inspection](skills/design-to-code-inspection/SKILL.md) | You want a build compared with a spec at phone and desktop widths. |
| [design-system-build](skills/design-system-build/SKILL.md) | You want tokens, components, and a contrast check. |
| [interaction-motion-study](skills/interaction-motion-study/SKILL.md) | You want one interaction specified, built, and checked for keyboard and reduced motion. |
| [visual-reference-analysis](skills/visual-reference-analysis/SKILL.md) | You want a reference measured, then an original study from what it teaches. |
| [web-design-guidelines](skills/web-design-guidelines/SKILL.md) | You want UI code checked against interface and accessibility guidelines. |
| [image-gen](skills/image-gen/SKILL.md) | You want images from your own API key, and you will approve the spend first. |
| [brand-kit](skills/brand-kit/SKILL.md) | You want a brand learned from its live site and saved as a kit. |

### Planning

| Skill | Use it when |
|---|---|
| [skill-router](skills/skill-router/SKILL.md) | You are not sure which skill fits, or the job has two or three stages. |
| [next-step](skills/next-step/SKILL.md) | The goal is a pile of notes and you want one next action. |
| [video-script](skills/video-script/SKILL.md) | You want a short script, 30 seconds to 3 minutes, in the creator's voice. |
| [writing-plans](skills/writing-plans/SKILL.md) | You have a spec and want an implementation plan before any code. |
| [handoff](skills/handoff/SKILL.md) | You are stopping and the next session needs a handoff. |
| [meeting-notes-to-tasks](skills/meeting-notes-to-tasks/SKILL.md) | You have meeting notes and need an owner and a date on every action. |
| [work-to-explanation](skills/work-to-explanation/SKILL.md) | You want a case study or a post built only from evidence you already have. |

### Documents

| Skill | Use it when |
|---|---|
| [pdf](skills/pdf/SKILL.md) | The file is a PDF: read it, merge it, fill it, or make one. |
| [docx](skills/docx/SKILL.md) | The deliverable is a Word document. |
| [pptx](skills/pptx/SKILL.md) | The deliverable is a slide deck. |
| [xlsx](skills/xlsx/SKILL.md) | The deliverable is a spreadsheet. |

## Check the kit

```bash
node tools/validate.mjs       # structure, metadata, links, licences
node tests/unit_paths.mjs
python tests/run_checks.py    # the recorded functional checks
node tools/gen-docs.mjs       # refresh the catalog, ledger, and matrix
```

A green validator means the collection is well formed. Whether a skill has been run is in the validation matrix. Offline CI definitions live in [ci/](ci/README.md) and stay out of `.github/workflows` until you turn them on.

To add a skill: create `skills/<name>/SKILL.md` with `name` and `description`, register it in [catalog/skills.mjs](catalog/skills.mjs), then run `node tools/gen-docs.mjs` and `node tools/validate.mjs`.

## On your machine

Almost all of this is local. **image-gen** is the paid call: it shows the plan and will not send anything until you pass `--approve-spend`. Keys stay in the environment or in `keys.env` outside the repo (`%APPDATA%\SumitCraft` on Windows, `~/.config/sumitcraft` elsewhere). Speech models download once, after you approve the size. Nothing here posts, emails, signs in, or deploys.

## Credits

SumitCraft keeps other people's work under their own licences. The full list, with commits and what was left out, is [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

- The 24 foundation skills come from [simcraft](https://github.com/dotslashsimran/simcraft) by Simran Sachdeva, MIT, imported here as commit `6f0e6ae`.
- [Glyph](https://github.com/sumitttt4/Glyph-Skill) is MIT, Glyph Contributors.
- [Glaze](https://github.com/sumitttt4/Glazeui) is Sumit's component library, Apache-2.0. The site is [glazeui.xyz](https://glazeui.xyz). This repo documents how to install it. It does not copy the components.
- Everyday skills for git, review, Compose, React performance, web guidelines, documents, captions, thumbnails, storyboards, and research notes are third-party (MIT or Apache-2.0). Each folder keeps its licence file.
- Geist and Geist Mono are SIL Open Font License 1.1.

SumitCraft's own code and text are [MIT](LICENSE). Changes: [CHANGELOG.md](CHANGELOG.md).
