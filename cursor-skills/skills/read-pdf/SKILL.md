---
name: read-pdf
description: Extract text from PDF files into readable .md files so agents without native PDF input can read them. Use when the user asks to read, summarize, or learn from a PDF and PDF reading fails or is unsupported, or when they mention converting/extracting PDF text.
---

# Read PDF

This environment's model cannot ingest PDF binary content. Workaround: extract the text to a `.md` file with pypdf (Python), then Read the extracted file.

## Workflow

1. Verify the PDF path exists.
2. Run the bundled extractor (creates `<pdfname>.extracted.md` next to the PDF, or in the given output dir):

   ```
   python "%USERPROFILE%\.claude\skills\read-pdf\extract_pdf.py" "C:\path\to\file.pdf" [-o OUTDIR]
   ```

   - Multiple PDFs may be passed in one call.
   - If pypdf is missing, install it first: `pip install pypdf`.
3. Read the produced `.extracted.md` file with the normal Read tool.
4. If extraction yields empty/garbled text, the PDF is likely scanned images. Tell the user OCR is needed (no OCR tool is configured by default).

## Output format

Each page is emitted as:

```
## Page N
<text>
```

A header line records the source file and page count. Pages with no extractable text are marked `[no extractable text]` (image-only page).

## Notes

- Scanned/image PDFs need OCR — not handled by this skill.
- Very large PDFs: the extracted .md may exceed Read's default window; use offset/limit paging.
