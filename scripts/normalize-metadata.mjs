import fs from 'node:fs/promises';
import path from 'node:path';

// Build-time metadata for the migration preview. Keep noindex until owner approval.
const root = path.resolve('public');
const origin = 'https://casa-hacienda-makati.vercel.app';
const brand = 'Casa Hacienda de San Pedro Macati';
const pages = [];
async function visit(dir) {
  for (const ent of await fs.readdir(dir, { withFileTypes: true })) {
    const file = path.join(dir, ent.name);
    if (ent.isDirectory()) await visit(file);
    else if (ent.name.endsWith('.html')) pages.push(file);
  }
}
await visit(root);
const titles = new Set();
let updated = 0;
for (const file of pages) {
  const rel = path.relative(root, file).split(path.sep).join('/');
  if (rel === '404.html') continue;
  let html = await fs.readFile(file, 'utf8');
  if (!/<meta\s+name="robots"\s+content="noindex,nofollow"/i.test(html))
    throw new Error('Missing migration noindex safeguard: ' + rel);
  const article = /^\d{4}\/\d{2}\/\d{2}\/[^/]+\/index\.html$/.test(rel);
  if (article) {
    const heading = html.match(/<header\s+class="entryhead"[\s\S]*?<h1[^>]*>([\s\S]*?)<\/h1>/i);
    if (!heading) throw new Error('Missing article heading: ' + rel);
    const name = heading[1].replace(/<[^>]*>/g, '').replace(/&amp;/g, '&').replace(/&nbsp;/g, ' ').trim();
    if (!name) throw new Error('Empty article heading: ' + rel);
    const title = name + ' | ' + brand;
    html = html.replace(/<title>[^<]*<\/title>/i, '<title>' + title.replace(/&/g, '&amp;') + '</title>');
  }
  const match = html.match(/<title>([^<]+)<\/title>/i);
  if (!match || titles.has(match[1])) throw new Error('Missing or duplicate page title: ' + rel);
  titles.add(match[1]);
  const pathname = '/' + rel.replace(/index\.html$/, '');
  const canonical = new URL(pathname, origin).href;
  const tag = '<link rel="canonical" href="' + canonical + '">';
  if (/<link\s+rel="canonical"/i.test(html))
    html = html.replace(/<link\s+rel="canonical"[^>]*>/i, tag);
  else
    html = html.replace('</head>', tag + '</head>');
  await fs.writeFile(file, html);
  updated++;
}
if (updated !== 16 || titles.size !== 16)
  throw new Error('Expected 16 unique canonical pages; found ' + updated);
console.log('Metadata QA: 16 unique page titles and canonical URLs; noindex preserved.');
