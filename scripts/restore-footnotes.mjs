import fs from 'node:fs/promises';
import path from 'node:path';

// Restore original WordPress footnote metadata without changing article prose.
// The source JSON was extracted from the owner's WordPress XML export.
const ops = path.resolve('ops');
const batches = (await fs.readdir(ops))
  .filter(name => /^original-footnotes-batch-\d+\.json$/.test(name))
  .sort();
if (!batches.length) throw new Error('No original WordPress footnote batches found');

const byArticle = new Map();
for (const filename of batches) {
  const batch = JSON.parse(await fs.readFile(path.join(ops, filename), 'utf8'));
  if (batch.source !== 'WordPress XML wp:postmeta footnotes (original export)') {
    throw new Error('Unexpected source for ' + filename);
  }
  for (const entry of batch.entries) {
    if (!/^public\/(?:\d{4}\/\d{2}\/\d{2}\/[^/]+\/)index\.html$/.test(entry.article_path)) {
      throw new Error('Unsafe or unexpected article path: ' + entry.article_path);
    }
    const notes = byArticle.get(entry.article_path) ?? new Map();
    for (const note of entry.notes) {
      if (!/^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/i.test(note.id)) {
        throw new Error('Invalid source-note identifier in ' + filename);
      }
      if (notes.has(note.id)) throw new Error('Duplicate source note: ' + note.id);
      if (/<(?:script|iframe|style|object|embed|svg|img)\b|\bon[a-z]+\s*=|javascript:/i.test(note.content)) {
        throw new Error('Unsafe markup in source note ' + note.id);
      }
      notes.set(note.id, note.content);
    }
    byArticle.set(entry.article_path, notes);
  }
}

let restored = 0;
for (const [articlePath, notes] of byArticle) {
  const html = await fs.readFile(articlePath, 'utf8');
  const ids = [...html.matchAll(/<sup\b[^>]*\bdata-fn="([^"]+)"/gi)].map(m => m[1]);
  if (!ids.length) throw new Error('No source-note references in ' + articlePath);
  if (new Set(ids).size !== ids.length) throw new Error('Duplicate citation identifiers in ' + articlePath);
  for (const id of notes.keys()) {
    if (!ids.includes(id)) throw new Error('Orphaned source note ' + id + ' in ' + articlePath);
  }
  if (html.includes('data-chm-restored-footnotes="1"')) {
    for (const id of notes.keys()) {
      if (!html.includes('id="' + id + '"')) throw new Error('Incomplete prior restoration: ' + id);
    }
    continue;
  }
  if (!html.includes('</article>')) throw new Error('Missing article closing tag: ' + articlePath);
  const ordered = ids.filter(id => notes.has(id));
  const items = ordered.map((id, index) =>
    '<li id="' + id + '">' + notes.get(id) +
    ' <a class="source-backlink" href="#' + id + '-link" aria-label="Return to citation ' +
    (index + 1) + '">↩</a></li>'
  );
  const section = '\n<section class="source-notes" data-chm-restored-footnotes="1" aria-label="Original source notes">' +
    '<h2>Original source notes</h2><ol>' + items.join('\n') + '</ol></section>\n';
  await fs.writeFile(articlePath, html.replace('</article>', section + '</article>'));
  restored += ordered.length;
  console.log('Restored', ordered.length, 'original source notes:', articlePath);
}
console.log('Original source-note targets restored:', restored);
