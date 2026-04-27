import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildExportBundle, recommendPalettes } from '../skill/vendor/scientific-color-lab-core/core.mjs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, '..');
const outputDir = path.join(repoRoot, 'docs', 'generated');

function escapeXml(value) {
  return `${value}`
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&apos;');
}

function wrapLines(value, maxLength) {
  const words = value.split(' ');
  const lines = [];
  let current = '';

  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (next.length > maxLength && current) {
      lines.push(current);
      current = word;
    } else {
      current = next;
    }
  }

  if (current) {
    lines.push(current);
  }

  return lines;
}

function block(title, x, y, width, height, fill, stroke, titleColor) {
  return [
    `<rect x="${x}" y="${y}" width="${width}" height="${height}" rx="20" fill="${fill}" stroke="${stroke}" />`,
    `<text x="${x + 24}" y="${y + 36}" fill="${titleColor}" font-size="20" font-weight="700">${escapeXml(title)}</text>`
  ].join('\n');
}

function textLines(lines, x, y, color, fontSize = 20, lineHeight = 30, weight = '500', anchor = 'start') {
  return lines.map((line, index) => (
    `<text x="${x}" y="${y + (index * lineHeight)}" fill="${color}" font-size="${fontSize}" font-weight="${weight}" text-anchor="${anchor}">${escapeXml(line)}</text>`
  )).join('\n');
}

function bulletLines(lines, x, y, color) {
  return lines.map((line, index) => {
    const yOffset = y + (index * 32);
    return [
      `<circle cx="${x}" cy="${yOffset - 6}" r="4" fill="#2D6A8A" />`,
      `<text x="${x + 16}" y="${yOffset}" fill="${color}" font-size="20" font-weight="500">${escapeXml(line)}</text>`
    ].join('\n');
  }).join('\n');
}

function paletteSwatches(hexes, x, y, swatchWidth, gap, height) {
  return hexes.map((hex, index) => {
    const xOffset = x + (index * (swatchWidth + gap));
    const darkText = ['#E2E7E7', '#D9D2CA', '#FCFDBF', '#F6F5F1', '#E8E4DE'].includes(hex);
    return [
      `<rect x="${xOffset}" y="${y}" width="${swatchWidth}" height="${height}" rx="18" fill="${hex}" stroke="#D9E2E8" />`,
      `<text x="${xOffset + 14}" y="${y + height - 18}" fill="${darkText ? '#173042' : '#F7FAFC'}" font-size="18" font-weight="700">${hex}</text>`
    ].join('\n');
  }).join('\n');
}

function gradientStops(hexes) {
  return hexes.map((hex, index) => {
    const offset = Math.round((index / Math.max(hexes.length - 1, 1)) * 100);
    return `<stop offset="${offset}%" stop-color="${hex}" />`;
  }).join('\n');
}

