"""
Document preprocessor for mutual fund HTML data.
Strips boilerplate and extracts structured text from Groww pages.
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
    """Parse HTML and remove unwanted tags including Groww popups/tooltips."""
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove script, style, header, footer, nav
    for tag in soup.find_all(["script", "style", "header", "footer", "nav", "noscript", "svg"]):
        tag.decompose()
        
    # Remove specific generic header/footer classes if they exist
    tags_to_remove = []
    for tag in soup.find_all("div", class_=re.compile("header|footer|nav", re.I)):
        # Don't remove fundDetails header divs or chat headers
        if tag.attrs is None:
            continue
        tag_classes = tag.get("class") or []
        classes = " ".join(tag_classes)
        if "fundDetails" in classes or "chat" in classes:
            continue
        tags_to_remove.append(tag)
    for tag in tags_to_remove:
        tag.decompose()
    
    # CRITICAL: Remove Groww's popup/tooltip sections that contain term DEFINITIONS
    # (not actual values). These have class names like exitLoadStampDutyTax_container, etc.
    for tag in list(soup.find_all("div", class_=re.compile(r"exitLoadStampDutyTax", re.I))):
        tag.decompose()
    
    # Also remove modal/rodal overlays
    for tag in list(soup.find_all("div", class_=re.compile(r"rodal", re.I))):
        tag.decompose()
        
    return soup


def extract_key_value_pairs(soup: BeautifulSoup) -> dict[str, str]:
    """
    Extract key-value pairs from the fundDetails section of Groww pages.
    
    Groww uses a specific structure:
      - Container: div.fundDetails_fundDetailsContainer
      - Each pair: div.fundDetails_gap4 containing label div + value div
    """
    extracted = {}
    
    # Strategy 1: Target Groww's fundDetails_fundDetailsContainer directly
    details_container = soup.find("div", class_=re.compile(r"fundDetails_fundDetailsContainer", re.I))
    
    if details_container:
        # Find all label divs (they have contentTertiary + fundDetails_gap4 classes)
        label_divs = details_container.find_all(
            "div", class_=re.compile(r"contentTertiary.*fundDetails_gap4|fundDetails_gap4.*contentTertiary", re.I)
        )
        
        for label_div in label_divs:
            label_text = label_div.get_text(strip=True)
            # The value is in the next sibling div
            value_div = label_div.find_next_sibling()
            if value_div:
                value_text = value_div.get_text(strip=True)
                if label_text and value_text:
                    # Normalize NAV labels: "NAV: 02 Jul '26" → "NAV"
                    if label_text.startswith("NAV"):
                        label_text = "NAV"
                    extracted[label_text] = value_text
    
    # Strategy 2: Fallback — look for key-value pairs in the remaining page
    # If Strategy 1 didn't find something, try generic approach
    fields_to_find = {
        "Expense ratio": None,
        "Min. for SIP": None,
        "Fund size (AUM)": None,
        "Rating": None,
        "NAV": None,
    }
    
    for field in fields_to_find:
        if field not in extracted:
            # Generic fallback: find label text and look at sibling
            label_tag = soup.find(string=re.compile(f"^{re.escape(field)}", re.I))
            if label_tag:
                parent = label_tag.find_parent()
                if parent:
                    next_node = parent.find_next_sibling()
                    if next_node:
                        val = next_node.get_text(strip=True)
                        if val and len(val) < 100:  # Sanity check: values should be short
                            extracted[field] = val
    
    # Strategy 3: Extract Exit Load from the body text using regex
    # Groww puts the actual exit load value in various places, often in table rows
    if "Exit load" not in extracted or len(extracted.get("Exit load", "")) > 80:
        full_text = soup.get_text(separator="\n")
        # Split text into lines and search line by line for exit load values
        for line in full_text.split("\n"):
            if not line.strip():
                continue
            # Look for exit load value pattern in this line
            match = re.search(
                r'(\d+%,?\s*(?:if\s+redeemed|If\s+redeemed)[^.;]*(?:year|month|days?|Nil)[^.;]*\.?)',
                line, re.IGNORECASE
            )
            if match:
                extracted["Exit load"] = match.group(1).strip()
                break
    
    return extracted


def get_main_text(soup: BeautifulSoup) -> str:
    """Extract and normalize all visible text, merging fragmented lines."""
    # Find main content container if possible
    main = soup.find("main") or soup.find(id="root") or soup
    
    text = main.get_text(separator="\n", strip=True)
    
    # Normalize whitespace
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    # Filter out likely navigation links (very short words, generic terms)
    ignore_exact = {"Stocks", "Mutual Funds", "F&O", "More", "Invest in Stocks", "Compare Funds"}
    
    # Merge fragmented percentage / return lines
    # e.g. "+13.94\n%\n3Y annualised" → "+13.94% 3Y annualised"
    merged_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line in ignore_exact:
            i += 1
            continue
        
        # If this line is just "%" and we have a previous line, merge with previous
        if line == "%" and merged_lines:
            merged_lines[-1] = merged_lines[-1] + "%"
            i += 1
            continue
        
        # If next line is just "%" merge it into current
        if i + 1 < len(lines) and lines[i + 1] == "%":
            line = line + "%"
            i += 1  # skip the "%" line
            # If the line after "%" is a descriptor like "3Y annualised", merge too
            if i + 1 < len(lines) and re.match(r'^[0-9]?[YMD]\s|^annualised|^return', lines[i + 1], re.I):
                line = line + " " + lines[i + 1]
                i += 1
        
        # Merge standalone "+" or "-" with the next number
        if line in ("+", "-") and i + 1 < len(lines):
            line = line + lines[i + 1]
            i += 1
            
        merged_lines.append(line)
        i += 1
        
    return "\n".join(merged_lines)


def extract_from_next_data(html: str) -> dict[str, str]:
    """
    Extract structured data from Groww's __NEXT_DATA__ JSON script tag.
    This contains accurate fund metadata like exit_load, expense_ratio, AUM, etc.
    Must be called BEFORE clean_html() which removes script tags.
    """
    extracted = {}
    try:
        soup = BeautifulSoup(html, "html.parser")
        next_data_tag = soup.find("script", id="__NEXT_DATA__")
        if not next_data_tag:
            return extracted
        
        import json as json_mod
        data = json_mod.loads(next_data_tag.string)
        
        # Navigate to the fund data
        page_props = data.get("props", {}).get("pageProps", {})
        mf_data = page_props.get("mfServerSideData", {})
        
        # Extract key fields
        if mf_data.get("exit_load"):
            extracted["Exit load"] = mf_data["exit_load"]
        if mf_data.get("expense_ratio"):
            extracted["Expense ratio"] = mf_data["expense_ratio"] + "%"
        if mf_data.get("aum"):
            aum = mf_data["aum"]
            extracted["Fund size (AUM)"] = f"₹{aum:,.2f} Cr"
        if mf_data.get("min_sip_investment"):
            extracted["Min. for SIP"] = f"₹{mf_data['min_sip_investment']}"
        if mf_data.get("groww_rating"):
            extracted["Rating"] = str(mf_data["groww_rating"])
        if mf_data.get("fund_manager") and mf_data["fund_manager"] != "null":
            extracted["Fund Manager"] = mf_data["fund_manager"]
        if mf_data.get("category"):
            extracted["Category"] = mf_data["category"]
        if mf_data.get("sub_category"):
            extracted["Sub-category"] = mf_data["sub_category"]
        if mf_data.get("benchmark_name"):
            extracted["Benchmark"] = mf_data["benchmark_name"]
            
    except Exception as e:
        logger.warning(f"Could not extract from __NEXT_DATA__: {e}")
    
    return extracted


def process_file(file_path: Path):
    """Read raw JSON, process it, and save to processed dir."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    html = data.get("html", "")
    if not html:
        logger.warning(f"No HTML found in {file_path}")
        return
    
    # Extract from __NEXT_DATA__ BEFORE cleaning HTML (which removes script tags)
    next_data_kv = extract_from_next_data(html)
    
    soup = clean_html(html)
    
    # Extract structural properties from the visible page
    kv_pairs = extract_key_value_pairs(soup)
    
    # Merge: __NEXT_DATA__ values fill in gaps (HTML values take priority for display fields)
    for key, value in next_data_kv.items():
        if key not in kv_pairs or len(kv_pairs.get(key, "")) > 80:
            kv_pairs[key] = value
    
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
