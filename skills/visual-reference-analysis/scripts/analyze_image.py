#!/usr/bin/env python3
"""Measure the visual structure of a reference image, as input for a written analysis.

  python analyze_image.py <image> [--out DIR] [--colors 6]

Decodes with ffmpeg (FFMPEG env var or PATH) and measures with numpy. Writes DIR/analysis.json, DIR/analysis.md and
DIR/overlay.svg (the image with a 3x3 grid of detail shares, the detail centroid and the palette).

Measured (numbers, not judgements):
  palette      k-means colours with the share of the image each covers (deterministic seed)
  value        share of dark / mid / light pixels, and the 5th-95th percentile luminance spread (overall contrast)
  saturation   median and 90th percentile chroma (how colourful, and how colourful the accents are)
  detail grid  share of edge energy in each third of the frame: where the eye has work to do
  quiet space  share of the frame with almost no edges (negative space)
  balance      centroid of edge energy (0..1 from the top-left) and left/right mirror similarity
  direction    share of edge energy that is horizontal, vertical or diagonal
These describe structure. Hierarchy, meaning, type choice and mood still need a person (or Claude) looking at it.
"""
import argparse, json, os, re, shutil, subprocess, sys
from pathlib import Path

try:
    import numpy as np
except ImportError:
    sys.exit("numpy is needed: pip install numpy (or use a SumitCraft skill venv that has it)")

FF = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"


