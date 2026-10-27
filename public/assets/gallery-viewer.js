/* Progressive enhancement for the two published WordPress galleries. No external services. */
(() => {
  const galleries = [...document.querySelectorAll('article.content .wp-block-gallery')];
  if (!galleries.length || typeof HTMLDialogElement === 'undefined' || !HTMLDialogElement.prototype.showModal) return;

  const dialog = document.createElement('dialog');
  dialog.className = 'chm-gallery-dialog';
  dialog.setAttribute('aria-labelledby', 'chm-gallery-title');
  const heading = document.createElement('h2');
  heading.id = 'chm-gallery-title';
  const close = document.createElement('button');
  close.type = 'button';
  close.className = 'chm-gallery-close';
  close.textContent = 'Close image';
  const image = document.createElement('img');
  image.className = 'chm-gallery-image';
  const caption = document.createElement('p');
  caption.className = 'chm-gallery-caption';
  const controls = document.createElement('div');
  controls.className = 'chm-gallery-controls';
  const previous = document.createElement('button');
  previous.type = 'button';
  previous.textContent = 'Previous image';
  const next = document.createElement('button');
  next.type = 'button';
  next.textContent = 'Next image';
  controls.append(previous, next);
  dialog.append(close, heading, image, caption, controls);
  document.body.append(dialog);

  let active = null;
  function show() {
    const item = active.items[active.index];
    heading.textContent = `Image ${active.index + 1} of ${active.items.length}`;
    image.src = item.image.currentSrc || item.image.src;
    image.alt = item.image.alt;
    caption.textContent = item.caption || item.image.alt;
    previous.disabled = active.index === 0;
    next.disabled = active.index === active.items.length - 1;
  }
  function open(items, index, trigger) {
    active = { items, index, trigger };
    show();
    dialog.showModal();
    close.focus();
  }
  function move(offset) {
    if (!active) return;
    const target = active.index + offset;
    if (target < 0 || target >= active.items.length) return;
    active.index = target;
    show();
  }
  close.addEventListener('click', () => dialog.close());
  previous.addEventListener('click', () => move(-1));
  next.addEventListener('click', () => move(1));
  dialog.addEventListener('close', () => {
    const trigger = active?.trigger;
    active = null;
    image.removeAttribute('src');
    if (trigger?.isConnected) trigger.focus({ preventScroll: true });
  });
  dialog.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      move(event.key === 'ArrowRight' ? 1 : -1);
    }
  });
  dialog.addEventListener('click', event => {
    if (event.target === dialog) dialog.close();
  });

  for (const gallery of galleries) {
    const figures = [...gallery.querySelectorAll('figure.wp-block-image')];
    const items = figures.map(figure => ({
      image: figure.querySelector('img'),
      caption: figure.querySelector('figcaption')?.textContent.trim() || ''
    }));
    if (items.length < 2 || items.some(item => !item.image?.alt.trim())) continue;
    items.forEach((item, index) => {
      const figure = figures[index];
      const originalLink = figure.querySelector('a[href]');
      if (originalLink) {
        originalLink.addEventListener('click', event => {
          if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
          event.preventDefault();
          open(items, index, originalLink);
        });
      } else {
        const trigger = document.createElement('button');
        trigger.type = 'button';
        trigger.className = 'chm-gallery-trigger';
        trigger.setAttribute('aria-label', `View image ${index + 1} of ${items.length}: ${item.image.alt}`);
        item.image.before(trigger);
        trigger.append(item.image);
        trigger.addEventListener('click', () => open(items, index, trigger));
      }
    });
  }
})();
