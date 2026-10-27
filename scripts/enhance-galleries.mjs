import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const GALLERY_PAGES = Object.freeze([
  ['2023/08/12/cultural-significance-no-1/index.html', 3],
  ['2023/10/21/history-of-barrio-olimpia-makati-rizal/index.html', 7]
]);
const css = '<link rel="stylesheet" href="/assets/gallery-viewer.css">';
const js = '<script defer src="/assets/gallery-viewer.js"></script>';

export function enhanceGalleryPage(html, expectedCount) {
  if (!/<meta name="robots" content="noindex,nofollow">/.test(html))
    throw Error('Gallery page must remain noindex');
  if (html.includes('gallery-viewer.js') || html.includes('gallery-viewer.css'))
    throw Error('Gallery enhancement must not be injected twice');
  if ([...html.matchAll(/<article\b[^>]*class="content"/g)].length !== 1 || [...html.matchAll(/<\/article>/g)].length !== 1)
    throw Error('Expected one published content article');
  if (html.split('class="wp-block-gallery').length !== 2)
    throw Error('Expected one published gallery');
  const start = html.indexOf('class="wp-block-gallery');
  const end = html.indexOf('</article>', start);
  if (end < 0) throw Error('Missing gallery article boundary');
  const region = html.slice(start, end);
  const count = [...region.matchAll(/<figure\b[^>]*class="[^"]*\bwp-block-image\b/gi)].length;
  if (count !== expectedCount) throw Error(`Gallery image count changed: ${count} != ${expectedCount}`);
  const alts = [...region.matchAll(/<img\b[^>]*\balt="([^"]*)"/gi)];
  if (alts.length !== count || alts.some(m => !m[1].trim()))
    throw Error('Gallery images require nonempty accessible descriptions');
  if (html.split('</head>').length !== 2 || html.split('</body>').length !== 2)
    throw Error('Missing unique HTML document boundary');
  return html.replace('</head>', css + '</head>').replace('</body>', js + '</body>');
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  for (const [relative, count] of GALLERY_PAGES) {
    const filename = path.join('public', relative);
    const original = await fs.readFile(filename, 'utf8');
    await fs.writeFile(filename, enhanceGalleryPage(original, count));
  }
  console.log('Gallery enhancement: 2 published galleries, 10 images; original WordPress links preserved.');
}
