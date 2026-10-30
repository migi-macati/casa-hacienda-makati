import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const css = readFileSync('public/assets/style.css', 'utf8');
const lock = JSON.parse(readFileSync('ops/published-search-sources.json', 'utf8'));
const gitBlob = content => {
  const bytes = Buffer.from(content);
  return createHash('sha1').update('blob ' + bytes.length).update(Buffer.from([0])).update(bytes).digest('hex');
};
assert.equal(gitBlob(css), lock.stylesheetGitBlob, 'reviewed stylesheet source lock');
assert.equal(lock.documents.length, 15, 'published source inventory must remain 13 posts and two pages');
assert.equal(lock.documents.filter(d => d.type === 'article').length, 13);
assert.equal(lock.documents.filter(d => d.type === 'page').length, 2);
let separators = 0;
let alpha = 0;
const byRoute = new Map();
for (const doc of lock.documents) {
  const html = readFileSync('public/' + doc.file, 'utf8');
  assert.ok(html.includes('<meta name="robots" content="noindex,nofollow">'), 'noindex retained');
  const nodes = [...html.matchAll(/<hr\b[^>]*class="[^"]*\bwp-block-separator\b[^"]*"[^>]*>/g)].map(m => m[0]);
  byRoute.set(doc.file, nodes.length);
  separators += nodes.length;
  alpha += nodes.filter(n => n.includes('has-alpha-channel-opacity')).length;
}
assert.equal(separators, 25, 'original published separator count');
assert.equal(alpha, 25, 'source alpha-channel class count');
assert.equal(byRoute.get('2023/08/12/cultural-significance-no-1/index.html'), 5);
assert.equal(byRoute.get('2023/10/21/history-of-barrio-olimpia-makati-rizal/index.html'), 3);
assert.equal(byRoute.get('2024/10/28/cultural-significance-no-12/index.html'), 1);
const marker = '/* Imported Gutenberg separators: restore narrow centered rules without source edits. */';
const rule = '.content .wp-block-separator{box-sizing:content-box;width:100px;max-width:100%;height:0;margin:2rem auto;border:0;border-bottom:2px solid currentColor;opacity:.4}\n' +
  '.content .wp-block-separator.has-alpha-channel-opacity{opacity:1}';
function validate(candidate) {
  assert.equal(candidate.split(marker).length, 2, 'one reviewed Gutenberg separator section');
  const next = '/* Imported Gutenberg Land Bank callout and striped evidence table: restore missing block styles. */';
  assert.equal(candidate.split(next).length, 2, 'one reviewed subsequent Gutenberg section');
  assert.equal(candidate.split(marker)[1].split(next)[0].trim(), rule, 'no unreviewed separator style change');
  assert.ok(!candidate.includes('@import'), 'no remote stylesheets');
}
validate(css);
const mutations = [
  ['width:100px', 'width:0'],
  ['max-width:100%', 'max-width:200vw'],
  ['height:0', 'height:100px'],
  ['margin:2rem auto', 'margin:0 0'],
  ['border:0', 'border:10px solid red'],
  ['border-bottom:2px solid currentColor', 'border-bottom:0'],
  ['opacity:.4', 'opacity:0'],
  ['has-alpha-channel-opacity{opacity:1}', 'has-alpha-channel-opacity{opacity:0}'],
  ['box-sizing:content-box', 'display:none;box-sizing:content-box'],
  [marker, '/* unreviewed styles */'],
  ['width:100px', 'background:url(https://example.org/track);width:100px']
];
for (const [before, after] of mutations) {
  assert.ok(before === marker || rule.includes(before), 'missing scoped mutation source: ' + before);
  const changed = before === marker ? css.replace(marker, after) : css.replace(rule, rule.replace(before, after));
  assert.notEqual(changed, css, 'mutation must modify reviewed separator section');
  assert.throws(() => validate(changed), 'mutation must fail: ' + before);
}
console.log('Published Gutenberg separators: 25 original rules, 13 articles + two pages preserved; 11 negative fixtures PASS.');
