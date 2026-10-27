import fs from 'node:fs/promises';
import path from 'node:path';
import { createHash } from 'node:crypto';

const root = path.resolve('public');
const dateFile = /^\d{4}\/\d{2}\/\d{2}\/[^/]+\/index\.html$/;
const gitBlob = data => createHash('sha1').update(`blob ${data.length}\0`).update(data).digest('hex');
const sha256 = data => createHash('sha256').update(data).digest('hex');
const routeFor = file => '/' + file.slice(0, -'index.html'.length);

async function loadLock() {
  const lock = JSON.parse(await fs.readFile('ops/published-search-sources.json', 'utf8'));
  if (lock.version !== 1 || !Array.isArray(lock.documents) || lock.documents.length !== 15 ||
      !/^[0-9a-f]{40}$/.test(lock.stylesheetGitBlob)) throw Error('Invalid published search source lock');
  const paths = new Set();
  for (const d of lock.documents) {
    if (!d || typeof d.file !== 'string' || !/^[0-9a-f]{40}$/.test(d.gitBlob) ||
        !(dateFile.test(d.file) && d.type === 'article' ||
          ['about/index.html', 'cultural-significance/index.html'].includes(d.file) && d.type === 'page') ||
        paths.has(d.file)) throw Error('Invalid or repeated published search route');
    paths.add(d.file);
  }
  if (lock.documents.filter(d => d.type === 'article').length !== 13 ||
      lock.documents.filter(d => d.type === 'page').length !== 2 ||
      !paths.has('about/index.html') || !paths.has('cultural-significance/index.html'))
    throw Error('Published route count or informational pages differ from source inventory');
  return lock;
}

async function publishedFiles() {
  const files = [];
  async function visit(dir) {
    for (const item of await fs.readdir(dir, { withFileTypes: true })) {
      const file = path.join(dir, item.name);
      if (item.isDirectory()) await visit(file);
      else if (item.name === 'index.html') {
        const rel = path.relative(root, file).split(path.sep).join('/');
        if (dateFile.test(rel) || ['about/index.html', 'cultural-significance/index.html'].includes(rel)) files.push(rel);
      }
    }
  }
  await visit(root);
  return files.sort();
}

