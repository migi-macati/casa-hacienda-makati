import { createHash } from 'node:crypto';

const ORIGINAL_ORIGIN = 'https://casahaciendamakati.wordpress.com';
const SHA256 = /^[0-9a-f]{64}$/;
const UPLOAD = /^\d{4}\/\d{2}\/[a-z0-9_.-]+$/i;

export function sourcePath(asset) {
  if (!asset || typeof asset.source !== 'string' || typeof asset.path !== 'string' ||
      typeof asset.convert !== 'boolean') throw Error('Malformed media manifest entry');
  const url = new URL(asset.source);
  if (url.origin !== ORIGINAL_ORIGIN || url.search || url.hash ||
      !url.pathname.startsWith('/wp-content/uploads/')) throw Error('Unapproved original media URL');
  const original = decodeURIComponent(url.pathname.slice('/wp-content/uploads/'.length));
  if (!UPLOAD.test(original)) throw Error('Unsafe original media path');
  const destination = '/media/' + (asset.convert
    ? original.replace(/\.(?:jpe?g|png)$/i, '.webp') : original);
  if (destination !== asset.path || (asset.convert && !/\.(?:jpe?g|png)$/i.test(original)))
    throw Error('Media output path does not match original: ' + original);
  return original;
}

export function verifySourceInventory(manifest, inventory) {
  if (inventory?.schema_version !== 1 || !Array.isArray(inventory.assets) ||
      !Array.isArray(manifest?.assets) || manifest.assets.length !== 82 ||
      inventory.assets.length !== manifest.assets.length ||
      !SHA256.test(inventory.source_wxr_sha256 || '') ||
      !SHA256.test(inventory.source_tar_sha256 || '')) throw Error('Incomplete source media provenance inventory');
  const records = new Map();
  for (const record of inventory.assets) {
    if (!record || typeof record.source_path !== 'string' || !UPLOAD.test(record.source_path) ||
        !Number.isSafeInteger(record.bytes) || record.bytes < 1 ||
        !SHA256.test(record.sha256 || '') || records.has(record.source_path))
      throw Error('Invalid or duplicate pinned source media record');
    records.set(record.source_path, record);
  }
  const seen = new Set();
  for (const asset of manifest.assets) {
    const original = sourcePath(asset);
    if (seen.has(original) || !records.has(original))
      throw Error('Missing or duplicate source media path: ' + original);
    seen.add(original);
  }
  if (seen.size !== records.size) throw Error('Unreferenced pinned source media record');
  return records;
}

export function assertSourceBytes(asset, bytes, records) {
  const original = sourcePath(asset);
  const expected = records.get(original);
  if (!expected || !Buffer.isBuffer(bytes) || bytes.length !== expected.bytes ||
      createHash('sha256').update(bytes).digest('hex') !== expected.sha256)
    throw Error('Original archive byte mismatch: ' + original);
}
