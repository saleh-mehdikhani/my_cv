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
  let html = theme.render(resume);
  const pdfOptions = theme.pdfRenderOptions || {};

  // Fix paragraphSplit double-wrapping: <p><p>text</p></p> → <p>text</p>
  html = html.replace(/<p>(<p>[\s\S]*?<\/p>)<\/p>/g, '$1');

  console.log('✓ HTML rendered from theme');

  // Launch Puppeteer
  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    headless: true,
  });

  try {
    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: 'networkidle0' });

    // Handlebars has a scope bug in the projects partial: {{#if summary}} inside
    // the .item div evaluates to false even though summary is non-empty. This is
    // a known issue with context restoration after certain block helpers.
    // Fix: inject project summaries directly into the DOM, bypassing Handlebars.
    await page.evaluate((projects) => {
      const projectItems = document.querySelectorAll('.project-item');
      projects.forEach((project, index) => {
        if (project.summary && projectItems[index]) {
          const itemDiv = projectItems[index].querySelector('.item');
          if (itemDiv) {
            // Create a summary div with the description text
            const summaryDiv = document.createElement('div');
            summaryDiv.className = 'summary';
            summaryDiv.style.marginBottom = '0.4em';
            summaryDiv.textContent = project.summary;
            // Insert before highlights if present, otherwise append
            const highlightsList = itemDiv.querySelector('.highlights');
            if (highlightsList) {
              itemDiv.insertBefore(summaryDiv, highlightsList);
            } else {
              itemDiv.appendChild(summaryDiv);
            }
          }
        }
      });
    }, resume.projects);

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