function lineExampleSvg(bundle) {
  const hexes = bundle.chosen.palette.hexes;
  const command = 'node skill/scripts/scientific-color-cli.mjs recommend --target scientific-figure --chart-type line-plot --palette-class qualitative --usage manuscript --background light --tone restrained --priority colorblind-safe --priority avoid-red-green';
  const commandLines = wrapLines(command, 110);
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg width="1200" height="820" viewBox="0 0 1200 820" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="1200" height="820" fill="#F4F8FB"/>
  <rect x="32" y="32" width="1136" height="756" rx="28" fill="#EAF2F7"/>
  <text x="72" y="96" fill="#173042" font-size="34" font-weight="800">Scientific Color Advisor</text>
  <text x="72" y="136" fill="#537085" font-size="22" font-weight="500">Fixed snapshot generated from the live manuscript line-plot recommendation.</text>
  ${block('Recommendation', 72, 176, 1056, 270, '#FFFFFF', '#D9E2E8', '#173042')}
  <text x="96" y="238" fill="#173042" font-size="28" font-weight="800">${escapeXml(bundle.chosen.template.name)}</text>
  <text x="96" y="274" fill="#537085" font-size="20" font-weight="500">${escapeXml(bundle.chosen.template.id)}</text>
  <text x="96" y="312" fill="#2D6A8A" font-size="21" font-weight="700">Score ${bundle.chosen.score} | ${escapeXml(bundle.chosen.diagnostics.summary)}</text>
  ${bulletLines(bundle.chosen.why.slice(0, 4), 96, 348, '#38566A')}
  ${block('Palette', 72, 476, 1056, 220, '#FFFFFF', '#D9E2E8', '#173042')}
  ${paletteSwatches(hexes, 96, 530, 188, 14, 84)}
  ${textLines(['Command', ...commandLines], 96, 646, '#537085', 18, 26, '500')}
</svg>`;
}

function heatmapExampleSvg(bundle) {
  const hexes = bundle.chosen.palette.hexes;
  const name = bundle.chosen.template.id.replaceAll('-', '_');
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg width="1200" height="720" viewBox="0 0 1200 720" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="heatmapRamp" x1="0" y1="0" x2="1" y2="0">
      ${gradientStops(hexes)}
    </linearGradient>
  </defs>
  <rect width="1200" height="720" fill="#111827"/>
  <rect x="32" y="32" width="1136" height="656" rx="28" fill="#182433"/>
  <text x="72" y="96" fill="#F8FAFC" font-size="34" font-weight="800">Heatmap Export Snapshot</text>
  <text x="72" y="136" fill="#B7C7D4" font-size="22" font-weight="500">Generated from the current sequential poster-on-dark export bundle.</text>
  ${block('Selected Template', 72, 176, 1056, 120, '#223447', '#314A61', '#F8FAFC')}
  <text x="96" y="242" fill="#F8FAFC" font-size="28" font-weight="800">${escapeXml(bundle.chosen.template.name)}</text>
  <text x="96" y="274" fill="#A7BCCB" font-size="20" font-weight="500">${escapeXml(bundle.chosen.template.id)}</text>
  ${block('Gradient', 72, 324, 1056, 120, '#223447', '#314A61', '#F8FAFC')}
  <rect x="96" y="372" width="1008" height="28" rx="14" fill="url(#heatmapRamp)" stroke="#3E5870" />
  <text x="96" y="428" fill="#D7E2EA" font-size="18" font-weight="700">${hexes[0]}</text>
  <text x="600" y="428" fill="#D7E2EA" font-size="18" font-weight="700" text-anchor="middle">${hexes[Math.floor(hexes.length / 2)]}</text>
  <text x="1104" y="428" fill="#D7E2EA" font-size="18" font-weight="700" text-anchor="end">${hexes.at(-1)}</text>
  ${block('Export Excerpts', 72, 472, 512, 184, '#223447', '#314A61', '#F8FAFC')}
  ${textLines([
    'matplotlib',
    `scientific_color_lab[0] = ${hexes[0]}`,
    `scientific_color_lab[4] = ${hexes[Math.floor(hexes.length / 2)]}`,
    `scientific_color_lab[${hexes.length - 1}] = ${hexes.at(-1)}`
  ], 96, 520, '#E6EEF4', 20, 32, '600')}
  ${block('CSS Excerpts', 616, 472, 512, 184, '#223447', '#314A61', '#F8FAFC')}
  ${textLines([
    ':root {',
    `  --${name}-1: ${hexes[0]};`,
    `  --${name}-5: ${hexes[Math.floor(hexes.length / 2)]};`,
    `  --${name}-${hexes.length}: ${hexes.at(-1)};`,
    '}'
  ], 640, 520, '#E6EEF4', 20, 32, '600')}
</svg>`;
}

