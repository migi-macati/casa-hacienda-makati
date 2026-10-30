import assert from 'node:assert/strict';
import fs from 'node:fs';
const marker='https://philhistoricsites.nhcp.gov.ph/registry_database/san-pedro-macati/';
const town='https://philhistoricsites.nhcp.gov.ph/registry_database/makati/';
function verify(html){
 assert.ok(html.includes('<meta name="robots" content="noindex,nofollow">'),'noindex missing');
 assert.equal((html.match(/<h1\b/g)||[]).length,1,'homepage H1 drift');
 assert.equal((html.match(/<article class="card"/g)||[]).length,13,'article cards drift');
 const matches=[...html.matchAll(/<section\b[^>]*data-heritage-feature="timeline"[^>]*>([\s\S]*?)<\/section>/g)];
 assert.equal(matches.length,1,'expected one explicit timeline section');
 const section=matches[0][1];
 assert.ok(matches[0][0].includes('aria-labelledby="heritage-timeline-title"'),'timeline lacks accessible name');
 assert.ok(section.includes('id="heritage-timeline-title"'),'timeline heading missing');
 assert.ok(section.includes('does not establish when the surviving structure'),'scope caveat missing');
 assert.ok(section.includes('not original deeds or building plans'),'source-date caveat missing');
 const rows=[...section.matchAll(/<li data-year="(\d{4})">([\s\S]*?)<\/li>/g)];
 assert.deepEqual(rows.map(r=>r[1]),['1607','1608','1620','1768','1769'],'chronology drift');
 assert.ok(rows.every(r=>r[2].includes('class="timeline-source"')),'source missing');
 assert.ok(rows.slice(0,4).every(r=>r[2].includes('https://philhistoricsites.nhcp.gov.ph/registry_database/')),'official marker sources changed');
 assert.ok(rows[4][2].includes('Historian Santiago Lorenzo García') && rows[4][2].includes('Santiago Lorenzo García, <em>La expulsión') && rows[4][2].includes('does not establish when the Makati hacienda changed ownership'),'1769 evidence boundary missing');
 assert.ok(section.includes(marker)&&section.includes(town),'both official markers required');
 assert.ok(!/<(?:img|video|audio|iframe|script|canvas)\b/i.test(section),'unapproved media or scripts');
 assert.ok(!/autoplay|setInterval|animation:/i.test(section),'motion behavior not authorized');
 const hrefs=[...section.matchAll(/href="([^"]+)"/g)].map(x=>x[1]);
 assert.ok(hrefs.every(x=>[marker,town,'https://www.digitaliapublishing.com/a/647/la-expulsion-de-los-jesuitas-de-filipinas','/about/','/cultural-significance/'].includes(x)),'unreviewed timeline link');
 return true;
}
const html=fs.readFileSync('public/index.html','utf8');
verify(html);
const bad=[
 html.replace('noindex,nofollow','index,follow'),
 html.replace('data-heritage-feature="timeline"','data-heritage-feature="other"'),
 html.replace('data-year="1608"','data-year="1609"'),
 html.replace('does not establish when the surviving structure','establishes when the surviving structure'),
 html.replace('not original deeds or building plans','original deeds and building plans'),
 html.replace(marker,'https://example.invalid/unverified/'),
 html.replace('1607 · Buenavista donation','1607 · Buenavista donation<img src="/unapproved.jpg" alt=""/>'),
 html.replace('aria-labelledby="heritage-timeline-title"',''),
 html.replace('data-year="1769"','data-year="1773"'),
 html.replace('does not establish when the Makati hacienda changed ownership','establishes when the Makati hacienda changed ownership'),
 html.replace('Santiago Lorenzo García','Unverified author')
];
for(const variant of bad)assert.throws(()=>verify(variant));
console.log('Evidence-led timeline: 5 sourced milestones, 11 fail-closed regressions PASS.');
