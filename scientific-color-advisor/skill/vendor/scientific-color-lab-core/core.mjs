import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const catalogPath = path.join(__dirname, 'catalog.json');
const metadataPath = path.join(__dirname, 'metadata.json');

const REQUEST_ENUMS = {
  target: new Set(['scientific-figure', 'ppt']),
  chart_type: new Set(['line-plot', 'scatter-plot', 'bar-chart', 'heatmap', 'concept-figure', 'presentation-slide']),
  palette_class: new Set(['qualitative', 'sequential', 'diverging', 'cyclic', 'concept']),
  usage: new Set(['manuscript', 'lab-meeting', 'poster', 'course-slides', 'online-document']),
  background: new Set(['light', 'dark']),
  tone: new Set(['restrained', 'balanced', 'strong']),
  priorities: new Set(['colorblind-safe', 'grayscale-safe', 'high-contrast', 'avoid-red-green', 'avoid-rainbow']),
  output: new Set(['human', 'json'])
};

const COMPATIBILITY = {
  'line-plot': new Set(['qualitative']),
  'scatter-plot': new Set(['qualitative']),
  'bar-chart': new Set(['qualitative']),
  heatmap: new Set(['sequential', 'diverging', 'cyclic']),
  'concept-figure': new Set(['concept']),
  'presentation-slide': new Set(['qualitative'])
};

const USAGE_TO_CATALOG = {
  manuscript: 'manuscript',
  'lab-meeting': 'lab meeting',
  poster: 'poster',
  'course-slides': 'course slides',
  'online-document': 'online document'
};

const TONE_TO_CATALOG = {
  restrained: ['Editorial Minimal', 'Publication Clean', 'Scientific Neutral'],
  balanced: ['Publication Clean', 'Scientific Neutral', 'Nature-like'],
  strong: ['Presentation Strong', 'Nature-like']
};

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function normalizeFlagList(values = []) {
  return [...new Set(values.flatMap((entry) => `${entry}`.split(',').map((item) => item.trim()).filter(Boolean)))];
}

function ensureHex(value) {
  return /^#?[0-9a-fA-F]{6}$/.test(value);
}

function normalizeHex(value) {
  const raw = value.startsWith('#') ? value : `#${value}`;
  return raw.toUpperCase();
}

function hexToRgb(hex) {
  const normalized = normalizeHex(hex).slice(1);
  return {
    r: Number.parseInt(normalized.slice(0, 2), 16),
    g: Number.parseInt(normalized.slice(2, 4), 16),
    b: Number.parseInt(normalized.slice(4, 6), 16)
  };
}

function rgbDistance(left, right) {
  const dr = left.r - right.r;
  const dg = left.g - right.g;
  const db = left.b - right.b;
  return Math.sqrt((dr * dr) + (dg * dg) + (db * db));
}

function relativeLuminance(rgb) {
  const convert = (channel) => {
    const unit = channel / 255;
    return unit <= 0.03928 ? unit / 12.92 : ((unit + 0.055) / 1.055) ** 2.4;
  };

  const r = convert(rgb.r);
  const g = convert(rgb.g);
  const b = convert(rgb.b);
  return (0.2126 * r) + (0.7152 * g) + (0.0722 * b);
}

