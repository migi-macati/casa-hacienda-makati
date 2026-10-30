import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Generated-output-only accessibility repair. Original WordPress HTML is source-locked.
// The No. 10 article has four references rendered as <a>1</a>0 ... <a>1</a>3.
export const ARTICLE = '2023/10/21/cultural-significance-no-10/index.html';
const raw = /<sup data-fn="([0-9a-f-]{36})" class="fn"><a href="#\1" id="\1-link">(\d+)<\/a>(\d*)<\/sup>/g;
const labeled = /<sup data-fn="([0-9a-f-]{36})" class="fn"><a href="#\1" id="\1-link" aria-label="Go to source note (\d+)">(\d+)<\/a><\/sup>/g;

export function transform(html) {
  assert.ok(html.includes('<meta name="robots" content="noindex,nofollow">'), 'noindex retained');
  const all = [...html.matchAll(/<sup\b[^>]*\bdata-fn="[^"]+"[^>]*>/g)];
  assert.equal(all.length, 13, 'original 13 source-note references');
  const already = html.includes('aria-label="Go to source note ');
  const matches = [...html.matchAll(already ? labeled : raw)];
  assert.equal(matches.length, 13, 'all references have exact approved markup');
  const ids = new Set();
  let splits = 0;
  for (const [index, match] of matches.entries()) {
    const id = match[1];
    assert.ok(!ids.has(id), 'unique source-note UUID');
    ids.add(id);
    const number = already ? match[2] : match[2] + match[3];
    assert.equal(number, String(index + 1), 'source-note ordinal retained');
    if (!already && match[3]) splits++;
    if (already) assert.equal(match[2], match[3], 'accessible name matches visible numeral');
  }
  if (!already) assert.equal(splits, 4, 'four split 10–13 references in original source');
  const output = already ? html : html.replace(raw, (_all, id, first, rest) => {
    const number = first + rest;
    return `<sup data-fn="${id}" class="fn"><a href="#${id}" id="${id}-link" aria-label="Go to source note ${number}">${number}</a></sup>`;
  });
  assert.equal([...output.matchAll(labeled)].length, 13, '13 complete accessible source-note links');
  if (output.includes('data-chm-restored-footnotes="1"')) {
    for (const id of ids) {
      assert.ok(output.includes(`<li id="${id}">`), 'restored source-note destination exists');
      assert.ok(output.includes(`href="#${id}-link"`), 'source-note return link exists');
    }
  }
  return output;
}

async function main() {
  const file = path.join('public', ARTICLE);
  const html = await fs.readFile(file, 'utf8');
  if (!html.includes('data-chm-restored-footnotes="1"'))
    throw Error('Original source notes must be restored before link repair');
  const updated = transform(html);
  if (updated !== html) await fs.writeFile(file, updated);
  console.log('No. 10 source-note links: 13 accessible references, four split numerals repaired; source HTML unchanged.');
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main();
