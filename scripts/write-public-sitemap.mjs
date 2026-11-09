// Source-locked public sitemap. This does not change robots/noindex policy.
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
const root = resolve(import.meta.dirname, '..');
const source = JSON.parse(readFileSync(resolve(root, 'ops/published-search-sources.json'), 'utf8'));
const expected = source.documents;
if (!Array.isArray(expected) || expected.length !== 15 ||
    expected.filter(d => d.type === 'article').length !== 13 ||
    expected.filter(d => d.type === 'page').length !== 2) {
  throw new Error('Published route inventory changed; review before sitemap release');
}
const base = 'https://casa-hacienda-makati.vercel.app';
// The homepage is an independently published route, outside the 13+2 source inventory.
const urls = [base + '/', ...expected.map(d => {
  if (typeof d.file !== 'string' || !/^(?:[a-z0-9-]+\/)*index\.html$/.test(d.file)) {
    throw new Error('Unsafe published route: ' + String(d.file));
  }
  return base + '/' + d.file.slice(0, -'index.html'.length);
})];
if (new Set(urls).size !== 16) throw new Error('Duplicate sitemap URL or homepage collision');
const xml = '<?xml version="1.0" encoding="UTF-8"?>\n' +
  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
  urls.map(url => '  <url><loc>' + url + '</loc></url>').join('\n') +
  '\n</urlset>\n';
writeFileSync(resolve(root, 'public/sitemap.xml'), xml, 'utf8');
const written = readFileSync(resolve(root, 'public/sitemap.xml'), 'utf8');
if (written !== xml || (written.match(/<url>/g) || []).length !== 16 ||
    !written.includes('<loc>' + base + '/</loc>')) {
  throw new Error('Sitemap verification failed');
}
console.log('Generated source-locked sitemap for homepage and 15 published routes; indexing remains disabled.');
