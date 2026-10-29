#!/usr/bin/env python3
"""Read-only generated-site PDF link and embed accessibility gate.

Does not OCR, change article content, republish, or certify source PDFs.
"""
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit, unquote

EXPECTED = {
    '/media/2024/04/2009-120.pdf',
    '/media/2024/04/2009-174.pdf',
    '/media/2024/04/2012decision_ebcaseno_12-12-275_december.pdf',
}
PINNED_PUBLISHED_LINKS = {
    '/media/2024/04/2009-120.pdf',
    '/media/2024/04/2009-174.pdf',
}


def classify_url(raw):
    """Return (local PDF path, error); unrelated external citations are ignored."""
    if not raw:
        return None, None
    parts = urlsplit(raw.replace('&amp;', '&'))
    candidate = unquote(parts.path)
    if not candidate.lower().endswith('.pdf'):
        return None, None
    if candidate.startswith('/media/'):
        if parts.netloc or parts.scheme or parts.query or parts.fragment:
            return None, 'local PDF has unexpected origin, query or fragment'
        if candidate not in EXPECTED:
            return None, 'unrecognized public media PDF: ' + candidate
        return candidate, None
    if 'casahaciendamakati.wordpress.com' in parts.netloc.lower() and '/wp-content/uploads/' in candidate:
        return None, 'unbundled original WordPress PDF URL'
    return None, None


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.groups = []
        self.group_stack = []
        self.anchors = []
        self.objects = []
        self.ids = {}
        self.errors = []
        self.current_anchor = None
        self.noindex = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta' and attrs.get('name', '').lower() == 'robots' and attrs.get('content') == 'noindex,nofollow':
            self.noindex = True
        if tag == 'div':
            self.depth += 1
            if 'wp-block-file' in attrs.get('class', '').split():
                self.groups.append({'depth': self.depth, 'links': []})
                self.group_stack.append(len(self.groups) - 1)
        group = self.group_stack[-1] if self.group_stack else None
        if tag in ('object', 'iframe', 'embed'):
            source = attrs.get('data', '') if tag == 'object' else attrs.get('src', '')
            target, error = classify_url(source)
            if error:
                self.errors.append(error)
            elif target is None:
                # A PDF embedded from a remote, relative, inline, or viewer URL would
                # otherwise evade the pinned-media checks. External citation anchors
                # remain permitted; embedded PDF readers must use bundled media.
                parsed = urlsplit(source.strip())
                pdf_path = unquote(parsed.path).lower().endswith('.pdf')
                pdf_type = attrs.get('type', '').split(';', 1)[0].strip().lower() == 'application/pdf'
                inline_pdf = source.strip().lower().startswith('data:application/pdf')
                if pdf_path or pdf_type or inline_pdf:
                    self.errors.append(f'{tag} unpinned PDF embed: {source[:120]}')
            if target:
                self.objects.append({'path': target, 'name': attrs.get('aria-label', '') or attrs.get('title', ''), 'group': group, 'element': tag})
        if tag == 'a':
            target, error = classify_url(attrs.get('href', ''))
            if error:
                self.errors.append(error)
            self.current_anchor = {
                'path': target, 'name': attrs.get('aria-label', ''), 'text': '',
                'describedby': attrs.get('aria-describedby', ''), 'id': attrs.get('id', ''), 'group': group
            }
            if target:
                self.anchors.append(self.current_anchor)
                if group is not None:
                    self.groups[group]['links'].append(self.current_anchor)

    def handle_data(self, data):
        if self.current_anchor is not None:
            self.current_anchor['text'] += data

    def handle_endtag(self, tag):
        if tag == 'a' and self.current_anchor is not None:
            anchor = self.current_anchor
            if anchor['id']:
                self.ids[anchor['id']] = (anchor['name'] or anchor['text']).strip()
            self.current_anchor = None
        if tag == 'div':
            if self.group_stack and self.groups[self.group_stack[-1]]['depth'] == self.depth:
                self.group_stack.pop()
            self.depth = max(0, self.depth - 1)


