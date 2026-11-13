// Unit check for the screencast URL resolver: drive letters are paths, not URL schemes; spaces and Unicode are encoded.
// Uses Node's Windows path rules explicitly, so it runs on any OS. Exit 1 on any failure.
//   node tests/unit_paths.mjs
import path from "node:path";
import { pathToFileURL } from "node:url";

const isScheme = (u) => /^[a-z][a-z0-9+.-]+:/i.test(u) && !/^[a-z]:[\\/]/i.test(u);   // same test as capture.mjs resolveUrl
const winUrl = (dir, u) => (isScheme(u) ? u : pathToFileURL(path.win32.resolve(dir, u), { windows: true }).href);
const posixUrl = (dir, u) => (isScheme(u) ? u : pathToFileURL(path.posix.resolve(dir, u), { windows: false }).href);
const cases = [
  [winUrl("C:\\Users\\Demo User\\site", "index.html"), "file:///C:/Users/Demo%20User/site/index.html"],
  [winUrl("C:\\work", "D:\\Démo ✓\\app.html"), "file:///D:/D%C3%A9mo%20%E2%9C%93/app.html"],
  [winUrl("C:\\work", "c:/x/y.html"), "file:///c:/x/y.html"],
  [winUrl("C:\\work", "http://localhost:3000/"), "http://localhost:3000/"],
  [posixUrl("/tmp/demo folder ü", "index.html"), "file:///tmp/demo%20folder%20%C3%BC/index.html"],
  [posixUrl("/srv", "https://example.com/a b"), "https://example.com/a b"],
];
let bad = 0;
for (const [got, want] of cases) { const ok = got.toLowerCase() === want.toLowerCase(); bad += !ok; console.log(`${ok ? "ok  " : "FAIL"} ${got}${ok ? "" : `  (want ${want})`}`); }
// the old upstream form, for comparison: "file://" + path.resolve(...) on Windows gives an invalid URL
console.log(`upstream form on Windows would give: ${"file://" + path.win32.resolve("C:\\Users\\Demo User\\site", "index.html")}`);
process.exit(bad ? 1 : 0);
