import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';

const MODES = new Set(['network', 'populate', 'offline']);

// A temporary, runner-local cache of verified original WordPress bytes.
// No source bytes are checked into Git or uploaded as a workflow artifact.
export function createSourceReader({ mode = 'network', cacheDir, fetchBytes, verifyBytes }) {
  if (!MODES.has(mode) || typeof fetchBytes !== 'function' || typeof verifyBytes !== 'function' ||
      (mode === 'network' && cacheDir) || (mode !== 'network' &&
        (typeof cacheDir !== 'string' || !path.isAbsolute(cacheDir)))) {
    throw Error('Invalid verified media cache configuration');
  }
  const cachePath = asset => path.join(cacheDir,
    createHash('sha256').update(asset.path).digest('hex') + '.bin');
  return async asset => {
    let bytes;
    if (mode === 'offline') {
      const file = cachePath(asset);
      const stat = await fs.lstat(file);
      if (!stat.isFile() || stat.isSymbolicLink()) throw Error('Unsafe cached media input');
      bytes = await fs.readFile(file);
    } else {
      bytes = await fetchBytes(asset.source);
    }
    // Both online and offline paths must match the pinned WXR/TAR provenance.
    verifyBytes(asset, bytes);
    if (mode === 'populate') {
      await fs.mkdir(cacheDir, { recursive: true, mode: 0o700 });
      await fs.writeFile(cachePath(asset), bytes, { flag: 'wx', mode: 0o600 });
    }
    return bytes;
  };
}