function contrastRatio(rgb, backgroundRgb) {
  const l1 = relativeLuminance(rgb);
  const l2 = relativeLuminance(backgroundRgb);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

function rgbToHsl(rgb) {
  const r = rgb.r / 255;
  const g = rgb.g / 255;
  const b = rgb.b / 255;
  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const delta = max - min;
  let hue = 0;

  if (delta !== 0) {
    if (max === r) {
      hue = ((g - b) / delta) % 6;
    } else if (max === g) {
      hue = ((b - r) / delta) + 2;
    } else {
      hue = ((r - g) / delta) + 4;
    }
    hue *= 60;
    if (hue < 0) {
      hue += 360;
    }
  }

  const lightness = (max + min) / 2;
  const saturation = delta === 0 ? 0 : delta / (1 - Math.abs((2 * lightness) - 1));

  return {
    h: Math.round(hue * 10) / 10,
    s: Math.round(saturation * 1000) / 10,
    l: Math.round(lightness * 1000) / 10
  };
}

function usageToCatalog(usage) {
  return USAGE_TO_CATALOG[usage];
}

function makeColor(hex, index, paletteName) {
  const rgb = hexToRgb(hex);
  return {
    id: `${paletteName}-${index + 1}`,
    name: `${paletteName} ${index + 1}`,
    hex: normalizeHex(hex),
    rgb,
    hsl: rgbToHsl(rgb),
    luminance: relativeLuminance(rgb)
  };
}

function createTemplatePalette(template) {
  const colors = template.hexes.map((hex, index) => makeColor(hex, index, template.id));
  return {
    id: template.id,
    name: template.name,
    chart_type: template.chartType,
    palette_class: template.paletteClass,
    usage: template.academicUsage,
    tone: template.tone,
    background: template.backgroundMode,
    tags: template.tags,
    description: template.description,
    colors
  };
}

function addDiagnostic(items, diagnostic) {
  items.push({
    id: `${diagnostic.code}-${items.length + 1}`,
    ...diagnostic
  });
}

function isMonotonic(values) {
  if (values.length < 2) {
    return true;
  }
  const direction = values[1] >= values[0] ? 'ascending' : 'descending';
  return values.every((value, index) => {
    if (index === 0) {
      return true;
    }
    return direction === 'ascending' ? value >= values[index - 1] : value <= values[index - 1];
  });
}

function deriveQuickFixes(items) {
  const quickFixes = new Set();
  items.forEach((item) => {
    if (item.code === 'oversaturation-risk') {
      quickFixes.add('reduce-chroma');
    }
    if (item.code === 'categorical-too-similar' || item.code === 'too-many-qualitative-colors') {
      quickFixes.add('increase-categorical-spacing');
    }
    if (item.code === 'red-green-conflict') {
      quickFixes.add('replace-red-green-pair');
    }
    if (item.code === 'sequential-non-monotonic' || item.code === 'rainbow-risk') {
      quickFixes.add('rebuild-sequential-ramp');
    }
    if (item.code === 'diverging-midpoint-chromatic') {
      quickFixes.add('rebalance-diverging-midpoint');
    }
    if (item.code === 'cyclic-endpoints-open') {
      quickFixes.add('close-cyclic-endpoints');
    }
  });
  if (items.length > 0) {
    quickFixes.add('suggest-safer-template');
  }
  return [...quickFixes];
}

function checkDiagnostics(palette) {
  const items = [];
  const backgroundRgb = palette.background === 'dark' ? { r: 20, g: 24, b: 31 } : { r: 246, g: 245, b: 241 };

  palette.colors.forEach((color) => {
    const contrast = contrastRatio(color.rgb, backgroundRgb);
    if (contrast < 3) {
      addDiagnostic(items, {
        code: 'low-interface-contrast',
        severity: 'warning',
        category: 'contrast',
        title: 'Low interface contrast',
        message: `${color.name} falls below 3:1 against the default canvas.`,
        suggestion: 'Reserve it for accents or raise its contrast.'
      });
    }
    if (color.hsl.s > 72) {
      addDiagnostic(items, {
        code: 'oversaturation-risk',
        severity: 'warning',
        category: 'palette-risk',
        title: 'Oversaturation risk',
        message: `${color.name} is highly saturated for restrained scientific layouts.`,
        suggestion: 'Reduce chroma slightly for paper-safe output.'
      });
    }
  });

  if (palette.palette_class === 'qualitative' && palette.colors.length > 8) {
    addDiagnostic(items, {
      code: 'too-many-qualitative-colors',
      severity: 'warning',
      category: 'palette-risk',
      title: 'Too many qualitative colors',
      message: 'Qualitative palettes become harder to read when they grow beyond eight categories.',
      suggestion: 'Reduce the count or separate primary and secondary categories.'
    });
  }

  palette.colors.forEach((color, index) => {
    palette.colors.slice(index + 1).forEach((candidate) => {
      const distance = rgbDistance(color.rgb, candidate.rgb);
      if (palette.palette_class === 'qualitative' && distance < 72) {
        addDiagnostic(items, {
          code: 'categorical-too-similar',
          severity: 'warning',
          category: 'categorical',
          title: 'Categorical colors are too similar',
          message: `${color.name} and ${candidate.name} are visually close.`,
          suggestion: 'Increase spacing between category anchors.'
        });
      }

      const redGreenPair =
        (((color.hsl.h <= 25 || color.hsl.h >= 335) && candidate.hsl.h >= 95 && candidate.hsl.h <= 155) ||
        ((candidate.hsl.h <= 25 || candidate.hsl.h >= 335) && color.hsl.h >= 95 && color.hsl.h <= 155)) &&
        Math.abs(color.luminance - candidate.luminance) < 0.14;

      if (redGreenPair) {
        addDiagnostic(items, {
          code: 'red-green-conflict',
          severity: 'warning',
          category: 'accessibility',
          title: 'Red/green conflict risk',
          message: `${color.name} and ${candidate.name} may collapse under common color-vision deficiencies.`,
          suggestion: 'Replace one side with a blue, violet, or neutral counterpoint.'
        });
      }
    });
  });

  if (palette.palette_class === 'sequential') {
    const luminances = palette.colors.map((color) => color.luminance);
    if (!isMonotonic(luminances)) {
      addDiagnostic(items, {
        code: 'sequential-non-monotonic',
        severity: 'error',
        category: 'sequential',
        title: 'Sequential lightness is non-monotonic',
        message: 'Sequential ramps should move in one luminance direction only.',
        suggestion: 'Use a monotonic ordered ramp.'
      });
    }

    const hueSpread = Math.max(...palette.colors.map((color) => color.hsl.h)) - Math.min(...palette.colors.map((color) => color.hsl.h));
    if (hueSpread > 210 && !isMonotonic(luminances)) {
      addDiagnostic(items, {
        code: 'rainbow-risk',
        severity: 'error',
        category: 'palette-risk',
        title: 'Rainbow risk',
        message: 'Large hue swings plus unstable luminance can mislead quantitative reading.',
        suggestion: 'Prefer a monotonic sequential map or a structured diverging map.'
      });
    }
  }

  if (palette.palette_class === 'diverging') {
    const midpoint = palette.colors[Math.floor(palette.colors.length / 2)];
    if (midpoint && midpoint.hsl.s > 20) {
      addDiagnostic(items, {
        code: 'diverging-midpoint-chromatic',
        severity: 'warning',
        category: 'diverging',
        title: 'Diverging midpoint is too chromatic',
        message: 'A quieter midpoint preserves centered structure better.',
        suggestion: 'Use a near-neutral midpoint.'
      });
    }
  }

  if (palette.palette_class === 'cyclic') {
    const first = palette.colors[0];
    const last = palette.colors[palette.colors.length - 1];
    if (rgbDistance(first.rgb, last.rgb) > 35) {
      addDiagnostic(items, {
        code: 'cyclic-endpoints-open',
        severity: 'warning',
        category: 'cyclic',
        title: 'Cyclic endpoints are not continuous',
        message: 'The first and last colors should close the loop smoothly.',
        suggestion: 'Align the endpoint hues and luminance more tightly.'
      });
    }
  }

  const errors = items.filter((item) => item.severity === 'error').length;
  const warnings = items.filter((item) => item.severity === 'warning').length;
  const score = Math.max(25, 100 - (errors * 14) - (warnings * 7));
  const status = errors > 0 || score < 68 ? 'high-risk' : warnings > 0 || score < 88 ? 'needs-attention' : 'healthy';

  return {
    score,
    status,
    summary: status === 'healthy' ? `Healthy score ${score}` : `${errors} errors, ${warnings} warnings, score ${score}`,
    quickFixes: deriveQuickFixes(items),
    items
  };
}

function classifyLabels(template, diagnostics) {
  const labels = new Set();
  const codes = new Set(diagnostics.items.map((item) => item.code));
  if (!codes.has('red-green-conflict')) {
    labels.add('colorblind-safer');
  }
  if (template.tags.includes('high-contrast') || template.structure === 'high-contrast-categorical' || template.tone === 'Presentation Strong') {
    labels.add('high-contrast');
  }
  if (template.paletteClass === 'sequential' && !codes.has('sequential-non-monotonic')) {
    labels.add('ordered-ramp');
  }
  if (template.paletteClass === 'diverging' && !codes.has('diverging-midpoint-chromatic')) {
    labels.add('structured-midpoint');
  }
  if (template.paletteClass === 'cyclic' && !codes.has('cyclic-endpoints-open')) {
    labels.add('closed-loop');
  }
  return [...labels];
}

function templateToneScore(requestTone, templateTone) {
  const allowed = TONE_TO_CATALOG[requestTone];
  const index = allowed.indexOf(templateTone);
  return index === -1 ? 0 : (12 - (index * 3));
}

function sourceColorScore(sourceColors, colors) {
  if (!sourceColors.length) {
    return 0;
  }
  const parsedSources = sourceColors.map((hex) => hexToRgb(hex));
  const distance = parsedSources.reduce((sum, source) => {
    const nearest = Math.min(...colors.map((color) => rgbDistance(source, color.rgb)));
    return sum + nearest;
  }, 0) / parsedSources.length;
  return Math.max(0, 10 - Math.round(distance / 32));
}

function priorityScore(request, labels, diagnostics) {
  const diagnosticCodes = new Set(diagnostics.items.map((item) => item.code));
  let score = 0;
  request.priorities.forEach((priority) => {
    if (priority === 'high-contrast' && labels.includes('high-contrast')) {
      score += 8;
    }
    if (priority === 'colorblind-safe' && !diagnosticCodes.has('red-green-conflict')) {
      score += 8;
    }
    if (priority === 'grayscale-safe' && !diagnosticCodes.has('low-interface-contrast')) {
      score += 6;
    }
    if (priority === 'avoid-red-green' && !diagnosticCodes.has('red-green-conflict')) {
      score += 8;
    }
    if (priority === 'avoid-rainbow' && !diagnosticCodes.has('rainbow-risk')) {
      score += 6;
    }
  });
  return score;
}

function sortByVisualWeight(colors) {
  return [...colors].sort((left, right) => right.luminance - left.luminance);
}

function darkestColor(colors) {
  return [...colors].sort((left, right) => left.luminance - right.luminance)[0];
}

function mostSaturatedColors(colors) {
  return [...colors].sort((left, right) => right.hsl.s - left.hsl.s);
}

function buildPptPack(request, palette) {
  const accents = mostSaturatedColors(palette.colors).slice(0, 3).map((color) => color.hex);
  const darkAnchor = darkestColor(palette.colors)?.hex ?? '#111827';
  const titleColor = request.background === 'dark' ? '#F6F5F1' : darkAnchor;
  const bodyTextColor = request.background === 'dark' ? '#E8E4DE' : '#374151';

  return {
    title_color: titleColor,
    body_text_color: bodyTextColor,
    accent_colors: accents,
    chart_palette: palette.colors.map((color) => color.hex),
    usage_notes: [
      request.background === 'dark'
        ? 'Use warm near-white text against dark slide backgrounds.'
        : 'Keep titles dark and reserve saturated colors for emphasis.',
      'Use the chart palette for figures and the accent colors for callouts or highlights.',
      'Avoid using more than two accent colors in a single PPT layout.'
    ]
  };
}

function buildExports(recommendation, request) {
  const paletteName = recommendation.template.name.replace(/[^a-z0-9]+/gi, '_').toLowerCase();
  const hexes = recommendation.palette.colors.map((color) => color.hex);
  const css = [':root {', ...hexes.map((hex, index) => `  --${paletteName}-${index + 1}: ${hex};`), '}'].join('\n');
  const matplotlib = ['scientific_color_lab = [', ...recommendation.palette.colors.map((color) => `    {"name": "${color.name}", "hex": "${color.hex}"},`), ']'].join('\n');
  const plotly = JSON.stringify({ layout: { colorway: hexes } }, null, 2);
  const matlab = ['scientific_color_lab = [', ...recommendation.palette.colors.map((color) => `    [${(color.rgb.r / 255).toFixed(4)}, ${(color.rgb.g / 255).toFixed(4)}, ${(color.rgb.b / 255).toFixed(4)}]; % ${color.name}`), '];'].join('\n');
  const summary = [
    `Template: ${recommendation.template.name}`,
    `Chart type: ${request.chart_type}`,
    `Palette class: ${request.palette_class}`,
    `Score: ${recommendation.diagnostics.score}`,
    'HEX:',
    ...hexes.map((hex, index) => `${index + 1}. ${hex}`)
  ].join('\n');
  const json = JSON.stringify({
    request,
    template: recommendation.template,
    diagnostics: recommendation.diagnostics,
    colors: recommendation.palette.colors.map((color) => ({
      name: color.name,
      hex: color.hex,
      rgb: color.rgb,
      hsl: color.hsl
    }))
  }, null, 2);

  return {
    matplotlib,
    plotly,
    matlab,
    css,
    json,
    summary
  };
}

export function normalizeRequest(input) {
  const request = {
    protocol_version: input.protocol_version ?? 1,
    target: input.target,
    chart_type: input.chart_type,
    palette_class: input.palette_class,
    usage: input.usage,
    background: input.background,
    tone: input.tone,
    series_count: input.series_count == null ? undefined : Number.parseInt(String(input.series_count), 10),
    priorities: normalizeFlagList(input.priorities || []),
    source_colors: normalizeFlagList(input.source_colors || []).map((color) => normalizeHex(color)),
    output: input.output ?? 'human'
  };

  if (request.protocol_version !== 1) {
    throw new Error(`Unsupported protocol_version: ${request.protocol_version}`);
  }

  for (const field of ['target', 'chart_type', 'palette_class', 'usage', 'background', 'tone', 'output']) {
    if (!REQUEST_ENUMS[field].has(request[field])) {
      throw new Error(`Invalid ${field}: ${request[field]}`);
    }
  }

  request.priorities.forEach((priority) => {
    if (!REQUEST_ENUMS.priorities.has(priority)) {
      throw new Error(`Invalid priority: ${priority}`);
    }
  });

  request.source_colors.forEach((hex) => {
    if (!ensureHex(hex)) {
      throw new Error(`Invalid source color: ${hex}`);
    }
  });

  if (request.series_count != null && (!Number.isInteger(request.series_count) || request.series_count < 1 || request.series_count > 24)) {
    throw new Error('series_count must be an integer between 1 and 24');
  }

  const allowedPaletteClasses = COMPATIBILITY[request.chart_type];
  if (!allowedPaletteClasses.has(request.palette_class)) {
    throw new Error(`Unsupported combination: ${request.chart_type} cannot use ${request.palette_class}`);
  }

  return request;
}

export function extractTemplateSeedsFromCatalogTs(source) {
  const match = source.match(/const seeds: TemplateSeed\[\] = (\[[\s\S]*?\n\]);/);
  if (!match) {
    throw new Error('Unable to extract template seeds from catalog.ts');
  }
  return vm.runInNewContext(`(${match[1]})`, {}, { timeout: 1000 });
}

function buildCatalogFromSeeds(seeds) {
  return seeds.flatMap((seed) => {
    const light = {
      ...seed,
      backgroundMode: 'light',
      tags: [...seed.tags, 'light']
    };
    const dark = {
      ...seed,
      id: `${seed.id}-dark`,
      name: `${seed.name} Dark`,
      description: `${seed.description} Adapted for darker surrounding UI and presentation backgrounds.`,
      backgroundMode: 'dark',
      tags: [...seed.tags, 'dark']
    };
    return [{ ...light, id: `${seed.id}-light` }, dark];
  });
}

export function loadCatalogFromRepo(repoPath) {
  const catalogSourcePath = path.join(repoPath, 'src', 'data', 'templates', 'catalog.ts');
  const source = fs.readFileSync(catalogSourcePath, 'utf8');
  return buildCatalogFromSeeds(extractTemplateSeedsFromCatalogTs(source));
}

export function loadRuntimeCatalog(options = {}) {
  const repoPath = options.repoPath || process.env.SCIENTIFIC_COLOR_LAB_REPO;
  if (repoPath) {
    return {
      runtime_mode: 'local-bridge',
      catalog: loadCatalogFromRepo(repoPath),
      metadata: {
        ...readJson(metadataPath),
        local_repo: path.resolve(repoPath)
      }
    };
  }

  return {
    runtime_mode: 'vendored',
    catalog: readJson(catalogPath),
    metadata: readJson(metadataPath)
  };
}

function buildWhy(template, request, diagnostics) {
  const reasons = [];
  reasons.push(`Matches ${request.chart_type} with a ${request.palette_class} palette.`);
  reasons.push(`Fits ${request.usage.replace('-', ' ')} usage on a ${request.background} background.`);
  if (template.tags.includes('high-contrast') || template.structure === 'high-contrast-categorical') {
    reasons.push('Carries high-contrast structure that holds up in charts and decks.');
  }
  if (!diagnostics.items.some((item) => item.code === 'red-green-conflict')) {
    reasons.push('Avoids an obvious red/green conflict warning.');
  }
  if (request.tone === 'restrained' && ['Editorial Minimal', 'Publication Clean', 'Scientific Neutral'].includes(template.tone)) {
    reasons.push('Keeps the palette publication-safe and restrained.');
  }
  if (request.tone === 'strong' && template.tone === 'Presentation Strong') {
    reasons.push('Pushes contrast harder for posters and slides.');
  }
  return reasons;
}

function scoreTemplate(template, request) {
  const palette = createTemplatePalette(template);
  const diagnostics = checkDiagnostics(palette);
  const labels = classifyLabels(template, diagnostics);
  const usageMatch = template.academicUsage === usageToCatalog(request.usage);
  const backgroundMatch = template.backgroundMode === request.background;
  const sourceScore = sourceColorScore(request.source_colors, palette.colors);
  const score =
    (template.chartType === request.chart_type ? 30 : 0) +
    (template.paletteClass === request.palette_class ? 25 : 0) +
    (usageMatch ? 15 : 0) +
    (backgroundMatch ? 10 : 0) +
    templateToneScore(request.tone, template.tone) +
    priorityScore(request, labels, diagnostics) +
    sourceScore +
    Math.round(diagnostics.score / 5);

  return {
    template,
    palette,
    diagnostics,
    labels,
    score,
    why: buildWhy(template, request, diagnostics)
  };
}

export function recommendPalettes(requestInput, options = {}) {
  const request = normalizeRequest(requestInput);
  const runtime = loadRuntimeCatalog(options);
  const candidates = runtime.catalog
    .filter((template) => template.chartType === request.chart_type && template.paletteClass === request.palette_class)
    .map((template) => scoreTemplate(template, request))
    .sort((left, right) => right.score - left.score || right.diagnostics.score - left.diagnostics.score || left.template.name.localeCompare(right.template.name))
    .slice(0, 5)
    .map((entry, index) => {
      const exports = buildExports(entry, request);
      return {
        rank: index + 1,
        score: entry.score,
        labels: entry.labels,
        template: {
          id: entry.template.id,
          name: entry.template.name,
          description: entry.template.description,
          chart_type: entry.template.chartType,
          palette_class: entry.template.paletteClass,
          background: entry.template.backgroundMode,
          tone: entry.template.tone,
          usage: entry.template.academicUsage,
          tags: entry.template.tags
        },
        palette: {
          name: entry.template.name,
          hexes: entry.palette.colors.map((color) => color.hex),
          colors: entry.palette.colors
        },
        diagnostics: entry.diagnostics,
        why: entry.why,
        exports,
        ppt_pack: request.target === 'ppt' ? buildPptPack(request, entry.palette) : undefined
      };
    });

  if (!candidates.length) {
    throw new Error('No acceptable recommendation found for this request.');
  }

  return {
    request,
    runtime,
    recommendations: candidates,
    chosen: candidates[0]
  };
}

export function buildExportBundle(requestInput, options = {}) {
  const request = normalizeRequest(requestInput);
  const bundle = recommendPalettes(request, options);
  return {
    request: bundle.request,
    runtime: bundle.runtime,
    chosen: bundle.chosen,
    exports: bundle.chosen.exports,
    ppt_pack: bundle.chosen.ppt_pack
  };
}

function readGitCommit(repoPath) {
  try {
    return execFileSync('git', ['-c', `safe.directory=${repoPath}`, '-C', repoPath, 'rev-parse', 'HEAD'], {
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore']
    }).trim();
  } catch {
    return null;
  }
}

export function doctor(options = {}) {
  const runtime = loadRuntimeCatalog(options);
  const repoPath = options.repoPath || process.env.SCIENTIFIC_COLOR_LAB_REPO;
  const expectedFiles = repoPath ? [
    path.join(repoPath, 'src', 'data', 'templates', 'catalog.ts'),
    path.join(repoPath, 'src', 'domain', 'diagnostics', 'engine.ts'),
    path.join(repoPath, 'src', 'domain', 'export', 'service.ts')
  ] : [];

  return {
    runtime_mode: runtime.runtime_mode,
    vendored_metadata: runtime.metadata,
    local_repo: repoPath
      ? {
          path: path.resolve(repoPath),
          exists: fs.existsSync(repoPath),
          expected_files: expectedFiles.map((filePath) => ({
            path: filePath,
            exists: fs.existsSync(filePath)
          })),
          git_commit: readGitCommit(repoPath)
        }
      : null
  };
}
