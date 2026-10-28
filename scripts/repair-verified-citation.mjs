import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
export const ARTICLE = 'public/2023/10/21/cultural-significance-no-10/index.html';
export const ID = 'f6108b4c-e2f6-443c-a916-4b442c5b6b84';
export const NEW = 'https://pacificwrecks.com/airfield/philippines/nichols/1945/aerial-manila-nichols-nielson.html';
const OLD_PATH = '/airfields/philippines/nichols/1945/aerial-manila-nichols-nielson.html';
const CREDIT = 'Aerial view of Nichols Field and Nielson Field from B-24 after bombing attack, 1945, USAAF, FEAF.';
export function repair(html, checkOnly = false) {
  if (!/<meta\s+name="robots"\s+content="noindex,nofollow"/i.test(html)) throw Error('noindex missing');
  if (!html.includes('data-chm-restored-footnotes="1"')) throw Error('notes not restored');
  const tag = '<li id="' + ID + '">', start = html.indexOf(tag);
  if (start < 0 || html.indexOf(tag, start + 1) !== -1) throw Error('pinned note count not one');
  const end = html.indexOf('</li>', start);
  if (end < 0) throw Error('note closing tag missing');
  const note = html.slice(start, end + 5);
  if (!note.includes(CREDIT)) throw Error('publisher credit mismatch');
  const links = [...note.matchAll(/<a\b[^>]*\bhref="([^"]+)"[^>]*>/g)].filter(m => {
    try { return new URL(m[1].replace(/&amp;/g, '&')).hostname === 'pacificwrecks.com'; }
    catch { return false; }
  });
  if (links.length !== 1) throw Error('publisher link count not one');
  const link = links[0], url = new URL(link[1].replace(/&amp;/g, '&'));
  if (url.href === NEW) return html;
  if (url.protocol !== 'https:' || url.pathname !== OLD_PATH ||
      (url.search && !/^\?fbclid=[A-Za-z0-9_-]+$/.test(url.search)) || url.hash)
    throw Error('unrecognized old URL');
  if (checkOnly) throw Error('obsolete publisher citation');
  const updated = note.replace(link[0], link[0].replace('href="' + link[1] + '"', 'href="' + NEW + '"'));
  if (updated === note) throw Error('replacement failed');
  return html.slice(0, start) + updated + html.slice(end + 5);
}
if (process.argv[1] && pathToFileURL(path.resolve(process.argv[1])).href === import.meta.url) {
  const check = process.argv.includes('--check');
  const html = await fs.readFile(ARTICLE, 'utf8');
  const updated = repair(html, check);
  if (!check && updated !== html) await fs.writeFile(ARTICLE, updated);
  console.log('Publisher citation', check ? 'checked' : updated === html ? 'already current' : 'repaired');
}
