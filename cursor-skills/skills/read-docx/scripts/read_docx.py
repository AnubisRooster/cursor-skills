#!/usr/bin/env python3
"""Extract text, headings, and tables from a .docx file. Stdlib-only (no pip installs)."""
import sys
import zipfile
import re
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
DC = "{http://purl.org/dc/elements/1.1/}"
CP = "{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}"


def text_of(el):
    parts = []
    for node in el.iter():
        if node.tag == W + "t":
            parts.append(node.text or "")
        elif node.tag == W + "tab":
            parts.append("\t")
        elif node.tag in (W + "br", W + "cr"):
            parts.append("\n")
    return "".join(parts)


def style_of(p):
    ps = p.find(W + "pPr/" + W + "pStyle")
    return ps.get(W + "val", "") if ps is not None else ""


def para_md(p):
    text = text_of(p).strip()
    if not text:
        return ""
    style = style_of(p)
    m = re.match(r"[Hh]eading(\d)", style)
    if m:
        return "#" * int(m.group(1)) + " " + text
    if style.lower() == "title":
        return "# " + text
    return text


def cell_text(tc):
    parts = [text_of(p).strip() for p in tc.findall(W + "p")]
    return "<br>".join(x for x in parts if x).replace("|", "\\|")


def table_md(tbl):
    rows = []
    for tr in tbl.findall(W + "tr"):
        cells = [cell_text(tc) for tc in tr.findall(W + "tc")]
        if cells:
            rows.append(cells)
    if not rows:
        return ""
    lines = ["| " + " | ".join(rows[0]) + " |",
             "| " + " | ".join(["---"] * len(rows[0])) + " |"]
    for r in rows[1:]:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines)


def read_meta(z):
    meta = []
    try:
        core = ET.fromstring(z.read("docProps/core.xml"))
    except KeyError:
        return meta
    for tag, label in ((DC + "title", "Title"), (DC + "creator", "Author"),
                       (CP + "lastModifiedBy", "Last modified by")):
        el = core.find(tag)
        if el is not None and el.text:
            meta.append(f"{label}: {el.text}")
    return meta


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) < 2:
        print("usage: python read_docx.py <file.docx>", file=sys.stderr)
        sys.exit(2)
    path = sys.argv[1]
    try:
        z = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as e:
        print(f"error: cannot open {path}: {e}", file=sys.stderr)
        print("hint: old .doc (binary) files are not ZIP; use Word COM automation instead",
              file=sys.stderr)
        sys.exit(1)
    with z:
        meta = read_meta(z)
        try:
            doc = ET.fromstring(z.read("word/document.xml"))
        except KeyError:
            print("error: not a valid .docx (word/document.xml missing)", file=sys.stderr)
            sys.exit(1)
        body = doc.find(W + "body")
        blocks = []
        if body is not None:
            for child in body:
                if child.tag == W + "p":
                    blocks.append(para_md(child))
                elif child.tag == W + "tbl":
                    blocks.append(table_md(child))
                elif child.tag == W + "sdt":
                    for p in child.iter(W + "p"):
                        blocks.append(para_md(p))
                    for tbl in child.iter(W + "tbl"):
                        blocks.append(table_md(tbl))
        text = "\n\n".join(b for b in blocks if b)
    if meta:
        print("<!-- " + " | ".join(meta) + " -->")
    print(text)


if __name__ == "__main__":
    main()
