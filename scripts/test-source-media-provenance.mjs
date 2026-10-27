import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { sourcePath, verifySourceInventory, assertSourceBytes } from './source-media-provenance.mjs';
const bytes = Buffer.from('immutable archival image fixture');
const digest = createHash('sha256').update(bytes).digest('hex');
const a = { source: 'https://casahaciendamakati.wordpress.com/wp-content/uploads/2023/07/sample.png', path: '/media/2023/07/sample.webp', convert: true };
const manifest = { assets: Array.from({length:82}, (_,i) => i===0 ? a : {
  source: 'https://casahaciendamakati.wordpress.com/wp-content/uploads/2023/07/sample-' + i + '.png',
  path: '/media/2023/07/sample-' + i + '.webp', convert: true
})};
const inventory = {schema_version:1,source_wxr_sha256:digest,source_tar_sha256:digest,
  assets:manifest.assets.map(x=>({source_path:sourcePath(x),bytes:bytes.length,sha256:digest}))};
const clone = x => structuredClone(x);
let passed=0;
function test(name,fn){fn();passed++;console.log('PASS',name)}
test('complete verified 82-asset inventory',()=>assert.equal(verifySourceInventory(manifest,inventory).size,82));
test('verified source bytes accepted',()=>assert.doesNotThrow(()=>assertSourceBytes(a,bytes,verifySourceInventory(manifest,inventory))));
test('changed original byte rejected',()=>assert.throws(()=>assertSourceBytes(a,Buffer.from('altered'),verifySourceInventory(manifest,inventory)),/byte mismatch/));
test('missing source record rejected',()=>{const i=clone(inventory);i.assets.pop();assert.throws(()=>verifySourceInventory(manifest,i),/Incomplete/)});
test('duplicate source record rejected',()=>{const i=clone(inventory);i.assets[1]=i.assets[0];assert.throws(()=>verifySourceInventory(manifest,i),/duplicate/)});
test('unapproved host rejected',()=>assert.throws(()=>sourcePath({...a,source:a.source.replace('wordpress.com','example.com')}),/Unapproved/));
test('path traversal rejected',()=>assert.throws(()=>sourcePath({...a,source:a.source.replace('sample.png','..%2Fsecret.png')}),/Unsafe/));
test('mismatched destination rejected',()=>assert.throws(()=>sourcePath({...a,path:'/media/2023/07/wrong.webp'}),/does not match/));
test('malformed checksum rejected',()=>{const i=clone(inventory);i.assets[0].sha256='0';assert.throws(()=>verifySourceInventory(manifest,i),/Invalid/)});
test('wrong original length rejected',()=>{const i=clone(inventory);i.assets[0].bytes++;assert.throws(()=>assertSourceBytes(a,bytes,verifySourceInventory(manifest,i)),/byte mismatch/)});
console.log('Original media provenance regression tests:',passed,'PASS');
