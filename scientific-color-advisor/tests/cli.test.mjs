import assert from 'node:assert/strict';
import path from 'node:path';
import { isDirectExecution, runCli } from '../skill/scripts/scientific-color-cli.mjs';

function capture(argv) {
  const chunks = [];
  const errors = [];
  const code = runCli(argv, {
    stdout: (value) => chunks.push(value),
    stderr: (value) => errors.push(value)
  });
  return {
    code,
    stdout: chunks.join('\n'),
    stderr: errors.join('\n')
  };
}

function run(name, fn) {
  try {
    fn();
    console.log(`PASS ${name}`);
  } catch (error) {
    console.error(`FAIL ${name}`);
    throw error;
  }
}

run('CLI recommend emits JSON output', () => {
  const result = capture([
    'recommend',
    '--target', 'scientific-figure',
    '--chart-type', 'scatter-plot',
    '--palette-class', 'qualitative',
    '--usage', 'lab-meeting',
    '--background', 'light',
    '--tone', 'balanced',
    '--output', 'json'
  ]);

  assert.equal(result.code, 0);
  const parsed = JSON.parse(result.stdout);
  assert.equal(parsed.request.chart_type, 'scatter-plot');
  assert.ok(parsed.chosen.template.id);
});

run('CLI export emits human-readable payload blocks', () => {
  const result = capture([
    'export',
    '--target', 'scientific-figure',
    '--chart-type', 'heatmap',
    '--palette-class', 'sequential',
    '--usage', 'poster',
    '--background', 'dark',
    '--tone', 'strong',
    '--format', 'summary',
    '--format', 'css'
  ]);

  assert.equal(result.code, 0);
  assert.ok(result.stdout.includes('=== summary ==='));
  assert.ok(result.stdout.includes('=== css ==='));
});

run('CLI entrypoint detection matches the script path', () => {
  const scriptPath = path.resolve('skill/scripts/scientific-color-cli.mjs');
  const metaUrl = new URL('../skill/scripts/scientific-color-cli.mjs', import.meta.url).href;
  assert.equal(isDirectExecution(metaUrl, scriptPath), true);
});
