import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { execFileSync } from 'node:child_process';

const repoArg = process.argv[2];
const commitArg = process.argv[3] || process.env.SCIENTIFIC_COLOR_LAB_COMMIT;
const defaultRepo = process.env.SCIENTIFIC_COLOR_LAB_REPO || path.resolve('..', 'Scientific-Color-Lab');
const repoPath = path.resolve(repoArg || defaultRepo);
const catalogTsPath = path.join(repoPath, 'src', 'data', 'templates', 'catalog.ts');
const outputDir = path.resolve('skill', 'vendor', 'scientific-color-lab-core');

function readSeeds(filePath) {
  const source = fs.readFileSync(filePath, 'utf8');
  const match = source.match(/const seeds: TemplateSeed\[\] = (\[[\s\S]*?\n\]);/);
  if (!match) {
    throw new Error(`Unable to extract template seeds from ${filePath}`);
  }

  return vm.runInNewContext(`(${match[1]})`, {}, { timeout: 1000 });
}

function variant(seed, backgroundMode) {
  return {
    ...seed,
    id: `${seed.id}-${backgroundMode}`,
    name: backgroundMode === 'dark' ? `${seed.name} Dark` : seed.name,
    description:
      backgroundMode === 'dark'
        ? `${seed.description} Adapted for darker surrounding UI and presentation backgrounds.`
        : seed.description,
    backgroundMode,
    tags: [...seed.tags, backgroundMode]
  };
}

function buildCatalog(repoCatalogTsPath) {
  const seeds = readSeeds(repoCatalogTsPath);
  return seeds.flatMap((seed) => [variant(seed, 'light'), variant(seed, 'dark')]);
}

function readGitCommit(repoDir) {
  try {
    const safeDir = repoDir.replace(/\\/g, '/');
    return execFileSync('git', ['-c', `safe.directory=${safeDir}`, '-C', repoDir, 'rev-parse', 'HEAD'], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore']
    }).trim();
  } catch {
    return 'unknown';
  }
}

fs.mkdirSync(outputDir, { recursive: true });
const catalog = buildCatalog(catalogTsPath);
const metadata = {
  upstream_repo: 'https://github.com/groele/Scientific-Color-Lab',
  upstream_commit: commitArg || readGitCommit(repoPath),
  synced_at: new Date().toISOString(),
  source_files: ['src/data/templates/catalog.ts', 'src/domain/diagnostics/engine.ts', 'src/domain/export/service.ts'],
  template_count: catalog.length
};

fs.writeFileSync(path.join(outputDir, 'catalog.json'), `${JSON.stringify(catalog, null, 2)}\n`);
fs.writeFileSync(path.join(outputDir, 'metadata.json'), `${JSON.stringify(metadata, null, 2)}\n`);

console.log(`Synced ${catalog.length} templates from ${repoPath}`);
