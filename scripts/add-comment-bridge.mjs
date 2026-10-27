import fs from 'node:fs/promises';
import path from 'node:path';
import { addCommentBridge } from './comment-bridge-lib.mjs';

const root = path.resolve('public');
const articlePattern = /^\d{4}\/\d{2}\/\d{2}\/[^/]+\/index\.html$/;
const paths = [];
async function visit(directory) {
  for (const entry of await fs.readdir(directory, { withFileTypes: true })) {
    const file = path.join(directory, entry.name);
    if (entry.isDirectory()) await visit(file);
    else if (entry.name === 'index.html') {
      const relative = path.relative(root, file).split(path.sep).join('/');
      if (articlePattern.test(relative)) paths.push({ file, route: '/' + relative.slice(0, -10) });
    }
  }
}
await visit(root);
if (paths.length !== 13) throw Error('Expected 13 published article routes; found ' + paths.length);
// Validate all inputs before writing any output, avoiding partial integration.
const updates = [];
for (const { file, route } of paths) {
  const original = await fs.readFile(file, 'utf8');
  updates.push({ file, original, updated: addCommentBridge(original, route) });
}
for (const { file, original, updated } of updates) {
  if (updated !== original) await fs.writeFile(file, updated);
}
console.log('WordPress discussion bridge verified:', updates.length, 'published articles');
