#!/usr/bin/env python3
"""Seven synthetic fail-closed cases for the offline archive verifier."""
import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile

source = Path(__file__).with_name('audit-source-archive.py')
spec = importlib.util.spec_from_file_location('chm_source_archive', source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
passed = 0

def case(directory, urls, members):
    xml, archive = directory / 'test.xml', directory / 'test.tar'
    xml.write_text(
        '<rss xmlns:wp="http://wordpress.org/export/1.2/"><channel>' +
        ''.join('<item><wp:post_type>attachment</wp:post_type>'
                '<wp:attachment_url>' + u + '</wp:attachment_url></item>'
                for u in urls) + '</channel></rss>', encoding='utf-8')
    with tarfile.open(archive, 'w') as out:
        for name, content in members:
            entry = tarfile.TarInfo(name)
            entry.size = len(content)
            out.addfile(entry, io.BytesIO(content))
    return xml, archive

def expect_failure(xml, archive):
    global passed
    try:
        module.audit(xml, archive, pin=False)
    except ValueError:
        passed += 1
        return
    raise AssertionError('Invalid source export was accepted')

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    url = 'https://casahaciendamakati.wordpress.com/wp-content/uploads/2023/01/a.png'
    data = b'\x89PNG\r\n\x1a\n' + b'12345678'
    xml, archive = case(root, [url], [('2023/01/a.png', data)])
    assert module.audit(xml, archive, pin=False)['path_match']
    passed += 1

    xml, archive = case(root, [url], [('2023/01/b.png', data)])
    expect_failure(xml, archive)
    xml, archive = case(root, [url], [('../escape.png', data)])
    expect_failure(xml, archive)
    xml, archive = case(root, [url], [('2023/01/a.png', b'not-png')])
    expect_failure(xml, archive)
    xml, archive = case(root, [url, url], [('2023/01/a.png', data)])
    expect_failure(xml, archive)
    xml, archive = case(root, [url], [('2023/01/a.png', data), ('2023/01/a.png', data)])
    expect_failure(xml, archive)
    xml, archive = case(root, [url], [('2023/01/a.png', data)])
    try:
        module.audit(xml, archive, pin=True)
    except ValueError:
        passed += 1
    else:
        raise AssertionError('Unknown export SHA accepted in pinned mode')
print(f'{passed}/7 synthetic source-archive checks passed')
