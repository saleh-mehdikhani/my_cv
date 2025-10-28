#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');

// Set Puppeteer launch args via environment
process.env.PUPPETEER_ARGS = '--no-sandbox,--disable-setuid-sandbox';

// Run resume-cli with the configured environment
const resumePath = path.join(__dirname, 'build', 'resume.json');
const outputPath = path.join(__dirname, 'build', 'resume.pdf');
const theme = 'stackoverflow';

const cmd = `npx resume export ${outputPath} --theme ${theme} --resume ${resumePath}`;

console.log(`Running: ${cmd}`);
console.log(`With Puppeteer args: ${process.env.PUPPETEER_ARGS}`);

try {
  execSync(cmd, { 
    stdio: 'inherit',
    env: {
      ...process.env,
      PUPPETEER_ARGS: '--no-sandbox,--disable-setuid-sandbox'
    }
  });
  console.log('PDF generated successfully!');
} catch (error) {
  console.error('Failed to generate PDF:', error.message);
  process.exit(1);
}