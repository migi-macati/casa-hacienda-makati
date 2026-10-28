import assert from 'node:assert/strict';
import {transform} from './enhance-mobile-navigation.mjs';
const links='<a href="/">Home</a><a href="/about/">About</a><a href="/cultural-significance/">Significance</a><a href="/#archive">Research</a><a href="https://facebook.com/casahaciendamakati">Facebook</a>';
const base='<meta name="robots" content="noindex,nofollow"><header class="siteheader"><div class="headrow"><a class="brand">Casa</a><nav>'+links+'</nav></div></header><main><h1>Public</h1></main>';
const result=transform(base);
assert.match(result,/<details class="mobile-nav"><summary>Menu<\/summary>/);
assert.match(result,/<nav class="desktop-nav" aria-label="Primary">/);
assert.equal(transform(result),result);
assert.equal((result.match(/<a href="\/"/g)||[]).length,2);
assert.ok(result.includes('<main><h1>Public</h1></main>'));
for(const bad of [
base.replace('noindex,nofollow','index,follow'),
base.replace('<nav>','<nav aria-label="old">'),
base.replace('href="/about/"','href="/private/"'),
base.replace('href="/#archive"','href="/draft/"'),
base.replace('</header>','</header><header class="siteheader"><div class="headrow"><nav>'+links+'</nav></div></header>')
])assert.throws(()=>transform(bad));
console.log('Native mobile nav synthetic tests PASS.');
