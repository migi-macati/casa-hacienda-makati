import assert from 'node:assert/strict';
import fs from 'node:fs';
const html = fs.readFileSync('public/index.html','utf8');
const extract = input => {
  const start = input.indexOf('<section class="wrap" id="heritage-people"');
  const end = input.indexOf('</section>', start);
  if (start < 0 || end < 0) throw Error('Missing people section');
  return input.slice(start,end+10);
};
function validate(input) {
  if (!input.includes('<meta name="robots" content="noindex,nofollow">')) throw Error('Noindex lost');
  const region = extract(input);
  if (!region.includes('data-heritage-feature="people" aria-labelledby="heritage-people-title"') ||
      !region.includes('<h2 id="heritage-people-title">People named in the historical records</h2>'))
    throw Error('Accessible named section changed');
  const ids = [...region.matchAll(/<li data-person-id="([^"]+)">/g)].map(x=>x[1]);
  if (JSON.stringify(ids)!==JSON.stringify(['pedro-de-brito','pedro-p-roxas','julia-tuason']))
    throw Error('Unexpected people identities');
  const hrefs = [...region.matchAll(/<a href="([^"]+)"/g)].map(x=>x[1]);
  const expected = [
    'https://philhistoricsites.nhcp.gov.ph/registry_database/san-pedro-macati/',
    'https://www.chanrobles.com/scdecisions/jurisprudence1907/dec1907/gr_l-3788_1907.php',
    'https://lawyerly.ph/juris/view/c15f'
  ];
  if (JSON.stringify(hrefs)!==JSON.stringify(expected)) throw Error('Source URL allowlist changed');
  for(const s of ['1937','1607','February 19, 1906','1907 Supreme Court','parcel C',
    '8,430-square-meter','includes appurtenances','boundary of parcel C',
    'not a building-construction date','not the house\'s footprint',
    'third-party transcriptions','official report scan and 1906 parcel plan have not been inspected',
    'no portraits or archival images are reproduced']) {
    if(!region.includes(s)) throw Error('Missing evidence qualification: '+s);
  }
  if (/<(?:img|video|audio|iframe|script|picture|source)\b/i.test(region)) throw Error('Unauthorized embedded content');
  if ((input.match(/data-heritage-feature="people"/g)||[]).length!==1) throw Error('Duplicate people feature');
}
validate(html);
const mutations = [
  [html.replace('noindex,nofollow','index,follow'),'noindex'],
  [html.replace('data-heritage-feature="people"','data-heritage-feature="events"'),'marker'],
  [html.replace('aria-labelledby="heritage-people-title"','aria-label=""'),'accessible label'],
  [html.replace('data-person-id="julia-tuason"','data-person-id="unknown"'),'identity'],
  [html.replace('February 19, 1906','February 19, 1907'),'event date'],
  [html.replace('includes appurtenances','is the house footprint'),'area interpretation'],
  [html.replace('not a building-construction date','a building-construction date'),'date qualification'],
  [html.replace('not the house\'s footprint','the house\'s footprint'),'footprint qualification'],
  [html.replace('official report scan and 1906 parcel plan have not been inspected','official report scan has been verified'),'source access'],
  [html.replace('https://lawyerly.ph/juris/view/c15f','https://example.invalid/c15f'),'source allowlist'],
  [html.replace('https://philhistoricsites.nhcp.gov.ph/registry_database/san-pedro-macati/','https://philhistoricsites.nhcp.gov.ph.evil.test/registry_database/san-pedro-macati/'),'host allowlist'],
  [html.replace('no portraits or archival images are reproduced','<img src="/media/unknown.webp"> no portraits or archival images are reproduced'),'embedded media']
];
for (const [candidate, label] of mutations) {
  assert.notEqual(candidate,html,'Mutation missing: '+label);
  assert.throws(()=>validate(candidate),undefined,label);
}
console.log('People feature: 3 source-grounded records and 12 fail-closed mutations PASS.');
