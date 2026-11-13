// Pick a Chromium WebGL backend per platform, allow an override, and report what was actually used.
//
//   SUMITCRAFT_GL=auto|default|metal|d3d11|gl|vulkan|swiftshader   (or --gl=... on the renderer command line)
//
// auto: macOS -> ANGLE Metal, Windows -> ANGLE D3D11, Linux and others -> Chromium's own default.
// A flag is only a request. The backend in use is read back from WebGL (UNMASKED_RENDERER_WEBGL), and
// "SwiftShader"/"llvmpipe" means software rendering, so no GPU acceleration is claimed from a flag alone.
// If WebGL cannot start with the requested backend, the browser is relaunched with Chromium's default.
import { chromium } from "playwright";

const ANGLE = { metal: "metal", d3d11: "d3d11", gl: "gl", vulkan: "vulkan", swiftshader: "swiftshader" };

export function requestedBackend(argv = process.argv) {
  const a = argv.find((x) => x.startsWith("--gl="));
  const v = (a ? a.slice(5) : process.env.SUMITCRAFT_GL || "auto").toLowerCase();
  if (v !== "auto") return v;
  return process.platform === "darwin" ? "metal" : process.platform === "win32" ? "d3d11" : "default";
}

function argsFor(backend, extra) {
  if (backend === "default" || !ANGLE[backend]) return [...extra];
  const gpu = backend === "swiftshader" ? [] : ["--enable-gpu", "--ignore-gpu-blocklist"];
  return [`--use-angle=${ANGLE[backend]}`, ...gpu, ...extra];
}

async function probe(browser) {
  const p = await browser.newPage();
  const info = await p.evaluate(() => {
    const c = document.createElement("canvas"), gl = c.getContext("webgl2") || c.getContext("webgl");
    if (!gl) return null;
    const ext = gl.getExtension("WEBGL_debug_renderer_info");
    return { version: gl.getParameter(gl.VERSION), vendor: ext ? gl.getParameter(ext.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR),
             renderer: ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER) };
  });
  await p.close();
  return info;
}

// Returns { browser, backend: { requested, launched, webgl, software, fellBack } }.
export async function launchForWebGL({ argv = process.argv, extraArgs = [] } = {}) {
  const requested = requestedBackend(argv);
  let launched = requested, browser = await chromium.launch({ args: argsFor(requested, extraArgs) });
  let webgl = await probe(browser), fellBack = false;
  if (!webgl && requested !== "default") {
    console.warn(`[gl] WebGL did not start with backend "${requested}", relaunching with Chromium's default`);
    await browser.close();
    launched = "default"; fellBack = true;
    browser = await chromium.launch({ args: argsFor("default", extraArgs) });
    webgl = await probe(browser);
  }
  if (!webgl) { await browser.close(); throw new Error("WebGL is not available in this Chromium. Run the SumitCraft doctor to check the browser install."); }
  const software = /swiftshader|llvmpipe|software|basic render/i.test(`${webgl.renderer} ${webgl.vendor}`);
  const backend = { requested, launched, fellBack, webgl, software, platform: process.platform };
  console.log(`[gl] requested ${requested}, launched ${launched}; renderer: ${webgl.renderer}${software ? " (software rendering, no GPU acceleration)" : ""}`);
  return { browser, backend };
}
