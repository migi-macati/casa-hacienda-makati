import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
import { createHash } from 'node:crypto';
import manifest from '../media-manifest.json' with { type: 'json' };
import { assertCommentBridge } from './comment-bridge-lib.mjs';
import { assertLinkSemantics } from './link-semantics.mjs';

// Build-time structural checks. These are migration regression gates, NOT
// proof of historical accuracy, media rights, live accessibility or browser QA.
const root = path.resolve('public');
const failures = [];
let emptyAlt = 0;
let images = 0;
let localLinks = 0;
const htmlFiles = [];

async function walk(dir) {
  for (const entry of await fs.readdir(dir, { withFileTypes: true })) {
    const filename = path.join(dir, entry.name);
    if (entry.isDirectory()) await walk(filename);
    else if (entry.name.endsWith('.html')) htmlFiles.push(filename);
  }
}
await walk(root);

const articleFiles = htmlFiles.filter(filename =>
  /^\d{4}\/\d{2}\/\d{2}\/[^/]+\/index\.html$/.test(path.relative(root, filename).split(path.sep).join('/')));
if (htmlFiles.length !== 17) failures.push('Expected 17 HTML files (homepage, 2 pages, 13 posts, 404 page); found ' + htmlFiles.length);
if (articleFiles.length !== 13) failures.push('Expected 13 published articles; found ' + articleFiles.length);
for (const required of ['index.html', '404.html', 'about/index.html', 'cultural-significance/index.html']) {
  if (!htmlFiles.includes(path.join(root, required))) failures.push('Missing required page: ' + required);
}
if (manifest.assets.length !== 82) failures.push('Expected 82 exported media; found ' + manifest.assets.length);

const htmlByFile = new Map();
for (const filename of htmlFiles) htmlByFile.set(filename, await fs.readFile(filename, 'utf8'));

function localTarget(raw, current) {
  if (!raw.startsWith('/') || raw.startsWith('//')) return null;
  const url = new URL(raw.replace(/&amp;/g, '&'), 'https://migration.invalid');
  const pathname = decodeURIComponent(url.pathname);
  const candidate = path.resolve(root, '.' + pathname, pathname.endsWith('/') ? 'index.html' : '');
  if (!candidate.startsWith(root + path.sep)) throw Error('Local path escapes site root: ' + raw);
  return { candidate, hash: decodeURIComponent(url.hash.slice(1)), raw, current };
}

