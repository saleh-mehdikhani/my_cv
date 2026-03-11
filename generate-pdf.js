#!/usr/bin/env node

/**
 * generate-pdf.js
 * Generates a PDF from a JSON Resume file by:
 *   1. Loading the theme directly (bypasses resume-cli theme resolution issues)
 *   2. Rendering the resume HTML using the theme's render() function
 *   3. Converting the HTML to PDF using Puppeteer
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function generatePDF() {
  const resumePath = path.resolve(__dirname, 'build', 'resume.json');
  const outputPath = path.resolve(__dirname, 'build', 'resume.pdf');
  const themePath = path.resolve(__dirname, 'node_modules', 'jsonresume-theme-stackoverflow');

  console.log(`Resume JSON: ${resumePath}`);
  console.log(`Output PDF:  ${outputPath}`);
  console.log(`Theme path:  ${themePath}`);

  // Load resume data
  if (!fs.existsSync(resumePath)) {
    console.error(`✗ Resume JSON not found at: ${resumePath}`);
    process.exit(1);
  }
  const resume = JSON.parse(fs.readFileSync(resumePath, 'utf-8'));

  // Load theme and render HTML
  const theme = require(themePath);
  const html = theme.render(resume);
  const pdfOptions = theme.pdfRenderOptions || {};

  console.log('✓ HTML rendered from theme');

  // Launch Puppeteer
  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    headless: true,
  });

  try {
    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: 'networkidle0' });

    await page.pdf({
      path: outputPath,
      format: 'A4',
      printBackground: true,
      ...pdfOptions,
    });

    const size = fs.statSync(outputPath).size;
    console.log(`✓ PDF generated successfully`);
    console.log(`  File: ${outputPath}`);
    console.log(`  Size: ${(size / 1024).toFixed(1)} KB`);
  } finally {
    await browser.close();
  }
}

generatePDF().catch((err) => {
  console.error('✗ PDF generation failed:', err.message);
  process.exit(1);
});