import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const css = readFileSync('public/assets/style.css', 'utf8');
const lock = JSON.parse(readFileSync('ops/published-search-sources.json', 'utf8'));
const about = readFileSync('public/about/index.html', 'utf8');
const significance = readFileSync('public/cultural-significance/index.html', 'utf8');
const gitBlob = text => {
  const bytes = Buffer.from(text);
  return createHash('sha1').update('blob ' + bytes.length).update(Buffer.from([0])).update(bytes).digest('hex');
};
assert.equal(lock.documents.length, 15, '13 articles and two published pages retained');
assert.equal(gitBlob(css), lock.stylesheetGitBlob, 'stylesheet source lock');
for (const html of [about, significance]) {
  assert.ok(html.includes('<meta name="robots" content="noindex,nofollow">'), 'noindex retained');
  assert.ok(html.includes('<article class="content">'), 'published WordPress content retained');
}
assert.equal((about.match(/has-small-font-size/g) || []).length, 14, 'About small-font fixtures');
assert.equal((significance.match(/has-small-font-size/g) || []).length, 12, 'Significance small-font fixtures');
assert.equal((significance.match(/has-medium-font-size/g) || []).length, 1, 'Significance medium-font fixture');
const marker = '/* Imported Gutenberg font-size presets: preserve source classes and readable small text. */';
function validate(text) {
  assert.equal(text.split(marker).length, 2, 'single reviewed font preset section');
  const after = text.split(marker)[1];
  const next = after.indexOf('\n\n/*');
  const section = next < 0 ? after : after.slice(0, next);
  assert.ok(section.includes('.content .has-small-font-size{font-size:.875rem;line-height:1.6}'), 'small font and readable line height');
  assert.ok(section.includes('.content .has-medium-font-size{font-size:1.25rem;line-height:1.55}'), 'medium font and readable line height');
  assert.ok(!/display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0/i.test(section), 'never hide original content');
  assert.ok(!/@import|url\(/i.test(section), 'no external font or tracking request');
}
validate(css);
const mutations = [
  ['.content .has-small-font-size', '.sidebar .has-small-font-size'],
  ['font-size:.875rem', 'font-size:.6rem'],
  ['font-size:.875rem;line-height:1.6', 'font-size:.875rem;line-height:1'],
  ['.content .has-medium-font-size', '.sidebar .has-medium-font-size'],
  ['font-size:1.25rem', 'font-size:1rem'],
  ['font-size:1.25rem;line-height:1.55', 'font-size:1.25rem;line-height:1'],
  [marker, '/* Unreviewed font override */'],
  ['font-size:.875rem', 'display:none;font-size:.875rem'],
  ['font-size:1.25rem', 'visibility:hidden;font-size:1.25rem'],
  ['font-size:1.25rem', 'background:url(https://example.org/x);font-size:1.25rem']
];
for (const [before, after] of mutations) {
  assert.ok(css.includes(before), 'missing mutation fixture: ' + before);
  assert.throws(() => validate(css.replace(before, after)), 'must reject mutation: ' + before);
}
console.log('Published Gutenberg font presets: 27 source classes, 10 fail-closed fixtures PASS.');
