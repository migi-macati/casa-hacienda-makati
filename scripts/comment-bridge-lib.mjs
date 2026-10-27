// The static migration does not accept comments. Preserve a verified route back
// to the original WordPress discussion without introducing a form or service.
const sourceOrigin = 'https://casahaciendamakati.wordpress.com';
const routePattern = /^\/(?:\d{4}\/\d{2}\/\d{2}\/)[a-z0-9-]+\/$/;
const originalPattern = /<div class="original">Original publication:\s*<a href="([^"]+)"[^>]*>[^<]*<\/a>([\s\S]*?)<\/div>/gi;
const commentPattern = /<p class="comment-bridge">Discussion remains on the original WordPress post\. <a href="([^"]+)" target="_blank" rel="noopener noreferrer">Read or leave a comment on WordPress ↗<\/a>\.<\/p>/g;

export function assertCommentBridge(html, route, requireBridge = true) {
  if (!routePattern.test(route)) throw Error('Invalid published article route: ' + route);
  if (!/<meta\s+name="robots"\s+content="noindex,nofollow"/i.test(html))
    throw Error('Missing migration noindex for ' + route);
  const originals = [...html.matchAll(originalPattern)];
  if (originals.length !== 1) throw Error('Expected one original-publication block for ' + route);
  const expected = sourceOrigin + route;
  if (originals[0][1] !== expected) throw Error('Original-publication URL differs from published route: ' + route);
  const bridges = [...html.matchAll(commentPattern)];
  if (requireBridge && bridges.length !== 1) throw Error('Expected one original discussion link for ' + route);
  if (bridges.length > 1 || bridges.some(b => b[1] !== expected + '#respond'))
    throw Error('Invalid original discussion link for ' + route);
  if (html.includes('class="comment-bridge"') && bridges.length !== 1)
    throw Error('Malformed original discussion link for ' + route);
  if (bridges.length && !originals[0][2].includes(bridges[0][0]))
    throw Error('Original discussion link outside the original-publication block: ' + route);
  return { original: expected, hasBridge: bridges.length === 1 };
}

export function addCommentBridge(html, route) {
  const { original, hasBridge } = assertCommentBridge(html, route, false);
  if (hasBridge) return html;
  const bridge = '<p class="comment-bridge">Discussion remains on the original WordPress post. ' +
    '<a href="' + original + '#respond" target="_blank" rel="noopener noreferrer">' +
    'Read or leave a comment on WordPress ↗</a>.</p>';
  const updated = html.replace(originalPattern, (whole, href, rest) =>
    whole.replace('</div>', bridge + '</div>'));
  assertCommentBridge(updated, route, true);
  return updated;
}
