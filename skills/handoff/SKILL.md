---
name: handoff
description: "Write a handoff file so a fresh agent can continue this conversation. Save it in the OS temp directory, redact secrets, and point at specs and commits instead of pasting them. Use when pausing to resume in another session. This is a session handoff, not a design spec."
argument-hint: What will the next session be used for?
disable-model-invocation: true
---
> SumitCraft import: the folder name and the description were set so this skill is discovered beside the existing workshop and points at one gap. The method below is the upstream skill. Licence: see the LICENSE file in this folder. Contract, prerequisites and validation status: [contract.md](contract.md).

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the temporary directory of the user's OS (`$TMPDIR`, else `/tmp`; `%TEMP%` on Windows) - not the current workspace.

Include a "suggested skills" section in the document, naming which skills the next agent should call the Skill tool for.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.
