import fs from 'node:fs/promises';
import path from 'node:path';

// Migration QA: check href="#..." against IDs on the same page.
// The original WordPress source-note UUIDs are not yet restored. They are
// reported as debt by default, and fail under --strict after restoration.
const root = path.resolve('public');
const strict = process.argv.includes('--strict');
let checked = 0;
let debt = 0;
const failures = [];
async function visit(dir) {
  for (const ent of await fs.readdir(dir, { withFileTypes: true })) {
    const file = path.join(dir, ent.name);
    if (ent.isDirectory()) { await visit(file); continue; }
    if (!file.endsWith('.html')) continue;
    const html = await fs.readFile(file, 'utf8');
    const noteIds = new Set([...html.matchAll(/<sup\b[^>]*\bdata-fn="([^"]+)"/gi)].map(m => m[1]));
    const label = path.relative(root, file);
    for (const m of html.matchAll(/\bhref\s*=\s*(["'])(#[^"'\s]+)\1/gi)) {
      checked++;
      let id;
      try { id = decodeURIComponent(m[2].slice(1)); }
      catch { failures.push(label + ': malformed fragment ' + m[2]); continue; }
      if (html.includes('id="' + id + '"') || html.includes("id='" + id + "'")) continue;
      if (noteIds.has(id) && !strict) { debt++; continue; }
      failures.push(label + ': missing fragment ' + m[2]);
    }
  }
}
await visit(root);
console.log('Same-page links checked:', checked, '| outstanding original source notes:', debt);
if (failures.length) {
  console.error(failures.join('\n'));
  process.exitCode = 1;
} else if (debt) {
  console.warn('Original WordPress footnotes remain missing. Re-run with --strict after restoration.');
}
