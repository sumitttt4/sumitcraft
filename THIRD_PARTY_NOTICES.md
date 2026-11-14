# Third-party notices

## simcraft (the foundation)

SumitCraft is built on **simcraft** by Simran Sachdeva.

- Source: https://github.com/dotslashsimran/simcraft
- Commit imported: `58224d131814572224537fb516b8c5d33dd5fa67` (2026-11-09), unmodified, as this repository's first commit (`6f0e6ae`).
- License: MIT, Copyright (c) 2026 Simran Sachdeva. The notice is kept in [LICENSE](LICENSE).
- The 24 foundation skills, their scripts, references, templates and examples are substantially upstream work. What
  SumitCraft changed is listed per skill in [docs/ORIGINALITY_LEDGER.md](docs/ORIGINALITY_LEDGER.md) and in
  [CHANGELOG.md](CHANGELOG.md); `git log` from `6f0e6ae` shows every change as a diff.
- Upstream itself credits: image-gen inspired by adamd9/skill-image-gen (MIT), vox-explainer inspired by Charlie Hills'
  vox-animation skill (MIT). Upstream states its code was written from scratch.

## Glyph (bundled design skill)

- Source: https://github.com/sumitttt4/Glyph-Skill, installable bundle `skills/glyph/` at commit
  `00d2bad340dd8ca7f20cbbf389513f2705fdec9f` (default branch, 2026-10-30).
