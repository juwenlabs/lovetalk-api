const fs = require("fs");
const path = require("path");

const serverPath = path.join(process.cwd(), "server.js");
let alreadyApplied = false;
try {
  const src = fs.readFileSync(serverPath, "utf8");
  alreadyApplied = src.includes("2026-08-24-potentia-v79-reply-quality-gate");
} catch (_) {}

if (alreadyApplied) {
  console.log("v79 reply quality gate preload: already applied");
} else {
  require("./patch_v79_reply_quality_gate_fixed.js");
}
