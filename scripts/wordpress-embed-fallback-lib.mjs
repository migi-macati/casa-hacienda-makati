// WordPress Gutenberg embed fallback: source URL becomes an ordinary external link.
// No iframe, SDK, tracking script, third-party request, or source HTML modification.
const WRAPPER = /<div class="wp-block-embed__wrapper">([\s\S]*?)<\/div>/g;
const URL_TEXT = /^\s*(https:\/\/[^\s<>"]+)\s*$/;

export function enhanceEmbedFallbacks(html) {
  if (typeof html !== 'string') throw Error('Expected published HTML string');
  let count = 0;
  const updated = html.replace(WRAPPER, (whole, inner) => {
    const match = inner.match(URL_TEXT);
    if (!match) throw Error('Unreviewed Gutenberg embed wrapper markup');
    const source = match[1];
    let parsed;
    try { parsed = new URL(source); } catch { throw Error('Invalid original embed URL'); }
    if (parsed.protocol !== 'https:' || parsed.username || parsed.password ||
        parsed.port || parsed.hash || parsed.href !== source)
      throw Error('Unsafe or noncanonical original embed URL');
    const facebook = parsed.hostname === 'www.facebook.com' &&
      /^\/(?:casahaciendamakati|casamacati|casahaciendamakatii)\/posts\/\d+$/.test(parsed.pathname);
    const wordpress = parsed.hostname === 'jfmsmandaluyong.wordpress.com' &&
      parsed.pathname === '/about/history/' && !parsed.search;
    if (!facebook && !wordpress) throw Error('Unreviewed original embed destination');
    const escaped = source.replaceAll('&', '&amp;').replaceAll('"', '&quot;');
    const anchor = '<a class="wp-embed-source-link" href="' + escaped +
      '" target="_blank" rel="noopener noreferrer" title="Opens the original source in a new tab">' +
      escaped + '</a>';
    count++;
    return whole.replace(inner, inner.replace(source, anchor));
  });
  return { html: updated, count };
}
