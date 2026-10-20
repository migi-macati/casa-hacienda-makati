import fs from 'node:fs/promises';
import path from 'node:path';

// Build-time metadata for the migration preview. Keep noindex until owner approval.
const root = path.resolve('public');
const origin = 'https://casa-hacienda-makati.vercel.app';
const brand = 'Casa Hacienda de San Pedro Macati';
const provenance = JSON.parse(await fs.readFile('ops/publication-provenance.json', 'utf8'));
const records = new Map();
for (const item of provenance.entries) {
  if (!item.route || records.has(item.route) || !['post', 'page'].includes(item.type))
    throw new Error('Duplicate or invalid publication provenance route');
  const published = new Date(item.published);
  const modified = new Date(item.modified);
  if (!Number.isFinite(+published) || !Number.isFinite(+modified) || modified < published ||
      published.toISOString().replace('.000Z', 'Z') !== item.published ||
      modified.toISOString().replace('.000Z', 'Z') !== item.modified)
    throw new Error('Invalid publication provenance timestamp: ' + item.route);
  records.set(item.route, item);
}
if (records.size !== 15 || [...records.values()].filter(item => item.type === 'post').length !== 13 ||
    [...records.values()].filter(item => item.type === 'page').length !== 2)
  throw new Error('Expected provenance for exactly 13 posts and 2 pages');
const pages = [];
const seen = new Set();
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
  // Only source-approved public documents get publication metadata; never expose draft data.
  const record = records.get(pathname);
  if (record) {
    if (seen.has(pathname) || (record.type === 'post') !== article)
      throw new Error('Unexpected publication provenance type/route: ' + pathname);
    seen.add(pathname);
    const originalDate = record.published.slice(0, 10);
    const updatedDate = record.modified.slice(0, 10);
    if (!/<header\s+class="entryhead"/i.test(html) ||
        !/<p\s+class="date">[\s\S]*?<\/p>/i.test(html))
      throw new Error('Missing original date/header: ' + pathname);
    if (article && !html.includes('Originally published ' + originalDate) &&
        !html.includes('datetime="' + record.published + '"'))
      throw new Error('Publication date differs from original article: ' + pathname);
    const dateHtml = '<p class="date">Originally published <time datetime="' + record.published + '">' +
      originalDate + '</time>; WordPress record last modified <time datetime="' + record.modified + '">' +
      updatedDate + '</time></p>';
    html = html.replace(/(<header\s+class="entryhead">[\s\S]*?)<p\s+class="date">[\s\S]*?<\/p>/i,
      (_, prefix) => prefix + dateHtml);
    html = html.replace(/<meta\s+name="datePublished"[^>]*>/gi, '').replace(/<meta\s+name="dateModified"[^>]*>/gi, '');
    html = html.replace('</head>', '<meta name="datePublished" content="' + record.published + '">' +
      '<meta name="dateModified" content="' + record.modified + '"></head>');
  } else if (article || pathname === '/about/' || pathname === '/cultural-significance/') {
    throw new Error('Unapproved public document missing publication provenance: ' + pathname);
  }
  await fs.writeFile(file, html);
  updated++;
}
if (updated !== 16 || titles.size !== 16 || seen.size !== 15)
  throw new Error('Expected 16 unique canonical pages and 15 provenance records; found ' + updated);
console.log('Metadata QA: 16 unique page titles/canonicals, 15 published+modified records; noindex preserved.');
