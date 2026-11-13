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

## SumitCraft fixtures

All SumitCraft fixtures (pricing card, Larkfield sign-up and garden UI, disclosure menu, posters, Fernwick test brand,
synthetic audio/video clips) are original, synthetic, and contain no real customer data or credentials. Brand names in
them are invented.