def inspect_html(html, filename):
    parser = PageParser()
    parser.feed(html)
    errors = [f'{filename}: {e}' for e in parser.errors]
    paths = set()
    if (parser.anchors or parser.objects) and not parser.noindex:
        errors.append(f'{filename}: noindex,nofollow missing on PDF-linking page')
    for anchor in parser.anchors:
        paths.add(anchor['path'])
        name = (anchor['name'] or anchor['text']).strip()
        if name.lower() in ('download', 'open', 'view', 'pdf', 'file'):
            ids = anchor['describedby'].split()
            if not ids or not any(len(parser.ids.get(i, '').strip()) >= 12 for i in ids):
                errors.append(f'{filename}: generic PDF link lacks a descriptive aria-describedby target: {anchor["path"]}')
        elif len(name) < 12:
            errors.append(f'{filename}: PDF link lacks descriptive name: {anchor["path"]}')
    for obj in parser.objects:
        paths.add(obj['path'])
        if len(obj['name'].strip()) < 12:
            errors.append(f'{filename}: {obj["element"]} PDF embed lacks descriptive name: {obj["path"]}')
        group = obj['group']
        if group is None or not any(link['path'] == obj['path'] for link in parser.groups[group]['links']):
            errors.append(f'{filename}: {obj["element"]} PDF embed lacks same-block fallback link: {obj["path"]}')
    return {'paths': paths, 'links': len(parser.anchors), 'embeds': len(parser.objects), 'errors': errors}


def audit(root):
    manifest = json.loads((root / 'media-manifest.json').read_text())
    pdfs = [a for a in manifest['assets'] if a['path'].lower().endswith('.pdf')]
    if len(pdfs) != 3 or {a['path'] for a in pdfs} != EXPECTED or any(a.get('convert') is not False for a in pdfs):
        raise ValueError('Public PDF manifest identity changed')
    html_files = sorted((root / 'public').rglob('*.html'))
    if len(html_files) != 17:
        raise ValueError(f'Expected 17 published HTML routes, found {len(html_files)}')
    refs = {p: [] for p in EXPECTED}
    errors = []
    links = embeds = 0
    for file in html_files:
        relative = file.relative_to(root / 'public').as_posix()
        result = inspect_html(file.read_text(), relative)
        links += result['links']
        embeds += result['embeds']
        errors.extend(result['errors'])
        for pdf in result['paths']:
            refs[pdf].append(relative)
    for pdf in sorted(PINNED_PUBLISHED_LINKS):
        if '2024/10/28/cultural-significance-no-12/index.html' not in refs[pdf]:
            errors.append('Original public PDF link lost from its published article: ' + pdf)
    report = {
        'schema_version': 1,
        'scope': 'read-only generated HTML PDF-link and fallback accessibility audit',
        'html_routes': len(html_files), 'pdf_links': links, 'pdf_embeds': embeds,
        'documents': [{'path': p, 'referenced_in': refs[p], 'unlinked_media_asset': not bool(refs[p])}
                      for p in sorted(EXPECTED)],
        'errors': errors, 'manual_screen_reader_review_required': True
    }
    if errors:
        raise ValueError('PDF link accessibility gate failed:\n' + '\n'.join(errors))
    return report


