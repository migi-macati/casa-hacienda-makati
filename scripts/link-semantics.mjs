// Published migration links: fail closed on inert or unsafe anchors.
export function assertLinkSemantics(html, label = 'page') {
  const errors = [];
  const attr = (tag, name) => {
    const re = new RegExp('\\s' + name + '\\s*=\\s*(?:"([^"]*)"|\'([^\']*)\'|([^\\s>]+))', 'i');
    const match = tag.match(re);
    return match ? (match[1] ?? match[2] ?? match[3]) : null;
  };
  for (const match of html.matchAll(/<a\b[^>]*>/gi)) {
    const tag = match[0];
    const href = attr(tag, 'href');
    if (href === null || !href.trim()) { errors.push('anchor without a destination'); continue; }
    if (/^(?:javascript|data|vbscript)\s*:/i.test(href.trim()))
      errors.push('unsafe anchor scheme');
    if (attr(tag, 'target')?.toLowerCase() === '_blank') {
      const rel = (attr(tag, 'rel') || '').toLowerCase().split(/\s+/);
      if (!rel.includes('noopener') || !rel.includes('noreferrer'))
        errors.push('new-window anchor lacks noopener noreferrer');
    }
  }
  if (errors.length) throw Error(label + ': ' + errors.join('; '));
}
