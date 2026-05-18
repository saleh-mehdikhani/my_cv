#!/usr/bin/env node

/**
 * generate-pdf-professional.js
 * Generates a PDF from a JSON Resume file using the "professional" theme by:
 *   1. Dynamically importing the pre-built ESM dist of @jsonresume/jsonresume-theme-professional
 *   2. Calling its render() function to get HTML
 *   3. Converting the HTML to PDF using Puppeteer
 *
 * Note: dynamic import() is used instead of require() because this theme is
 * an ESM-only package (dist/index.mjs). Dynamic import() works fine inside
 * a CommonJS file in Node.js >= 14.
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const { pathToFileURL } = require('url');

async function generatePDF() {
  const resumePath = path.resolve(__dirname, 'build', 'resume.json');
  const outputPath = path.resolve(__dirname, 'build', 'resume-professional.pdf');

  console.log(`Resume JSON: ${resumePath}`);
  console.log(`Output PDF:  ${outputPath}`);

  // Load resume data
  if (!fs.existsSync(resumePath)) {
    console.error(`✗ Resume JSON not found at: ${resumePath}`);
    process.exit(1);
  }
  const resume = JSON.parse(fs.readFileSync(resumePath, 'utf-8'));

  // Remove empty array sections so the theme components (which only check !prop instead of prop.length === 0) will return null and not render empty headers.
  for (let key in resume) {
    if (Array.isArray(resume[key]) && resume[key].length === 0) {
      delete resume[key];
    }
  }

  // Map website to url for the professional theme to render it in the header
  if (resume.basics && !resume.basics.url && resume.basics.website) {
    resume.basics.url = resume.basics.website;
  }

  // Preprocess resume specifically for the Professional theme:
  if (resume.work) {
    resume.work = resume.work.map(job => {
      const newJob = { ...job };
      const lines = job.summary ? job.summary.split('\n') : [];
      const bullets = [];
      const nonBullets = [];

      for (let line of lines) {
        let trimmed = line.trim();
        if (trimmed.startsWith('-') || trimmed.startsWith('*')) {
          let content = trimmed.replace(/^[-*]\s*/, '').replace(/\*\*([^*]+)\*\*/g, '$1');
          bullets.push(content);
        } else if (trimmed) {
          nonBullets.push(trimmed.replace(/\*\*([^*]+)\*\*/g, '$1'));
        }
      }

      newJob.summary = nonBullets.join('\n');
      newJob.highlights = bullets;
      return newJob;
    });
  }

  if (resume.projects) {
    resume.projects = resume.projects.map(proj => {
      const newProj = { ...proj };
      if (proj.summary) {
        newProj.summary = proj.summary.replace(/\*\*([^*]+)\*\*/g, '$1');
        newProj.description = newProj.summary;
      }
      if (proj.highlights) {
        newProj.highlights = proj.highlights.map(hl => hl.replace(/\*\*([^*]+)\*\*/g, '$1'));
      }
      return newProj;
    });
  }

  // Import the pre-built ESM dist directly by file path to bypass exports map resolution issues
  const distPath = path.resolve(__dirname, 'node_modules', '@jsonresume', 'jsonresume-theme-professional', 'dist', 'index.mjs');
  const theme = await import(pathToFileURL(distPath).href);

  if (typeof theme.render !== 'function') {
    console.error('✗ Theme does not export a render() function. Exported keys:', Object.keys(theme));
    process.exit(1);
  }

  // Render HTML and point font paths to the JSON Resume CDN
  let html = theme.render(resume);
  html = html.replace(/\/fonts\//g, 'https://registry.jsonresume.org/fonts/');
  // Inject custom print styles to keep sections together in the PDF
  const customStyles = `
    <style>
      @media print {
        /* Keep Education, Certificates, and Skills sections fully intact on a single page */
        body > div > div:nth-child(n+5) {
          page-break-inside: avoid !important;
          break-inside: avoid !important;
        }
      }
    </style>
  `;
  html = html.replace('</head>', `${customStyles}</head>`);
  const pdfOptions = theme.pdfRenderOptions || {};

  console.log('✓ HTML rendered');

  // Launch Puppeteer
  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
    headless: true,
  });

  try {
    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: 'networkidle0' });

    // Dynamically clean up DOM structure
    await page.evaluate(() => {
      // 1. Hide all project dates
      const headers = Array.from(document.querySelectorAll('h2'));
      const projectsHeader = headers.find(h => h.textContent.trim() === 'Projects');
      if (projectsHeader) {
        const hrElement = projectsHeader.nextElementSibling;
        if (hrElement) {
          const itemsContainer = hrElement.nextElementSibling;
          if (itemsContainer) {
            const projectItems = itemsContainer.children;
            for (let item of projectItems) {
              const meta = item.firstElementChild;
              if (meta) {
                const secondaryDiv = meta.querySelector('.secondary');
                if (secondaryDiv) {
                  secondaryDiv.style.display = 'none';
                }
              }
            }
          }
        }
      }

      // 2. Split contact details and social links into two symmetrical lines
      const basicInfoContainer = document.querySelector('.sc-lgpSej.jeAkFT') || document.querySelector('[class*="jeAkFT"]');
      if (basicInfoContainer) {
        const children = Array.from(basicInfoContainer.children);
        const contactItems = [];
        const linkItems = [];
        
        for (let child of children) {
          if (child.querySelector('a')) {
            linkItems.push(child);
          } else {
            contactItems.push(child);
          }
        }
        
        if (linkItems.length > 0) {
          basicInfoContainer.innerHTML = '';
          
          const row1 = document.createElement('div');
          row1.style.display = 'flex';
          row1.style.justifyContent = 'center';
          row1.style.gap = '20px';
          row1.style.width = '100%';
          row1.style.flexWrap = 'wrap';
          contactItems.forEach(item => row1.appendChild(item));
          
          const row2 = document.createElement('div');
          row2.style.display = 'flex';
          row2.style.justifyContent = 'center';
          row2.style.gap = '20px';
          row2.style.width = '100%';
          row2.style.flexWrap = 'wrap';
          row2.style.marginTop = '6px';
          linkItems.forEach(item => row2.appendChild(item));
          
          basicInfoContainer.appendChild(row1);
          basicInfoContainer.appendChild(row2);
          
          basicInfoContainer.style.flexDirection = 'column';
          basicInfoContainer.style.alignItems = 'center';
        }
      }
    });

    // Get the final processed HTML from the page to save it for inspection
    const finalHtml = await page.content();
    const htmlOutputPath = path.resolve(__dirname, 'build', 'resume-professional.html');
    fs.writeFileSync(htmlOutputPath, finalHtml, 'utf-8');
    console.log(`✓ HTML saved successfully: ${htmlOutputPath}`);

    await page.pdf({
      path: outputPath,
      format: 'A4',
      printBackground: true,
      margin: {
        top: '0.55in',
        bottom: '0.55in',
        left: '0.55in',
        right: '0.55in'
      },
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
