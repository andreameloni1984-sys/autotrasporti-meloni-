import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from config import REQUEST_TIMEOUT
from filters import analyze
from database import add_opportunity, init_db
from sources import SOURCES

USER_AGENT = "Autotrasporti-Meloni/2.0"
MAX_LINKS_PER_SOURCE = 25
MAX_DEEP_PAGES = 8


def _same_domain(a, b):
    return urlparse(a).netloc == urlparse(b).netloc


def _page_links(base_url, soup):
    links = []
    seen = set()
    for link in soup.find_all("a", href=True):
        href = urljoin(base_url, link["href"]).split("#")[0]
        title = link.get_text(" ", strip=True)
        if not title or len(title) < 8:
            continue
        if not href.startswith(("http://", "https://")) or not _same_domain(base_url, href):
            continue
        if href in seen:
            continue
        seen.add(href)
        links.append((title, href))
        if len(links) >= MAX_LINKS_PER_SOURCE:
            break
    return links


def _extract_candidates(page_url, soup):
    candidates = []

    page_title = soup.title.get_text(" ", strip=True) if soup.title else ""
    for tag in soup.find_all(["h1", "h2", "h3"]):
        text = tag.get_text(" ", strip=True)
        if text and len(text) >= 10:
            candidates.append((text, page_url))

    for link in soup.find_all("a", href=True):
        title = link.get_text(" ", strip=True)
        href = urljoin(page_url, link["href"]).split("#")[0]
        if title and len(title) >= 10 and href.startswith(("http://", "https://")):
            candidates.append((title, href))

    if page_title:
        candidates.append((page_title, page_url))

    return candidates


def _scan_page(url, source_name, visited):
    if url in visited:
        return 0, []
    visited.add(url)

    try:
        r = requests.get(url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT})
        r.raise_for_status()
    except requests.RequestException:
        return 0, []

    soup = BeautifulSoup(r.text, "html.parser")
    inserted = 0
    discovered = _page_links(url, soup)

    for title, href in _extract_candidates(url, soup):
        result = analyze(title)
        if not result["relevant"]:
            continue
        if add_opportunity(
            title=title,
            url=href,
            source=source_name,
            categories=result["categories"],
            score=result["score"]
        ):
            inserted += 1

    return inserted, discovered


def scan_source(source):
    visited = set()
    queue = list(source.get("discovery_urls", []))
    queue.insert(0, source["url"])
    inserted = 0
    deep_pages = 0

    while queue and deep_pages < MAX_DEEP_PAGES + 1:
        url = queue.pop(0)
        if url in visited:
            continue

        added, links = _scan_page(url, source["name"], visited)
        inserted += added
        deep_pages += 1

        for _, href in links:
            if href not in visited and href not in queue:
                queue.append(href)
            if len(queue) > MAX_LINKS_PER_SOURCE:
                queue = queue[:MAX_LINKS_PER_SOURCE]

    return inserted


def run_scan():
    init_db()
    total = 0
    for source in SOURCES:
        total += scan_source(source)
    return total


if __name__ == "__main__":
    print(f"Nuove opportunità trovate: {run_scan()}")