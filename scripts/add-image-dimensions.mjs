import fs from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
import manifest from '../media-manifest.json' with { type: 'json' };

const root = path.resolve('public');
const sizes = new Map();
for (const asset of manifest.assets) {
  if (!/^\/media\/[\w./-]+$/.test(asset.path) || asset.path.includes('..')) throw Error('Unsafe media path: ' + asset.path);
  if (!/\.(webp|png|gif|jpe?g)$/i.test(asset.path)) continue;
  const file = path.resolve(root, '.' + asset.path);
  if (!file.startsWith(root + path.sep)) throw Error('Media path escapes public root');
  const { width, height } = await sharp(file).metadata();
  if (!width || !height) throw Error('Missing intrinsic dimensions: ' + asset.path);
  sizes.set(asset.path, { width, height });
}
let updated = 0, images = 0;
async function walk(dir) {
  for (const entry of await fs.readdir(dir, { withFileTypes: true })) {
    const file = path.join(dir, entry.name);
    if (entry.isDirectory()) { await walk(file); continue; }
    if (!entry.name.endsWith('.html')) continue;
    const before = await fs.readFile(file, 'utf8');
    const after = before.replace(/<img\b[^>]*>/gi, tag => {
      const src = tag.match(/\bsrc\s*=\s*(["'])(.*?)\1/i)?.[2];
      if (!src) throw Error('Image without src: ' + file);
      const mediaPath = src.split(/[?#]/)[0];
      const dim = sizes.get(mediaPath);
      if (!dim) {
        if (mediaPath.startsWith('/media/')) throw Error('Unresolved local image: ' + mediaPath);
        return tag;
      }
      const w = /\bwidth\s*=/.test(tag), h = /\bheight\s*=/.test(tag);
      if (w && h) return tag;
      const attrs = (w ? '' : ' width="' + dim.width + '"') + (h ? '' : ' height="' + dim.height + '"');
      images++;
      return tag.replace(/\s*\/>$/, attrs + ' />').replace(/(?<!\/)\>$/, attrs + '>');
    });
    if (before !== after) { await fs.writeFile(file, after); updated++; }
  }
}
await walk(root);
console.log('Added intrinsic dimensions:', images, 'images in', updated, 'HTML files');
