import assert from 'node:assert/strict';
import fs from 'node:fs';

// Checks the npm-generated dependency lock's integrity and source constraints.
// Does not certify npm publisher identities or make installation air-gapped.
export function validateLock(manifest, lock) {
  assert.equal(lock.lockfileVersion, 3, 'npm lockfile v3 required');
  assert.equal(lock.name, manifest.name, 'lockfile project name mismatch');
  assert.equal(lock.version, manifest.version, 'lockfile project version mismatch');
  assert.ok(lock.packages && typeof lock.packages === 'object', 'missing package entries');
  assert.ok(lock.packages[''] && typeof lock.packages[''] === 'object', 'missing root entry');
  assert.deepEqual(lock.packages[''].dependencies, manifest.dependencies,
    'locked root dependencies must exactly match package.json');
  assert.equal(lock.packages['node_modules/sharp']?.version, manifest.dependencies.sharp,
    'Sharp dependency must resolve to its exact manifest version');
  let checked = 0;
  for (const [path, entry] of Object.entries(lock.packages)) {
    if (path === '') continue;
    assert.match(path, /^(?:node_modules\/)+(?:@[^/]+\/)?[^/]+(?:\/node_modules\/(?:@[^/]+\/)?[^/]+)*$/,
      `Unexpected package path: ${path}`);
    assert.match(String(entry.version || ''), /^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.+-]+)?$/,
      `Missing pinned package version: ${path}`);
    assert.match(String(entry.integrity || ''), /^sha(?:512|384|256)-[A-Za-z0-9+/]+={0,2}(?:\s+sha(?:512|384|256)-[A-Za-z0-9+/]+={0,2})*$/,
      `Missing cryptographic package integrity: ${path}`);
    const source = new URL(String(entry.resolved || ''));
    assert.equal(source.protocol, 'https:', `Non-HTTPS package source: ${path}`);
    assert.equal(source.hostname, 'registry.npmjs.org', `Unapproved package registry: ${path}`);
    assert.equal(source.username, '', `Credentialed package source: ${path}`);
    assert.equal(source.password, '', `Credentialed package source: ${path}`);
    assert.equal(source.search, '', `Query-bearing package source: ${path}`);
    assert.equal(source.hash, '', `Fragment-bearing package source: ${path}`);
    assert.ok(source.pathname.endsWith('.tgz'), `Non-tarball package source: ${path}`);
    checked++;
  }
  assert.ok(checked > 0, 'Empty dependency graph');
  return checked;
}

const fixtureManifest = { name: 'casa-hacienda-makati', version: '1.0.0', dependencies: { sharp: '0.35.5' } };
const fixture = {
  name: 'casa-hacienda-makati', version: '1.0.0', lockfileVersion: 3,
  packages: {
    '': { dependencies: { sharp: '0.35.5' } },
    'node_modules/sharp': {
      version: '0.35.5',
      resolved: 'https://registry.npmjs.org/sharp/-/sharp-0.35.5.tgz',
      integrity: 'sha512-aabbcc==',
    },
  },
};
function selfTest() {
  assert.equal(validateLock(fixtureManifest, fixture), 1);
  const rejects = [
    l => { l.lockfileVersion = 2; },
    l => { l.packages[''].dependencies.sharp = '^0.35.5'; },
    l => { l.packages['node_modules/sharp'].version = '0.35.4'; },
    l => { delete l.packages['node_modules/sharp'].integrity; },
    l => { l.packages['node_modules/sharp'].resolved = 'http://registry.npmjs.org/sharp/-/sharp-0.35.5.tgz'; },
    l => { l.packages['node_modules/sharp'].resolved = 'https://evil.example/sharp.tgz'; },
    l => { l.packages['node_modules/sharp'].resolved = 'git+https://github.com/example/sharp'; },
    l => { delete l.packages['node_modules/sharp'].resolved; },
    l => { l.packages['node_modules/sharp'].resolved += '?token=secret'; },
    l => { delete l.packages['node_modules/sharp']; },
  ];
  for (const [i, mutate] of rejects.entries()) {
    const broken = structuredClone(fixture);
    mutate(broken);
    assert.throws(() => validateLock(fixtureManifest, broken), undefined,
      `Unsafe lockfile mutation ${i + 1} passed`);
  }
  console.log(`npm lockfile provenance fixtures PASS: ${rejects.length} fail-closed mutations`);
}

if (process.argv.includes('--self-test')) {
  selfTest();
} else {
  const manifest = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  const lock = JSON.parse(fs.readFileSync('package-lock.json', 'utf8'));
  const count = validateLock(manifest, lock);
  console.log(`npm lockfile provenance PASS: ${count} registry-pinned packages`);
}
