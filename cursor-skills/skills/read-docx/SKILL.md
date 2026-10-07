---
name: read-docx
description: Extract text, headings, and tables from Microsoft Word .docx files without opening Word. Use when the user provides, mentions, or asks to read a Word document, .docx file, or asks "can you read Word files" — also for summarizing, searching, or extracting content from .docx attachments.
---

# Read Word Files (.docx)

A .docx is a ZIP archive containing XML. Extract content with the bundled script — it needs only the Python standard library (no pip installs).

## Primary method: bundled script

Execute (do not rewrite) the script, using forward slashes in paths:

```bash
python scripts/read_docx.py <path/to/file.docx>
```

Output: document metadata as an HTML comment, then body content — headings as markdown `#`, tables as markdown tables, paragraphs as plain text.

## Fallback: PowerShell (when Python is unavailable)

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead("<path/to/file.docx>")
$entry = $zip.GetEntry("word/document.xml")
$sr = New-Object System.IO.StreamReader($entry.Open())
$xml = [xml]$sr.ReadToEnd(); $sr.Close(); $zip.Dispose()
$ns = New-Object System.Xml.XmlNamespaceManager($xml.NameTable)
$ns.AddNamespace("w", "http://schemas.openxmlformats.org/wordprocessingml/2006/main")
$xml.SelectNodes("//w:p", $ns) | ForEach-Object {
  ($_.SelectNodes(".//w:t", $ns) | ForEach-Object { $_.InnerText }) -join ""
}
```

## When to use Word COM automation instead

MS Word is installed on this machine. Use COM (`New-Object -ComObject Word.Application`) only when the script output is insufficient:

- Old binary `.doc` files (not ZIP-based; the script will error)
- Content in headers/footers, footnotes/endnotes, text boxes
- Tracked changes and comments (the script excludes deleted text by design)

## Known limitations

- List numbering/bullets are not reconstructed (text is extracted without the number/character)
- Images are ignored (mention `[image]` only if layout context demands it)
