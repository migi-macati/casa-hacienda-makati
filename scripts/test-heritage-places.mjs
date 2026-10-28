import assert from 'node:assert/strict';
import fs from 'node:fs';
const original='/2023/08/12/cultural-significance-no-3/';
const independent='https://bluprint-onemega.com/architecture/heritage/poblacion-heritage-district/';
function verify(html){
 assert.ok(html.includes('<meta name="robots" content="noindex,nofollow">'),'noindex missing');
 assert.equal((html.match(/<h1\\b/g)||[]).length,1,'homepage H1 drift');
 assert.equal((html.match(/<article class="card"/g)||[]).length,13,'published cards drift');
 const matches=[...html.matchAll(/<section\\b[^>]*data-heritage-feature="places"[^>]*>([\\s\\S]*?)<\\/section>/g)];
 assert.equal(matches.length,1,'one places section required');
 const full=matches[0][0],section=matches[0][1];
 assert.ok(full.includes('aria-labelledby="heritage-places-title"')&&section.includes('id="heritage-places-title"'),'named region missing');
 const ids=[...section.matchAll(/<li data-place-id="([^"]+)">/g)].map(x=>x[1]);
 assert.deepEqual(ids,['olympia-claim','poblacion-account'],'two distinct claims required');
 assert.ok(section.includes('9126 Sultana Street, Barangay Olympia'),'original site claim missing');
 assert.ok(section.includes('expressly distinguishes this location'),'original two-site distinction missing');
 assert.ok(section.includes('now Poblacion Park'),'Poblacion account missing');
 assert.ok(section.includes('Independent secondary account'),'evidence tier missing');
 assert.ok(section.includes('have not yet been independently verified against this parcel'),'Olympia uncertainty missing');
 assert.ok(section.includes('cannot establish that the surviving Olympia remains and the former Poblacion offices are the same building'),'continuity caveat missing');
 assert.ok(section.includes('not a verified parcel-level identification'),'parcel certainty caveat missing');
 assert.ok(section.includes('reproduction rights remain unverified'),'rights boundary missing');
 assert.ok(section.includes('No historical photograph, map image or location overlay is reproduced here'),'media boundary missing');
 const hrefs=[...section.matchAll(/href="([^"]+)"/g)].map(x=>x[1]);
 assert.deepEqual(hrefs,[original,independent,'/about/'],'source link allowlist drift');
 assert.ok(!/<(?:img|video|audio|iframe|script|canvas|object|embed)\\b/i.test(section),'unapproved media or scripts');
 assert.ok(!/autoplay|setInterval|animation:/i.test(section),'motion not authorized');
 return true;
}
const html=fs.readFileSync('public/index.html','utf8');
verify(html);
const variants=[
 html.replace('noindex,nofollow','index,follow'),
 html.replace('data-heritage-feature="places"','data-heritage-feature="other"'),
 html.replace('aria-labelledby="heritage-places-title"',''),
 html.replace('data-place-id="poblacion-account"','data-place-id="olympia-claim"'),
 html.replace('expressly distinguishes this location','equates this location'),
 html.replace('Independent secondary account','Verified original deed'),
 html.replace('have not yet been independently verified against this parcel','prove this parcel'),
 html.replace('cannot establish that the surviving Olympia remains and the former Poblacion offices are the same building','proves that both are the same building'),
 html.replace('not a verified parcel-level identification','a verified parcel-level identification'),
 html.replace(independent,'https://example.invalid/unverified'),
 html.replace('No historical photograph, map image or location overlay is reproduced here','<img src="/unapproved-photo.jpg" alt="photo">')
];
for(const variant of variants)assert.throws(()=>verify(variant));
console.log('Two-location research guide: 2 claims, 11 fail-closed regressions PASS.');
