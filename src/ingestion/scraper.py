"""
Web scraper for fetching mutual fund scheme data from Groww.
Reads URLs from data/urls.json, fetches the HTML content, and saves it
to data/raw/ along with metadata.
"""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from src.config import URLS_FILE, RAW_DATA_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Common headers to avoid basic scraping blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def load_corpus_urls() -> list[dict]:
    """Load the corpus definition from urls.json."""
    if not URLS_FILE.exists():
        logger.error(f"URLs file not found at {URLS_FILE}")
        return []
        
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("corpus", [])


def sanitize_filename(name: str) -> str:
    """Convert a scheme name to a safe filename."""
    return "".join(c if c.isalnum() else "_" for c in name.lower()).strip("_")


def scrape_url(url: str) -> str | None:
    """Fetch HTML content from a URL with basic error handling."""
    try:
        logger.info(f"Fetching: {url}")
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None


def run_scraper() -> None:
    """Run the scraping process for all URLs in the corpus."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    corpus = load_corpus_urls()
    if not corpus:
        logger.warning("No URLs found to scrape.")
        return

    success_count = 0
    for item in corpus:
        scheme_name = item["scheme_name"]
        url = item["url"]
        
        html_content = scrape_url(url)
        
        if html_content:
            # Create a combined payload with metadata and raw HTML
            payload = {
                "source_url": url,
                "scheme_name": scheme_name,
                "category": item.get("category"),
                "plan": item.get("plan"),
                "scrape_date": datetime.now(timezone.utc).isoformat(),
                "html": html_content
            }
            
            filename = f"{sanitize_filename(scheme_name)}.json"
            output_path = RAW_DATA_DIR / filename
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Saved raw data to {output_path.name}")
            success_count += 1
            
        # Be polite and wait between requests
        time.sleep(2)
        
    logger.info(f"Scraping completed: {success_count}/{len(corpus)} successful.")


if __name__ == "__main__":
    run_scraper()
