import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { ARTICLE, transform } from './repair-footnote-link-numbers.mjs';

const source = readFileSync('public/' + ARTICLE, 'utf8');
const lock = JSON.parse(readFileSync('ops/published-search-sources.json', 'utf8'));
const record = lock.documents.find(x => x.file === ARTICLE);
assert.ok(record && lock.documents.length === 15, 'source-locked published inventory');
const blob = bytes => createHash('sha1').update('blob ' + bytes.length + '\0').update(bytes).digest('hex');
assert.equal(blob(Buffer.from(source)), record.gitBlob, 'original article Git blob remains pinned');
const repaired = transform(source);
assert.equal(transform(repaired), repaired, 'idempotent generated output');
const plain = text => text.replace(/<[^>]+>/g, '');
const sup = /<sup\b[^>]*\bdata-fn="[^"]+"[^>]*>[\s\S]*?<\/sup>/g;
const before = [...source.matchAll(sup)].map(x => plain(x[0]));
const after = [...repaired.matchAll(sup)].map(x => plain(x[0]));
assert.deepEqual(after, before, 'original visible citation numbers preserved');
assert.deepEqual(after, Array.from({length:13},(_,i)=>String(i+1)), 'all 13 visible ordinals');
assert.equal((repaired.match(/aria-label="Go to source note /g)||[]).length,13);
assert.equal((source.match(/<\/a>[0-3]<\/sup>/g)||[]).length,4,'four real split references');
assert.equal((repaired.match(/<\/a>[0-3]<\/sup>/g)||[]).length,0,'no split reference remains');
const first = source.match(/<sup data-fn="[^"]+" class="fn"><a href="#[^"]+" id="[^"]+">1<\/a><\/sup>/)[0];
const mutations = [
  source.replace('noindex,nofollow','index,follow'),
  source.replace(first,''),
  source.replace(first,first+first),
  source.replace('class="fn"','class="wrong"'),
  source.replace('data-fn=','data-unknown='),
  source.replace(/<a href="#[0-9a-f-]{36}" id="/,'<a href="#wrong" id="'),
  source.replace(/id="[0-9a-f-]{36}-link"/,'id="wrong-link"'),
  source.replace('>1</a>0</sup>','>1</a>9</sup>'),
  source.replace('>1</a>0</sup>','>1</a></sup>'),
  source.replace('>9</a></sup>','>8</a></sup>'),
  source.replace(/<sup data-fn="[0-9a-f-]{36}"/,'<sup data-fn="00000000-0000-0000-0000-000000000000"')
];
for (const [i,mutation] of mutations.entries()) {
  assert.notEqual(mutation,source,'mutation fixture '+i+' must change source');
  assert.throws(()=>transform(mutation),'mutation '+i+' must fail closed');
}
console.log('Source-note link accessibility: 13 labels, four split numerals, 11 fail-closed fixtures PASS.');
