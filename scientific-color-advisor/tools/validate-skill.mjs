import fs from 'node:fs';
import path from 'node:path';

const skillPath = path.resolve('skill');
const skillMdPath = path.join(skillPath, 'SKILL.md');

function fail(message) {
  console.error(message);
  process.exit(1);
}

if (!fs.existsSync(skillMdPath)) {
  fail('SKILL.md not found');
}

const content = fs.readFileSync(skillMdPath, 'utf8');
const match = content.match(/^---\n([\s\S]*?)\n---/);
if (!match) {
  fail('No YAML frontmatter found');
}

const frontmatter = Object.fromEntries(
  match[1]
    .split('\n')
    .filter(Boolean)
    .map((line) => {
      const index = line.indexOf(':');
      return [line.slice(0, index).trim(), line.slice(index + 1).trim()];
    })
);

if (!frontmatter.name || !frontmatter.description) {
  fail('Frontmatter must include name and description');
}

if (!/^[a-z0-9-]+$/.test(frontmatter.name)) {
  fail(`Invalid skill name: ${frontmatter.name}`);
}

if (frontmatter.description.length > 1024) {
  fail('Description is too long');
}

console.log('Skill frontmatter is valid.');
