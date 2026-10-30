import assert from 'node:assert/strict';
import fs from 'node:fs';
const sourceUrls=[
 'https://philhistoricsites.nhcp.gov.ph/registry_database/san-pedro-macati/',
 'https://philhistoricsites.nhcp.gov.ph/registry_database/makati/',
 'https://searcharchives.bl.uk/catalog/040-002027896',
 'https://www.digitaliapublishing.com/a/647/la-expulsion-de-los-jesuitas-de-filipinas'
];
function verify(html){
 assert.ok(html.includes('<meta name="robots" content="noindex,nofollow">'),'noindex missing');
 assert.equal((html.match(/<h1\b/g)||[]).length,1,'H1 drift');
 assert.equal((html.match(/<article class="card"/g)||[]).length,13,'published cards drift');
 const matches=[...html.matchAll(/<section\b[^>]*data-heritage-feature="sources"[^>]*>([\s\S]*?)<\/section>/g)];
 assert.equal(matches.length,1,'one sources section required');
 const section=matches[0][1];
 assert.ok(matches[0][0].includes('aria-labelledby="heritage-sources-title"'),'accessible name missing');
 assert.ok(section.includes('id="heritage-sources-title"'),'heading missing');
 const ids=[...section.matchAll(/<li data-source-id="([^"]+)">/g)].map(x=>x[1]);
 assert.deepEqual(ids,['nhcp-1937','nhcp-1991','bl-1775','ua-1999'],'source inventory drift');
 assert.ok(section.includes('not the original deed'),'marker evidence boundary missing');
 assert.ok(section.includes('a different act from the 1607 donation'),'1607/1608 distinction missing');
 assert.ok(section.includes('The map sheet has not been examined'),'map limitation missing');
 assert.ok(section.includes('does not establish that the Olympia house appears'),'site certainty caveat missing');
 assert.ok(section.includes('No map image is reproduced here'),'rights caveat missing');
 assert.ok(section.includes('the monograph’s full text and original estate records were not examined'),'new source limitation missing');
 assert.ok(section.includes('Santiago Lorenzo García'),'scholarly source identity missing');
 assert.ok(section.includes('Add MS 17641 C')&&section.includes('040-002027896'),'BL catalog identity missing');
 const hrefs=[...section.matchAll(/href="([^"]+)"/g)].map(x=>x[1]);
 assert.deepEqual(hrefs,[...sourceUrls,'/cultural-significance/'],'source link allowlist drift');
 assert.ok(!/<(?:img|video|audio|iframe|script|canvas|object|embed)\b/i.test(section),'unapproved media');
 assert.ok(!/autoplay|setInterval|animation:/i.test(section),'motion not authorized');
 return true;
}
const html=fs.readFileSync('public/index.html','utf8');
verify(html);
const variants=[
 html.replace('noindex,nofollow','index,follow'),
 html.replace('data-heritage-feature="sources"','data-heritage-feature="other"'),
 html.replace('data-source-id="bl-1775"','data-source-id="bl-1800"'),
 html.replace('Add MS 17641 C','Add MS 17641 D'),
 html.replace('The map sheet has not been examined','The map sheet proves the building'),
 html.replace('not the original deed','the original deed'),
 html.replace('does not establish that the Olympia house appears','establishes that the Olympia house appears'),
 html.replace(sourceUrls[2],'https://example.invalid/unverified'),
 html.replace('No map image is reproduced here','<img src="/unapproved-map.jpg" alt="Map">'),
 html.replace('aria-labelledby="heritage-sources-title"',''),
 html.replace('data-source-id="ua-1999"','data-source-id="unverified"'),
 html.replace('the monograph’s full text and original estate records were not examined','the monograph and original estate records were examined'),
 html.replace('The University of Alicante publication by Santiago Lorenzo García','The University of Alicante publication by Unverified author')
];
for(const variant of variants)assert.throws(()=>verify(variant));
console.log('Institutional source register: 4 records, 13 fail-closed regressions PASS.');
