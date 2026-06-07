# DOCX Text Extraction (Sandbox-Compatible)

When a user shares a `.docx` file and you need to extract its text content for processing (e.g., summarizing, reformatting, writing to Notion), `python-docx` is often **not available** in the sandbox environment.

## Working Fallback: unzip + xml.dom.minidom

```bash
# 1. Copy file to /tmp to avoid path issues
cp "/path/to/file.docx" /tmp/target.docx

# 2. Unzip the DOCX (it's a zip archive)
unzip -o /tmp/target.docx -d /tmp/docx_extracted/ > /dev/null 2>&1

# 3. Parse the XML with Python stdlib
python3 -c "
import xml.dom.minidom
with open('/tmp/docx_extracted/word/document.xml') as f:
    doc = xml.dom.minidom.parseString(f.read())
print(doc.toprettyxml(indent='  ')[:50000])
"
```

## Key Notes

- **DO NOT** use `pip install python-docx --break-system-packages` in sandbox — it installs to the wrong Python environment. The sandbox uses a separate venv; the installed module won't be found.
- **Use terminal tool** for this workflow, not execute_code sandbox, since terminal has access to the full filesystem and can run unzip natively.
- `python-docx` via terminal may work if you install it correctly: `pip install python-docx -q --break-system-packages` (try this first if unzip approach is too slow for large files).
- The XML output contains all paragraph text but **loses formatting** (bold, italic, headings). Strip tags and read plain `.text` for content-only extraction.

## When to Use This vs. python-docx

| Scenario | Tool |
|----------|------|
| python-docx available | `python-docx` (preserves styles) |
| python-docx unavailable | `unzip + xml.dom.minidom` |
| Need styles preserved | `python-docx` only |
| Content-only extraction | Either works, prefer unzip fallback |

## Quick Verify
```bash
# Check if python-docx is importable
python3 -c "from docx import Document; print('ok')" 2>&1
# If "ModuleNotFoundError" → use unzip fallback
```