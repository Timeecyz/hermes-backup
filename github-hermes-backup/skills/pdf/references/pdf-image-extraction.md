# PDF Image Extraction: What Works and What Doesn't

## The Problem

Extracting images (especially full-page renders) from vector-based PDFs via PDF libraries alone is unreliable. The PDF may:
- Contain embedded JPEG *streams* (DCTDecode filter) that aren't valid standalone JPEG files
- Have corrupt headers when extracted naively (extraneous bytes before markers)
- Use vector graphics rather than raster images at all

## What DOESN'T work

| Approach | Why it fails |
|----------|-------------|
| `pdf-lib` + raw JPEG offset extraction | JPEG streams have corrupt headers outside PDF context |
| `sharp` on extracted "JPEG" buffers | VipsJpeg: Corrupt JPEG data (DCTDecode produces malformed standalone JPEGs) |
| `pdfimages` CLI | Often not installed, can't rely on it |
| `pypdf` / `pdfplumber` text extract | Only gives text, not images |
| `python-docx` | Wrong format entirely |

## What WORKS

### Option 1: Playwright headless browser (recommended for reliability)

```javascript
// Serve PDF via local HTTP server, render with Playwright
const { chromium } = require('playwright');
const http = require('http');
const fs = require('fs');
const path = require('path');

// Serve PDF files
const server = http.createServer((req, res) => {
  const file = path.join('/tmp', req.url);
  res.setHeader('Content-Type', 'application/pdf');
  fs.createReadStream(file).pipe(res);
});
server.listen(8765);

// Screenshot each page
const browser = await chromium.launch();
const page = await browser.newPage();
await page.setViewportSize({ width: 1440, height: 900 });
for (let i = 5; i <= 16; i++) {
  await page.goto(`http://localhost:8765/page_${i}.pdf`, { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(2000);
  const screenshot = await page.screenshot({ type: 'jpeg', quality: 80 });
  fs.writeFileSync(`/tmp/page_${i}.jpg`, screenshot);
}
await browser.close();
```

**Key gotcha:** `page.goto(file://...)` triggers download — use HTTP server instead.

### Option 2: pdf-lib + copyPages to single-page PDFs

```javascript
const { PDFDocument } = require('pdf-lib');
const fs = require('fs');

const pdf = await PDFDocument.load(fs.readFileSync('input.pdf'));
const pages = pdf.getPages();

// Extract pages 5-16 (0-indexed: 4-15)
for (let i = 4; i < Math.min(16, pages.length); i++) {
  const newPdf = await PDFDocument.create();
  const [copied] = await newPdf.copyPages(pdf, [i]);
  newPdf.addPage(copied);
  fs.writeFileSync(`/tmp/page_${i+1}.pdf`, await newPdf.save());
}
```

### Option 3: pdf.js in Node (for text extraction)

```javascript
// pdf.js (not pdf-lib) can extract text and annotations
const pdfjsLib = require('pdfjs-lib');
const doc = await pdfjsLib.getDocument('input.pdf').promise;
for (let i = 1; i <= doc.numPages; i++) {
  const page = await doc.getPage(i);
  const content = await page.getTextContent();
  console.log(`Page ${i}:`, content.items.map(x => x.str).join(' '));
}
```

## Practical workflow for PDF page screenshots

1. Split PDF into single-page PDFs with `pdf-lib` (copyPages approach)
2. Serve via `python3 -m http.server` (background)
3. Use Playwright to navigate and screenshot each page
4. Resize with `sharp` if needed

```bash
# Step 1: Extract pages
node -e "
const { PDFDocument } = require('pdf-lib');
const fs = require('fs');
(async()=>{
  const pdf = await PDFDocument.load(fs.readFileSync('input.pdf'));
  for(let i=4;i<16;i++){
    const np=await PDFDocument.create();
    const[c]=await np.copyPages(pdf,[i]);
    np.addPage(c);
    fs.writeFileSync('/tmp/page_'+(i+1)+'.pdf',await np.save());
  }
})();
"

# Step 2: Serve
cd /tmp && python3 -m http.server 8765 &

# Step 3: Screenshot with Playwright (see Option 1 above)

# Step 4: Resize
node -e "
const sharp=require('sharp');
for(let i=5;i<=16;i++){
  sharp('/tmp/page_'+i+'.jpg')
    .resize(800,null,{fit:'inside'})
    .jpeg({quality:85})
    .toFile('/tmp/resized_'+i+'.jpg');
}
"
```

## Session context (May 2026)

Tested on: `/home/agentuser/.hermes/cache/documents/doc_ff9bdf78a595_（7月7日发团）启富未来-深港科创亲子研学营4天3晚.pdf`
- 20-page PDF, pages 5-16 needed
- Available Node modules: `playwright@1.59.1`, `sharp`, `pdfjs-dist@5.7.284`, `pdf-lib`
- Available Python: basic stdlib, NO pymupdf/pillow/pypdf (not installed)
- Chromium headless PDF rendering behavior: `file://` URLs trigger download guard (net::ERR_ABORTED); `data:application/pdf;base64,...` also triggers download; even HTTP server approach may trigger download depending on Chromium flags and PDF Content-Disposition header

### Approaches that failed in this environment

| Approach | Error/Behavior |
|----------|---------------|
| Playwright `page.goto('file://...')` | `page.goto: Download is starting` — Chromium download guard intercepts |
| Playwright `page.goto('data:application/pdf;base64,...')` | `net::ERR_ABORTED` — data URL treated as downloadable |
| HTTP server + `Content-Disposition: inline` | Still triggers download guard in some Chromium headless configs |
| `sharp` on PDF buffer | `Input buffer contains unsupported image format` — sharp doesn't decode PDF pages |
| pdfjs-dist legacy build in Node | `DOMMatrix is not defined` — pdfjs needs browser DOM polyfills |
| `canvas` module | Not installed in this environment |
| `pip install pymupdf` | Times out / environment managed |
| `pip install pillow` | Times out / environment managed |

### What to try next

1. **Playwright with `--enable-features=PDFViewer` and explicit navigation to the HTTP-served PDF** — try navigating to the PDF URL (not object/embed HTML wrapper) with proper `waitUntil: 'networkidle'` and longer wait
2. **Use `--enable-in-browsing-pdf` Chromium flag** combined with HTTP server serving single-page PDFs via `/page_N.pdf` path
3. **HTML wrapper with `pdf.js` viewer** — inject pdf.js web viewer (hosted externally) and load PDF via that
4. **Manual screenshot** — if automated approaches keep failing, ask the user to open the PDF locally and screenshot pages 5-16

### Reliable script pattern (when Chromium PDF rendering works)

The `scripts/pdf-page-screenshot.js` script uses this sequence:
1. Split PDF into single-page PDFs with `pdf-lib`
2. Serve via in-process HTTP server (port 8765)
3. Playwright navigates to each page's URL (not file://)
4. Wait 1500ms for render, screenshot as JPEG
5. Resize with `sharp`

```bash
node /home/agentuser/.hermes/hermes-agent/node_modules/agent-browser/../..  # check playwright path
```

**Available executables in this environment:**
- Node: `/usr/local/bin/node` (v22.22.2)
- Python: `/home/agentuser/.hermes/hermes-agent/venv/bin/python3` (3.11.15, 234 packages)
- Playwright browsers: pre-installed at `~/.cache/ms-playwright/`
