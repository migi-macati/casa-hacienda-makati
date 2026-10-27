import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
import manifest from '../media-manifest.json' with { type: 'json' };
import provenance from '../ops/original-media-provenance.json' with { type: 'json' };
import { verifySourceInventory, assertSourceBytes } from './source-media-provenance.mjs';

const { assets } = manifest;
// Fail before writing any output if the original 82-file archive inventory drifts.
const sourceRecords = verifySourceInventory(manifest, provenance);
const root = path.resolve('public');
const map = new Map();
for (const a of assets) {
  const p = new URL(a.source).pathname.split('/wp-content/uploads/')[1];
  if (p) map.set(decodeURIComponent(p), a.path);
}
let next = 0;
let copied = 0;
const errors = [];

function goodBytes(data, output) {
  if (data.length < 32) return false;
  const s = data.subarray(0, 16).toString('latin1');
  if (output.endsWith('.webp')) return s.startsWith('RIFF') && s.slice(8, 12) === 'WEBP';
  if (output.endsWith('.pdf')) return s.startsWith('%PDF');
  if (output.endsWith('.gif')) return s.startsWith('GIF8');
  return true;
}

async function get(url) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 35000);
  try {
    const r = await fetch(url, { redirect: 'follow', signal: controller.signal });
    if (!r.ok) throw Error('HTTP ' + r.status);
    const bytes = Buffer.from(await r.arrayBuffer());
    if (bytes.length > 18000000) throw Error('oversized asset');
    return bytes;
  } finally {
    clearTimeout(timeout);
  }
}

async function copy(asset) {
  const output = path.join(root, asset.path.slice(1));
  await fs.mkdir(path.dirname(output), { recursive: true });
  let error;
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      // Verify original WordPress bytes against the owner-supplied TAR before
      // any conversion. Never trust mutable mirrors as source provenance.
      let bytes = await get(asset.source);
      assertSourceBytes(asset, bytes, sourceRecords);
      if (asset.convert) {
        bytes = await sharp(bytes, { limitInputPixels: 150000000 })
          .rotate()
          .resize({ width: 2600, height: 2600, fit: 'inside', withoutEnlargement: true })
          .webp({ quality: 76, effort: 3 })
          .toBuffer();
      }
      if (!goodBytes(bytes, asset.path)) throw Error('Verified source produced invalid output');
      await fs.writeFile(output, bytes);
      copied++;
      if (copied % 15 === 0) console.log('Bundled', copied, '/', assets.length, 'media files');
      return;
    } catch (e) {
      error = e;
      if (attempt < 3) await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
    }
  }
  errors.push(asset.path + ': ' + error?.message);
}

async function worker() {
  while (next < assets.length) await copy(assets[next++]);
}
await Promise.all(Array.from({ length: 5 }, worker));
if (errors.length || copied !== assets.length) {
  console.error('Incomplete media bundle:\n' + errors.join('\n'));
  process.exit(1);
}

// Replace WordPress upload links in the *build output* with local media paths.
// Original article text and all other external archival/source links remain untouched.
let rewritten = 0;
let unmatched = new Set();
async function updateHtml(directory) {
  for (const entry of await fs.readdir(directory, { withFileTypes: true })) {
    const p = path.join(directory, entry.name);
    if (entry.isDirectory()) { await updateHtml(p); continue; }
    if (!entry.name.endsWith('.html')) continue;
    const html = await fs.readFile(p, 'utf8');
    const changed = html.replace(
      /https?:\/\/casahaciendamakati\.wordpress\.com\/wp-content\/uploads\/([^\s"'<>)]*)/g,
      (old, rest) => {
        const raw = rest.split('?')[0].replace(/&amp;.*/, '');
        const name = decodeURIComponent(raw);
        const dest = map.get(name) || map.get(name.replace(/-\d+x\d+(?=\.[^.]+$)/, ''));
        if (!dest) { unmatched.add(name); return old; }
        rewritten++;
        return dest;
      }
    );
    if (changed !== html) await fs.writeFile(p, changed);
  }
}
await updateHtml(root);
console.log('Media bundle complete:', copied, 'verified original source files;', rewritten, 'local URL rewrites.');
if (unmatched.size) {
  console.error('WordPress upload references not present in export:', [...unmatched].join(', '));
  process.exit(1);
}
