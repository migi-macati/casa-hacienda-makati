import assert from 'node:assert/strict';
import fs from 'node:fs';
const html = fs.readFileSync('public/index.html','utf8');
function extract(input) {
  const start = input.indexOf('<section class="wrap" id="heritage-events"');
  const end = input.indexOf('</section>',start);
  if(start<0 || end<0) throw Error('Missing events section');
  return input.slice(start,end+10);
}
function validate(input) {
  if(!input.includes('<meta name="robots" content="noindex,nofollow">')) throw Error('Noindex lost');
  const region=extract(input);
  if(!region.includes('data-heritage-feature="events" aria-labelledby="heritage-events-title"') ||
     !region.includes('<h2 id="heritage-events-title">Events in the estate\'s legal record</h2>')) throw Error('Accessible events region changed');
  const ids=[...region.matchAll(/<li data-event-id="([^"]+)">/g)].map(x=>x[1]);
  assert.deepEqual(ids,['1906-registration-application','1907-court-decision']);
  const hrefs=[...region.matchAll(/<a href="([^"]+)"/g)].map(x=>x[1]);
  assert.deepEqual(hrefs,['https://www.chanrobles.com/scdecisions/jurisprudence1907/dec1907/gr_l-3788_1907.php','https://lawyerly.ph/juris/view/c15f']);
  for(const term of ['February 19, 1906','December 21, 1907','G.R. No. L-3788','9 Phil. 408','parcels A through D','An application is not proof','a deed was executed','parcel C','not a building-construction record','includes appurtenances','not the house\'s footprint','third-party transcriptions','official 1907 report scan and original 1906 parcel plan have not been inspected','do not establish a completed land transfer','No archival image or map is reproduced']) {
    if(!region.includes(term)) throw Error('Missing source or limit: '+term);
  }
  if(/<(?:img|video|audio|iframe|script|picture|source)\b/i.test(region)) throw Error('Embedded media prohibited');
  if((input.match(/data-heritage-feature="events"/g)||[]).length!==1) throw Error('Duplicate events section');
}
validate(html);
const original=extract(html);
const changed=(from,to)=>html.replace(original,original.replace(from,to));
const mutations=[
 [html.replace('noindex,nofollow','index,follow'),'privacy'],
 [changed('data-heritage-feature="events"','data-heritage-feature="event"'),'feature marker'],
 [changed('aria-labelledby="heritage-events-title"','aria-label=""'),'accessible name'],
 [changed('data-event-id="1906-registration-application"','data-event-id="1905-registration-application"'),'event identity'],
 [changed('February 19, 1906','February 19, 1905'),'1906 date'],
 [changed('December 21, 1907','December 21, 1908'),'1907 date'],
 [changed('An application is not proof','An application is proof'),'application limit'],
 [changed('includes appurtenances','is a footprint'),'area limit'],
 [changed('official 1907 report scan and original 1906 parcel plan have not been inspected','official 1907 report scan has been verified'),'uninspected source'],
 [changed('https://lawyerly.ph/juris/view/c15f','https://example.invalid/c15f'),'source URL'],
 [changed('https://www.chanrobles.com/scdecisions/jurisprudence1907/dec1907/gr_l-3788_1907.php','https://www.chanrobles.com.evil.test/1907'),'host'],
 [changed('No archival image or map is reproduced','<img src="/media/unknown.jpg"> No archival image or map is reproduced'),'embedded image']
];
for(const [candidate,label] of mutations){
  assert.notEqual(candidate,html,'Mutation failed to apply: '+label);
  assert.throws(()=>validate(candidate),undefined,label);
}
console.log('Events feature: two attributed legal events and 12 fail-closed mutations PASS.');
