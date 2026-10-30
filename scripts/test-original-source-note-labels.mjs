import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { TARGETS, transform } from './label-original-source-notes.mjs';

const lock = JSON.parse(readFileSync('ops/published-search-sources.json', 'utf8'));
assert.equal(lock.documents.length, 15, 'published inventory');
const gitBlob = data => createHash('sha1').update('blob ' + data.length + '\0').update(data).digest('hex');
let checked = 0;
for (const [article, count] of TARGETS) {
  const record = lock.documents.find(x => x.file === article);
  assert.ok(record && record.type === 'article', 'source-locked public article');
  const bytes = readFileSync('public/' + article);
  assert.equal(gitBlob(bytes), record.gitBlob, 'original source Git blob');
  const source = bytes.toString('utf8');
  const named = transform(source, count);
  assert.equal(transform(named, count), named, 'idempotent');
  const refs = /<sup\b[^>]*\bdata-fn="[^"]+"[^>]*>[\s\S]*?<\/sup>/g;
  const visible = text => [...text.matchAll(refs)].map(m => m[0].replace(/<[^>]+>/g, ''));
  assert.deepEqual(visible(named), visible(source), 'original citation text unchanged');
  assert.deepEqual(visible(named), Array.from({length:count},(_,i)=>String(i+1)));
  assert.equal((named.match(/aria-label="Go to source note /g)||[]).length, count);
  const first = source.match(refs)[0];
  const mutateFirst = replacement => source.replace(first, replacement);
  const changes = [
    source.replace('noindex,nofollow', 'index,follow'),
    mutateFirst(''),
    mutateFirst(first + first),
    mutateFirst(first.replace('class="fn"', 'class="other"')),
    mutateFirst(first.replace(/href="#[^"]+"/, 'href="#wrong"')),
    mutateFirst(first.replace(/id="[^"]+-link"/, 'id="wrong-link"')),
    mutateFirst(first.replace('>1</a>', '>2</a>')),
    mutateFirst(first.replace('data-fn=', 'data-other=')),
    mutateFirst(first.replace(/data-fn="[^"]+"/, 'data-fn="00000000-0000-0000-0000-000000000000"')),
    named.replace('Go to source note 1', 'Go to source note 99')
  ];
  for (const [i, changed] of changes.entries()) {
    assert.notEqual(changed, i===9?named:source, 'fixture must mutate ' + i);
    assert.throws(() => transform(changed, count), 'reject unsafe mutation ' + i);
  }
  checked += count;
}
assert.equal(checked, 22);
console.log('Original source-note labels PASS: 22 references, three source-locked articles, 30 fail-closed fixtures.');
