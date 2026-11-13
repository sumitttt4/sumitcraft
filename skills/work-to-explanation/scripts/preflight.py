#!/usr/bin/env python3
"""Check a write-up (case study, tutorial, post draft) before anyone else sees it. Standard library only.

  python preflight.py draft.md [--root DIR] [--json report.json]

Blockers (exit 1):
  secret        something that looks like a key, token, private key or auth header
  private-path  a home-folder path that names a user (/home/<name>, /Users/<name>, C:\\Users\\<name>)
  evidence      an [evidence: path] link whose file does not exist (relative to the draft, or --root)
  front-matter  missing "status:" or "permissions:" in the YAML-style header at the top
Warnings (reported, exit 0):
  unsupported   a sentence with a number (%, x, ms, s, MB, a count) and no [evidence: ...] or link in its paragraph
  contact       an email address or phone-number-like string (fine if it is yours and intended; check)
  overclaim     words like "always", "guaranteed", "never fails", "proves", "100%" outside code
It reads the draft only. It does not post, send or upload anything.
"""
import json, re, sys
from pathlib import Path

SECRET = [r"AKIA[0-9A-Z]{16}", r"gh[pousr]_[A-Za-z0-9]{30,}", r"sk-[A-Za-z0-9_-]{20,}", r"xox[baprs]-[A-Za-z0-9-]{10,}",
          r"-----BEGIN [A-Z ]*PRIVATE KEY-----", r"(?i)authorization:\s*(bearer|basic)\s+[A-Za-z0-9._~+/=-]{12,}",
          r"AIza[0-9A-Za-z_-]{35}", r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"]
PRIVATE = r"(/home/(?!user\b|runner\b)[a-z][\w.-]+/|/Users/(?!Shared\b)[A-Za-z][\w.-]+/|[A-Za-z]:\\Users\\(?!Public\b)[^\\\s]+\\)"
NUMBER = re.compile(r"\b\d+(?:[.,]\d+)?\s?(?:%|x\b|ms\b|s\b|MB\b|GB\b|seconds\b|minutes\b|times\b|runs\b|files\b|commits\b|pixels\b)")
OVER = re.compile(r"(?i)\b(always works|guaranteed|never fails|proves that|100% (?:safe|secure|accurate)|bulletproof|zero bugs)\b")
CONTACT = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\+?\d[\d ()-]{8,}\d")


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    draft = Path(a[0]); root = Path(a[a.index("--root") + 1]) if "--root" in a else draft.parent
    text = draft.read_text(encoding="utf-8")
    block, warn = [], []
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    head = fm.group(1) if fm else ""
    for key in ("status", "permissions"):
        if not re.search(rf"^{key}\s*:", head, re.M):
            block.append(("front-matter", f'missing "{key}:" in the header', 0))
    body = re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)  # keep line numbers, skip code for prose checks
    for i, line in enumerate(text.splitlines(), 1):
        for pat in SECRET:
            if re.search(pat, line):
                block.append(("secret", "looks like a credential (value not printed)", i))
        if re.search(PRIVATE, line):
            block.append(("private-path", re.search(PRIVATE, line).group(0), i))
        for m in re.finditer(r"\[evidence:\s*([^\]]+)\]", line):
            for ref in [x.strip() for x in m.group(1).split(",")]:
                if not (root / ref).exists() and not (draft.parent / ref).exists():
                    block.append(("evidence", f"{ref} not found", i))
    paragraphs, start = [], 1
    for chunk in re.split(r"\n\s*\n", body):
        paragraphs.append((start, chunk)); start += chunk.count("\n") + 2
    for ln, para in paragraphs:
        if para.lstrip().startswith(("|", "#", "---")) and "[evidence" not in para:
            pass
        cited = "[evidence" in para or re.search(r"\]\([^)]+\)", para)
        if NUMBER.search(para) and not cited and not para.lstrip().startswith("---"):
            warn.append(("unsupported", para.strip().splitlines()[0][:90], ln))
        for m in OVER.finditer(para):
            warn.append(("overclaim", m.group(0), ln))
        for m in CONTACT.finditer(para):
            warn.append(("contact", m.group(0)[:3] + "…", ln))
    for kind, what, ln in block:
        print(f"BLOCK {kind:13} line {ln}: {what}")
    for kind, what, ln in warn:
        print(f"warn  {kind:13} line {ln}: {what}")
    print(f"{len(block)} blockers, {len(warn)} warnings" + ("" if block else " (no blockers: a person still reads it before it goes anywhere)"))
    if "--json" in a:
        Path(a[a.index("--json") + 1]).write_text(json.dumps({"draft": draft.name, "blockers": block, "warnings": warn}, indent=2), encoding="utf-8")
    sys.exit(1 if block else 0)


if __name__ == "__main__":
    main()
