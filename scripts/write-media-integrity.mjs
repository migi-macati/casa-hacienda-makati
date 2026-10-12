import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';
import manifest from '../media-manifest.json' with { type: 'json' };

// Deterministic build artifact for later byte-for-byte comparison.
// This records output bytes, not copyright clearance or original-source authenticity.
const root = path.resolve('public');
const assets = [];
const seen = new Set();
for (const asset of manifest.assets) {
  if (!asset.path.startsWith('/media/') || seen.has(asset.path)) {
    throw Error('Duplicate or invalid manifest media path: ' + asset.path);
  }
  seen.add(asset.path);
  const file = path.resolve(root, '.' + asset.path);
  if (!file.startsWith(root + path.sep)) throw Error('Media path escapes public root');
  const bytes = await fs.readFile(file);
  assets.push({
    path: asset.path,
    bytes: bytes.length,
    sha256: createHash('sha256').update(bytes).digest('hex')
  });
}
assets.sort((a, b) => a.path.localeCompare(b.path, 'en'));
const output = { schema_version: 1, assets };
await fs.writeFile(path.join(root, 'media-integrity.json'), JSON.stringify(output, null, 2) + '\n');
console.log('Media integrity manifest generated:', assets.length, 'assets');
