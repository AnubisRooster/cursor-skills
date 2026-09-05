#!/usr/bin/env python3
"""crawl_spa.py - Render a JS SPA with Playwright, crawl same-host routes BFS,
save each page as markdown (with frontmatter) into an output dir for graphify."""
import sys, os, time, json, re
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

START = sys.argv[1] if len(sys.argv) > 1 else "https://corp.akolades.com"
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else "akolades-crawl"
MAX_PAGES = int(sys.argv[3]) if len(sys.argv) > 3 else 50

base = urlparse(START)
HOST = base.netloc
SCHEME = base.scheme

def same_host(url):
    u = urlparse(url)
    return u.netloc == HOST and u.scheme in ("http", "https")

def clean_text(el):
    txt = el.inner_text()
    txt = re.sub(r'\n{3,}', '\n\n', txt)
    return txt.strip()

def main():
    os.makedirs(OUTDIR, exist_ok=True)
    visited = {}
    queue = [START]
    manifest = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (compatible; crawler/1.0)")
        while queue and len(visited) < MAX_PAGES:
            url = queue.pop(0)
            if url in visited:
                continue
            try:
                page.goto(url, timeout=45000, wait_until="networkidle")
                page.wait_for_timeout(800)
            except Exception as e:
                manifest.append({"url": url, "status": "ERROR", "error": str(e)})
                visited[url] = "ERROR"
                continue
            title = page.title()
            # main content vs full body
            main_el = page.query_selector("main") or page.query_selector("body")
            text = clean_text(main_el) if main_el else ""
            slug = urlparse(url).path.strip("/") or "index"
            slug = re.sub(r'[^A-Za-z0-9_-]+', '_', slug).strip('_') or "index"
            md_path = os.path.join(OUTDIR, f"{slug}.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(f"---\ntitle: {title}\nurl: {url}\nsource: {url}\ncaptured_at: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n---\n\n")
                f.write(f"# {title}\n\n")
                f.write(text + "\n")
            manifest.append({"url": url, "status": "OK", "title": title, "file": md_path})
            visited[url] = "OK"
            # discover same-host links
            for a in page.query_selector_all("a[href]"):
                href = a.get_attribute("href")
                if not href or href.startswith("#"):
                    continue
                abs_url = urljoin(url, href)
                if same_host(abs_url) and abs_url not in visited:
                    clean = abs_url.split("#")[0]
                    if clean not in visited:
                        queue.append(clean)
            print(f"OK  {url} -> {title} ({len(text)} chars)")
        browser.close()
    with open(os.path.join(OUTDIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\nDone. Crawled {len(visited)} pages into {OUTDIR}")

if __name__ == "__main__":
    main()
