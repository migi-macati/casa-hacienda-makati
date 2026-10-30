import fs from 'node:fs/promises';
import path from 'node:path';
import { enhanceEmbedFallbacks } from './wordpress-embed-fallback-lib.mjs';

const root = path.resolve('public');
const lock = JSON.parse(await fs.readFile('ops/published-search-sources.json', 'utf8'));
if (lock.documents?.length !== 15) throw Error('Published source closure changed');
const staged = [];
let total = 0;
for (const item of lock.documents) {
  const file = path.join(root, item.file);
  const original = await fs.readFile(file, 'utf8');
  if (!original.includes('<meta name="robots" content="noindex,nofollow">'))
    throw Error('Noindex missing from published source');
  const { html, count } = enhanceEmbedFallbacks(original);
  if (count) staged.push({ file, html });
  total += count;
}
if (total !== 28 || staged.length !== 8)
  throw Error('Expected exactly 28 original embed URLs across 8 published documents');
// Stage and validate the entire fixed inventory before changing any generated HTML.
for (const item of staged) await fs.writeFile(item.file, item.html);
console.log('Gutenberg embed fallback: 28 source links across 8 published routes, no remote embeds.');
