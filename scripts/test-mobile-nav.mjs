import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import {transform} from './enhance-mobile-navigation.mjs';
const links='<a href="/">Home</a><a href="/about/">About</a><a href="/cultural-significance/">Significance</a><a href="/#archive">Research</a><a href="https://facebook.com/casahaciendamakati">Facebook</a>';
const base='<!doctype html><head><meta name="robots" content="noindex,nofollow"></head><body><header class="siteheader"><div class="headrow"><a class="brand">Casa</a><nav>'+links+'</nav></div></header><main><h1>Public</h1></main>';
const result=transform(base);
assert.match(result,/<details class="mobile-nav"><summary>Menu<\/summary>/);
assert.match(result,/<nav class="desktop-nav" aria-label="Primary">/);
assert.equal(transform(result),result);
assert.equal((result.match(/<script defer src="\/assets\/mobile-nav-keyboard\.js"><\/script>/g)||[]).length,1);
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
 result.replace('class="skip-link"','class="skip-hidden"'),
 result.replace('<script defer src="/assets/mobile-nav-keyboard.js"></script>',''),
 result.replace('</head>','<script defer src="/assets/mobile-nav-keyboard.js"></script></head>')
])assert.throws(()=>transform(bad));

const code=readFileSync(new URL('../public/assets/mobile-nav-keyboard.js',import.meta.url),'utf8');
let keydown, modal=false, focused=0, prevented=0;
const summary={focus(options){assert.equal(options.preventScroll,true);focused++;}};
const link={};
const menu={open:true,querySelector(selector){assert.equal(selector,'summary');return summary;},
 contains(node){return node===summary||node===link;}};
const document={
 activeElement:link,
 querySelector(selector){
  if(selector==='details.mobile-nav')return menu;
  if(selector==='dialog:modal')return modal?{}:null;
  throw Error('Unexpected selector: '+selector);
 },
 addEventListener(type,fn){assert.equal(type,'keydown');keydown=fn;}
};
runInNewContext(code,{document});
assert.equal(typeof keydown,'function');
const press=key=>keydown({key,preventDefault(){prevented++;}});
press('ArrowDown');assert.equal(menu.open,true);assert.equal(prevented,0);
modal=true;press('Escape');assert.equal(menu.open,true);assert.equal(prevented,0);
modal=false;document.activeElement={};press('Escape');assert.equal(menu.open,true);
document.activeElement=link;press('Escape');
assert.equal(menu.open,false);assert.equal(prevented,1);assert.equal(focused,1);
press('Escape');assert.equal(prevented,1);
menu.open=true;document.activeElement=summary;press('Escape');
assert.equal(menu.open,false);assert.equal(prevented,2);assert.equal(focused,2);

console.log('Native mobile nav synthetic and shipped-JS Escape runtime tests PASS.');
