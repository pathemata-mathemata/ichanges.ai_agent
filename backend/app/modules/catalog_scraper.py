import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from typing import List, Optional, Dict
from urllib.parse import urlparse
from app.config import settings

def google_search_raw(query: str, num: int = 3) -> List[str]:
    service = build("customsearch", "v1", developerKey=settings.GOOGLE_API_KEY)
    res = service.cse().list(q=query, cx=settings.SEARCH_ENGINE_ID, num=num).execute()
    return [item["link"] for item in res.get("items", [])]

def find_institution_domain(institution_name: str) -> Optional[str]:
    query = f"{institution_name} official site"
    results = google_search_raw(query, num=3)
    for url in results:
        parsed = urlparse(url)
        domain = parsed.netloc
        if institution_name.lower().replace(' ', '') in domain.lower():
            return domain
    return urlparse(results[0]).netloc if results else None

def search_catalog_urls(course_code: str, domain: str, max_results: int = 3) -> List[str]:
    search_url = f"https://{domain}/search?q={course_code.replace(' ', '+')}"
    try:
        resp = requests.get(search_url, timeout=5)
        resp.raise_for_status()
    except:
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    links: List[str] = []
    for a in soup.select('a'):
        href = a.get('href')
        if not href:
            continue
        if href.startswith('/'):
            href = f"https://{domain}{href}"
        if domain in href and course_code.replace(' ', '').lower() in href.replace('/', '').lower():
            links.append(href)
            if len(links) >= max_results:
                break
    return links

def scrape_course_page(url: str, quarter: str) -> Optional[Dict]:
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        units_text   = soup.select_one(".course-units").get_text(strip=True)
        offered_text = soup.select_one(".term-offered").get_text(strip=True)
        instructors  = [li.get_text(strip=True) for li in soup.select(".instructor-list li")]
        return {
            "url":         url,
            "units":       float(units_text),
            "offered":     quarter.lower() in offered_text.lower(),
            "instructors": instructors,
        }
    except:
        return None

def find_course_info(course_code: str, quarter: str, origin_institution: str) -> Dict:
    domain = origin_institution
    if '.' not in domain:
        d = find_institution_domain(origin_institution)
        if d:
            domain = d
    urls = search_catalog_urls(course_code, domain)
    for link in urls:
        info = scrape_course_page(link, quarter)
        if info:
            return info
    return {"url": None, "units": None, "offered": False, "instructors": []}
