import assert from 'node:assert/strict';
import { addCommentBridge, assertCommentBridge } from './comment-bridge-lib.mjs';

const route = '/2023/08/12/example-post/';
const original = 'https://casahaciendamakati.wordpress.com' + route;
const fixture = '<!doctype html><head><meta name="robots" content="noindex,nofollow"></head>' +
  '<article class="content"><p>Published article body</p></article>' +
  '<div class="original">Original publication: <a href="' + original + '" target="_blank" rel="noopener noreferrer">' + original + '</a></div>';
let cases = 0;
const check = (fn) => { fn(); cases++; };
check(() => {
  const html = addCommentBridge(fixture, route);
  assert.match(html, /class="comment-bridge"/);
  assert.equal(addCommentBridge(html, route), html);
  assert.equal(assertCommentBridge(html, route).original, original);
  assert.match(html, /<article class="content"><p>Published article body<\/p><\/article>/);
});
check(() => assert.throws(() => addCommentBridge(fixture.replace('noindex,nofollow', 'index,follow'), route), /noindex/));
check(() => assert.throws(() => addCommentBridge(fixture.replace('wordpress.com', 'example.com'), route), /differs/));
check(() => assert.throws(() => addCommentBridge(fixture, '/private-draft/'), /Invalid published/));
check(() => assert.throws(() => addCommentBridge(fixture + fixture, route), /one original/));
check(() => assert.throws(() => addCommentBridge(fixture.replace('class="original"', 'class="missing"'), route), /one original/));
check(() => assert.throws(() => addCommentBridge(fixture + '<p class="comment-bridge">broken</p>', route), /Malformed/));
check(() => assert.throws(() => addCommentBridge(fixture.replace('example-post/', 'another-post/'), route), /differs/));
console.log('WordPress discussion bridge regression tests:', cases, 'PASS');
