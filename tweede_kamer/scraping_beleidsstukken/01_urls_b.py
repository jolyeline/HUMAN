"""
Fetch beleidsstukken from the Rijksoverheid Open Data API.
No browser / Selenium needed — plain HTTP requests.

API docs: https://www.rijksoverheid.nl/opendata/documenten

Output: beleidsstukken.json
"""

import json
import time
import requests
from datetime import datetime

# ── Configuration ────────────────────────────────────────────────────────────

BASE_URL    = "https://opendata.rijksoverheid.nl/v1/documents"
DOC_TYPE    = "beleidsnota"          # infotype value for beleidsstukken
DATE_FROM   = "20150101"             # lastmodifiedsince  (YYYYMMDD)
DATE_TO     = "20250831"             # we filter this ourselves after fetching
ROWS        = 200                    # max allowed per request
OUTPUT_FILE = "beleidsstukken.json"
SLEEP_SEC   = 0.5                    # pause between requests (be polite)

# ── Helpers ──────────────────────────────────────────────────────────────────

def parse_date(s: str) -> datetime | None:
    """Parse ISO-ish date strings returned by the API."""
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s[:19], fmt)
        except (ValueError, TypeError):
            pass
    return None


def fetch_page(offset: int, session: requests.Session) -> dict:
    params = {
        "type":              DOC_TYPE,
        "lastmodifiedsince": DATE_FROM,
        "rows":              ROWS,
        "offset":            offset,
        "output":            "json",
    }
    r = session.get(BASE_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    session   = requests.Session()
    session.headers.update({"User-Agent": "beleidsstukken-scraper/1.0"})

    cutoff    = datetime.strptime(DATE_TO, "%Y%m%d")
    out       = []
    seen      = set()
    offset    = 0
    page      = 0
    stop_early = False

    while True:
        page += 1
        print(f"[INFO] Page {page}  (offset={offset})")

        try:
            data = fetch_page(offset, session)
        except requests.HTTPError as e:
            print(f"[ERROR] HTTP error: {e}")
            break

        # The API returns a list of document dicts at the top level
        docs = data if isinstance(data, list) else data.get("documents", [])

        if not docs:
            print("[INFO] Empty page — done.")
            break

        for doc in docs:
            uid   = doc.get("id") or doc.get("canonicallink", "")
            if uid in seen:
                continue

            # Date filter: skip anything modified after our cutoff
            mod_str = doc.get("lastmodified") or doc.get("available") or ""
            mod_dt  = parse_date(mod_str)
            if mod_dt and mod_dt > cutoff:
                continue  # too recent for our window — keep going

            seen.add(uid)
            record = {
                "id":           uid,
                "title":        doc.get("title", "").strip(),
                "type":         doc.get("type", ""),
                "lastmodified": mod_str,
                "url":          doc.get("canonicallink", ""),
                "dataurl":      doc.get("dataurl", ""),
                "introduction": doc.get("introduction", ""),
            }
            out.append(record)
            print(f"  → {record['lastmodified'][:10]}  {record['title'][:80]}")

        # If the page returned fewer rows than requested, we've hit the end
        if len(docs) < ROWS or stop_early:
            print("[INFO] Last page reached — done.")
            break

        offset += ROWS
        time.sleep(SLEEP_SEC)

    # ── Save ─────────────────────────────────────────────────────────────────
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n[INFO] Saved {len(out)} records to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()