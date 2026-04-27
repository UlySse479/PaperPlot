#!/usr/bin/env node
import { fileURLToPath } from 'node:url';
import { buildExportBundle, doctor, recommendPalettes } from '../vendor/scientific-color-lab-core/core.mjs';

export function parseArgs(argv) {
  const [subcommand, ...rest] = argv;
  const result = { subcommand, flags: {}, lists: {} };

  for (let index = 0; index < rest.length; index += 1) {
    const token = rest[index];
    if (!token.startsWith('--')) {
      continue;
    }

    const key = token.slice(2);
    const next = rest[index + 1];
    if (next == null || next.startsWith('--')) {
      result.flags[key] = true;
      continue;
    }

    if (key === 'priority' || key === 'source-color' || key === 'format') {
      result.lists[key] ??= [];
      result.lists[key].push(next);
    } else {
      result.flags[key] = next;
    }
    index += 1;
  }

  return result;
}

export function toRequest(parsed) {
  if (parsed.flags['request-json']) {
    return JSON.parse(parsed.flags['request-json']);
  }

  return {
    protocol_version: 1,
    target: parsed.flags.target,
    chart_type: parsed.flags['chart-type'],
    palette_class: parsed.flags['palette-class'],
    usage: parsed.flags.usage,
    background: parsed.flags.background,
    tone: parsed.flags.tone,
    series_count: parsed.flags['series-count'],
    priorities: parsed.lists.priority || [],
    source_colors: parsed.lists['source-color'] || [],
    output: parsed.flags.output || 'human'
  };
}

export function formatRecommendationHuman(bundle) {
  const chosen = bundle.chosen;
  const lines = [
    `Runtime mode: ${bundle.runtime.runtime_mode}`,
    `Recommended template: ${chosen.template.name} (${chosen.template.id})`,
    `Score: ${chosen.score}`,
    `Diagnostics: ${chosen.diagnostics.summary}`,
    '',
    'Why it fits:'
  ];

  chosen.why.forEach((reason, index) => {
    lines.push(`${index + 1}. ${reason}`);
  });

  lines.push('', 'HEX palette:');
  chosen.palette.hexes.forEach((hex, index) => {
    lines.push(`${index + 1}. ${hex}`);
  });

  if (chosen.diagnostics.quickFixes.length) {
    lines.push('', `Quick fixes: ${chosen.diagnostics.quickFixes.join(', ')}`);
  }

  if (chosen.ppt_pack) {
    lines.push('', 'PPT pack:');
    lines.push(`Title color: ${chosen.ppt_pack.title_color}`);
    lines.push(`Body text color: ${chosen.ppt_pack.body_text_color}`);
    lines.push(`Accent colors: ${chosen.ppt_pack.accent_colors.join(', ')}`);
  }

  return lines.join('\n');
}

export function formatExportHuman(bundle, formats) {
  const sections = [
    `Runtime mode: ${bundle.runtime.runtime_mode}`,
    `Selected template: ${bundle.chosen.template.name} (${bundle.chosen.template.id})`,
    ''
  ];

  formats.forEach((format) => {
    const key = format === 'ppt-pack' ? 'ppt_pack' : format;
    const payload = key === 'ppt_pack' ? JSON.stringify(bundle.ppt_pack, null, 2) : bundle.exports[key];
    sections.push(`=== ${format} ===`);
    sections.push(payload || `No payload available for ${format}`);
    sections.push('');
  });

  return sections.join('\n');
}

export function runCli(argv, io = { stdout: console.log, stderr: console.error }) {
  const parsed = parseArgs(argv);
  const options = {
    repoPath: parsed.flags.repo
  };

  try {
    switch (parsed.subcommand) {
      case 'recommend': {
        const bundle = recommendPalettes(toRequest(parsed), options);
        if (bundle.request.output === 'json') {
          io.stdout(JSON.stringify(bundle, null, 2));
        } else {
          io.stdout(formatRecommendationHuman(bundle));
        }
        return 0;
      }
      case 'export': {
        const bundle = buildExportBundle(toRequest(parsed), options);
        const formats = parsed.lists.format?.length ? parsed.lists.format.flatMap((entry) => `${entry}`.split(',').map((item) => item.trim()).filter(Boolean)) : ['summary'];
        if (bundle.request.output === 'json') {
          io.stdout(JSON.stringify({
            request: bundle.request,
            runtime: bundle.runtime,
            chosen: bundle.chosen,
            exports: Object.fromEntries(formats.map((format) => [format, format === 'ppt-pack' ? bundle.ppt_pack : bundle.exports[format]]))
          }, null, 2));
        } else {
          io.stdout(formatExportHuman(bundle, formats));
        }
        return 0;
      }
      case 'doctor': {
        const report = doctor(options);
        io.stdout(JSON.stringify(report, null, 2));
        return 0;
      }
      default:
        io.stderr('Usage: node scripts/scientific-color-cli.mjs <recommend|export|doctor> [flags]');
        return 64;
    }
  } catch (error) {
    io.stderr(error instanceof Error ? error.message : String(error));
    return 2;
  }
}

export function isDirectExecution(metaUrl, argv1) {
  return Boolean(argv1) && fileURLToPath(metaUrl) === argv1;
}

function main() {
  const code = runCli(process.argv.slice(2));
  if (code !== 0) {
    process.exit(code);
  }
}

if (isDirectExecution(import.meta.url, process.argv[1])) {
  main();
}
