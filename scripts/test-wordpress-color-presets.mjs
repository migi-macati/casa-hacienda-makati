import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';

const css = readFileSync('public/assets/style.css', 'utf8');
const lock = JSON.parse(readFileSync('ops/published-search-sources.json', 'utf8'));
const gitBlob = text => {
  const bytes = Buffer.from(text);
  return createHash('sha1').update('blob ' + bytes.length + '\0').update(bytes).digest('hex');
};
assert.equal(lock.documents.length, 15);
assert.equal(lock.documents.filter(x => x.type === 'article').length, 13);
assert.equal(lock.documents.filter(x => x.type === 'page').length, 2);
assert.equal(gitBlob(css), lock.stylesheetGitBlob, 'stylesheet Git blob pinned');
const counts = {'has-primary-color': 0, 'has-foreground-color': 0, 'has-black-color': 0};
for (const doc of lock.documents) {
  const html = readFileSync('public/' + doc.file, 'utf8');
  assert.equal(gitBlob(html), doc.gitBlob, 'published WordPress source unchanged: ' + doc.file);
  assert.ok(html.includes('<meta name="robots" content="noindex,nofollow">'));
  for (const m of html.matchAll(/class="([^"]+)"/g)) {
    const classes = m[1].split(/\s+/);
    for (const name of Object.keys(counts)) if (classes.includes(name)) {
      assert.ok(classes.includes('has-text-color'), 'Gutenberg text-color class pairing: ' + doc.file);
      counts[name]++;
    }
  }
}
assert.deepEqual(counts, {'has-primary-color': 16, 'has-foreground-color': 55, 'has-black-color': 5});
const marker = '/* Original Gutenberg text-color classes: conservative readable palette fallbacks. */';
const rules = [
  '.content .has-primary-color.has-text-color{color:#1c3b30}',
  '.content .has-foreground-color.has-text-color{color:var(--ink)}',
  '.content .has-black-color.has-text-color{color:#111}'
];
function validate(candidate) {
  assert.equal(candidate.split(marker).length, 2, 'one color fallback section');
  const after = candidate.split(marker)[1];
  const next = after.indexOf('\n\n/*');
  assert.equal((next < 0 ? after : after.slice(0, next)).trim(), rules.join('\n'),
               'source-scoped readable colors without external dependencies');
  assert.ok(!candidate.includes('@import'), 'no remote stylesheet imports');
}
validate(css);
const mutations = [
  [rules[0], rules[0].replace('.content ', 'body ')],
  [rules[0], rules[0].replace('has-primary-color', 'has-unknown-color')],
  [rules[0], rules[0].replace('#1c3b30', 'transparent')],
  [rules[0], rules[0].replace('#1c3b30', '#ffffff')],
  [rules[1], rules[1].replace('has-foreground-color', 'has-background-color')],
  [rules[1], rules[1].replace('var(--ink)', 'inherit')],
  [rules[1], rules[1].replace('var(--ink)', 'transparent')],
  [rules[2], rules[2].replace('has-black-color', 'has-white-color')],
  [rules[2], rules[2].replace('#111', '#fff')],
  [rules[2], rules[2].replace('#111', 'transparent')],
  [rules[2], rules[2].replace('color:#111', 'display:none;color:#111')],
  [rules[2], rules[2].replace('#111', 'url(https://example.org/track)')],
];
for (const [before, after] of mutations) {
  assert.ok(css.includes(before) && before !== after, 'valid mutation fixture');
  const changed = css.replace(before, after);
  assert.notEqual(changed, css);
  assert.throws(() => validate(changed), 'mutation must fail closed');
}
console.log('Gutenberg color presets PASS: 16 primary, 55 foreground, 5 black, 12 negative mutations.');
