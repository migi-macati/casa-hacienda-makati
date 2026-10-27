import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { enhanceGalleryPage, GALLERY_PAGES } from './enhance-galleries.mjs';

const figure = i => `<figure class="wp-block-image"><img src="/media/test${i}.webp" alt="Scanned page ${i}"></figure>`;
const fixture = n => `<html><head><meta name="robots" content="noindex,nofollow"></head><body><article class="content"><figure class="wp-block-gallery">${Array.from({length:n},(_,i)=>figure(i+1)).join('')}</figure></article></body></html>`;
const valid = fixture(3);
const result = enhanceGalleryPage(valid, 3);
assert.ok(result.includes('gallery-viewer.css'));
assert.ok(result.includes('gallery-viewer.js'));
assert.equal(result.replace('<link rel="stylesheet" href="/assets/gallery-viewer.css">','').replace('<script defer src="/assets/gallery-viewer.js"></script>',''), valid);
assert.throws(() => enhanceGalleryPage(result, 3), /twice/);
assert.throws(() => enhanceGalleryPage(valid.replace('noindex,nofollow','index,follow'), 3), /noindex/);
assert.throws(() => enhanceGalleryPage(valid, 7), /count changed/);
assert.throws(() => enhanceGalleryPage(valid.replace('alt="Scanned page 2"','alt=""'), 3), /nonempty/);
assert.throws(() => enhanceGalleryPage(valid.replace('class="wp-block-gallery"','class="other"'), 3), /one published gallery/);
assert.throws(() => enhanceGalleryPage(valid.replace('</article>', '</article><article>other</article>'), 3), /one published content article/);
for (const [relative, count] of GALLERY_PAGES) {
  const html = await fs.readFile('public/' + relative, 'utf8');
  const enhanced = enhanceGalleryPage(html, count);
  assert.ok(enhanced.includes('gallery-viewer.js'));
}
console.log('Gallery enhancement synthetic/source checks PASS: two pinned galleries, 10 images, noindex, alt and single injection.');