for (const [filename, html] of htmlByFile) {
  const label = path.relative(root, filename);
  if (/^\d{4}\/\d{2}\/\d{2}\/[^/]+\/index\.html$/.test(label.split(path.sep).join('/'))) {
    const route = '/' + label.split(path.sep).join('/').slice(0, -10);
    try { assertCommentBridge(html, route); }
    catch (error) { failures.push(label + ': ' + error.message); }
  }
  try { assertLinkSemantics(html, label); }
  catch (error) { failures.push(error.message); }
  const headings = [...html.matchAll(/<h1(?:\s|>)/gi)].length;
  if (headings !== 1) failures.push(label + ': expected one H1, found ' + headings);
  if (!/<title>[^<]+<\/title>/i.test(html)) failures.push(label + ': missing page title');
  if (!/<meta\s+name="robots"\s+content="noindex,nofollow"/i.test(html))
    failures.push(label + ': migration noindex safeguard missing');
  if (/https?:\/\/casahaciendamakati\.wordpress\.com\/wp-content\/uploads\//i.test(html))
    failures.push(label + ': WordPress media URL not bundled');

  for (const match of html.matchAll(/<img\b[^>]*>/gi)) {
    images++;
    const tag = match[0];
    const alt = tag.match(/\balt\s*=\s*(["'])(.*?)\1/i);
    if (!alt) failures.push(label + ': image lacks alt attribute');
    else if (!alt[2].trim()) {
      emptyAlt++;
      // Empty alt is valid for genuinely decorative images, but that intent
      // must be documented explicitly to prevent accidental silent omissions.
      if (!/\bdata-decorative\s*=\s*(["'])true\1/i.test(tag))
        failures.push(label + ': empty image alt without data-decorative="true"');
    }
  }

  for (const match of html.matchAll(/\b(?:href|src)\s*=\s*(["'])(.*?)\1/gi)) {
    let target;
    try { target = localTarget(match[2], filename); }
    catch (error) { failures.push(label + ': invalid local URL ' + match[2] + ' (' + error.message + ')'); continue; }
    if (!target) continue;
    localLinks++;
    try {
      const stat = await fs.stat(target.candidate);
      if (!stat.isFile()) failures.push(label + ': local link not a file: ' + target.raw);
    } catch { failures.push(label + ': missing local target: ' + target.raw); continue; }
    if (target.hash && target.candidate.endsWith('.html')) {
      const targetHtml = htmlByFile.get(target.candidate) || await fs.readFile(target.candidate, 'utf8');
      if (!targetHtml.includes('id="' + target.hash + '"') && !targetHtml.includes("id='" + target.hash + "'"))
        failures.push(label + ': missing fragment target: ' + target.raw);
    }
  }
}

const index = JSON.parse(await fs.readFile(path.join(root, 'search-index.json'), 'utf8'));
if (!Array.isArray(index) || index.length !== 15) failures.push('Search index must contain 13 articles and 2 informational pages');
else {
  const urls = new Set(index.map(entry => entry.url));
  if (urls.size !== 15) failures.push('Search index has duplicate routes');
  if (index.filter(entry => entry.type === 'article').length !== 13) failures.push('Search index article count is not 13');
  if (index.filter(entry => entry.type === 'page').length !== 2) failures.push('Search index informational-page count is not 2');
  for (const url of ['/about/', '/cultural-significance/']) {
    if (!urls.has(url)) failures.push('Search index missing informational page ' + url);
  }
  for (const filename of articleFiles) {
    const url = '/' + path.relative(root, filename).split(path.sep).join('/').slice(0, -10);
    if (!urls.has(url)) failures.push('Search index missing ' + url);
  }
}

for (const asset of manifest.assets) {
  const filename = path.resolve(root, '.' + asset.path);
  if (!filename.startsWith(root + path.sep)) { failures.push('Invalid media path: ' + asset.path); continue; }
  let data;
  try { data = await fs.readFile(filename); }
  catch { failures.push('Missing media file: ' + asset.path); continue; }
  const header = data.subarray(0, 16).toString('latin1');
  if (asset.path.endsWith('.webp')) {
    if (!(header.startsWith('RIFF') && header.slice(8, 12) === 'WEBP')) {
      failures.push('Invalid WebP signature: ' + asset.path);
      continue;
    }
    try {
      const meta = await sharp(data).metadata();
      if (meta.format !== 'webp' || !meta.width || !meta.height)
        failures.push('Invalid WebP dimensions: ' + asset.path);
    } catch { failures.push('Unreadable WebP: ' + asset.path); }
  } else if (asset.path.endsWith('.pdf') && !header.startsWith('%PDF')) {
    failures.push('Invalid PDF signature: ' + asset.path);
  } else if (asset.path.endsWith('.gif') && !header.startsWith('GIF8')) {
    failures.push('Invalid GIF signature: ' + asset.path);
  }
}

// Verify that the generated integrity inventory covers exactly the exported assets
// and that each checksum describes the actual bytes in this build output.
// This does not authenticate upstream WordPress sources or establish media rights.
try {
  const integrity = JSON.parse(await fs.readFile(path.join(root, 'media-integrity.json'), 'utf8'));
  if (integrity.schema_version !== 1 || !Array.isArray(integrity.assets)) {
    failures.push('Media integrity inventory has an unsupported schema');
  } else {
    const expected = new Set(manifest.assets.map(asset => asset.path));
    const actual = new Set();
    for (const entry of integrity.assets) {
      if (typeof entry.path !== 'string' || !expected.has(entry.path) || actual.has(entry.path)) {
        failures.push('Unexpected or duplicate media integrity entry: ' + String(entry.path));
        continue;
      }
      actual.add(entry.path);
      if (!Number.isSafeInteger(entry.bytes) || entry.bytes < 1 ||
          typeof entry.sha256 !== 'string' || !/^[0-9a-f]{64}$/.test(entry.sha256)) {
        failures.push('Invalid media integrity metadata: ' + entry.path);
        continue;
      }
      const file = path.resolve(root, '.' + entry.path);
      if (!file.startsWith(root + path.sep)) {
        failures.push('Media integrity path escapes public root: ' + entry.path);
        continue;
      }
      try {
        const data = await fs.readFile(file);
        const digest = createHash('sha256').update(data).digest('hex');
        if (data.length !== entry.bytes || digest !== entry.sha256)
          failures.push('Media checksum mismatch: ' + entry.path);
      } catch {
        failures.push('Media integrity asset unreadable: ' + entry.path);
      }
    }
    for (const expectedPath of expected) {
      if (!actual.has(expectedPath)) failures.push('Missing media integrity entry: ' + expectedPath);
    }
    if (integrity.assets.length !== manifest.assets.length)
      failures.push('Media integrity count differs from exported manifest');
  }
} catch (error) {
  failures.push('Media integrity inventory unavailable or invalid: ' + error.message);
}

console.log('Static migration QA:', htmlFiles.length, 'HTML pages,', articleFiles.length,
  'published articles,', manifest.assets.length, 'media files,', localLinks,
  'local links,', images, 'images.');
console.log('Image alternative audit:', emptyAlt, 'explicitly decorative empty alt attributes.');
if (failures.length) {
  console.error('Migration QA FAILED:\n' + failures.join('\n'));
  process.exitCode = 1;
} else {
  console.log('Migration structural QA PASSED. Live HTTP, historical fidelity, rights and browser QA remain separate.');
}
