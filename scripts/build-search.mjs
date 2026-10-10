import fs from 'node:fs/promises';
import path from 'node:path';

const root = path.resolve('public');
const entries = [];

async function visit(directory) {
  for (const item of await fs.readdir(directory, { withFileTypes: true })) {
    const filename = path.join(directory, item.name);
    if (item.isDirectory()) { await visit(filename); continue; }
    if (item.name !== 'index.html') continue;
    const relative = path.relative(root, filename).split(path.sep).join('/');
    if (!/^\d{4}\/\d{2}\/\d{2}\/[^/]+\/index\.html$/.test(relative)) continue;
    const html = await fs.readFile(filename, 'utf8');
    const heading = html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/i)?.[1] || '';
    const article = html.match(/<article[^>]*class="content"[^>]*>([\s\S]*?)<\/article>/i)?.[1] || html;
    const plain = value => value.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, ' ').replace(/<[^>]*>/g, ' ').replace(/&nbsp;/gi, ' ').replace(/&amp;/gi, '&').replace(/\s+/g, ' ').trim();
    entries.push({ url: '/' + relative.slice(0, -10), title: plain(heading), text: plain(article) });
  }
}
await visit(root);
if (entries.length !== 13) throw new Error('Expected 13 published posts, found ' + entries.length);
await fs.writeFile(path.join(root, 'search-index.json'), JSON.stringify(entries));
console.log('Indexed ' + entries.length + ' published articles');
