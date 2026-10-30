import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const html = readFileSync('public/index.html', 'utf8');
const expected = [
  ['heritage-timeline', 'Timeline'],
  ['heritage-sources', 'Sources'],
  ['heritage-places', 'Places'],
  ['heritage-people', 'People'],
  ['heritage-events', 'Events'],
  ['archive', 'Published articles']
];
function validate(candidate) {
  assert.ok(candidate.includes('<meta name="robots" content="noindex,nofollow">'), 'noindex required');
  const start = candidate.indexOf('<nav class="research-jump" aria-label="On this page">');
  assert.ok(start >= 0, 'named navigation required');
  const end = candidate.indexOf('</nav>', start);
  assert.ok(end > start, 'navigation must close');
  const nav = candidate.slice(start, end + 6);
  assert.equal((candidate.match(/class="research-jump"/g) || []).length, 1, 'one jump navigation');
  assert.ok(start > candidate.indexOf('<section class="hero">') &&
    start < candidate.indexOf('<section class="wrap"><span class="kicker">The place</span>'),
    'navigation follows hero and precedes research');
  const links = [...nav.matchAll(/<a href="#([^"]+)">([^<]+)<\/a>/g)]
    .map(match => [match[1], match[2]]);
  assert.deepEqual(links, expected, 'only six pinned published-section links');
  for (const [id] of expected) {
    assert.equal((candidate.match(new RegExp('id="' + id + '"', 'g')) || []).length, 1,
      'one anchor target for ' + id);
  }
  assert.equal((candidate.match(/<article class="card"/g) || []).length, 13, 'published article count');
  assert.ok(candidate.includes('id="search-status" role="status"'), 'accessible search status retained');
  assert.ok(candidate.includes('min-height:44px'), 'keyboard/touch targets retained');
  assert.ok(candidate.includes('scroll-margin-top:6rem'), 'sticky header anchor clearance retained');
}
validate(html);
const changed = (before, after) => {
  assert.ok(html.includes(before), 'missing fixture: ' + before);
  return html.replace(before, after);
};
const mutations = [
  changed('noindex,nofollow', 'index,follow'),
  changed('aria-label="On this page"', 'aria-label=""'),
  changed('href="#heritage-timeline"', 'href="/private/"'),
  changed('href="#heritage-sources"', 'href="#missing"'),
  changed('>Published articles</a>', '>Drafts</a>'),
  changed('id="heritage-people"', 'id="other-people"'),
  changed('id="archive"', 'id="unpublished"'),
  changed('min-height:44px', 'min-height:20px'),
  changed('scroll-margin-top:6rem', 'scroll-margin-top:0'),
  changed('<article class="card"', '<article class="other"'),
  changed('<nav class="research-jump"', '<nav class="not-jumps"')
];
for (const candidate of mutations) assert.throws(() => validate(candidate));
console.log('Homepage research section navigation: six targets and 11 fail-closed regressions PASS.');
