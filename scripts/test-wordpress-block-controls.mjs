import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const css = readFileSync('public/assets/style.css', 'utf8');
const lock = JSON.parse(readFileSync('ops/published-search-sources.json', 'utf8'));
const about = readFileSync('public/about/index.html', 'utf8');
const significance = readFileSync('public/cultural-significance/index.html', 'utf8');
const blob = text => {
  const bytes = Buffer.from(text);
  return createHash('sha1').update('blob ' + bytes.length).update(Buffer.from([0])).update(bytes).digest('hex');
};
assert.equal(lock.documents.length, 15, '13 articles and two pages');
assert.equal(blob(css), lock.stylesheetGitBlob, 'reviewed stylesheet source lock');
assert.equal((significance.match(/class="wp-block-button__link/g) || []).length, 12, '12 published Gutenberg CTAs');
assert.equal((significance.match(/height:100px/g) || []).length, 12, '12 imported desktop spacers');
assert.ok(about.includes('has-text-align-center'), 'published About alignment fixture');
for (const html of [about, significance]) {
  assert.ok(html.includes('<meta name="robots" content="noindex,nofollow">'), 'privacy retained');
  assert.ok(html.includes('<article class="content">'), 'published source remains');
}
function validate(text) {
  const section = text.split('/* Imported WordPress Gutenberg editorial controls:')[1];
  assert.ok(section, 'Gutenberg block parity section');
  for (const fragment of [
    '.content .has-text-align-center{text-align:center}',
    '.content .wp-block-image.aligncenter{margin-left:auto;margin-right:auto;text-align:center}',
    '.content .wp-block-buttons{display:flex;flex-wrap:wrap;gap:.75rem}',
    '.content .wp-block-button__link{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:.65rem 1.2rem;background:#1c3b30;color:#fffdf5;border-radius:3px;font-weight:700;line-height:1.4;text-decoration:none}',
    '.content .wp-block-button__link:hover{background:#294b3e}',
    '.content .wp-block-button__link:focus-visible{outline:3px solid var(--focus);outline-offset:3px}',
    '@media(max-width:710px)',
    '.content .wp-block-spacer[style*="height:100px"]{max-height:36px}'
  ]) assert.ok(section.includes(fragment), 'missing reviewed control: ' + fragment);
  assert.ok(!section.includes('display:none'), 'must not hide source content');
  assert.ok(!section.includes('visibility:hidden'), 'must not hide source content');
}
validate(css);
const mutations = [
  ['.content .has-text-align-center{text-align:center}', '.content .has-text-align-center{text-align:left}'],
  ['margin-left:auto;margin-right:auto', 'margin-left:0;margin-right:0'],
  ['display:flex;flex-wrap:wrap;gap:.75rem', 'display:block;flex-wrap:wrap;gap:.75rem'],
  ['display:inline-flex;align-items:center', 'display:inline;align-items:center'],
  ['min-height:44px', 'min-height:20px'],
  ['background:#1c3b30', 'background:transparent'],
  ['color:#fffdf5', 'color:#1c3b30'],
  ['text-decoration:none', 'text-decoration:underline'],
  ['.content .wp-block-button__link:hover', '.sidebar .wp-block-button__link:hover'],
  ['.content .wp-block-button__link:focus-visible', '.sidebar .wp-block-button__link:focus-visible'],
  ['@media(max-width:710px)', '@media(max-width:310px)'],
  ['max-height:36px', 'max-height:100px']
];
const marker = '/* Imported WordPress Gutenberg editorial controls:';
const pos = css.indexOf(marker);
assert.ok(pos >= 0);
for (const [before, after] of mutations) {
  const prefix = css.slice(0, pos), section = css.slice(pos);
  assert.ok(section.includes(before), 'missing mutation fixture: ' + before);
  assert.throws(() => validate(prefix + section.replace(before, after)), 'must reject: ' + before);
}
console.log('WordPress Gutenberg block controls: 12 published CTAs, 12 spacers, 12 fail-closed mutations PASS.');