def self_test():
    path = '/media/2024/04/2009-120.pdf'
    valid = ("<meta name='robots' content='noindex,nofollow'>"
             "<div class='wp-block-file'><object data='" + path + "' aria-label='Makati City Resolution No. 2009-120'></object>"
             "<a id='document-label' href='" + path + "'>Makati City Resolution No. 2009-120</a>"
             "<a href='" + path + "' aria-describedby='document-label'>Download</a></div>")
    assert not inspect_html(valid, 'fixture')['errors']
    # Every HTML embedding element must obey the same name and fallback rules.
    for element in ('iframe', 'embed'):
        alternate = valid.replace("<object data='", f"<{element} src='")
        alternate = alternate.replace('</object>', '</iframe>' if element == 'iframe' else '')
        assert not inspect_html(alternate, 'fixture')['errors'], f'valid {element} rejected'
        without_name = alternate.replace("aria-label='Makati City Resolution No. 2009-120'", "aria-label='PDF'")
        assert any('lacks descriptive name' in e for e in inspect_html(without_name, 'fixture')['errors']), f'unlabelled {element} accepted'
        without_fallback = alternate.replace("<a id='document-label' href='" + path + "'>Makati City Resolution No. 2009-120</a>", '')
        without_fallback = without_fallback.replace("<a href='" + path + "' aria-describedby='document-label'>Download</a>", '')
        assert any('same-block fallback' in e for e in inspect_html(without_fallback, 'fixture')['errors']), f'{element} without fallback accepted'
        unbundled = alternate.replace(path, 'https://casahaciendamakati.wordpress.com/wp-content/uploads/2024/04/2009-120.pdf')
        assert any('unbundled original WordPress' in e for e in inspect_html(unbundled, 'fixture')['errors']), f'unbundled {element} accepted'
    mutations = [
        valid.replace('noindex,nofollow', 'index,follow'),
        valid.replace("aria-label='Makati City Resolution No. 2009-120'", "aria-label='PDF'"),
        valid.replace("aria-describedby='document-label'", "aria-describedby='missing'"),
        valid.replace("id='document-label'", "id='wrong-label'"),
        valid.replace("<a id='document-label' href='" + path + "'>Makati City Resolution No. 2009-120</a>", ''),
        valid.replace(path, 'https://casahaciendamakati.wordpress.com/wp-content/uploads/2024/04/2009-120.pdf'),
        valid.replace(path, '/media/2024/04/other.pdf'),
    ]
    for idx, mutation in enumerate(mutations):
        assert mutation != valid, f'mutation {idx} did not apply'
        assert inspect_html(mutation, 'fixture')['errors'], f'unsafe PDF mutation {idx} accepted'
    assert classify_url('https://history.army.mil/external.pdf') == (None, None)
    # External scholarly citations are allowed as links, but an external PDF
    # rendered in an embedded reader must not bypass fallback/privacy checks.
    citation = ("<a href='https://history.army.mil/external.pdf'>"
                "Historical external PDF citation</a>")
    assert not inspect_html(citation, 'fixture')['errors']
    for element in ('object', 'iframe', 'embed'):
        embed = valid.replace("<object data='", f"<{element} src='")
        embed = embed.replace('</object>', '</iframe>' if element == 'iframe' else '')
        for bad_source in ('https://example.org/remote.pdf',
                           '//example.org/remote.pdf',
                           'relative/remote.pdf',
                           'data:application/pdf;base64,JVBERi0='):
            mutation = embed.replace(path, bad_source, 1)
            assert any('unpinned PDF embed' in e for e in inspect_html(mutation, 'fixture')['errors']), (element, bad_source)
        declared = embed.replace("aria-label='Makati City", "type='application/pdf' aria-label='Makati City", 1)
        declared = declared.replace(path, 'https://example.org/reader', 1)
        assert any('unpinned PDF embed' in e for e in inspect_html(declared, 'fixture')['errors']), element
    print('Public PDF links: 3 valid embedding fixtures + 28 fail-closed mutations + external citation PASS')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--output', type=Path, default=Path('artifacts/pdf-link-accessibility.json'))
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    self_test()
    if not args.self_test:
        report = audit(args.root.resolve())
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n')
        print('Public PDF link accessibility:', report['html_routes'], 'routes,', report['pdf_links'],
              'links,', report['pdf_embeds'], 'embeds; manual screen-reader review still required.')
