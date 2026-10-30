import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const css = readFileSync('public/assets/style.css', 'utf8');
const lock = JSON.parse(readFileSync('ops/published-search-sources.json', 'utf8'));
const blob = text => {
  const bytes = Buffer.from(text);
  return createHash('sha1').update('blob ' + bytes.length).update(Buffer.from([0])).update(bytes).digest('hex');
};
assert.equal(blob(css), lock.stylesheetGitBlob, 'reviewed stylesheet Git blob');
assert.equal(lock.documents.length, 15, '13 articles and two pages remain locked');
assert.equal(lock.documents.filter(x => x.type === 'article').length, 13);
const doc = lock.documents.find(x => x.file === '2024/10/28/cultural-significance-no-12/index.html');
assert.ok(doc && doc.type === 'article', 'published Land Bank source route');
const html = readFileSync('public/' + doc.file, 'utf8');
assert.ok(html.includes('<meta name="robots" content="noindex,nofollow">'));
assert.equal((html.match(/wp-block-group has-accent-background-color has-background/g) || []).length, 1);
assert.equal((html.match(/wp-block-table is-style-stripes/g) || []).length, 1);
assert.equal((html.match(/<tr>/g) || []).length, 5);
assert.equal((html.match(/<td>/g) || []).length, 10);
assert.ok(html.includes('Properties Available for Negotiated Sale'), 'original evidence heading');
const marker = "/* Imported Gutenberg Land Bank callout and striped evidence table: restore missing block styles. */";
const rule = ".content .wp-block-group.has-accent-background-color.has-background{--wp--preset--spacing--10:1rem;min-width:0;max-width:100%;overflow-x:auto;background:#f0e2c9;padding:1rem}\n.content .wp-block-table.is-style-stripes{display:block;width:100%;min-width:0;max-width:100%;overflow-x:auto}\n.content .wp-block-table.is-style-stripes table{display:table;width:100%;min-width:320px;table-layout:fixed}\n.content .wp-block-table.is-style-stripes tbody tr:nth-child(even){background:#f4f0e8}\n.content .wp-block-table.is-style-stripes td{vertical-align:top;overflow-wrap:anywhere}\n@media(max-width:920px){.layout{grid-template-columns:minmax(0,1fr)}}";
function validate(candidate) {
  assert.equal(candidate.split(marker).length, 2, 'one reviewed table section');
  const after = candidate.split(marker)[1];
  const next = after.indexOf('\n\n/*');
  assert.equal((next < 0 ? after : after.slice(0, next)).trim(), rule, 'exact scoped callout/table rules');
  assert.ok(!candidate.includes('@import'), 'no remote stylesheet');
}
validate(css);
const mutations = [
  ['background:#f0e2c9', 'background:transparent'],
  ['padding:1rem', 'padding:0'],
  ['max-width:100%', 'max-width:200vw'],
  ['overflow-x:auto', 'overflow-x:visible'],
  ['display:table', 'display:none'],
  ['width:100%', 'width:0'],
  ['min-width:320px', 'min-width:900px'],
  ['table-layout:fixed', 'table-layout:auto'],
  ['nth-child(even)', 'nth-child(odd)'],
  ['background:#f4f0e8', 'background:transparent'],
  ['overflow-wrap:anywhere', 'overflow-wrap:normal'],
  ['vertical-align:top', 'vertical-align:bottom'],
  ['padding:1rem', 'padding:1rem;background:url(https://example.org/tracker)'],
  ['grid-template-columns:minmax(0,1fr)', 'grid-template-columns:1fr'],
  ['--wp--preset--spacing--10:1rem', '--wp--preset--spacing--10:0']
];
for (const [from, to] of mutations) {
  assert.ok(rule.includes(from), 'missing scoped fixture ' + from);
  const changed = css.replace(rule, rule.replace(from, to));
  assert.notEqual(changed, css);
  assert.throws(() => validate(changed), 'mutation must fail: ' + from);
}
console.log('Land Bank WordPress source table: one callout, five rows, ten cells, 15 fail-closed fixtures PASS.');
