import json

with open("data/processed/icici_prudential_large_cap_fund_processed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

content = data.get("content", "")

with open("scratch/analysis.txt", "w", encoding="utf-8") as f:
    f.write("=== PREPROCESSED CONTENT (First 3000 chars) ===\n")
    f.write(content[:3000])
    f.write("\n\n=== TOTAL CHARACTERS ===\n")
    f.write(str(len(content)))
    f.write("\n\n=== TOTAL LINES ===\n")
    f.write(str(len(content.splitlines())))
