#!/usr/bin/env python3
"""Compare complete generated public trees by path and SHA256, rejecting symlinks."""
import argparse
import hashlib
import tempfile
from pathlib import Path


def inventory(root):
    root = Path(root)
    if not root.is_dir() or root.is_symlink():
        raise ValueError('Build output root is missing or a symlink')
    entries = {}
    for item in root.rglob('*'):
        if item.is_symlink():
            raise ValueError('Symlink in build output: ' + str(item.relative_to(root)))
        if item.is_file():
            relative = item.relative_to(root).as_posix()
            entries[relative] = (item.stat().st_size, hashlib.sha256(item.read_bytes()).hexdigest())
        elif not item.is_dir():
            raise ValueError('Unexpected filesystem entry')
    if not entries:
        raise ValueError('Empty build output')
    return entries


def compare(a, b):
    first, second = inventory(a), inventory(b)
    missing = sorted(set(first) - set(second))
    added = sorted(set(second) - set(first))
    changed = sorted(k for k in first.keys() & second.keys() if first[k] != second[k])
    if missing or added or changed:
        raise ValueError('Build outputs differ: missing=' + repr(missing[:10]) +
                         ', added=' + repr(added[:10]) + ', changed=' + repr(changed[:10]))
    return len(first)


def self_test():
    with tempfile.TemporaryDirectory() as root:
        a, b = Path(root) / 'a', Path(root) / 'b'
        a.mkdir(); b.mkdir()
        (a / 'index.html').write_text('same')
        (b / 'index.html').write_text('same')
        assert compare(a, b) == 1
        (b / 'index.html').write_text('different')
        try: compare(a, b)
        except ValueError: pass
        else: raise AssertionError('Byte drift accepted')
        (b / 'index.html').write_text('same')
        (b / 'extra').write_text('extra')
        try: compare(a, b)
        except ValueError: pass
        else: raise AssertionError('Extra file accepted')
        (b / 'extra').unlink()
        (b / 'link').symlink_to('index.html')
        try: compare(a, b)
        except ValueError: pass
        else: raise AssertionError('Symlink accepted')
    print('Build tree comparator synthetic regressions PASS: 4 assertions')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--self-test', action='store_true')
    p.add_argument('--first')
    p.add_argument('--second')
    args = p.parse_args()
    if args.self_test:
        self_test()
    elif args.first and args.second:
        print('Reproducible generated output PASS:', compare(args.first, args.second), 'byte-identical files')
    else:
        p.error('Supply --self-test or --first and --second')
