import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config import REQUEST_TIMEOUT
from filters import analyze
from database import add_opportunity, init_db
from sources import SOURCES

USER_AGENT = "Autotrasporti-Meloni/1.0"


def scan_source(source):
    try:
        r = requests.get(
            source["url"],
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT}
        )
        r.raise_for_status()
    except requests.RequestException:
        return 0

    soup = BeautifulSoup(r.text, "html.parser")
    inserted = 0

    for link in soup.find_all("a", href=True):
        title = link.get_text(" ", strip=True)
        href = urljoin(source["url"], link["href"])

        if not title or len(title) < 10:
            continue

        result = analyze(title)

        if not result["relevant"]:
            continue

        if add_opportunity(
            title=title,
            url=href,
            source=source["name"],
            categories=result["categories"],
            score=result["score"]
        ):
            inserted += 1

    return inserted


def run_scan():
    init_db()
    total = 0

    for source in SOURCES:
        total += scan_source(source)

    return total


if __name__ == "__main__":
    print(f"Nuove opportunità trovate: {run_scan()}")
