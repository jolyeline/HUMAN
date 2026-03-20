import os
import json
import time
import hashlib
import csv
from pathlib import Path
from urllib.parse import urlparse, unquote
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# =========================
# Config
# =========================
PAUSE_SECONDS = 0.4        # politeness delay between requests
MAX_RETRIES = 3
BACKOFF_FACTOR = 0.5
TIMEOUT = 30
DATA_DIR_NAME = "vergaderstukken_html"     # folder to store HTML
JSON_GLOB = "vergaderstukken.json"       # read all json files in this folder

# =========================
# Helpers
# =========================
def read_all_json_lists(folder: Path):
    """Read every JSON file in folder. Each JSON must be a list of dicts with 'url'."""
    items = []
    for p in folder.glob(JSON_GLOB):
        try:
            with p.open("r", encoding="utf-8") as f:
                obj = json.load(f)
            if isinstance(obj, list):
                items.extend(obj)
        except Exception as e:
            print(f"[WARN] Skipping {p.name}: {e}")
    return items

def unique_urls(items):
    """Yield unique URLs in original order."""
    seen = set()
    for it in items:
        url = (it.get("url") or it.get("dataurl")) if isinstance(it, dict) else None
        if not url or url in seen:
            continue
        seen.add(url)
        yield url

def slug_from_url(url: str) -> str:
    """
    Make a compact, filesystem-safe slug from the URL path.
    We also include an md5 of the full URL to guarantee uniqueness.
    """
    parsed = urlparse(url)
    # e.g., /kamerstukken/plenaire_verslagen/detail/b5d8f5bc-... -> take path parts
    path = unquote(parsed.path).strip("/")
    # keep only safe chars
    safe = []
    for ch in path:
        if ch.isalnum() or ch in ("-", "_"):
            safe.append(ch)
        elif ch in ("/", " "):
            safe.append("-")
        else:
            safe.append("_")
    base = "".join(safe).replace("--", "-")
    if not base:
        base = "index"
    # shorten but keep meaning
    base = base[:120].rstrip("-_")
    # md5 of full URL to avoid collisions (and differentiate querystrings if present)
    h = hashlib.md5(url.encode("utf-8")).hexdigest()[:8]
    return f"{base}_{h}"

def make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                       "Version/18.1.1 Safari/605.1.15"),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.8,nl;q=0.7",
    })
    retries = Retry(
        total=MAX_RETRIES,
        connect=MAX_RETRIES,
        read=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s

# =========================
# Main
# =========================
def main():
    here = Path(__file__).resolve().parent
    data_dir = here / DATA_DIR_NAME
    data_dir.mkdir(parents=True, exist_ok=True)
    error_log_path = here / "download_errors.csv"

    # 1) Load JSONs and collect URLs
    items = read_all_json_lists(here)
    urls = list(unique_urls(items))
    print(f"[INFO] Found {len(urls)} unique URLs from JSON files.")

    if not urls:
        print("[INFO] No URLs to download. Exiting.")
        return

    # 2) Session with retries
    session = make_session()

    # 3) Download loop
    errors = []
    for i, url in enumerate(urls, 1):
        slug = slug_from_url(url)
        out_path = data_dir / f"{slug}.html"

        if out_path.exists() and out_path.stat().st_size > 0:
            print(f"[{i}/{len(urls)}] Skip (exists): {url}")
            continue

        print(f"[{i}/{len(urls)}] GET {url}")
        try:
            r = session.get(url, timeout=TIMEOUT)
            # Some pages might redirect; keep final URL for traceability if needed
            if r.status_code == 200 and r.content:
                out_path.write_bytes(r.content)  # write exact bytes
                # be polite
                time.sleep(PAUSE_SECONDS)
            else:
                print(f"   -> Failed: HTTP {r.status_code}")
                errors.append((url, r.status_code, "empty" if not r.content else ""))
        except Exception as e:
            print(f"   -> Exception: {e}")
            errors.append((url, "", str(e)))

    # 4) Error log
    if errors:
        with error_log_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["url", "status_code", "error"])
            w.writerows(errors)
        print(f"[INFO] Logged {len(errors)} failures to {error_log_path}")
    else:
        print("[INFO] All downloads succeeded.")

    print(f"[INFO] HTML files stored in: {data_dir}")

if __name__ == "__main__":
    main()
