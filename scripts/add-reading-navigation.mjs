import fs from 'node:fs/promises';
import path from 'node:path';

// Build-time research reading order. The Barrio Olimpia essay is a companion
// between Nos. 3 and 4; original WordPress No. 8 permalink ends in -7-2.
// This does not modify source article bodies or remove migration noindex.
const reading = [
  ['2023/08/12/cultural-significance-no-1', 'Cultural Significance No. 1'],
  ['2023/08/12/cultural-significance-no-2', 'Cultural Significance No. 2'],
  ['2023/08/12/cultural-significance-no-3', 'Cultural Significance No. 3'],
  ['2023/10/21/history-of-barrio-olimpia-makati-rizal', 'History of Barrio Olimpia (companion)'],
  ['2023/10/21/cultural-significance-no-4', 'Cultural Significance No. 4'],
  ['2023/10/21/cultural-significance-no-5', 'Cultural Significance No. 5'],
  ['2023/10/21/cultural-significance-no-6', 'Cultural Significance No. 6'],
  ['2023/10/21/cultural-significance-no-7', 'Cultural Significance No. 7'],
  ['2023/10/21/cultural-significance-no-7-2', 'Cultural Significance No. 8'],
  ['2023/10/21/cultural-significance-no-9', 'Cultural Significance No. 9'],
  ['2023/10/21/cultural-significance-no-10', 'Cultural Significance No. 10'],
  ['2024/02/06/cultural-significance-no-11', 'Cultural Significance No. 11'],
  ['2024/10/28/cultural-significance-no-12', 'Cultural Significance No. 12'],
];
const root = path.resolve(process.env.CHM_PUBLIC_ROOT || 'public');
const write = process.argv.includes('--write');
if (process.argv.some(x => x.startsWith('--') && x !== '--write')) throw Error('Unknown argument');
const marker = 'aria-label="Research reading order"';
const insertion = '</article><div class="original">';
const updates = [];
const discovered = [];
async function walk(dir) {
  for (const e of await fs.readdir(dir, { withFileTypes: true })) {
    const f = path.join(dir, e.name);
    if (e.isDirectory()) await walk(f);
    else if (e.name === 'index.html' && /^\d{4}\/\d{2}\/\d{2}\/[^/]+\/index\.html$/.test(path.relative(root, f).split(path.sep).join('/'))) discovered.push(f);
  }
}
await walk(root);
if (discovered.length !== 13) throw Error(`Expected 13 public article HTML files; found ${discovered.length}`);
const expectedFiles = new Set(reading.map(([slug]) => path.join(root, slug, 'index.html')));
if (expectedFiles.size !== 13 || discovered.some(f => !expectedFiles.has(f))) throw Error('Unexpected or missing article route');
for (let i = 0; i < reading.length; i++) {
  const [slug, name] = reading[i];
  const filename = path.join(root, slug, 'index.html');
  const html = await fs.readFile(filename, 'utf8');
  if (!/<meta\s+name="robots"\s+content="noindex,nofollow"/i.test(html)) throw Error('Missing noindex: ' + slug);
  if ((html.match(/<article\s+class="content">/g) || []).length !== 1 || (html.split(insertion).length !== 2 && !html.includes('</article><nav class="reading-nav" ' + marker))) throw Error('Article structure changed: ' + slug);
  if (!html.includes(`<h1>${(name.includes('Barrio Olimpia') ? 'History of Barrio Olimpia, Makati, Rizal' : name)}</h1>`)) throw Error('Unexpected article heading: ' + slug);
  const prev = i ? reading[i - 1] : null;
  const next = i + 1 < reading.length ? reading[i + 1] : null;
  const link = (item, label) => `<a href="/${item[0]}/" rel="${label === 'Previous' ? 'prev' : 'next'}"><span class="reading-nav-label">${label}</span><span>${item[1]}</span></a>`;
  const nav = `<nav class="reading-nav" ${marker}>${prev ? link(prev, 'Previous') : '<a href="/cultural-significance/"><span class="reading-nav-label">Series</span><span>Research overview</span></a>'}${next ? link(next, 'Next') : '<a href="/cultural-significance/"><span class="reading-nav-label">Series</span><span>Research overview</span></a>'}</nav>`;
  const already = (html.match(/aria-label="Research reading order"/g) || []).length;
  let updated = html;
  if (already === 0) updated = html.replace(insertion, '</article>' + nav + '<div class="original">');
  else if (already === 1 && html.includes(nav)) { /* idempotent */ }
  else throw Error('Unexpected existing reading navigation: ' + slug);
  if (updated.split('<article class="content">')[1].split('</article>')[0] !== html.split('<article class="content">')[1].split('</article>')[0]) throw Error('Article body mutation: ' + slug);
  updates.push([filename, updated, html]);
}
// All files pass preflight before the first write.
if (write) for (const [file, updated, original] of updates) if (updated !== original) await fs.writeFile(file, updated);
console.log(JSON.stringify({status:'PASS', articles:updates.length, changed:updates.filter(x=>x[1]!==x[2]).length, write, noindexPreserved:true, articleBodiesPreserved:true}));
