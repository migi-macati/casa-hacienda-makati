#!/usr/bin/env python3
"""Read-only original WXR/TAR provenance audit.

Usage: python scripts/audit-source-archive.py original.xml original.tar
Requires only Python's standard library. Reports aggregate counts only: no
draft metadata, media filenames, or source bytes are published.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

WP = '{http://wordpress.org/export/1.2/}'
WXR_SHA256 = '7ca0c47f6435764ceaebb7a2a869546b72d8282c65503dae85bfc9e45a7cd00a'
TAR_SHA256 = '2b818bcd0fe0035342c5fce4c11477ed4550e726864df0171a040a135cc974a6'
FORMATS = {'.jpg': 49, '.png': 29, '.gif': 1, '.pdf': 3}

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()

def safe_path(path):
    if (not path or path.startswith('/') or '\\' in path or
            any(x in ('', '.', '..') for x in path.split('/')) or
            PurePosixPath(path).as_posix() != path):
        raise ValueError('Unsafe or noncanonical archive path')
    return path

def wxr_paths(xml):
    paths = []
    for item in ET.parse(xml).getroot().findall('.//item'):
        if item.findtext(WP + 'post_type') != 'attachment':
            continue
        url = item.findtext(WP + 'attachment_url')
        if not url:
            raise ValueError('Attachment without source URL')
        p = unquote(urlsplit(url).path)
        marker = '/wp-content/uploads/'
        if marker not in p:
            raise ValueError('Attachment URL outside WordPress uploads')
        paths.append(safe_path(p.split(marker, 1)[1]))
    if len(paths) != len(set(paths)):
        raise ValueError('Duplicate WXR attachment path')
    return set(paths)

def good_signature(name, head):
    return {
        '.jpg': lambda: head.startswith(b'\xff\xd8\xff'),
        '.png': lambda: head.startswith(b'\x89PNG\r\n\x1a\n'),
        '.gif': lambda: head.startswith((b'GIF87a', b'GIF89a')),
        '.pdf': lambda: head.startswith(b'%PDF-'),
    }.get(PurePosixPath(name).suffix.lower(), lambda: False)()

def audit(xml, tar, pin=True):
    wxr_sha, tar_sha = sha256(xml), sha256(tar)
    if pin and (wxr_sha != WXR_SHA256 or tar_sha != TAR_SHA256):
        raise ValueError('Export SHA256 mismatch against owner-supplied originals')
    expected = wxr_paths(xml)
    found, hashes, formats = set(), defaultdict(list), Counter()
    total = 0
    with tarfile.open(tar, mode='r:') as archive:
        for member in archive:
            if not member.isfile():
                raise ValueError('Unexpected non-regular TAR member')
            name = safe_path(member.name)
            if name in found or name not in expected:
                raise ValueError('Duplicate or unexpected TAR path')
            found.add(name)
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError('Unreadable TAR member')
            digest = hashlib.sha256()
            head, size = b'', 0
            for block in iter(lambda: stream.read(1 << 20), b''):
                if not head:
                    head = block[:16]
                digest.update(block)
                size += len(block)
            if size != member.size or not good_signature(name, head):
                raise ValueError('Invalid source bytes or media signature')
            formats[PurePosixPath(name).suffix.lower()] += 1
            total += size
            hashes[digest.hexdigest()].append(size)
    if found != expected:
        raise ValueError('Missing original media')
    if pin and (len(expected) != 82 or dict(formats) != FORMATS):
        raise ValueError('Unexpected original media inventory')
    repeated = [v for v in hashes.values() if len(v) > 1]
    return {
        'wxr_sha256': wxr_sha, 'tar_sha256': tar_sha,
        'wxr_attachments': len(expected), 'tar_members': len(found),
        'path_match': True, 'valid_signatures': len(found),
        'formats': dict(sorted(formats.items())), 'original_bytes': total,
        'unique_payload_hashes': len(hashes),
        'duplicate_payload_groups': len(repeated),
        'redundant_duplicate_files': sum(len(v)-1 for v in repeated),
        'redundant_original_bytes': sum(sum(v[1:]) for v in repeated),
        'not_verified': 'Deployed WebP hashes, licensing, privacy, rendered/browser fidelity'
    }

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('wxr', type=Path)
    p.add_argument('tar', type=Path)
    p.add_argument('--unpin', action='store_true', help='Only for synthetic fixtures')
    args = p.parse_args()
    print(json.dumps(audit(args.wxr, args.tar, pin=not args.unpin), indent=2))