def decode(path, long_side=512):
    err = subprocess.run([FF, "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
    m = re.search(r"(\d{2,5})x(\d{2,5})", err.split("Video:", 1)[-1])
    if not m:
        sys.exit(f"ffmpeg could not read an image size from {path}")
    w, h = int(m.group(1)), int(m.group(2))
    s = min(1.0, long_side / max(w, h))
    W, H = max(8, int(w * s)), max(8, int(h * s))
    raw = subprocess.run([FF, "-v", "error", "-i", str(path), "-frames:v", "1", "-vf", f"scale={W}:{H}:flags=area",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float64) / 255, (w, h)


def kmeans(px, k, iters=25, seed=7):
    rng = np.random.default_rng(seed)
    sample = px[rng.choice(len(px), min(len(px), 20000), replace=False)]
    cent = [sample[rng.integers(len(sample))]]
    for _ in range(1, k):  # k-means++ seeding
        d = np.min(((sample[:, None, :] - np.array(cent)[None]) ** 2).sum(-1), axis=1)
        cent.append(sample[rng.choice(len(sample), p=d / d.sum())] if d.sum() > 0 else sample[rng.integers(len(sample))])
    cent = np.array(cent)
    for _ in range(iters):
        lab = np.argmin(((sample[:, None, :] - cent[None]) ** 2).sum(-1), axis=1)
        new = np.array([sample[lab == i].mean(0) if (lab == i).any() else cent[i] for i in range(k)])
        if np.allclose(new, cent, atol=1e-5):
            break
        cent = new
    lab = np.argmin(((px[:, None, :] - cent[None]) ** 2).sum(-1), axis=1)
    share = np.bincount(lab, minlength=k) / len(px)
    order = np.argsort(-share)
    return cent[order], share[order]


def hexc(c):
    return "#%02x%02x%02x" % tuple(int(round(v * 255)) for v in c)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--out", default="reference-analysis")
    ap.add_argument("--colors", type=int, default=6)
    a = ap.parse_args()
    img, (ow, oh) = decode(a.image)
    H, W, _ = img.shape
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    lum = 0.2126 * img[..., 0] + 0.7152 * img[..., 1] + 0.0722 * img[..., 2]
    chroma = img.max(-1) - img.min(-1)
    cent, share = kmeans(img.reshape(-1, 3), a.colors)
    gx = np.zeros_like(lum); gy = np.zeros_like(lum)
    gx[:, 1:-1] = lum[:, 2:] - lum[:, :-2]
    gy[1:-1, :] = lum[2:, :] - lum[:-2, :]
    mag = np.hypot(gx, gy)
    total = mag.sum() or 1.0
    grid = [[float(mag[r * H // 3:(r + 1) * H // 3, c * W // 3:(c + 1) * W // 3].sum() / total) for c in range(3)] for r in range(3)]
    ys, xs = np.mgrid[0:H, 0:W]
    centroid = (float((mag * xs).sum() / total / (W - 1)), float((mag * ys).sum() / total / (H - 1)))
    blk = 16
    cells = mag[:H // blk * blk, :W // blk * blk].reshape(H // blk, blk, W // blk, blk).mean((1, 3))
    quiet = float((cells < 0.01).mean())
    mirror = float(1 - np.abs(lum - lum[:, ::-1]).mean() / max(1e-9, lum.std() * 2 + 1e-9))
    ang = np.degrees(np.arctan2(gy, gx)) % 180  # gradient direction; an edge runs perpendicular to it
    strong = mag > np.percentile(mag, 75)
    w = mag[strong]; t = ang[strong]
    vert_edges = ((t < 22.5) | (t >= 157.5)); horiz_edges = (t >= 67.5) & (t < 112.5)
    tot_w = w.sum() or 1.0
    direction = {"horizontal": float(w[horiz_edges].sum() / tot_w), "vertical": float(w[vert_edges].sum() / tot_w),
                 "diagonal": float(w[~(horiz_edges | vert_edges)].sum() / tot_w)}
    res = {
        "tool": "sumitcraft visual-reference-analysis analyze_image.py", "image": Path(a.image).name, "size": [ow, oh], "analysed_at": [W, H],
        "palette": [{"hex": hexc(c), "share": round(float(s), 4)} for c, s in zip(cent, share)],
        "value": {"dark_share": round(float((lum < 0.25).mean()), 4), "mid_share": round(float(((lum >= 0.25) & (lum <= 0.75)).mean()), 4),
                  "light_share": round(float((lum > 0.75).mean()), 4), "spread_p5_p95": round(float(np.percentile(lum, 95) - np.percentile(lum, 5)), 4)},
        "saturation": {"median_chroma": round(float(np.median(chroma)), 4), "p90_chroma": round(float(np.percentile(chroma, 90)), 4)},
        "detail_grid_thirds": [[round(v, 3) for v in row] for row in grid],
        "quiet_space_share": round(quiet, 4), "detail_centroid_xy": [round(v, 3) for v in centroid],
        "mirror_similarity_lr": round(mirror, 3), "edge_direction": {k: round(v, 3) for k, v in direction.items()},
    }
    (out / "analysis.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    md = [f"# Measured structure: {res['image']} ({ow}x{oh})", "",
          "| Palette colour | Share |", "|---|---:|"] + [f"| `{p['hex']}` | {p['share'] * 100:.1f}% |" for p in res["palette"]] + [
          "", f"Value: dark {res['value']['dark_share'] * 100:.0f}%, mid {res['value']['mid_share'] * 100:.0f}%, light {res['value']['light_share'] * 100:.0f}%; "
          f"spread (p5 to p95 luminance) {res['value']['spread_p5_p95']:.2f}.",
          f"Saturation: median chroma {res['saturation']['median_chroma']:.2f}, 90th percentile {res['saturation']['p90_chroma']:.2f}.",
          f"Quiet space: {quiet * 100:.0f}% of the frame has almost no edges.",
          f"Detail centroid: x {centroid[0]:.2f}, y {centroid[1]:.2f} (0.5, 0.5 is the centre). Left/right mirror similarity {mirror:.2f}.",
          f"Edge direction: horizontal {direction['horizontal'] * 100:.0f}%, vertical {direction['vertical'] * 100:.0f}%, diagonal {direction['diagonal'] * 100:.0f}%.",
          "", "Detail by thirds (share of all edge energy):", "", "| | left | centre | right |", "|---|---:|---:|---:|"] + [
          f"| {n} | " + " | ".join(f"{v * 100:.0f}%" for v in row) + " |" for n, row in zip(("top", "middle", "bottom"), grid)] + [
          "", "These are measurements. The written analysis (hierarchy, type, texture, meaning) is a separate, human-reviewed step."]
    (out / "analysis.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    rel = os.path.relpath(Path(a.image).resolve(), out.resolve()).replace(os.sep, "/")
    sw = "".join(f'<rect x="{ow + 20}" y="{20 + i * 70}" width="60" height="60" fill="{p["hex"]}" stroke="#000"/><text x="{ow + 90}" y="{58 + i * 70}" font-size="22" font-family="sans-serif">{p["hex"]} {p["share"] * 100:.0f}%</text>' for i, p in enumerate(res["palette"]))
    gl = "".join(f'<line x1="{ow * i / 3}" y1="0" x2="{ow * i / 3}" y2="{oh}" stroke="#ff00c8" stroke-width="2"/><line x1="0" y1="{oh * i / 3}" x2="{ow}" y2="{oh * i / 3}" stroke="#ff00c8" stroke-width="2"/>' for i in (1, 2))
    gt = "".join(f'<text x="{ow * (c + .5) / 3}" y="{oh * (r + .5) / 3}" font-size="{max(14, ow // 30)}" text-anchor="middle" fill="#ff00c8" stroke="#fff" stroke-width="3" paint-order="stroke" font-family="sans-serif">{grid[r][c] * 100:.0f}%</text>' for r in range(3) for c in range(3))
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{ow + 320}" height="{max(oh, 40 + 70 * len(res["palette"]))}">'
           f'<rect width="100%" height="100%" fill="#fff"/><image href="{rel}" xlink:href="{rel}" width="{ow}" height="{oh}"/>{gl}{gt}'
           f'<circle cx="{centroid[0] * ow}" cy="{centroid[1] * oh}" r="{max(8, ow // 60)}" fill="none" stroke="#00b7ff" stroke-width="4"/>{sw}</svg>')
    (out / "overlay.svg").write_text(svg, encoding="utf-8")
    print(f"palette {', '.join(p['hex'] for p in res['palette'])}; quiet {quiet * 100:.0f}%; centroid {centroid[0]:.2f},{centroid[1]:.2f} -> {out / 'analysis.md'}")


if __name__ == "__main__":
    main()
