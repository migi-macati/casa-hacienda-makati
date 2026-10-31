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
assert.equal(lock.documents.length, 15, '13 published articles and two informational pages');
assert.equal(lock.documents.filter(x => x.type === 'article').length, 13);
const read = path => readFileSync('public/' + path, 'utf8');
const history = read('2023/10/21/history-of-barrio-olimpia-makati-rizal/index.html');
const about = read('about/index.html');
const significance = read('cultural-significance/index.html');
const occurrences = (text, needle) => text.split(needle).length - 1;
assert.equal(occurrences(history, 'padding-left:var(--wp--preset--spacing--70)'), 29, 'original Olympia source paragraph indents');
assert.equal(occurrences(about, 'margin-top:var(--wp--preset--spacing--70)'), 1, 'original About columns margin');
assert.equal(occurrences(significance, 'padding-bottom:var(--wp--preset--spacing--60)'), 1, 'original Significance heading padding');
const marker = '/* Imported Gutenberg spacing preset fallbacks: preserve source inline values. */';
const rule = '.content{--wp--preset--spacing--60:min(10.5rem,13vw);--wp--preset--spacing--70:3.38rem}';
function validate(candidate) {
  assert.equal(occurrences(candidate, marker), 1, 'one reviewed spacing section');
  const after = candidate.slice(candidate.indexOf(marker) + marker.length);
  const next = after.indexOf('\n\n/*');
  const section = (next < 0 ? after : after.slice(0, next)).trim();
  assert.equal(section, rule, 'exact scoped WordPress core fallback');
  assert.ok(!candidate.includes('@import'), 'no remote stylesheet');
}
validate(css);
const mutations = [
  ['.content{', 'body{'],
  ['.content{', '.hero{'],
  ['--wp--preset--spacing--60:min(10.5rem,13vw)', '--wp--preset--spacing--60:0'],
  ['--wp--preset--spacing--70:3.38rem', '--wp--preset--spacing--70:0'],
  ['--wp--preset--spacing--60', '--wp--preset--spacing--80'],
  ['--wp--preset--spacing--70', '--wp--preset--spacing--80'],
  ['min(10.5rem,13vw)', '22.5rem'],
  ['3.38rem', '33.8rem'],
  ['min(10.5rem,13vw)', 'min(10.5rem,130vw)'],
  ['.content{', '.content p{'],
  [';--wp--preset--spacing--70', ';--wp--preset--spacing--70;--tracking:url(https://example.invalid)']
];
for (const [from, to] of mutations) {
  assert.ok(rule.includes(from), 'missing fixture: ' + from);
  const altered = css.replace(rule, rule.replace(from, to));
  assert.notEqual(altered, css);
  assert.throws(() => validate(altered), 'unsafe spacing mutation must fail: ' + from);
}
const duplicated = css + '\n' + marker + '\n' + rule;
assert.throws(() => validate(duplicated), 'duplicate spacing section must fail');
const removed = css.replace(marker + '\n' + rule, '');
assert.throws(() => validate(removed), 'missing spacing section must fail');
console.log('Gutenberg spacing: 29 paragraph indents, About columns margin, Significance heading padding; 12 fail-closed mutations PASS.');
