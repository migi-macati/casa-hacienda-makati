import assert from 'node:assert/strict';
import fs from 'node:fs/promises';

// Deployment-configuration regression gate, not a live HTTP audit.
// Unlike HTML meta robots, the global response header covers PDFs and images.
function assertPrivateDeployment(config, robots) {
  assert.equal(config.version, 2, 'Expected Vercel v2 configuration');
  assert.ok(Array.isArray(config.headers), 'Missing Vercel response headers');
  const global = config.headers.filter(rule => rule.source === '/(.*)');
  assert.equal(global.length, 1, 'Exactly one global response-header rule required');
  assert.ok(Array.isArray(global[0].headers), 'Missing global response headers');
  const headers = global[0].headers;
  const byName = name => headers.filter(entry =>
    typeof entry.key === 'string' && entry.key.toLowerCase() === name.toLowerCase());
  const xRobots = byName('X-Robots-Tag');
  assert.equal(xRobots.length, 1, 'Exactly one global X-Robots-Tag required');
  const tokens = String(xRobots[0].value).toLowerCase().split(',').map(s => s.trim());
  assert.ok(tokens.includes('noindex') && tokens.includes('nofollow'),
    'Global X-Robots-Tag must prohibit indexing and following');
  assert.ok(!tokens.includes('index') && !tokens.includes('follow'),
    'Global X-Robots-Tag must not contain contradictory indexing directives');
  assert.equal(byName('X-Content-Type-Options').length, 1, 'Preserve nosniff');
  assert.equal(byName('X-Content-Type-Options')[0].value.toLowerCase(), 'nosniff');
  assert.equal(byName('X-Frame-Options').length, 1, 'Preserve frame policy');
  assert.equal(byName('Referrer-Policy').length, 1, 'Preserve referrer policy');
  assert.match(robots, /^User-agent:\s*\*\s*\nDisallow:\s*\/\s*$/m,
    'Preserve original full-site robots.txt disallow policy');
}

const config = JSON.parse(await fs.readFile('vercel.json', 'utf8'));
const robots = await fs.readFile('public/robots.txt', 'utf8');
assertPrivateDeployment(config, robots);
const mutate = fn => { const clone = structuredClone(config); fn(clone); return clone; };
const rejects = [
  mutate(c => { c.headers[0].source = '/articles/(.*)'; }),
  mutate(c => { c.headers[0].headers = c.headers[0].headers.filter(h => h.key !== 'X-Robots-Tag'); }),
  mutate(c => { c.headers[0].headers.find(h => h.key === 'X-Robots-Tag').value = 'index, follow'; }),
  mutate(c => { c.headers[0].headers.find(h => h.key === 'X-Robots-Tag').value = 'noindex'; }),
  mutate(c => { c.headers[0].headers.push({ key: 'x-robots-tag', value: 'index' }); }),
  mutate(c => { c.headers[0].headers.find(h => h.key === 'X-Content-Type-Options').value = 'off'; }),
  mutate(c => { c.headers[0].headers = c.headers[0].headers.filter(h => h.key !== 'Referrer-Policy'); }),
];
for (const [index, broken] of rejects.entries()) {
  assert.throws(() => assertPrivateDeployment(broken, robots), undefined,
    'Unsafe deployment header mutation ' + (index + 1) + ' passed');
}
assert.throws(() => assertPrivateDeployment(config, 'User-agent: *\nAllow: /\n'));
console.log('Deployment privacy header PASS: global PDF/media noindex, existing security headers, robots disallow, 8 fail-closed mutations.');