function assertPage(html, route) {
  if (!/<meta\s+name=["']robots["']\s+content=["']noindex,nofollow["']/i.test(html))
    throw Error(`Noindex missing: ${route}`);
  const articles = [...html.matchAll(/<article\b([^>]*)>([\s\S]*?)<\/article>/gi)];
  if (articles.length !== 1 || !/\bclass\s*=\s*(["'])content\1/i.test(articles[0][1]))
    throw Error(`Expected exactly one explicit content article: ${route}`);
  const headings = [...html.matchAll(/<h1\b[^>]*>([\s\S]*?)<\/h1>/gi)];
  if (headings.length !== 1) throw Error(`Expected exactly one H1: ${route}`);
  // Embedded PDFs are nontext; the surrounding download links remain searchable.
  const body = articles[0][2].replace(/<object\b[^>]*>[\s\S]*?<\/object>/gi, ' ');
  if (/<(?:script|style|template|noscript|iframe|object|embed|svg)\b/i.test(body))
    throw Error(`Active or nontext article markup: ${route}`);
  if (/<[^>]+\s(?:hidden|inert)(?:\s|=|>)/i.test(body) ||
      /<[^>]+\bstyle\s*=\s*["'][^"']*(?:display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0(?:\D|$))/i.test(body))
    throw Error(`Hidden or inline-invisible article markup needs review: ${route}`);
  const cleaned = body.replace(/<div\b(?=[^>]*\baria-hidden\s*=\s*["']true["'])[^>]*>\s*<\/div>/gi, '');
  if (/<[^>]+\baria-hidden\s*=\s*["']true["']/i.test(cleaned))
    throw Error(`Unreviewed aria-hidden article content: ${route}`);
  return { title: headings[0][1], body: cleaned };
}

const entities = {amp:'&',nbsp:' ',lt:'<',gt:'>',quot:'"',apos:"'",lsquo:'‘',rsquo:'’',ldquo:'“',rdquo:'”',ndash:'–',mdash:'—',hellip:'…',bull:'•',copy:'©',reg:'®',deg:'°',thinsp:' ',euro:'€',trade:'™',times:'×',laquo:'«',raquo:'»',cent:'¢',pound:'£'};
function plain(html) {
  const noComments = html.replace(/<!--[\s\S]*?-->/g, ' ');
  const noTags = noComments.replace(/<[^>]*>/g, ' ');
  const decoded = noTags.replace(/&(#x[0-9a-f]+|#\d+|[a-z][a-z0-9]+);/gi, (whole, code) => {
    if (code.startsWith('#')) {
      const value = code[1].toLowerCase() === 'x' ? parseInt(code.slice(2), 16) : parseInt(code.slice(1), 10);
      if (value < 32 && value !== 10 || value > 0x10ffff || value >= 0xd800 && value <= 0xdfff)
        throw Error('Invalid numeric HTML entity');
      return String.fromCodePoint(value);
    }
    const result = entities[code.toLowerCase()];
    if (result === undefined) throw Error(`Unrecognized HTML entity ${whole}`);
    return result;
  });
  return decoded.replace(/\s+/g, ' ').trim();
}

function assertRouteSet(found, lock) {
  const expected = lock.documents.map(d => d.file).sort();
  if (JSON.stringify([...found].sort()) !== JSON.stringify(expected))
    throw Error('Published HTML route inventory drift');
}

async function assertSourceClosure(lock) {
  assertRouteSet(await publishedFiles(), lock);
  const css = await fs.readFile(path.join(root, 'assets/style.css'));
  if (gitBlob(css) !== lock.stylesheetGitBlob) throw Error('CSS changed without computed-visibility review');
  for (const d of lock.documents) {
    const bytes = await fs.readFile(path.join(root, d.file));
    if (gitBlob(bytes) !== d.gitBlob) throw Error(`Source changed without approved search lock: ${d.file}`);
    assertPage(bytes.toString('utf8'), routeFor(d.file));
  }
  return sha256(JSON.stringify(lock));
}

async function buildEntries(lock) {
  assertRouteSet(await publishedFiles(), lock);
  const entries = [];
  for (const d of lock.documents) {
    const html = await fs.readFile(path.join(root, d.file), 'utf8');
    const route = routeFor(d.file);
    const { title, body } = assertPage(html, route);
    const expectedCanonical = 'https://casa-hacienda-makati.vercel.app' + route;
    if (!html.includes(`<link rel="canonical" href="${expectedCanonical}">`))
      throw Error(`Canonical missing or unexpected: ${route}`);
    const text = plain(body), heading = plain(title);
    if (!text || !heading) throw Error(`Empty published search document: ${route}`);
    entries.push({ url: route, title: heading, text, type: d.type });
  }
  return entries;
}

const command = process.argv[2];
if (command === 'test') {
  const assert = (await import('node:assert/strict')).default;
  const route = '/2023/08/12/example/';
  const ok = '<meta name="robots" content="noindex,nofollow"><h1>Published</h1><article class="content"><p>Public text</p></article>';
  assert.equal(plain(assertPage(ok, route).body), 'Public text');
  for (const html of [
    ok.replace('noindex,nofollow', 'index,follow'),
    ok.replace('class="content"', 'class="content other"'),
    ok.replace('class="content"', 'class="other"'),
    ok.replace('</article>', '</article><article class="content">private</article>'),
    ok.replace('Public text', '<span hidden>Private</span>Public text'),
    ok.replace('Public text', '<span style="display:none">Private</span>Public text'),
    ok.replace('Public text', '<span aria-hidden="true">Private</span>Public text'),
    ok.replace('Public text', '<script>Private</script>Public text')
  ]) assert.throws(() => assertPage(html, route));
  assert.equal(plain('Hello &amp; &#8217; world'), 'Hello & ’ world');
  assert.throws(() => plain('Unknown &unapprovedentity;'));
  const lock = await loadLock();
  const routes = lock.documents.map(d => d.file);
  assertRouteSet(routes, lock);
  assert.throws(() => assertRouteSet([...routes, '2026/01/01/unauthorized/index.html'], lock));
  assert.throws(() => assertRouteSet(routes.slice(1), lock));
  console.log('Search privacy synthetic regressions PASS: 14 assertions.');
} else if (command === 'prebuild') {
  const lock = await loadLock();
  const lockSha256 = await assertSourceClosure(lock);
  await fs.writeFile('ops/.search-source-attestation.json', JSON.stringify({ lockSha256 }));
  console.log('Search source lock PASS: 13 articles, 2 pages and CSS pinned before build.');
} else if (command === 'build') {
  const lock = await loadLock();
  const attestation = JSON.parse(await fs.readFile('ops/.search-source-attestation.json', 'utf8'));
  if (attestation.lockSha256 !== sha256(JSON.stringify(lock))) throw Error('Missing or stale prebuild source attestation');
  const entries = await buildEntries(lock);
  const index = JSON.stringify(entries);
  await fs.writeFile(path.join(root, 'search-index.json'), index);
  await fs.writeFile(path.join(root, 'search-provenance.json'), JSON.stringify({
    version: 1, sourceLockSha256: attestation.lockSha256, indexSha256: sha256(index),
    routes: entries.map(e => e.url)
  }));
  console.log('Fail-closed search index:', entries.length, 'locked published routes.');
} else if (command === 'audit') {
  const lock = await loadLock();
  const expected = await buildEntries(lock);
  const raw = await fs.readFile(path.join(root, 'search-index.json'), 'utf8');
  const index = JSON.parse(raw);
  if (JSON.stringify(index) !== JSON.stringify(expected)) throw Error('Search output differs from locked published source');
  const attestation = JSON.parse(await fs.readFile('ops/.search-source-attestation.json', 'utf8'));
  const provenance = JSON.parse(await fs.readFile(path.join(root, 'search-provenance.json'), 'utf8'));
  if (attestation.lockSha256 !== sha256(JSON.stringify(lock)) ||
      provenance.sourceLockSha256 !== attestation.lockSha256 ||
      provenance.indexSha256 !== sha256(raw) ||
      JSON.stringify(provenance.routes) !== JSON.stringify(expected.map(e => e.url)))
    throw Error('Search source/build attestation mismatch');
  console.log('Postbuild search privacy PASS: exact 15-route closure, noindex, canonicals and indexed text.');
} else {
  throw Error('Usage: node scripts/search-privacy.mjs test|prebuild|build|audit');
}
