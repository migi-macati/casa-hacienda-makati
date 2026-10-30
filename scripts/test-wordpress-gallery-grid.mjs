import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';

const css=readFileSync('public/assets/style.css','utf8');
const lock=JSON.parse(readFileSync('ops/published-search-sources.json','utf8'));
const blob=text=>{const bytes=Buffer.from(text);return createHash('sha1').update('blob '+bytes.length).update(Buffer.from([0])).update(bytes).digest('hex')};
assert.equal(blob(css),lock.stylesheetGitBlob,'reviewed CSS lock');
assert.equal(lock.documents.length,15,'published WordPress source closure');
const galleries=[
  ['2023/08/12/cultural-significance-no-1/index.html',3,'columns-default'],
  ['2023/10/21/history-of-barrio-olimpia-makati-rizal/index.html',7,'columns-4']
];
for(const [file,count,columns] of galleries){
  const doc=lock.documents.find(x=>x.file===file);
  assert.ok(doc && doc.type==='article','published route pinned');
  const html=readFileSync('public/'+file,'utf8');
  assert.ok(html.includes('<meta name="robots" content="noindex,nofollow">'));
  assert.equal((html.match(/wp-block-gallery has-nested-images/g)||[]).length,1);
  assert.ok(html.includes(columns),'original column count');
  const region=html.split('class="wp-block-gallery has-nested-images')[1]?.split('</article>')[0]||'';
  assert.equal((region.match(/<figure class="wp-block-image/g)||[]).length,count,'original gallery figure count');
  assert.equal((region.match(/<img /g)||[]).length,count,'original gallery image count');
}
const marker="/* Published Gutenberg nested galleries: keep the existing ten scans readable in source order. */";
const rule=".content .wp-block-gallery.has-nested-images{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;align-items:start}\n.content .wp-block-gallery.has-nested-images.columns-4{grid-template-columns:repeat(4,minmax(0,1fr))}\n.content .wp-block-gallery.has-nested-images>figure.wp-block-image{display:block;min-width:0;margin:0}\n.content .wp-block-gallery.has-nested-images>figure.wp-block-image>a,.content .wp-block-gallery.has-nested-images>figure.wp-block-image>.chm-gallery-trigger{display:block;width:100%}\n.content .wp-block-gallery.has-nested-images>figure.wp-block-image img{display:block;width:100%;max-width:100%;height:auto;object-fit:contain}\n@media(max-width:710px){.content .wp-block-gallery.has-nested-images,.content .wp-block-gallery.has-nested-images.columns-4{grid-template-columns:repeat(2,minmax(0,1fr))}}\n@media(max-width:350px){.content .wp-block-gallery.has-nested-images,.content .wp-block-gallery.has-nested-images.columns-4{grid-template-columns:minmax(0,1fr)}}";
function validate(candidate){
  assert.equal(candidate.split(marker).length,2,'one gallery CSS section');
  const after=candidate.split(marker)[1];
  const next=after.indexOf('\n\n/*');
  assert.equal((next<0?after:after.slice(0,next)).trim(),rule,'exact source-preserving gallery CSS');
  assert.ok(!candidate.includes('@import'),'no remote CSS');
}
validate(css);
const mutations=[
 ['display:grid','display:none'],['repeat(3,minmax(0,1fr))','repeat(1,minmax(0,1fr))'],
 ['repeat(4,minmax(0,1fr))','repeat(7,minmax(0,1fr))'],
 ['gap:12px','gap:0'],['min-width:0','min-width:600px'],
 ['margin:0','margin:2rem'],['display:block;width:100%','display:none;width:100%'],
 ['max-width:100%','max-width:200vw'],['object-fit:contain','object-fit:cover'],
 ['max-width:710px','max-width:210px'],['repeat(2,minmax(0,1fr))','repeat(4,minmax(0,1fr))'],
 ['max-width:350px','max-width:250px'],['grid-template-columns:minmax(0,1fr)','grid-template-columns:repeat(4,minmax(0,1fr))']
];
for(const [before,after] of mutations){
 assert.ok(rule.includes(before),'missing mutation fixture '+before);
 const altered=css.replace(rule,rule.replace(before,after));
 assert.notEqual(altered,css);
 assert.throws(()=>validate(altered),'gallery mutation must fail '+before);
}
assert.throws(()=>validate(css+'\n'+marker+'\n'+rule),'duplicate section');
console.log('Published Gutenberg galleries: 2 original galleries, 10 images, 13 fail-closed mutations PASS.');