- License: MIT, Copyright (c) 2026 Glyph Contributors; its own `LICENSE`, `THIRD_PARTY_NOTICES.md` (including the MIT
  notice for Emil Kowalski's design-engineering guidance it adapts) and `MIGRATION.md` travel with it in `skills/glyph/`.
- Imported byte for byte, except one appended line in its SKILL.md linking SumitCraft's `contract.md`. The Glyph
  website (Next.js app, images, website fonts) is not included.

## Bundled assets audited separately

The top-level MIT license covers code and text. It does not grant rights to third-party fonts, brands, art or model
outputs. Each bundled asset:

| Asset | Where | Licence / status | Decision |
|---|---|---|---|
| Geist, Geist Mono fonts (woff2) | `skills/repo-timelapse/engine/fonts/`, `skills/vox-explainer/engine/fonts/` | SIL Open Font License 1.1, Copyright (c) 2023 Vercel with basement.studio | Kept; `OFL.txt` placed next to both copies (upstream had it next to one). |
| 4D simplex noise GLSL | `skills/code-loop/templates/shader_starter.html` | MIT, Ian McEwan and Stefan Gustavson (attributed in the file) | Kept with its in-file credit. |
| three.js, Playwright | installed by npm, not vendored | MIT / Apache-2.0 | Not redistributed here. |
| perspective-illusion cut-out PNGs (12 images: characters, food, products) | upstream `skills/video/perspective-illusion/templates/cutouts/` | Provenance not stated (they look generated; generated images and any likeness of brands or characters are not covered by the code licence) | **Not imported.** `scramble_night.html` still references them; supply your own or fetch upstream's at the pinned commit for private use after checking rights. |
| dx-audit uv example screenshots, page snapshots, journey.mp4 | upstream `skills/coding/dx-audit/examples/uv-first-project/` | Screenshots and copied text of Astral's uv documentation (third-party content) | **Not imported.** The audit text is kept; its screenshot links point at the upstream commit. |
| Brand kits | per-user data folder, never in the repo | Third-party fonts and logos | Never committed; fixtures use a made-up brand. |

## Vendored gap skills

These were added so one install covers everyday gaps the foundation does not. Each folder keeps the upstream
licence file. SumitCraft changed only the folder name, the frontmatter description (so the agent can tell it
apart from a skill already in the workshop), and a link to `contract.md`. The method is upstream. None of these
has been run here.

The skills-bundle snapshot is the zip supplied for this change, built 2026-11-13. It did not record a git SHA.
Cloned skills are pinned to the commit below.

| Skill | Gap | Source | Licence | Pin |
|---|---|---|---|---|
| vlog-auto-edit | Mixed-footage edit and a quiet music mix | https://github.com/znyupup/ai-video-editing-skill | MIT, nyx研究所 (znyupup) | `b6429ab` |
| burned-in-captions | Captions burned into a finished video | https://github.com/xianyu110/ecommerce-video-skills | MIT, xianyu110 | `96c49b3` |
| thumbnail-ab | Thumbnail and title variants | same ecommerce-video-skills repo | MIT, xianyu110 | `96c49b3` |
| platform-video-export | Upload packaging (aspect ratio and encode) | same ecommerce-video-skills repo | MIT, xianyu110 | `96c49b3` |
| long-form-storyboard | Long-form script, sections, and a shot list | https://github.com/genfeedai/skills | MIT, Genfeed.ai | `b5f8c25` |
| git-authoring | Commit messages, pull-request text, git operations | https://github.com/n-shadloo/git-authoring | MIT, Nima Shadloo | skills-bundle snapshot 2026-11-13 |
| systematic-debugging | Root-cause debugging before a fix | https://github.com/obra/superpowers | MIT, Jesse Vincent | skills-bundle snapshot 2026-11-13 |
| test-driven-development | Test-first implementation | https://github.com/obra/superpowers | MIT, Jesse Vincent | skills-bundle snapshot 2026-11-13 |
| writing-plans | Implementation plan before coding | https://github.com/obra/superpowers | MIT, Jesse Vincent | skills-bundle snapshot 2026-11-13 |
| verification-before-completion | Run the check before claiming done | https://github.com/obra/superpowers | MIT, Jesse Vincent | skills-bundle snapshot 2026-11-13 |
| code-review | Diff review against standards and the spec | https://github.com/mattpocock/skills | MIT, Matt Pocock | skills-bundle snapshot 2026-11-13 |
| handoff | Session handoff for another agent | https://github.com/mattpocock/skills | MIT, Matt Pocock | skills-bundle snapshot 2026-11-13 |
| primary-source-research | Research notes from primary sources | https://github.com/mattpocock/skills | MIT, Matt Pocock | skills-bundle snapshot 2026-11-13 |
| docker-compose-patterns | Local multi-service Compose setup | https://github.com/docker/skills | Apache-2.0, Docker, Inc. | skills-bundle snapshot 2026-11-13 |
| react-best-practices | React and Next.js performance rules | https://github.com/vercel-labs/agent-skills | MIT, stated in that repo's README | skills-bundle snapshot 2026-11-13 |
| web-design-guidelines | Web interface guidelines audit of UI code | https://github.com/vercel-labs/agent-skills | MIT, stated in that repo's README | skills-bundle snapshot 2026-11-13 |
| meeting-notes-to-tasks | Meeting notes to owned, dated tasks | https://github.com/DevelopersGlobal/ai-agent-skills | MIT, DevelopersGlobal | skills-bundle snapshot 2026-11-13 |
| pdf, docx, pptx, xlsx | PDF, Word, slides, spreadsheets | https://github.com/anthropics/skills | Apache-2.0 | skills-bundle snapshot 2026-11-13 |

Anthropic's repository README says the document skills (docx, pdf, pptx, xlsx) are Apache-2.0, and each skill
ships Apache-2.0 as `LICENSE.txt`, which allows redistribution when that licence travels with the files. It
does. The same README's third-party notices name ffmpeg (GPL) and imageio (BSD) as dependencies of Anthropic's
product. Those programs are not included in this copy. The Office XML schemas under the docx, pptx, and xlsx
skills are part of the upstream skill and are kept with it.

Vercel states MIT in the README of vercel-labs/agent-skills and does not put a copyright line or the full
permission text inside the skill. This copy keeps upstream's pointer and adds the MIT permission text so
recipients have the terms.

### Not vendored (optional external install)

| Item | Why it is not in this repo | If you still want it |
|---|---|---|
| Remotion agent skills, including remotion-captions and remotion-multimedia | Remotion's licence allows use for making videos. It does not allow copying Remotion code into another product that is relicensed or redistributed. | `npx skills add remotion-dev/skills` |
| inference.sh storyboard skill | The repository publishes no licence. | https://github.com/inference-sh/skills (guides/video/storyboard-creation) |
| A separate music or sound-effects skill | No maintained, permissively licensed skill was found that was not a paid API wrapper. vlog-auto-edit includes a local ffmpeg music mix. | Remotion's multimedia skill, under the Remotion licence above |
| 00-skill-index from the skills bundle | skill-router already picks from installed descriptions. | |
| coding-posture | A general execution loop. skill-router plus the specialist skills above cover the same jobs. | https://github.com/alexei-led/coding-posture (MIT) |
| addyosmani debugging-and-error-recovery | Same root-cause gap as systematic-debugging. | https://github.com/addyosmani/agent-skills (MIT) |
| mattpocock `pr` | Pull-request writing is part of git-authoring. | https://github.com/mattpocock/skills (MIT) |
| davidondrej deep-research | Paid DeepAPI. primary-source-research is the local research skill. | https://github.com/davidondrej/skills (MIT) |
| davidondrej keep-track | Overlaps next-step. | https://github.com/davidondrej/skills (MIT) |
| developersglobal research-and-summarize | A layered summary. learn-a-domain and work-to-explanation already cover study and write-up. | https://github.com/DevelopersGlobal/ai-agent-skills (MIT) |
| anthropics frontend-design | Overlaps glyph. | `npx skills add anthropics/skills` (Apache-2.0) |
| hallmark | Overlaps glyph and design-critique. | https://github.com/Nutlope/hallmark (MIT) |

## Glaze

Sumit's component library. The `glaze` skill documents how to install it. The component source is not copied into this repository.

- Site: https://glazeui.xyz
- Source: https://github.com/sumitttt4/Glazeui at `ae670d209b6557b24007686d84cb8d2d35bb9398`
- Licence: Apache-2.0. Redistributing the library's source requires its `LICENSE` and `NOTICE.md`.
- Portfolio: https://sumitsharma.pro (the Glaze card links the project site)

## SumitCraft fixtures

All SumitCraft fixtures (pricing card, Larkfield sign-up and garden UI, disclosure menu, posters, Fernwick test brand,
synthetic audio/video clips) are original, synthetic, and contain no real customer data or credentials. Brand names in
them are invented.
