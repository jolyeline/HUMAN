from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

GECKO = r"C:\Users\joly-\Github\HUMAN\tweede_kamer\scraping_plen_ver\geckodriver.exe"
BASE = "https://www.tweedekamer.nl"
LIST_URL = ("https://www.tweedekamer.nl/kamerstukken"
            "?fld_tk_categorie=Kamerstukken"
            "&fromdate=01/01/2015"
            "&qry=%2A"
            "&srt=date%3Adesc%3Adate"
            "&todate=31/08/2025"
            "&page={page}")

opts = Options()
opts.add_argument("--headless")
driver = webdriver.Firefox(service=Service(GECKO), options=opts)
wait = WebDriverWait(driver, 15)

out, seen = [], set()

try:
    for page in range(0, 200):
        url = LIST_URL.format(page=page)
        print(f"[INFO] Page {page+1} → {url}")
        driver.get(url)
        try:                                          # ← fixed indentation (was one space too many)
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'a[href*="/kamerstukken/detail?id="]')
            ))
        except:
            print(f"[INFO] No results on page {page+1}, stopping.")
            break
        soup = BeautifulSoup(driver.page_source, "lxml")
        for a in soup.select('a[href*="/kamerstukken/detail?id="]'):
            href = a.get("href")
            if not href:
                continue
            full = urljoin(BASE, href)
            title = (a.get_text() or "").strip()
            if full in seen:
                continue
            seen.add(full)
            out.append({"url": full, "title": title})
            print(out[-1])
finally:
    driver.quit()

with open("beleidsstukken_search.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(f"[INFO] Saved {len(out)} records")