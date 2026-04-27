import { generateReadmeExamples } from './generate-readme-examples.mjs';

await import('../tests/core.test.mjs');
await import('../tests/cli.test.mjs');
await import('./validate-skill.mjs');
await generateReadmeExamples({ check: true });
