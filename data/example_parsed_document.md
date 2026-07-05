# Example: Parsed Document

This is an example of what the parsed JSON looks like after `preprocessor.py` runs and cleans the raw HTML. These files are stored in `data/processed/`.

```json
{
  "source_url": "https://groww.in/mutual-funds/icici-prudential-large-cap-fund-direct-growth",
  "scheme_name": "ICICI Prudential Large Cap Fund",
  "category": "Large Cap",
  "plan": "Direct Growth",
  "scrape_date": "2026-07-02T22:16:47.113614+00:00",
  "content": "Scheme Name: ICICI Prudential Large Cap Fund\nCategory: Large Cap\n... (full cleaned text of the page) ...",
  "extracted_kv": {
    "Expense ratio": "1.05%",
    "Exit load": "A fee payable to a mutual fund house for exiting a fund (fully or partially) before the completion of a specified period from the date of investment.",
    "Min. for SIP": "₹100",
    "Rating": "5",
    "NAV": "₹120.20"
  }
}
```
