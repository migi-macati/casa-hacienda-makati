import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { createSourceReader } from './media-source-cache.mjs';

const dir = await fs.mkdtemp(path.join(os.tmpdir(), 'chm-verified-media-'));
const asset = { path: '/media/2023/01/example.webp', source: 'https://example.invalid/original' };
const original = Buffer.from('Verified original image payload for synthetic cache test');
const digest = createHash('sha256').update(original).digest('hex');
let requests = 0;
const fetchBytes = async () => { requests++; return original; };
const verifyBytes = (_asset, bytes) => {
  assert.equal(createHash('sha256').update(bytes).digest('hex'), digest);
};
let checks = 0;
async function passes(fn) { await fn(); checks++; }
async function rejects(fn) { await assert.rejects(fn); checks++; }
try {
  await passes(async () => assert.deepEqual(await createSourceReader({ fetchBytes, verifyBytes })(asset), original));
  await passes(async () => assert.equal(requests, 1));
  await passes(async () => assert.deepEqual(await createSourceReader({ mode: 'populate', cacheDir: dir, fetchBytes, verifyBytes })(asset), original));
  await passes(async () => assert.equal((await fs.readdir(dir)).length, 1));
  const offline = createSourceReader({ mode: 'offline', cacheDir: dir, fetchBytes: async () => { throw Error('NETWORK USED'); }, verifyBytes });
  await passes(async () => assert.deepEqual(await offline(asset), original));
  await passes(async () => assert.equal(requests, 2));
  const filename = path.join(dir, (await fs.readdir(dir))[0]);
  await rejects(async () => createSourceReader({ mode: 'populate', cacheDir: dir, fetchBytes, verifyBytes })(asset));
  await fs.writeFile(filename, Buffer.from('tampered'));
  await rejects(async () => offline(asset));
  await fs.rm(filename);
  await rejects(async () => offline(asset));
  await fs.symlink(path.join(dir, 'missing'), filename);
  await rejects(async () => offline(asset));
  await passes(async () => assert.throws(() => createSourceReader({ mode: 'offline', cacheDir: 'relative', fetchBytes, verifyBytes })));
  await passes(async () => assert.throws(() => createSourceReader({ mode: 'network', cacheDir: dir, fetchBytes, verifyBytes })));
  console.log('Verified media cache synthetic regressions PASS:', checks, 'assertions');
} finally {
  await fs.rm(dir, { recursive: true, force: true });
}
