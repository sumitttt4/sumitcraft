#!/usr/bin/env python3
"""Turn design tokens (JSON) into CSS custom properties, and check them before anyone builds on them.

  python tokens.py tokens.json --css tokens.css [--report report.md] [--json report.json] [--no-fail]
  python tokens.py --pair "#555555" "#ffffff"          one WCAG 2.x contrast ratio
  python tokens.py --audit-css page.html [more files]  list hard-coded colours and px sizes that bypass the tokens

tokens.json groups (all optional): color, space, radius, font (family/size/weight/line), shadow, motion (duration/easing),
plus "pairs" (foreground/background combinations that will really be used, with what they are used for) and
"components" (which tokens each component uses and which interaction states it defines).
A value can reference another token as "{group.name}" (or "{font.size.md}").

Checks, each reported with the measured number:
  contrast   every declared pair meets WCAG 2.x: 4.5:1 for "text", 3:1 for "large-text" and "ui" (borders, icons, focus rings)
  refs       every {reference} resolves, with no cycles
  scale      space and font.size scales increase strictly in the order written (a scale you can reason about)
  duplicates two names with the same raw value in one group (a maintenance smell: is it one decision or two?)
  states     every component lists default, hover, focus-visible and disabled (and the tokens for them exist)
  motion     durations are in ms; a prefers-reduced-motion block is generated that sets every duration to 0ms
Standard library only. Exits 1 when a check fails, unless --no-fail.
"""
import json, re, sys
from pathlib import Path

REF = re.compile(r"\{([a-z0-9_.-]+)\}", re.I)
NEED_STATES = ["default", "hover", "focus-visible", "disabled"]
LIMIT = {"text": 4.5, "large-text": 3.0, "ui": 3.0}


