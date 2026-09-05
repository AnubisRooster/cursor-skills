---
name: web-crawl
description: >
  Crawl an external website to discover and log bugs.
  Fetches pages, extracts links, follows navigation up to a configurable depth,
  and flags pages whose titles/URLs contain bug-related keywords.
  Outputs a CSV of discovered pages with bug-indicator, title, and source URL.
disable-model-invocation: true
---

# /web-crawl

Crawl an external website to discover and log bugs.

## Usage

```
/web-crawl <url>                           # crawl start URL (default depth 3, max 50 pages)
/web-crawl <url> --max-pages N           # stop after N pages
/web-crawl <url> --max-depth N           # stop following links at depth N
/web-crawl <url> --bug-keywords "kw1,kw2" # only flag pages with these words in title/URL
/web-crawl <url> --no-recurse            # only fetch the start URL, no link following
```

## What it does

1. **Fetches** the start URL (and optional follow-up pages) using the web fetch tool
2. **Extracts** all hyperlinks (`<a href>`) from each page
3. **Follows** links up to `--max-depth` or until `--max-pages` is reached
4. **Flags** pages whose `<title>` or URL contains any of the `--bug-keywords` (default: `bug,issue,fix,todo,changelog`)
5. **Writes** a CSV file `web-crawl-results.csv` in the current directory with columns:
   - `depth` — link hop number (0 = start URL)
   - `url` — the page URL
   - `title` — `<title>` tag content, or fallback `Untitled`
   - `bug-indicator` — `YES` if any bug keyword matched, `NO` otherwise
   - `source` — the URL where the link was discovered

## How to use

1. Invoke `/web-crawl https://example.com --max-pages 20 --bug-keywords "bug,issue,task"`
2. The skill writes `web-crawl-results.csv` to the current working directory
3. Open the CSV to review discovered pages; rows with `bug-indicator=YES` are likely bug-related
4. Re-run with different keywords or a deeper max-depth to broaden/narrow the scan

## Tips

- External sites may block aggressive crawling; keep `--max-pages` moderate (20–50) and `--max-depth` low (2–3)
- If a page requires JavaScript rendering, this skill cannot see it — it only reads static HTML
- Use `--no-recurse` to just validate the start URL's title/links without following anything
- The CSV can be imported into spreadsheets, databases, or issue trackers

## Caveats

- Only follows `<a href>` links; does not render CSS/JS or interact with forms
- Respects robots.txt implicitly (no guarantee) — keep crawling responsible
- Same-domain only: links pointing outside the start URL's host are ignored to avoid infinite cross-site crawling
- If `--bug-keywords` match only the URL path (not the title), consider using more specific terms that appear in bug trackers
## Crawling JavaScript SPAs

Static fetches return an empty shell for React/Vue/Angular sites (no links, no
content - just a <div id=\"root\">). For those, use the companion Playwright
renderer crawl_spa.py in this folder:

```powershell
python crawl_spa.py https://corp.example.com ./example-crawl 30
```

- Requires pip install playwright && playwright install chromium
- Renders each route headlessly, extracts main-content text, follows same-host
  links BFS, and saves one markdown file per page (with YAML frontmatter:
  title, url, captured_at) plus a manifest.json - ready for graphify ingestion.
- Choose by site type: web-crawl.ps1 for server-rendered sites, crawl_spa.py
  when the first fetch returns an empty shell.
