/* Progressive enhancement: native <details> remains usable without JavaScript. */
(() => {
  const menu = document.querySelector('details.mobile-nav');
  const summary = menu?.querySelector('summary');
  if (!summary) return;

  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || !menu.open ||
        !menu.contains(document.activeElement) ||
        document.querySelector('dialog:modal')) return;
    event.preventDefault();
    menu.open = false;
    summary.focus({ preventScroll: true });
  });
})();
