import assert from 'node:assert/strict';
import { buildExportBundle, doctor, normalizeRequest, recommendPalettes } from '../skill/vendor/scientific-color-lab-core/core.mjs';

function run(name, fn) {
  try {
    fn();
    console.log(`PASS ${name}`);
  } catch (error) {
    console.error(`FAIL ${name}`);
    throw error;
  }
}

run('normalizeRequest rejects unsupported chart/palette combinations', () => {
  assert.throws(() => normalizeRequest({
    protocol_version: 1,
    target: 'scientific-figure',
    chart_type: 'line-plot',
    palette_class: 'sequential',
    usage: 'manuscript',
    background: 'light',
    tone: 'restrained',
    output: 'human'
  }), /Unsupported combination/);
});

run('recommendPalettes returns a ranked manuscript line plot recommendation', () => {
  const bundle = recommendPalettes({
    protocol_version: 1,
    target: 'scientific-figure',
    chart_type: 'line-plot',
    palette_class: 'qualitative',
    usage: 'manuscript',
    background: 'light',
    tone: 'restrained',
    priorities: ['colorblind-safe', 'avoid-red-green'],
    output: 'json'
  });

  assert.equal(bundle.request.chart_type, 'line-plot');
  assert.equal(bundle.recommendations[0].template.chart_type, 'line-plot');
  assert.ok(bundle.recommendations[0].palette.hexes.length >= 5);
  assert.ok(bundle.recommendations[0].exports.summary.includes('Template:'));
});

run('recommendPalettes returns a PPT pack for presentation-slide requests', () => {
  const bundle = recommendPalettes({
    protocol_version: 1,
    target: 'ppt',
    chart_type: 'presentation-slide',
    palette_class: 'qualitative',
    usage: 'course-slides',
    background: 'dark',
    tone: 'strong',
    priorities: ['high-contrast'],
    output: 'json'
  });

  assert.ok(bundle.chosen.ppt_pack);
  assert.equal(bundle.chosen.ppt_pack.chart_palette.length, bundle.chosen.palette.hexes.length);
});

run('buildExportBundle returns requested export payloads', () => {
  const bundle = buildExportBundle({
    protocol_version: 1,
    target: 'scientific-figure',
    chart_type: 'heatmap',
    palette_class: 'diverging',
    usage: 'poster',
    background: 'dark',
    tone: 'strong',
    priorities: ['avoid-rainbow', 'high-contrast'],
    output: 'json'
  });

  assert.ok(bundle.exports.matplotlib.includes('scientific_color_lab'));
  assert.ok(bundle.exports.css.includes(':root'));
  assert.ok(bundle.exports.plotly.includes('colorway'));
});

run('doctor reports vendored metadata', () => {
  const report = doctor();
  assert.equal(report.runtime_mode, 'vendored');
  assert.ok(report.vendored_metadata.template_count > 0);
  assert.notEqual(report.vendored_metadata.upstream_commit, 'unknown');
});