def lum(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError(f"not a #rrggbb colour: {h!r}")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def flatten(d, prefix=""):
    out = {}
    for k, v in d.items():
        if k in ("pairs", "components", "$schema", "about"):
            continue
        p = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(flatten(v, p + "."))
        else:
            out[p] = v
    return out


def resolve(flat):
    res, errs = {}, []

    def get(name, seen):
        if name in res:
            return res[name]
        if name not in flat:
            raise KeyError(name)
        if name in seen:
            raise RecursionError(" -> ".join(seen + [name]))
        v = flat[name]
        if isinstance(v, str):
            v = REF.sub(lambda m: str(get(m.group(1), seen + [name])), v)
        res[name] = v
        return v
    for n in flat:
        try:
            get(n, [])
        except KeyError as e:
            errs.append(f"{n}: reference to missing token {e.args[0]!r}")
        except RecursionError as e:
            errs.append(f"{n}: reference cycle {e.args[0]}")
    return res, errs


def num(v):
    m = re.match(r"^\s*(-?[\d.]+)\s*(px|rem|em|ms|s)?\s*$", str(v))
    if not m:
        return None
    x = float(m.group(1))
    return x * 16 if m.group(2) in ("rem", "em") else x * 1000 if m.group(2) == "s" else x


def css_name(n):
    return "--" + n.replace(".", "-").replace("_", "-")


def main():
    a = sys.argv[1:]
    if a and a[0] == "--pair":
        r = ratio(a[1], a[2])
        print(f"{a[1]} on {a[2]}: {r:.2f}:1  text {'pass' if r >= 4.5 else 'FAIL'} (4.5)  large/ui {'pass' if r >= 3 else 'FAIL'} (3.0)")
        return
    if a and a[0] == "--audit-css":
        bad = 0
        for f in a[1:]:
            text = Path(f).read_text(encoding="utf-8")
            css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", text, re.S)) if f.endswith((".html", ".htm")) else text
            for i, line in enumerate(css.splitlines(), 1):
                if line.strip().startswith("--"):
                    continue  # token definitions themselves
                hits = re.findall(r"#[0-9a-fA-F]{3,8}\b|\b(?!0px)\d+(?:\.\d+)?px\b", line.split("/*")[0])
                if hits:
                    bad += 1
                    print(f"{f}: style line {i}: {', '.join(hits)}  ->  {line.strip()[:90]}")
        print(f"{bad} lines with hard-coded values" + ("" if bad else " (everything goes through tokens)"))
        sys.exit(1 if bad and "--no-fail" not in a else 0)
    if not a or a[0].startswith("--"):
        sys.exit(__doc__)
    opt = lambda k: a[a.index(k) + 1] if k in a else None
    src = Path(a[0])
    tok = json.loads(src.read_text(encoding="utf-8"))
    flat = flatten(tok)
    res, ref_errs = resolve(flat)
    rows, fails = [], []

    def check(kind, what, ok, measured, expected):
        rows.append((kind, what, ok, measured, expected))
        if not ok:
            fails.append(f"{kind}: {what} ({measured}, needs {expected})")

    for e in ref_errs:
        check("refs", e.split(":")[0], False, e.split(": ", 1)[1], "a defined token")
    for p in tok.get("pairs", []):
        fg, bg, use = p["fg"], p["bg"], p.get("use", "text")
        fv, bv = res.get(fg, fg), res.get(bg, bg)
        try:
            r = ratio(fv, bv)
            check("contrast", f"{fg} on {bg} ({use}{': ' + p['why'] if p.get('why') else ''})", r >= LIMIT[use], f"{r:.2f}:1", f"{LIMIT[use]}:1")
        except (ValueError, KeyError) as e:
            check("contrast", f"{fg} on {bg}", False, str(e), "two #rrggbb colours")
    for group in ("space", "font.size"):
        names = [n for n in flat if n.startswith(group + ".") and n.count(".") == group.count(".") + 1]
        vals = [num(res.get(n)) for n in names]
        if len(names) > 1 and None not in vals:
            inc = all(x < y for x, y in zip(vals, vals[1:]))
            check("scale", group, inc, ", ".join(f"{n.split('.')[-1]}={v:g}" for n, v in zip(names, vals)), "strictly increasing in written order")
    by_group = {}
    for n, v in flat.items():
        if isinstance(v, str) and REF.search(v):
            continue  # an alias is a deliberate reuse, not a duplicate
        by_group.setdefault(n.rsplit(".", 1)[0], {}).setdefault(str(v).lower(), []).append(n)
    for g, vals in by_group.items():
        for v, names in vals.items():
            if len(names) > 1:
                check("duplicates", g, False, f"{', '.join(names)} = {v}", "one name per decision, or an alias {...}")
    for comp, spec in tok.get("components", {}).items():
        states = spec.get("states", [])
        missing = [s for s in NEED_STATES if s not in states]
        check("states", comp, not missing, "has " + ", ".join(states), "also " + ", ".join(missing) if missing else ", ".join(NEED_STATES))
        for t in spec.get("tokens", []):
            check("refs", f"{comp} uses {t}", t in res, "defined" if t in res else "missing", "a defined token")
    durations = {n: v for n, v in res.items() if n.startswith("motion.duration.")}
    for n, v in durations.items():
        check("motion", n, str(v).endswith("ms"), str(v), "a value in ms")

    css = [f"/* generated by sumitcraft design-system-build tokens.py from {src.name}; edit the JSON, not this file */", ":root {"]
    css += [f"  {css_name(n)}: {v};" for n, v in res.items()]
    css.append("}")
    if durations:
        css += ["@media (prefers-reduced-motion: reduce) {", "  :root {"] + [f"    {css_name(n)}: 0ms;" for n in durations] + ["  }", "}"]
    if opt("--css"):
        Path(opt("--css")).write_text("\n".join(css) + "\n", encoding="utf-8")
    md = [f"# Token check: {src.name}", "", f"{len(rows)} checks, **{len(fails)} failed**.", "", "| Check | Subject | Measured | Needs | |", "|---|---|---|---|---|"]
    md += [f"| {k} | {w} | {m} | {e} | {'ok' if ok else '**FAIL**'} |" for k, w, ok, m, e in rows]
    if opt("--report"):
        Path(opt("--report")).write_text("\n".join(md) + "\n", encoding="utf-8")
    if opt("--json"):
        Path(opt("--json")).write_text(json.dumps({"tool": "sumitcraft tokens.py", "source": src.name, "checks": len(rows), "failed": len(fails),
                                                   "rows": [dict(check=k, subject=w, ok=ok, measured=m, needs=e) for k, w, ok, m, e in rows]}, indent=2), encoding="utf-8")
    print(f"{len(rows)} checks, {len(fails)} failed")
    for f in fails:
        print("  FAIL " + f)
    if fails and "--no-fail" not in a:
        sys.exit(1)


if __name__ == "__main__":
    main()
