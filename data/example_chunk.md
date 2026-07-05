# Example: Document Chunk

This is an example of what a text chunk looks like after `chunker.py` splits the parsed documents, just before it gets embedded and stored in ChromaDB.

```json
{
  "page_content": "Scheme: ICICI Prudential Bharat 22 FOF (Category: Fund of Funds (Thematic)). The Expense ratio is 0.12%. The Exit load is A fee payable to a mutual fund house for exiting a fund (fully or partially) before the completion of a specified period from the date of investment.. Min. for SIP is ₹1,000. Rating is None. NAV is ₹34.76.",
  "metadata": {
    "source_url": "https://groww.in/mutual-funds/icici-prudential-bharat-22-fof-direct-growth",
    "scheme_name": "ICICI Prudential Bharat 22 FOF",
    "chunk_type": "golden_facts"
  }
}
```

> **Note:** The `chunk_type` can be either `golden_facts` (structured key-value pairs combined into a rich paragraph) or `detailed_text` (running text split via RecursiveCharacterTextSplitter).
