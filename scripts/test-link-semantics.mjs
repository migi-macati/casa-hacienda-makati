import assert from 'node:assert/strict';
import { assertLinkSemantics } from './link-semantics.mjs';
const good = [
  '<a href="/about/">About</a>',
  '<a href="#source">Source</a>',
  '<a href="https://example.org" target="_blank" rel="noopener noreferrer">Source</a>',
  '<a href="mailto:archive@example.org">Contact</a>'
];
for (const tag of good) assert.doesNotThrow(() => assertLinkSemantics(tag));
const bad = [
  '<a>Inert label</a>',
  '<a href="">Empty</a>',
  '<a href="javascript:alert(1)">Script</a>',
  '<a href="data:text/html,x">Data</a>',
  '<a href="https://example.org" target="_blank">Missing rel</a>',
  '<a href="https://example.org" target="_blank" rel="noopener">Missing noreferrer</a>'
];
for (const tag of bad) assert.throws(() => assertLinkSemantics(tag));
console.log('Link semantics synthetic checks PASS: 10/10');
