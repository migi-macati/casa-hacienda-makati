import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const css = readFileSync('public/assets/style.css', 'utf8');
const lock = JSON.parse(readFileSync('ops/published-search-sources.json', 'utf8'));
const about = readFileSync('public/about/index.html', 'utf8');
const significance = readFileSync('public/cultural-significance/index.html', 'utf8');
const gitBlob = text => { const bytes = Buffer.from(text); return createHash('sha1').update('blob ' + bytes.length).update(Buffer.from([0])).update(bytes).digest('hex'); };

assert.equal(lock.documents.length, 15, 'published source closure');
assert.equal(gitBlob(css), lock.stylesheetGitBlob, 'reviewed CSS must match search privacy source lock');
for (const html of [about, significance]) {
  assert.ok(html.includes('<meta name="robots" content="noindex,nofollow">'), 'noindex retained');
  assert.ok(html.includes('<article class="content">'), 'published Gutenberg article retained');
}
assert.ok(about.includes('style="padding-right:80px;flex-basis:66.66%"'), 'desktop inline gutter fixture');
assert.ok(about.includes('font-size:50px'), 'desktop inline heading fixture');
assert.ok(significance.includes('style="flex-basis:33.33%"'), 'published column fixture');

function validate(text) {
  const section = text.split('/* Imported Gutenberg blocks carry desktop inline widths')[1];
  assert.ok(section, 'reviewed mobile-only Gutenberg section');
  assert.ok(section.includes('@media(max-width:710px)'), 'narrow-screen breakpoint');
  assert.ok(section.includes('.content .wp-block-columns{gap:1.25rem}'), 'published column spacing');
  assert.ok(section.includes('.content .wp-block-column{flex:1 1 100%!important;min-width:0;padding-left:0!important;padding-right:0!important}'),
    'narrow columns must clear desktop widths and inline gutters');
  assert.ok(section.includes('.content .wp-block-heading[style*="font-size:50px"]{font-size:clamp(1.75rem,7vw,2.25rem)!important;line-height:1.25!important}'),
    'oversized imported heading must adapt without changing desktop styles');
  assert.ok(!section.includes('display:none'), 'do not hide WordPress source content');
  assert.ok(!section.includes('visibility:hidden'), 'do not hide WordPress source content');
}
validate(css);
const mutations = [
  ['@media(max-width:710px)', '@media(max-width:310px)'],
  ['gap:1.25rem', 'gap:0'],
  ['flex:1 1 100%!important', 'flex:1 1 50%!important'],
  ['min-width:0;padding-left', 'min-width:200px;padding-left'],
  ['padding-left:0!important', 'padding-left:80px!important'],
  ['padding-right:0!important', 'padding-right:80px!important'],
  ['.content .wp-block-column{flex:1 1 100%', '.sidebar .wp-block-column{flex:1 1 100%'],
  ['[style*="font-size:50px"]', '[style*="font-size:40px"]'],
  ['font-size:clamp(1.75rem,7vw,2.25rem)!important', 'font-size:50px!important'],
  ['line-height:1.25!important', 'line-height:3!important'],
  ['/* Imported Gutenberg blocks carry desktop inline widths', '/* Unreviewed layout'],
  ['.content .wp-block-columns{gap:1.25rem}', '.content .wp-block-columns{display:none}']
];
const marker = '/* Imported Gutenberg blocks carry desktop inline widths';
const split = css.indexOf(marker);
assert.ok(split >= 0, 'responsive section start');
const prefix = css.slice(0, split);
const responsive = css.slice(split);
for (const [before, after] of mutations) {
  assert.ok(responsive.includes(before), 'missing responsive fixture: ' + before);
  assert.throws(() => validate(prefix + responsive.replace(before, after)),
    'responsive mutation must fail: ' + before);
}
console.log('Published Gutenberg mobile layout: pinned CSS, two source pages, 12 negative fixtures PASS.');
