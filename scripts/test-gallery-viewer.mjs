import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';
import { enhanceGalleryPage, GALLERY_PAGES } from './enhance-galleries.mjs';

const figure = i => `<figure class="wp-block-image"><img src="/media/test${i}.webp" alt="Scanned page ${i}"></figure>`;
const fixture = n => `<html><head><meta name="robots" content="noindex,nofollow"></head><body><article class="content"><figure class="wp-block-gallery">${Array.from({length:n},(_,i)=>figure(i+1)).join('')}</figure></article></body></html>`;
const valid = fixture(3);
const result = enhanceGalleryPage(valid, 3);
assert.ok(result.includes('gallery-viewer.css'));
assert.ok(result.includes('gallery-viewer.js'));
assert.equal(result.replace('<link rel="stylesheet" href="/assets/gallery-viewer.css">','').replace('<script defer src="/assets/gallery-viewer.js"></script>',''), valid);
assert.throws(() => enhanceGalleryPage(result, 3), /twice/);
assert.throws(() => enhanceGalleryPage(valid.replace('noindex,nofollow','index,follow'), 3), /noindex/);
assert.throws(() => enhanceGalleryPage(valid, 7), /count changed/);
assert.throws(() => enhanceGalleryPage(valid.replace('alt="Scanned page 2"','alt=""'), 3), /nonempty/);
assert.throws(() => enhanceGalleryPage(valid.replace('class="wp-block-gallery"','class="other"'), 3), /one published gallery/);
assert.throws(() => enhanceGalleryPage(valid.replace('</article>', '</article><article>other</article>'), 3), /one published content article/);
for (const [relative, count] of GALLERY_PAGES) {
  const html = await fs.readFile('public/' + relative, 'utf8');
  const enhanced = enhanceGalleryPage(html, count);
  assert.ok(enhanced.includes('gallery-viewer.js'));
}
console.log('Gallery enhancement synthetic/source checks PASS: two pinned galleries, 10 images, noindex, alt and single injection.');

 
// Exercise the actual shipped browser script in a minimal isolated DOM.
// This is deterministic, offline and requires no additional dependency.
function fakeNode(tag) {
  const listeners = new Map(), attrs = new Map();
  return {
    tag, children: [], isConnected: true,
    append(...nodes) { this.children.push(...nodes); },
    before(node) { this.beforeNode = node; },
    addEventListener(event, fn) { listeners.set(event, fn); },
    setAttribute(key, value) { attrs.set(key, value); },
    getAttribute(key) { return attrs.get(key); },
    removeAttribute(key) { attrs.delete(key); if (key === 'src') this.src = undefined; },
    focus(options) { this.focused = true; this.focusOptions = options; },
    showModal() { this.open = true; },
    close() { this.open = false; listeners.get('close')?.(); },
    fire(event, properties = {}) {
      let prevented = false;
      listeners.get(event)?.({ ...properties, preventDefault() { prevented = true; } });
      return prevented;
    },
  };
}
const galleryImages = Array.from({ length: 3 }, (_, i) => Object.assign(fakeNode('img'), {
  alt: 'Original description ' + (i + 1),
  src: '/media/photo' + (i + 1) + '.webp',
  currentSrc: '/media/photo' + (i + 1) + '.webp',
}));
const figures = galleryImages.map((img, i) => ({
  querySelector(selector) {
    if (selector === 'img') return img;
    if (selector === 'figcaption') return i === 2 ? null : { textContent: 'Caption ' + (i + 1) };
    if (selector === 'a[href]') return null;
  },
}));
const gallery = { querySelectorAll(selector) {
  assert.equal(selector, 'figure.wp-block-image');
  return figures;
}};
const body = fakeNode('body');
const fakeDocument = {
  body, createElement: fakeNode,
  querySelectorAll(selector) {
    assert.equal(selector, 'article.content .wp-block-gallery');
    return [gallery];
  },
};
class FakeDialog {}
FakeDialog.prototype.showModal = () => {};
vm.runInNewContext(await fs.readFile('public/assets/gallery-viewer.js', 'utf8'), {
  document: fakeDocument, HTMLDialogElement: FakeDialog,
});
const dialog = body.children[0];
assert.equal(dialog.tag, 'dialog');
assert.equal(dialog.getAttribute('aria-labelledby'), 'chm-gallery-title');
assert.equal(dialog.getAttribute('aria-describedby'), 'chm-gallery-help');
const [close, heading, help, modalImage, caption, status, controls] = dialog.children;
assert.equal(heading.getAttribute('aria-live'), undefined);
assert.equal(status.getAttribute('role'), 'status');
assert.equal(status.getAttribute('aria-live'), 'polite');
assert.equal(status.getAttribute('aria-atomic'), 'true');
assert.match(help.textContent, /Home and End/);
assert.match(help.textContent, /Escape to close/);
const [previous, next] = controls.children;
const trigger = galleryImages[0].beforeNode;
assert.equal(trigger.tag, 'button');
trigger.fire('click');
assert.equal(dialog.open, true);
assert.equal(close.focused, true);
assert.equal(heading.textContent, 'Image 1 of 3');
assert.equal(modalImage.src, '/media/photo1.webp');
assert.equal(caption.textContent, 'Caption 1');
assert.equal(status.textContent, 'Image 1 of 3. Caption 1');
assert.equal(caption.id, 'chm-gallery-caption');
assert.equal(modalImage.getAttribute('aria-describedby'), caption.id);
assert.equal(previous.disabled, true);
assert.equal(next.disabled, false);
assert.equal(dialog.fire('keydown', { key: 'End' }), true);
assert.equal(heading.textContent, 'Image 3 of 3');
assert.equal(caption.textContent, 'Original description 3');
assert.equal(status.textContent, 'Image 3 of 3. Original description 3');
assert.equal(modalImage.getAttribute('aria-describedby'), undefined);
assert.equal(next.disabled, true);
assert.equal(dialog.fire('keydown', { key: 'ArrowRight' }), true);
assert.equal(heading.textContent, 'Image 3 of 3');
assert.equal(dialog.fire('keydown', { key: 'Home' }), true);
assert.equal(heading.textContent, 'Image 1 of 3');
assert.equal(dialog.fire('keydown', { key: 'ArrowRight' }), true);
assert.equal(heading.textContent, 'Image 2 of 3');
assert.equal(status.textContent, 'Image 2 of 3. Caption 2');
assert.equal(modalImage.getAttribute('aria-describedby'), caption.id);
assert.equal(dialog.fire('keydown', { key: 'ArrowLeft' }), true);
assert.equal(heading.textContent, 'Image 1 of 3');
assert.equal(dialog.fire('keydown', { key: 'Tab' }), false);
close.fire('click');
assert.equal(dialog.open, false);
assert.equal(modalImage.src, undefined);
assert.equal(trigger.focused, true);
assert.equal(trigger.focusOptions.preventScroll, true);
console.log('Gallery keyboard runtime PASS: announcements, Home/End, arrows, bounds and focus restoration.');
