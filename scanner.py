import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from config import REQUEST_TIMEOUT, MAIN_CATEGORIES
from filters import analyze
from database import add_opportunity, init_db
from sources import SOURCES

USER_AGENT = "Autotrasporti-Meloni/3.0"
MAX_LINKS_PER_SOURCE = 35
MAX_DEEP_PAGES = 10
PRIORITY_DEEP_PAGES = 18
TARGET_TERMS = ("bando","bandi","agevol","incentiv","contribut","finanzi","credito","rimborso","accisa","gasolio","autotrasport","trasporto","artigian","impresa","investiment","veicol","camion","rimessa","capannon","energia","fotovolta","formazione","lavoro","pedaggi","porto","logistica","sardegna","sipes","de minimis","domande","scadenza","avviso","misura")
LAST_SCAN_ERRORS = []

def _same_domain(a,b): return urlparse(a).netloc == urlparse(b).netloc
def _clean(text): return re.sub(r"\s+"," ",text or "").strip()
def _priority(title,href):
    value=f"{title} {href}".lower()
    return sum(1 for term in TARGET_TERMS if term in value)

def _page_links(base_url,soup):
    links=[]; seen=set()
    for link in soup.find_all("a",href=True):
        href=urljoin(base_url,link["href"]).split("#")[0]
        title=_clean(link.get_text(" ",strip=True))
        if len(title)<5 or not href.startswith(("http://","https://")) or not _same_domain(base_url,href) or href in seen: continue
        seen.add(href); links.append((title,href))
    links.sort(key=lambda item:_priority(*item),reverse=True)
    return links[:MAX_LINKS_PER_SOURCE]

def _visible_text(soup):
    for tag in soup(["script","style","noscript","svg"]): tag.decompose()
    return _clean(soup.get_text(" ",strip=True))

def _extract_date(text):
    low=text.lower()
    patterns=[r"(?:scadenza|chiusura|entro|domande.*?fino).*?(\d{1,2}[/-]\d{1,2}[/-]\d{4})",r"(?:scadenza|chiusura).*?(\d{1,2}\s+(?:gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+\d{4})"]
    for pattern in patterns:
        match=re.search(pattern,low,re.I)
        if match: return match.group(1)
    return ""

def _extract_benefit(text):
    found=[]
    for match in re.finditer(r"(?:€|euro)\s?[\d\.,]+|\d{1,3}%[^.]{0,80}",text,re.I):
        found.append(match.group(0).strip())
        if len(found)>=3: break
    return "; ".join(found)

def _extract_status(text):
    low=text.lower()
    if any(x in low for x in ("domande aperte","presentazione delle domande","istanza potrà essere presentata","apertura dello sportello")): return "APERTO"
    if any(x in low for x in ("chiuso","scaduto","scadenza superata")): return "SCADUTO"
    return "DA VERIFICARE"

def _best_title(soup,fallback):
    for tag in soup.find_all(["h1","h2"]):
        value=_clean(tag.get_text(" ",strip=True))
        if len(value)>=15: return value[:500]
    if soup.title:
        value=_clean(soup.title.get_text(" ",strip=True))
        if len(value)>=15: return value[:500]
    return fallback[:500]

def _main_category(text):
    low=(text or "").lower()
    scores={k:sum(1 for term in terms if term in low) for k,terms in MAIN_CATEGORIES.items()}
    return max(scores,key=scores.get) if scores and max(scores.values())>0 else "altro"

def _scan_page(url,source_name,visited):
    if url in visited: return 0,[]
    visited.add(url)
    try:
        response=requests.get(url,timeout=REQUEST_TIMEOUT,headers={"User-Agent":USER_AGENT},allow_redirects=True)
        response.raise_for_status()
    except requests.RequestException as exc:
        LAST_SCAN_ERRORS.append(f"{source_name}: {url} -> {type(exc).__name__}")
        return 0,[]
    if "html" not in response.headers.get("content-type","").lower(): return 0,[]
    soup=BeautifulSoup(response.text,"html.parser")
    page_text=_visible_text(soup)
    page_title=_best_title(soup,source_name)
    discovered=_page_links(response.url,soup)
    result=analyze(f"{page_title} {page_text[:12000]}")
    inserted=0
    if result["relevant"]:
        if add_opportunity(title=page_title,url=response.url,source=source_name,categories=result["categories"],score=result["score"],deadline=_extract_date(page_text),status=_extract_status(page_text),benefit=_extract_benefit(page_text),requirements=page_text[:1200],main_category=_main_category(f"{page_title} {page_text}")):
            inserted+=1
    return inserted,discovered

def scan_source(source):
    visited=set(); queue=[]
    for url in source.get("priority_urls",[]): queue.append((100,url))
    for url in source.get("discovery_urls",[]): queue.append((90,url))
    queue.append((80,source["url"]))
    inserted=0; pages=0
    limit=PRIORITY_DEEP_PAGES if source.get("priority") else MAX_DEEP_PAGES
    while queue and pages<limit:
        queue.sort(key=lambda item:item[0],reverse=True)
        _,url=queue.pop(0)
        if url in visited: continue
        added,links=_scan_page(url,source["name"],visited)
        inserted+=added; pages+=1
        for title,href in links:
            if href in visited: continue
            priority=_priority(title,href)
            if priority: queue.append((priority,href))
        if len(queue)>MAX_LINKS_PER_SOURCE:
            queue.sort(key=lambda item:item[0],reverse=True); queue=queue[:MAX_LINKS_PER_SOURCE]
    return inserted

def run_scan():
    global LAST_SCAN_ERRORS
    LAST_SCAN_ERRORS=[]
    init_db(); total=0
    for source in SOURCES: total+=scan_source(source)
    print(f"Scanner: nuove opportunità={total}; errori={len(LAST_SCAN_ERRORS)}")
    for error in LAST_SCAN_ERRORS[:10]: print(f"Scanner error: {error}")
    return total

def get_last_scan_errors(): return list(LAST_SCAN_ERRORS)

if __name__=="__main__": print(f"Nuove opportunità trovate: {run_scan()}")
