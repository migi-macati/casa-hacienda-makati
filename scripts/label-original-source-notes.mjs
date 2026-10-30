import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Generated-output-only accessibility enhancement. These three published sources
// are locked; CS No. 10 has a separate repair and CS No. 12 is excluded.
export const TARGETS = [
  ['2023/08/12/cultural-significance-no-1/index.html', 4],
  ['2023/10/21/history-of-barrio-olimpia-makati-rizal/index.html', 4],
  ['2024/02/06/cultural-significance-no-11/index.html', 14]
];
const raw = /<sup data-fn="([0-9a-f-]{36})" class="fn"><a href="#\1" id="\1-link">(\d+)<\/a><\/sup>/g;
const named = /<sup data-fn="([0-9a-f-]{36})" class="fn"><a href="#\1" id="\1-link" aria-label="Go to source note (\d+)">(\d+)<\/a><\/sup>/g;

export function transform(html, expected) {
  assert.ok(html.includes('<meta name="robots" content="noindex,nofollow">'), 'noindex retained');
  assert.ok(Number.isInteger(expected) && expected > 0, 'known source-note count');
  const tags = [...html.matchAll(/<sup\b[^>]*\bdata-fn=/g)];
  assert.equal(tags.length, expected, 'source-note inventory unchanged');
  const before = [...html.matchAll(raw)];
  const after = [...html.matchAll(named)];
  assert.ok((before.length === expected && after.length === 0) ||
    (before.length === 0 && after.length === expected), 'all note links use exact approved markup');
  const matches = before.length ? before : after;
  const ids = new Set();
  for (const [index, match] of matches.entries()) {
    const uid = match[1];
    assert.ok(!ids.has(uid), 'unique note UUID');
    ids.add(uid);
    const visible = before.length ? match[2] : match[3];
    assert.equal(visible, String(index + 1), 'original visible ordinal');
    if (after.length) assert.equal(match[2], visible, 'descriptive accessible name');
    if (html.includes('data-chm-restored-footnotes="1"')) {
      assert.ok(html.includes('<li id="' + uid + '">'), 'restored note target');
      assert.ok(html.includes('href="#' + uid + '-link"'), 'restored note return link');
    }
  }
  const result = before.length ? html.replace(raw, (_all, uid, n) =>
    '<sup data-fn="' + uid + '" class="fn"><a href="#' + uid +
    '" id="' + uid + '-link" aria-label="Go to source note ' + n +
    '">' + n + '</a></sup>') : html;
  assert.equal([...result.matchAll(named)].length, expected, 'all notes named');
  return result;
}

async function main() {
  const lock = JSON.parse(await fs.readFile('ops/published-search-sources.json', 'utf8'));
  assert.equal(lock.documents.length, 15, 'locked published inventory');
  for (const [article, count] of TARGETS) {
    assert.ok(lock.documents.some(x => x.file === article), 'locked public article');
    const filename = path.join('public', article);
    const html = await fs.readFile(filename, 'utf8');
    assert.ok(html.includes('data-chm-restored-footnotes="1"'), 'original note targets restored first');
    const output = transform(html, count);
    if (output !== html) await fs.writeFile(filename, output);
  }
  console.log('Original source-note labels: 22 named references across three public articles.');
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main();
