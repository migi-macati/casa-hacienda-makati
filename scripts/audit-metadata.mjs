import fs from 'node:fs/promises';
import path from 'node:path';

const root = path.resolve('public');
const origin = 'https://casa-hacienda-makati.vercel.app';
const titles = new Set();
const canonicals = new Set();
const problems = [];
let pages = 0;

async function scan(dir) {
  for (const item of await fs.readdir(dir, { withFileTypes: true })) {
    const file = path.join(dir, item.name);
    if (item.isDirectory()) { await scan(file); continue; }
    if (!item.name.endsWith('.html')) continue;
    const relative = path.relative(root, file).split(path.sep).join('/');
    if (relative === '404.html') continue;
    pages++;
    const html = await fs.readFile(file, 'utf8');
    const title = [...html.matchAll(/<title>([^<]+)<\/title>/gi)];
    if (title.length !== 1 || !title[0][1].trim()) problems.push(relative + ': missing or repeated title');
    else if (titles.has(title[0][1])) problems.push(relative + ': duplicate title');
    else titles.add(title[0][1]);
    const canonical = [...html.matchAll(/<link\s+rel="canonical"\s+href="([^"]+)"[^>]*>/gi)];
    const expected = new URL('/' + relative.replace(/index\.html$/, ''), origin).href;
    if (canonical.length !== 1 || canonical[0][1] !== expected) problems.push(relative + ': invalid canonical (expected ' + expected + ')');
    else if (canonicals.has(expected)) problems.push(relative + ': duplicate canonical');
    else canonicals.add(expected);
    if (!/<meta\s+name="robots"\s+content="noindex,nofollow"/i.test(html))
      problems.push(relative + ': missing migration noindex');
  }
}
await scan(root);
if (pages !== 16 || titles.size !== 16 || canonicals.size !== 16)
  problems.push('Expected 16 unique public pages; got ' + pages + ' pages, ' + titles.size + ' titles, ' + canonicals.size + ' canonicals');
if (problems.length) {
  console.error('Independent metadata QA FAILED:\n' + problems.join('\n'));
  process.exitCode = 1;
} else {
  console.log('Independent metadata QA PASSED: 16 unique titles, canonical URLs, and noindex safeguards.');
}
