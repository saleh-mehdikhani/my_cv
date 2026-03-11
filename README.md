# Hugo CV & Resume Builder

This repository contains the source code for my personal CV and resume, built using Hugo and JSON Resume. It automatically generates a web-based CV and a PDF version from Markdown sources.

## Local Build Instructions

To build the resume on your local machine, follow these steps:

### Prerequisites

- **Python 3**: Used for converting Markdown content to JSON Resume format.
- **Node.js**: Used for generating the PDF using Puppeteer and a customized theme.

### Steps

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Generate Resume**:
   Run the orchestration script that handles the conversion and PDF generation:
   ```bash
   python3 build_resume.py
   ```

### Output

The build process will create a `build/` directory containing:
- `resume.json`: The CV in standard JSON Resume format.
- `resume.pdf`: The final PDF version of the resume.

---

## Continuous Integration & Deployment

### Automatic Build
Every time changes are pushed to the `main` branch, a GitHub Action is triggered to:
1. Parse the latest Markdown content.
2. Generate an updated `resume.pdf`.
3. Upload the PDF as a **workflow artifact** for easy download.

### Live Website
The website at **[https://saleh.fi](https://saleh.fi)** is automatically updated upon pushing. The site is built using Hugo and deployed via Netlify, ensuring the web version always reflects the latest changes in the repository.
