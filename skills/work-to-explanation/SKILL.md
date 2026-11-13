---
name: work-to-explanation
description: Turn a real piece of work (an experiment, a failure, a fix, a design decision, a benchmark) into an honest case study, tutorial or post draft, built only from the evidence that exists: commands, outputs, diffs, screenshots and measured numbers, with failed attempts and limits included. Checks permissions for any people, companies or data mentioned, links every number to an evidence file, and runs a preflight that blocks credentials, private paths and broken evidence links. Never posts or sends anything. Use when the user says "write this up", "turn this into a blog post / case study / tutorial / thread", "explain what we did", "postmortem draft", or wants to share what they learned. For short video scripts use video-script.
---

# Work to explanation

The best technical writing is a true story with receipts: what we tried, what happened, what we measured, what it means, and what we still do not know. This skill writes that story from the evidence that exists, and refuses to round failures into successes.

`<skill>` is the folder with this SKILL.md. `scripts/preflight.py` is standard-library Python 3.9+. Nothing leaves the machine; publishing is the user's own action.

## Steps

1. **Collect the evidence first.** Commands and their real output, before/after numbers, diffs, screenshots, logs, the failed attempts. Put them (or links to them) in an `evidence/` folder next to the draft. If a claim has no evidence, it either gets measured now or is written as a hypothesis.
2. **Pick the form and reader** with the user: a case study (decision and outcome), a tutorial (steps someone can repeat), or a post (one idea, one story). One reader, one question.
3. **Check permissions.** List every person, company, customer, dataset, screenshot and quote in the draft. Each needs a basis: the user's own work, public information, or explicit permission. Write the list in the header (`permissions:`). Unknown means ask; never assume. Private repositories, client names and colleagues' messages stay out unless the user confirms.
4. **Write the draft** (`draft.md`, header with `title`, `status: draft, not posted`, `audience`, `permissions`). Structure: the question; the setup; what was tried in order, including what failed; the measured result with `[evidence: path]` after each number; what it means; limits and what was not tested; how to reproduce.
5. **Preflight:**
   ```
   python <skill>/scripts/preflight.py draft.md
   ```
   Blockers (credentials, private home paths, broken evidence links, missing header) must be fixed. Warnings (numbers without evidence, contact details, overclaiming words) get a decision each.
6. **Hand over** the draft and the preflight result. Say what is unverified. The user publishes, if and where they choose.

## Rules

- No number without evidence. No evidence, no number.
- Failed attempts and limits stay in. They are what makes the story credible.
- Generated images are labelled as illustrations, never presented as screenshots or evidence.
- Never auto-post, schedule, email or upload.

## Example

`examples/webgl-backend-case-study/` is a real write-up of a SumitCraft change (the code-loop renderer's GPU backend), with its evidence files and a passing preflight.

Contract and validation status: [contract.md](contract.md).
