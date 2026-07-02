"""
Document preprocessor for mutual fund HTML data.
Strips boilerplate and extracts structured text.
"""
import json
import logging
import re
from pathlib import Path
from bs4 import BeautifulSoup

from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def clean_html(html: str) -> BeautifulSoup:
    """Parse HTML and remove unwanted tags."""
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove script, style, header, footer, nav
    for tag in soup.find_all(["script", "style", "header", "footer", "nav", "noscript", "svg"]):
        tag.decompose()
        
    # Remove specific generic header/footer classes if they exist
    for tag in soup.find_all("div", class_=re.compile("header|footer|nav", re.I)):
        tag.decompose()
        
    return soup


def extract_key_value_pairs(soup: BeautifulSoup) -> dict[str, str]:
    """Extract key-value pairs (like Expense ratio, Exit load)."""
    extracted = {}
    
    # Commonly sought fields in mutual fund pages
    fields = [
        "Expense ratio",
        "Exit load",
        "Min. for SIP",
        "Fund size (AUM)",
        "Rating",
        "NAV",
        "Age",
        "Lock-in"
    ]
    
    # Text is often organized where the label is in a div and the value is in a sibling div
    # Or in tables
    for field in fields:
        # Looking for text matching the field
        label_tag = soup.find(string=re.compile(f"^{field}", re.I))
        if label_tag:
            parent = label_tag.find_parent()
            if parent:
                # Often the value is in the next sibling or somewhere nearby
                # Try to get the next sibling div or span that contains text
                next_node = parent.find_next_sibling()
                if next_node:
                    val = next_node.get_text(strip=True)
                    if val:
                        extracted[field] = val
                        continue
                        
                # If not in sibling, maybe it's in the next td if it's a table
                if parent.name == "td":
                    next_td = parent.find_next_sibling("td")
                    if next_td:
                        extracted[field] = next_td.get_text(strip=True)
                        continue
    
    return extracted


def get_main_text(soup: BeautifulSoup) -> str:
    """Extract and normalize all visible text."""
    # Find main content container if possible
    main = soup.find("main") or soup.find(id="root") or soup
    
    text = main.get_text(separator="\n", strip=True)
    
    # Normalize whitespace
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    # Filter out likely navigation links (very short words, generic terms)
    # This is a heuristic
    filtered_lines = []
    ignore_exact = {"Stocks", "Mutual Funds", "F&O", "More", "Invest in Stocks", "Compare Funds"}
    
    for line in lines:
        if line in ignore_exact:
            continue
        filtered_lines.append(line)
        
    return "\n".join(filtered_lines)


def process_file(file_path: Path):
    """Read raw JSON, process it, and save to processed dir."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    html = data.get("html", "")
    if not html:
        logger.warning(f"No HTML found in {file_path}")
        return
        
    soup = clean_html(html)
    
    # Extract structural properties
    kv_pairs = extract_key_value_pairs(soup)
    
    # Get all clean text
    clean_text = get_main_text(soup)
    
    # We can format the output document cleanly
    output_lines = [
        f"Scheme Name: {data['scheme_name']}",
        f"Category: {data['category']}",
        f"Plan: {data['plan']}",
        f"Source URL: {data['source_url']}",
        f"Last Scraped: {data['scrape_date']}",
        ""
    ]
    
    if kv_pairs:
        output_lines.append("## Key Details")
        for k, v in kv_pairs.items():
            output_lines.append(f"- {k}: {v}")
        output_lines.append("")
        
    output_lines.append("## Detailed Information")
    output_lines.append(clean_text)
    
    final_text = "\n".join(output_lines)
    
    # Prepare payload
    processed_data = {
        "source_url": data["source_url"],
        "scheme_name": data["scheme_name"],
        "category": data["category"],
        "plan": data["plan"],
        "scrape_date": data["scrape_date"],
        "content": final_text,
        "extracted_kv": kv_pairs
    }
    
    out_filename = file_path.stem + "_processed.json"
    out_path = PROCESSED_DATA_DIR / out_filename
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Processed {data['scheme_name']} -> {out_path.name}")


def run_preprocessor():
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    raw_files = list(RAW_DATA_DIR.glob("*.json"))
    
    if not raw_files:
        logger.warning("No raw files found. Run the scraper first.")
        return
        
    for f in raw_files:
        process_file(f)
        
    logger.info(f"Finished processing {len(raw_files)} files.")


if __name__ == "__main__":
    run_preprocessor()
