---
title: "One flag, three platforms: picking a WebGL backend instead of assuming Metal"
status: draft, not posted
audience: people rendering WebGL to video with headless Chromium
permissions: "Our own change to SumitCraft. Mentions simcraft (public MIT project by Simran Sachdeva) by name and quotes one line of its code, with credit. No other people, companies or private data."
---

# One flag, three platforms

**The question.** SumitCraft's loop renderer came from simcraft, where it was written and tested on Apple Silicon.
Would it run on Windows and Linux, and if it did, how would we know whether the GPU was doing the work?

**What was there.** The renderer launched Chromium with one hard-coded backend flag
[evidence: evidence/upstream-launch-line.txt]:

```
const browser = await chromium.launch({ args: ["--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist"] });
```

Metal exists only on macOS. On Windows the useful ANGLE backend is D3D11; on Linux, Chromium's own default is the safe choice.
The flag also said nothing about what actually ran.

**What we changed.** A small module picks a backend per platform (Metal on macOS, D3D11 on Windows, the default
elsewhere), accepts an override (`--gl=` or `SUMITCRAFT_GL`), relaunches with the default if WebGL fails to start,
and reads the renderer string back from WebGL. A renderer named SwiftShader or llvmpipe is reported as software
rendering, so no one claims GPU acceleration from a flag. The result goes into a manifest beside each render.

**What we measured, on the machine we had.** A Linux container with no GPU. The manifest records the backend as
requested "default", launched "default", and the renderer as SwiftShader, which is labelled software
[evidence: evidence/render-manifest.json]. The loop checks still did their job there. On the real loop, the frame at
the loop length matched frame 0 to within 1 level out of 255. On a copy with a deliberately non-integer cycle count,
31105 pixels differed by more than 2 levels. A small final render passed all three checks
[evidence: evidence/code-loop-checks.txt].

**What failed along the way.** At preview settings (one sample per frame, JPEG frames), the real loop failed the
"seam pop" heuristic with a jump of 2.8 levels against a threshold of 2. Upstream's guidance is to judge on finals,
and the small final passed [evidence: evidence/code-loop-checks.txt]. We kept the preview failure in the record rather
than raising the threshold.

**Limits.** Nothing here ran on Windows or macOS, so the D3D11 and Metal paths are unverified. Software rendering
is slow, so we rendered at 480x270 and 320x180 only. The related URL fix for paths with spaces, Unicode and drive
letters was checked with Windows path rules on Linux [evidence: evidence/unit_paths.txt], which is not the same as
running on Windows.

**Reproduce.** `python tests/run_checks.py code-loop` in the SumitCraft repository, then read
`evidence/code-loop/run.log.txt`.
