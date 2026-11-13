# Setup

Windows is the primary target; macOS and Linux use the same tools. Nothing here needs WSL, Bash, symlinks, a Mac or a
fixed home folder. The doctor tells you what is missing; nothing installs itself silently.

## Supported versions

| Thing | Supported | Tested |
|---|---|---|
| Windows | Windows 10 version 1809 (build 17763) and later, Windows 11; x64. PowerShell 5.1 or 7. | **Not yet run on native Windows.** Commands below are the reproduction recipe. |
| macOS | 13+ (Apple Silicon or Intel) | Not run in SumitCraft (upstream was developed on Apple Silicon). |
| Linux | Any current distribution with glibc | Ubuntu-based container: see the validation matrix. |
| Node.js | 18.19+ (20 or 22 LTS recommended); recorded runs used 22.23 | 22.23.4 |
| Python | 3.9+; recorded runs used 3.13 | 3.13.18 |
| Playwright | 1.63.0 (pinned in package.json; its Chromium build matches) | 1.63.0, Chromium 153 |
| ffmpeg | 6.x or 7.x with libx264 | 6.1.1 |
| three.js | 0.170.0 (installed per work folder by the 3D video skills) | 0.170.0 |

The doctor reports your exact Windows family and build (`Windows 10`/`Windows 11`, build number), not an assumption.

## Core setup on Windows (PowerShell)

Each line is something you run yourself. Skip what the doctor says you already have.

```powershell
winget install OpenJS.NodeJS.LTS        # Node.js
winget install Python.Python.3.12       # Python (use `py` afterwards)
winget install Git.Git                  # Git
winget install Gyan.FFmpeg              # ffmpeg + ffprobe; open a NEW terminal afterwards
# or, without winget: install them by hand and set FFMPEG to the full path of ffmpeg.exe:
#   $env:FFMPEG = "C:\tools\ffmpeg\bin\ffmpeg.exe"

git clone https://github.com/sumitttt4/sumitcraft
cd sumitcraft
npm install                             # the Playwright npm package (small)
npx playwright install chromium         # the browser binary itself (about 150-200 MB) - a separate step
py -3 -m pip install --user numpy       # used by the video checkers and image analysis
powershell -ExecutionPolicy Bypass -File tools\doctor.ps1
```

## Opt-in extras (per skill)

| Extra | For | Command (shows a plan; add `--yes` to do it) | Size |
|---|---|---|---|
| Speech-to-text | rough-cut, clean-audio, vox-explainer transcription | `py skills\rough-cut\setup.py` | package ~100 MB; model on first use: small ~0.5 GB, medium ~1.5 GB |
| OpenCV (+ optional Whisper) | reverse-engineer-video fast-move tracking | `py skills\reverse-engineer-video\setup.py [--extra whisper]` | ~60 MB (+ model) |
| matplotlib, pypdf (+ optional PyTorch) | paper-to-runnable | `py skills\paper-to-runnable\setup.py [--extra torch]` | ~50 MB (PyTorch CPU: several hundred MB) |
| tesseract | on-screen text in reverse-engineer-video | `winget install UB-Mannheim.TesseractOCR` | ~100 MB |
| three.js | code-loop (three starter), perspective-illusion | `npm i three@0.170.0` inside the work folder | ~30 MB |
| Provider keys | image-gen only | set `GEMINI_API_KEY` or `OPENAI_API_KEY` yourself, or put them in `%APPDATA%\SumitCraft\keys.env` | paid per call |

Each setup.py writes only into that skill's own `.venv` folder (`.venv\Scripts\python.exe` on Windows). Delete the
folder to uninstall it.

## GPU and WebGL

The 3D renderers choose a WebGL backend per platform: ANGLE **D3D11** on Windows, **Metal** on macOS, Chromium's
default elsewhere. Override with `--gl=default|d3d11|metal|gl|vulkan|swiftshader` or `SUMITCRAFT_GL`. The backend that
actually ran is read back from WebGL, printed as a `[gl]` line, and saved in the render manifest. "SwiftShader" or
"llvmpipe" means software rendering: correct but slow, and no GPU acceleration is claimed.

## Installing the skills into Claude Code

See the README: plugin install (namespaced, recommended), per-project copy, or global copy with `--yes`.
`node tools/install.mjs status --scope user` shows what SumitCraft put where; `uninstall` removes only its own folders.

## Verify on Windows

Run these on a Windows machine and paste the output into an issue or the validation matrix. Until then every
Windows row stays "not run".

```powershell
powershell -ExecutionPolicy Bypass -File tools\doctor.ps1 --json > doctor-windows.json
node tools\validate.mjs
node tests\unit_paths.mjs
py tests\run_checks.py design-system-build design-to-code-inspection interaction-motion-study scripted-screencast code-loop bisect-anything flaky-test-killer from-scratch
node tools\gen-docs.mjs
```

What to look at in particular: the `[gl]` line from code-loop (D3D11 or a fallback), screencast output from a folder
with spaces and non-ASCII characters, bisect-anything's timeout path (taskkill), and flaky-test-killer's stress sweep
(the open-files stressor is skipped on Windows by design; timezone stressors may behave differently).

## Unix notes (optional)

`setup.sh` files remain as two-line wrappers around `setup.py`. Use `python3` where this guide says `py`.
