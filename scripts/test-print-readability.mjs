import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';

const css=readFileSync('public/assets/style.css','utf8');
const lock=JSON.parse(readFileSync('ops/published-search-sources.json','utf8'));
const gitBlob=s=>{const b=Buffer.from(s);return createHash('sha1').update('blob '+b.length).update(Buffer.from([0])).update(b).digest('hex');};
assert.equal(lock.documents.length,15);
assert.equal(lock.documents.filter(x=>x.type==='article').length,13);
assert.equal(lock.documents.filter(x=>x.type==='page').length,2);
assert.equal(gitBlob(css),lock.stylesheetGitBlob,'stylesheet pinned');
for(const doc of lock.documents){
  const html=readFileSync('public/'+doc.file,'utf8');
  assert.equal(gitBlob(html),doc.gitBlob,'original source pinned: '+doc.file);
  assert.ok(html.includes('<meta name="robots" content="noindex,nofollow">'));
}
const marker='/* Print-only archival reading: preserve original published text, source links and scans. */';
const required=[
 '@media print{','@page{margin:16mm}',
 'body{background:#fff!important;color:#111!important;font:11pt/1.5 Georgia,serif}',
 '.notice,.siteheader,.skip-link,.sidebar,footer,.research-jump,.comment-bridge{display:none!important}',
 '.layout{display:block;max-width:none;padding:0}',
 '.content{font-size:11pt;line-height:1.5;overflow:visible;overflow-wrap:anywhere}',
 '.content h1,.content h2,.content h3{break-after:avoid}',
 '.content p,.content li{orphans:3;widows:3}',
 '.content img{max-width:100%!important;height:auto!important;object-fit:contain}',
 '.content .wp-block-spacer{display:none!important}',
 '.content .wp-block-column{display:block;width:auto!important;min-width:0!important;padding:0!important}',
 '.content .wp-block-gallery.has-nested-images{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}',
 '.content .wp-block-table.is-style-stripes{overflow:visible}',
 '.content .wp-block-table.is-style-stripes table{min-width:0;width:100%}',
 '.content .wp-block-group.has-accent-background-color.has-background{overflow:visible;background:#fff!important;border:1px solid #777}',
 '.content .wp-block-button__link{background:#fff!important;color:#111!important;border:1px solid #777}',
 '.content a{color:#111!important;text-decoration:underline}',
 '.original{background:#fff!important;border-top:1px solid #777}'
];
function validate(candidate){
  assert.equal(candidate.split(marker).length,2,'exactly one print section');
  const section=candidate.split(marker)[1];
  assert.equal(section.trim().slice(-1),'}','print block closed');
  for(const rule of required)assert.ok(section.includes(rule),'missing print rule: '+rule);
  assert.ok(!section.includes('@import'),'no remote styles');
  assert.ok(!section.includes('url('),'no print tracking');
  assert.ok(!section.includes('.content{display:none'),'published text must remain visible');
}
validate(css);
const changes=[
 [required[0],'@media screen{'],
 [required[1],'@page{margin:0}'],
 [required[2],required[2].replace('11pt','5pt')],
 [required[3],required[3].replace('.sidebar','article.content')],
 [required[4],required[4].replace('display:block','display:none')],
 [required[5],required[5].replace('overflow:visible','overflow:hidden')],
 [required[6],required[6].replace('break-after:avoid','break-after:always')],
 [required[7],required[7].replace('orphans:3','orphans:1')],
 [required[8],required[8].replace('max-width:100%','max-width:300%')],
 [required[9],required[9].replace('.wp-block-spacer','.wp-block-group')],
 [required[10],required[10].replace('padding:0!important','padding:80px!important')],
 [required[11],required[11].replace('repeat(2','repeat(5')],
 [required[12],required[12].replace('overflow:visible','overflow:hidden')],
 [required[13],required[13].replace('min-width:0','min-width:600px')],
 [required[14],required[14].replace('background:#fff','background:#000')],
 [required[15],required[15].replace('color:#111','color:transparent')],
 [required[16],required[16].replace('text-decoration:underline','text-decoration:none')],
 [required[17],required[17].replace('border-top:1px','border-top:0px')]
];
for(const [before,after] of changes){
  assert.ok(css.includes(before) && before!==after,'mutation fixture');
  assert.throws(()=>validate(css.replace(before,after)),'print mutation must fail closed: '+before);
}
console.log('Print-only archival reading PASS: 15 pinned sources and '+changes.length+' negative mutations.');
