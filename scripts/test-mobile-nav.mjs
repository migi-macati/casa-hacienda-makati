import assert from 'node:assert/strict';
import {transform} from './enhance-mobile-navigation.mjs';
const links='<a href="/">Home</a><a href="/about/">About</a><a href="/cultural-significance/">Significance</a><a href="/#archive">Research</a><a href="https://facebook.com/casahaciendamakati">Facebook</a>';
const base='<meta name="robots" content="noindex,nofollow"><header class="siteheader"><div class="headrow"><a class="brand">Casa</a><nav>'+links+'</nav></div></header><main><h1>Public</h1></main>';
const result=transform(base);
assert.match(result,/<details class="mobile-nav"><summary>Menu<\/summary>/);
assert.match(result,/<nav class="desktop-nav" aria-label="Primary">/);
assert.equal(transform(result),result);
assert.equal((result.match(/<a href="\/"/g)||[]).length,2);
assert.ok(result.includes('<main id="main-content" tabindex="-1"><h1>Public</h1></main>'));
assert.equal((result.match(/class="skip-link"/g)||[]).length,1);
assert.ok(result.indexOf('class="skip-link"') < result.indexOf('class="siteheader"'));
assert.match(result,/<a class="skip-link" href="#main-content">Skip to main content<\/a>/);
for(const bad of [
base.replace('noindex,nofollow','index,follow'),
base.replace('<main>','<div>'),
base.replace('<main>','<main id="main-content">'),
base.replace('<main>','<main></main><main>'),
base.replace('<nav>','<nav aria-label="old">'),
base.replace('href="/about/"','href="/private/"'),
base.replace('href="/#archive"','href="/draft/"'),
base.replace('</header>','</header><header class="siteheader"><div class="headrow"><nav>'+links+'</nav></div></header>')
])assert.throws(()=>transform(bad));
for(const bad of [
 result.replace('href="#main-content"','href="#wrong"'),
 result.replace('tabindex="-1"','tabindex="0"'),
 result.replace('class="skip-link"','class="skip-hidden"')
])assert.throws(()=>transform(bad));
console.log('Native mobile nav synthetic tests PASS.');
