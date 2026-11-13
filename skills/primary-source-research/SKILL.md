---
name: primary-source-research
description: "Investigate a question against primary sources (official docs, source code, specs, first-party APIs) and write one Markdown file in the repo with a citation on every claim. Use when research notes should live in the project. For a learning plan, use learn-a-domain. For a paper implemented as code, use paper-to-runnable. For a case study of work already done, use work-to-explanation."
---
> SumitCraft import: the folder name and the description were set so this skill is discovered beside the existing workshop and points at one gap. The method below is the upstream skill. Licence: see the LICENSE file in this folder. Contract, prerequisites and validation status: [contract.md](contract.md).

Spin up a **background agent** to do the research, so you keep working while it reads. Start it with a fresh context window.

Its job:

1. Investigate the question against **primary sources** (official docs, source code, specs, first-party APIs), not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Save it where the repo already keeps such notes; match the existing convention, and if there is none, put it somewhere sensible and say where.
