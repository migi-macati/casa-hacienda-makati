import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { enhanceEmbedFallbacks } from './wordpress-embed-fallback-lib.mjs';

const lock = JSON.parse(readFileSync('ops/published-search-sources.json', 'utf8'));
const css = readFileSync('public/assets/style.css', 'utf8');
const blob = text => {
  const data = Buffer.from(text);
  return createHash('sha1').update('blob ' + data.length).update(Buffer.from([0])).update(data).digest('hex');
};
assert.equal(blob(css), lock.stylesheetGitBlob, 'CSS pinned to reviewed source');
assert.equal(lock.documents.length, 15, 'Published source inventory');
let total = 0, routes = 0;
for (const doc of lock.documents) {
  const source = readFileSync('public/' + doc.file, 'utf8');
  assert.equal(blob(source), doc.gitBlob, 'Published source pinned: ' + doc.file);
  const wrappers = (source.match(/<div class="wp-block-embed__wrapper">/g) || []).length;
  const { html, count } = enhanceEmbedFallbacks(source);
  assert.equal(count, wrappers, 'Every original wrapper enhanced');
  assert.equal((html.match(/class="wp-embed-source-link"/g) || []).length, wrappers);
  assert.equal(html.replace(/<a class="wp-embed-source-link"[^>]*>([^<]*)<\/a>/g,
    (_, text) => text.replaceAll('&amp;', '&')), source, 'Original visible text preserved');
  assert.equal((html.match(/<iframe\b/gi) || []).length, (source.match(/<iframe\b/gi) || []).length,
    'No third-party iframe introduced');
  assert.ok(html.includes('<meta name="robots" content="noindex,nofollow">'));
  if (count) routes++;
  total += count;
}
assert.equal(total, 28, 'Exact Gutenberg embed inventory');
assert.equal(routes, 8, 'Exact affected route inventory');
const wrap = url => '<figure class="wp-block-embed"><div class="wp-block-embed__wrapper"> ' +
  url + ' </div></figure>';
const good = 'https://www.facebook.com/casahaciendamakati/posts/123456';
assert.equal(enhanceEmbedFallbacks(wrap(good)).count, 1);
for (const bad of [
  'http://www.facebook.com/casahaciendamakati/posts/123456',
  'javascript:alert(1)',
  'https://www.facebook.com.evil.example/casahaciendamakati/posts/123456',
  'https://user:pass@www.facebook.com/casahaciendamakati/posts/123456',
  'https://www.facebook.com:8443/casahaciendamakati/posts/123456',
  'https://www.facebook.com/casahaciendamakati/photos/123456',
  'https://www.facebook.com/casahaciendamakati/posts/not-a-number',
  'https://jfmsmandaluyong.wordpress.com/wp-admin/',
  'https://www.facebook.com/casahaciendamakati/posts/123456#fragment',
  '<iframe src="https://www.facebook.com/"></iframe>'
]) assert.throws(() => enhanceEmbedFallbacks(wrap(bad)), 'Must reject unreviewed embed: ' + bad);
console.log('WordPress embed fallback: 28 sources, 8 routes, 10 fail-closed URL fixtures PASS.');
