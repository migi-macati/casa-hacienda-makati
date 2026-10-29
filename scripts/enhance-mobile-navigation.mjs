import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root=path.resolve('public');
const header=/<header class="siteheader"><div class="headrow">([\s\S]*?)<nav>([\s\S]*?)<\/nav><\/div><\/header>/g;
export function transform(html,file='fixture'){
 if(!html.includes('<meta name="robots" content="noindex,nofollow">'))throw Error('Missing noindex: '+file);
 if(html.includes('class="mobile-nav"')){
  if((html.match(/class="mobile-nav"/g)||[]).length!==1||
    !html.includes('<nav class="desktop-nav" aria-label="Primary">')||
    (html.match(/class="skip-link"/g)||[]).length!==1||
    !html.includes('<a class="skip-link" href="#main-content">Skip to main content</a>')||
    !html.includes('<main id="main-content" tabindex="-1">'))
    throw Error('Invalid prior enhancement: '+file);
  return html;
 }
 if((html.match(/<main>/g)||[]).length!==1||
    html.includes('id="main-content"')||html.includes('class="skip-link"'))
   throw Error('Missing or ambiguous main landmark: '+file);
 let count=0;
 const result=html.replace(header,(_all,before,links)=>{
  count++;
  if((links.match(/<a\s/g)||[]).length!==5||
    !['href="/"','href="/about/"','href="/cultural-significance/"','href="/#archive"','href="https://facebook.com/casahaciendamakati"'].every(s=>links.includes(s)))
    throw Error('Unexpected navigation: '+file);
  return '<header class="siteheader"><div class="headrow">'+before+
   '<nav class="desktop-nav" aria-label="Primary">'+links+'</nav>'+
   '<details class="mobile-nav"><summary>Menu</summary><nav aria-label="Mobile">'+links+'</nav></details></div></header>';
 });
 if(count!==1)throw Error('Missing or duplicate header: '+file);
 return result
  .replace('<header class="siteheader">','<a class="skip-link" href="#main-content">Skip to main content</a><header class="siteheader">')
  .replace('<main>','<main id="main-content" tabindex="-1">');
}
export async function enhance(){
 const lock=JSON.parse(await fs.readFile('ops/published-search-sources.json','utf8'));
 if(!Array.isArray(lock.documents)||lock.documents.length!==15)throw Error('Published route lock mismatch');
 const files=['index.html','404.html',...lock.documents.map(d=>d.file)];
 if(new Set(files).size!==17)throw Error('Duplicate navigation route');
 const pending=[];
 for(const file of files){const full=path.join(root,file);pending.push([full,transform(await fs.readFile(full,'utf8'),file)]);}
 for(const [file,html] of pending)await fs.writeFile(file,html);
 console.log('Native mobile navigation enhanced 17 public routes.');
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))await enhance();
