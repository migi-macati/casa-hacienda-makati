#!/usr/bin/env python3
"""Read-only inventory of published migration PDFs, not a PDF/UA or WCAG certification.

Requires pypdf==5.9.0. Never OCR, modify, or republish source PDF bytes.
"""
import argparse
import hashlib
import json
from pathlib import Path
from pypdf import PdfReader

EXPECTED = {
    '/media/2024/04/2009-120.pdf',
    '/media/2024/04/2009-174.pdf',
    '/media/2024/04/2012decision_ebcaseno_12-12-275_december.pdf',
}


def classify(page_characters, has_structure, has_language):
    """A text layer or tag flag alone never establishes screen-reader usability."""
    if not page_characters:
        raise ValueError('PDF has no pages')
    textless = sum(chars < 20 for chars in page_characters)
    reasons = []
    if textless:
        reasons.append(f'{textless} pages have fewer than 20 extracted text characters')
    if not has_structure:
        reasons.append('no document structure tree')
    if not has_language:
        reasons.append('no document language declaration')
    return {'textless_pages': textless, 'requires_manual_review': True,
            'automated_concerns': reasons,
            'status': 'manual_accessibility_review_required'}


def audit(root):
    manifest = json.loads((root / 'media-manifest.json').read_text())
    assets = [a for a in manifest['assets'] if a['path'].lower().endswith('.pdf')]
    paths = {a['path'] for a in assets}
    if len(assets) != 3 or paths != EXPECTED or any(a.get('convert') is not False for a in assets):
        raise ValueError('Public PDF source inventory changed; review provenance and rights before accepting')
    inventory = []
    for asset in sorted(assets, key=lambda a: a['path']):
        relative = asset['path'].lstrip('/')
        path = (root / 'public' / relative).resolve()
        public_root = (root / 'public').resolve()
        if not path.is_relative_to(public_root) or not path.is_file():
            raise ValueError(f'Public PDF missing or outside generated root: {relative}')
        data = path.read_bytes()
        if not data.startswith(b'%PDF-'):
            raise ValueError(f'Invalid PDF signature: {relative}')
        reader = PdfReader(path, strict=False)
        if reader.is_encrypted:
            raise ValueError(f'Encrypted PDF needs separate owner review: {relative}')
        catalog = reader.trailer['/Root'].get_object()
        structure = bool(catalog.get('/StructTreeRoot'))
        language = bool(str(catalog.get('/Lang', '')).strip())
        page_characters = []
        for page in reader.pages:
            try:
                text = page.extract_text() or ''
            except Exception as exc:
                raise ValueError(f'PDF text extraction failed for {relative}: {exc}') from exc
            page_characters.append(len(text.strip()))
        record = {'path': asset['path'], 'bytes': len(data),
                  'sha256': hashlib.sha256(data).hexdigest(),
                  'pages': len(page_characters),
                  'extracted_text_characters_per_page': page_characters,
                  'has_structure_tree': structure,
                  'has_language': language}
        record.update(classify(page_characters, structure, language))
        inventory.append(record)
    total_pages = sum(a['pages'] for a in inventory)
    if total_pages != 9:
        raise ValueError(f'PDF page inventory changed: expected 9, found {total_pages}; investigate before release')
    return {'schema_version': 1, 'source': 'public published migration assets only',
            'scope': 'read-only structural inventory, not PDF/UA or WCAG compliance',
            'pdf_count': len(inventory), 'total_pages': total_pages,
            'all_require_manual_review': True, 'pdfs': inventory}


def self_test():
    assert classify([0, 4, 500], False, False)['textless_pages'] == 2
    assert classify([300], True, True)['requires_manual_review'] is True
    assert classify([300], True, True)['automated_concerns'] == []
    assert classify([300], False, True)['automated_concerns'] == ['no document structure tree']
    try:
        classify([], True, True)
    except ValueError:
        pass
    else:
        raise AssertionError('Empty PDF must fail')
    print('PDF accessibility classification: 5 fail-closed/positive fixtures PASS')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--output', type=Path, default=Path('artifacts/pdf-accessibility.json'))
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    self_test()
    if not args.self_test:
        report = audit(args.root.resolve())
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n')
        print('PDF accessibility inventory:', report['pdf_count'], 'public PDFs,', report['total_pages'],
              'pages. All require manual review; no source bytes modified.')
