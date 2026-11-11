import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const root = fileURLToPath(new URL('../site/', import.meta.url));
let count = 0;
async function visit(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const filename = path.join(directory, entry.name);
    if (entry.isDirectory()) { await visit(filename); continue; }
    if (!entry.name.endsWith('.html')) continue;
    const html = await readFile(filename, 'utf8');
    let ordinal = 0;
    for (const [, attrs, code] of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script\s*>/gi)) {
      ordinal++;
      if (/\bsrc\s*=/i.test(attrs) || /\btype\s*=\s*["']application\/(?:ld\+)?json["']/i.test(attrs)) continue;
      if (/\btype\s*=\s*["']module["']/i.test(attrs)) throw Error(`Module parser required: ${filename}`);
      new vm.Script(code, { filename: `${path.relative(root, filename)}#script-${ordinal}` });
      count++;
    }
  }
}
await visit(root);
console.log(JSON.stringify({status: 'pass', node: process.version, inline_scripts_parsed: count, executed: false}));
