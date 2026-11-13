---
name: web-design-guidelines
description: "Check UI code against Vercel's Web Interface Guidelines and report file:line findings for accessibility, forms, focus, and interaction rules. Fetches the current rule list from the upstream URL. Use for a guidelines audit of code. For a visual critique of a rendered page with before/after pixels, use design-critique. For contrast tokens, use design-system-build."
metadata: ""
---
> SumitCraft import: the folder name and the description were set so this skill is discovered beside the existing workshop and points at one gap. The method below is the upstream skill. Licence: see the LICENSE file in this folder. Contract, prerequisites and validation status: [contract.md](contract.md).

# Web Interface Guidelines

Review files for compliance with Web Interface Guidelines.

## How It Works

1. Fetch the latest guidelines from the source URL below
2. Read the specified files (or prompt user for files/pattern)
3. Check against all rules in the fetched guidelines
4. Output findings in the terse `file:line` format

## Guidelines Source

Fetch fresh guidelines before each review:

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

Use WebFetch to retrieve the latest rules. The fetched content contains all the rules and output format instructions.

## Usage

When a user provides a file or pattern argument:
1. Fetch guidelines from the source URL above
2. Read the specified files
3. Apply all rules from the fetched guidelines
4. Output findings using the format specified in the guidelines

If no files specified, ask the user which files to review.
