import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';

const css = readFileSync('public/assets/style.css', 'utf8');
const lock = JSON.parse(readFileSync('ops/published-search-sources.json', 'utf8'));
const gitBlob = text => {
  const bytes = Buffer.from(text);
  return createHash('sha1').update('blob ' + bytes.length + '\0').update(bytes).digest('hex');
};
assert.equal(lock.documents.length, 15, 'published WordPress route closure');
assert.equal(lock.documents.filter(x => x.type === 'article').length, 13);
assert.equal(lock.documents.filter(x => x.type === 'page').length, 2);
assert.equal(gitBlob(css), lock.stylesheetGitBlob, 'pinned reviewed stylesheet');
const source = lock.documents.find(x => x.file === 'cultural-significance/index.html');
assert.ok(source && source.type === 'page', 'published Significance page pinned');
const html = readFileSync('public/' + source.file, 'utf8');
assert.equal(gitBlob(html), source.gitBlob, 'original published HTML unchanged');
assert.ok(html.includes('<meta name="robots" content="noindex,nofollow">'));
const original = [...html.matchAll(/<p class="([^"]+)" style="border-width:15px">/g)]
  .filter(m => m[1].split(/\s+/).includes('has-border-color') && m[1].split(/\s+/).includes('has-base-border-color'));
assert.equal(original.length, 12, 'all 12 original Gutenberg text frames');
assert.equal((html.match(/has-base-border-color/g) || []).length, 12, 'no unaccounted border presets');
const marker = '/* Gutenberg base-border preset: restore 12 original Significance text frames. */';
const rule = '.content p.has-border-color.has-base-border-color{border-style:solid;border-color:var(--paper)}';
function validate(candidate) {
  assert.equal(candidate.split(marker).length, 2, 'single border-preset section');
  const after = candidate.split(marker)[1];
  const next = after.indexOf('\n\n/*');
  assert.equal((next < 0 ? after : after.slice(0, next)).trim(), rule, 'exact source-scoped border fallback');
  assert.ok(!candidate.includes('@import'), 'no remote stylesheet imports');
}
validate(css);
const mutations = [
  ['.content p.has-border-color', 'body p.has-border-color'],
  ['p.has-border-color.has-base-border-color', 'p.has-border-color.has-unknown-border-color'],
  ['border-style:solid', 'border-style:none'],
  ['border-style:solid', 'border-style:dashed'],
  ['border-color:var(--paper)', 'border-color:transparent'],
  ['border-color:var(--paper)', 'border-color:var(--ink)'],
  ['border-color:var(--paper)', 'border-color:var(--paper);background:url(https://example.org/track)'],
  ['border-style:solid', 'display:none;border-style:solid'],
];
for (const [before, after] of mutations) {
  assert.ok(rule.includes(before), 'fixture source must exist: ' + before);
  const altered = css.replace(rule, rule.replace(before, after));
  assert.notEqual(altered, css, 'fixture must alter stylesheet');
  assert.throws(() => validate(altered), 'mutation must fail closed: ' + before);
}
console.log('Gutenberg border presets: 12 source-locked frames, 8 fail-closed mutations PASS.');