function pptExampleSvg(bundle) {
  const pack = bundle.chosen.ppt_pack;
  const accents = pack.accent_colors;
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg width="1200" height="720" viewBox="0 0 1200 720" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="1200" height="720" fill="#1A2230"/>
  <rect x="32" y="32" width="1136" height="656" rx="28" fill="#202B3A"/>
  <text x="72" y="96" fill="#F7FAFC" font-size="34" font-weight="800">PPT Role Pack Snapshot</text>
  <text x="72" y="136" fill="#B6C5D1" font-size="22" font-weight="500">Generated from the current course-slides presentation recommendation.</text>
  ${block('Template', 72, 176, 1056, 120, '#29384A', '#374E64', '#F7FAFC')}
  <text x="96" y="242" fill="#F7FAFC" font-size="28" font-weight="800">${escapeXml(bundle.chosen.template.name)}</text>
  <text x="96" y="274" fill="#B6C5D1" font-size="20" font-weight="500">Title ${pack.title_color} | Body ${pack.body_text_color}</text>
  ${block('Slide Preview', 72, 324, 528, 300, '#29384A', '#374E64', '#F7FAFC')}
  <rect x="106" y="364" width="460" height="220" rx="20" fill="#141C28" stroke="#3A4F63" />
  <text x="142" y="430" fill="${pack.title_color}" font-size="34" font-weight="800">Results Overview</text>
  <text x="142" y="474" fill="${pack.body_text_color}" font-size="20" font-weight="500">A dark-slide system with restrained neutrals and focused accents.</text>
  <rect x="142" y="512" width="110" height="18" rx="9" fill="${accents[0]}" />
  <rect x="266" y="512" width="110" height="18" rx="9" fill="${accents[1]}" />
  <rect x="390" y="512" width="110" height="18" rx="9" fill="${accents[2]}" />
  ${block('Role Colors', 632, 324, 496, 300, '#29384A', '#374E64', '#F7FAFC')}
  <rect x="664" y="396" width="148" height="68" rx="18" fill="${pack.title_color}" stroke="#587084" />
  <rect x="832" y="396" width="148" height="68" rx="18" fill="${pack.body_text_color}" stroke="#587084" />
  <rect x="664" y="506" width="96" height="68" rx="18" fill="${accents[0]}" stroke="#587084" />
  <rect x="780" y="506" width="96" height="68" rx="18" fill="${accents[1]}" stroke="#587084" />
  <rect x="896" y="506" width="96" height="68" rx="18" fill="${accents[2]}" stroke="#587084" />
  ${textLines(['Title', pack.title_color], 664, 388, '#E8F0F5', 18, 22, '700')}
  ${textLines(['Body', pack.body_text_color], 832, 388, '#E8F0F5', 18, 22, '700')}
  ${textLines(['Accent A', accents[0]], 664, 498, '#E8F0F5', 17, 20, '700')}
  ${textLines(['Accent B', accents[1]], 780, 498, '#E8F0F5', 17, 20, '700')}
  ${textLines(['Accent C', accents[2]], 896, 498, '#E8F0F5', 17, 20, '700')}
</svg>`;
}

async function writeSnapshot(fileName, content, check) {
  const filePath = path.join(outputDir, fileName);
  if (check) {
    const existing = await fs.readFile(filePath, 'utf8');
    if (existing !== content) {
      throw new Error(`Snapshot out of date: docs/generated/${fileName}`);
    }
    return;
  }

  await fs.mkdir(outputDir, { recursive: true });
  await fs.writeFile(filePath, content, 'utf8');
}

export async function generateReadmeExamples({ check = false } = {}) {
  const lineBundle = recommendPalettes({
    protocol_version: 1,
    target: 'scientific-figure',
    chart_type: 'line-plot',
    palette_class: 'qualitative',
    usage: 'manuscript',
    background: 'light',
    tone: 'restrained',
    priorities: ['colorblind-safe', 'avoid-red-green'],
    source_colors: [],
    output: 'json'
  });

  const heatmapBundle = buildExportBundle({
    protocol_version: 1,
    target: 'scientific-figure',
    chart_type: 'heatmap',
    palette_class: 'sequential',
    usage: 'poster',
    background: 'dark',
    tone: 'strong',
    priorities: [],
    source_colors: [],
    output: 'json'
  });

  const pptBundle = recommendPalettes({
    protocol_version: 1,
    target: 'ppt',
    chart_type: 'presentation-slide',
    palette_class: 'qualitative',
    usage: 'course-slides',
    background: 'dark',
    tone: 'strong',
    priorities: [],
    source_colors: [],
    output: 'json'
  });

  await writeSnapshot('line-plot-example.svg', lineExampleSvg(lineBundle), check);
  await writeSnapshot('heatmap-export-example.svg', heatmapExampleSvg(heatmapBundle), check);
  await writeSnapshot('ppt-role-pack-example.svg', pptExampleSvg(pptBundle), check);
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const check = process.argv.includes('--check');
  generateReadmeExamples({ check })
    .then(() => {
      if (!check) {
        console.log('Generated README example snapshots.');
      }
    })
    .catch((error) => {
      console.error(error instanceof Error ? error.message : String(error));
      process.exit(1);
    });
}
