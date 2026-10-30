import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const css = readFileSync('public/assets/style.css', 'utf8');
const lock = JSON.parse(readFileSync('ops/published-search-sources.json', 'utf8'));
const blob = text => {
  const bytes = Buffer.from(text);
  return createHash('sha1').update('blob ' + bytes.length).update(Buffer.from([0])).update(bytes).digest('hex');
};
assert.equal(blob(css), lock.stylesheetGitBlob, 'reviewed CSS source lock');
assert.equal(lock.documents.length, 15, '13 posts and two pages');
const articleFiles = lock.documents.filter(item => item.type === 'article');
assert.equal(articleFiles.length, 13);
const counts = {large:0, xlarge:0, small:0, medium:0, routesWithXlarge:0};
for (const item of articleFiles) {
  const html = readFileSync('public/' + item.file, 'utf8');
  assert.ok(html.includes('<meta name="robots" content="noindex,nofollow">'));
  assert.ok(html.includes('<article class="content">'));
  const count = className => (html.match(new RegExp('\\b' + className + '\\b', 'g')) || []).length;
  const xl = count('has-x-large-font-size');
  counts.large += count('has-large-font-size');
  counts.xlarge += xl;
  counts.small += count('has-small-font-size');
  counts.medium += count('has-medium-font-size');
  if (xl) counts.routesWithXlarge++;
}
assert.deepEqual(counts, {large:4, xlarge:12, small:72, medium:8, routesWithXlarge:12},
  'locked published Gutenberg article typography inventory');
const marker = '/* Published article Gutenberg large headings: preserve editorial hierarchy. */';
function validate(text) {
  assert.equal(text.split(marker).length, 2, 'one reviewed article typography section');
  const after = text.split(marker)[1];
  const next = after.indexOf('\n\n/*');
  const section = next < 0 ? after : after.slice(0, next);
  assert.ok(section.includes('.content .has-large-font-size{font-size:clamp(1.75rem,3vw,2.25rem);line-height:1.3}'));
  assert.ok(section.includes('.content .has-x-large-font-size{font-size:clamp(2rem,3.7vw,2.625rem);line-height:1.24}'));
  assert.ok(!section.includes('display:none') && !section.includes('visibility:hidden') && !section.includes('opacity:0'), 'never hide original content');
  assert.ok(!section.includes('@import') && !section.includes('url('), 'no remote CSS assets');
}
validate(css);
const mutations = [
  ['.content .has-large-font-size', '.sidebar .has-large-font-size'],
  ['font-size:clamp(1.75rem,3vw,2.25rem)', 'font-size:1rem'],
  ['font-size:clamp(1.75rem,3vw,2.25rem)', 'font-size:clamp(.7rem,3vw,2.25rem)'],
  ['line-height:1.3', 'line-height:1'],
  ['.content .has-x-large-font-size', '.sidebar .has-x-large-font-size'],
  ['font-size:clamp(2rem,3.7vw,2.625rem)', 'font-size:6rem'],
  ['font-size:clamp(2rem,3.7vw,2.625rem)', 'font-size:clamp(1rem,3.7vw,2.625rem)'],
  ['line-height:1.24', 'line-height:.8'],
  [marker, '/* unreviewed typography */'],
  ['font-size:clamp(2rem,3.7vw,2.625rem)', 'display:none;font-size:clamp(2rem,3.7vw,2.625rem)'],
  ['font-size:clamp(2rem,3.7vw,2.625rem)', 'background:url(https://example.org/track);font-size:clamp(2rem,3.7vw,2.625rem)']
];
for (const [before, after] of mutations) {
  assert.ok(css.includes(before), 'missing mutation fixture: ' + before);
  assert.throws(() => validate(css.replace(before, after)), 'mutation must fail: ' + before);
}
console.log('Published Gutenberg article typography: 12 x-large, 4 large, 72 small, 8 medium classes; 11 fail-closed fixtures PASS.');
