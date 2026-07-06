"""
Pipeline Verification Test Script
Tests data extraction, vectorstore retrieval, and validates correctness.
"""
import json
import sys
import os
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

sys.stdout.reconfigure(encoding='utf-8')

PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARN = "⚠️  WARN"

results = []

def check(test_name, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((test_name, condition))
    print(f"  {status}  {test_name}" + (f" — {detail}" if detail else ""))
    return condition


print("=" * 70)
print("TEST 1: Processed Data - Key-Value Extraction Quality")
print("=" * 70)

processed_dir = PROJECT_ROOT / "data" / "processed"
processed_files = list(processed_dir.glob("*_processed.json"))

check("Processed files exist", len(processed_files) == 8, f"Found {len(processed_files)} files")

# Track known expected values from Groww
expected_fields = ["NAV", "Min. for SIP", "Fund size (AUM)", "Expense ratio", "Rating"]

for pf in sorted(processed_files):
    with open(pf, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    scheme = data["scheme_name"]
    kv = data.get("extracted_kv", {})
    
    print(f"\n  --- {scheme} ---")
    
    # Check that all expected fields are present
    for field in expected_fields:
        check(f"  {field} extracted", field in kv, kv.get(field, "MISSING")[:60])
    
    # Check Exit load is present AND is NOT a tooltip definition
    exit_load = kv.get("Exit load", "")
    is_not_tooltip = "A fee payable" not in exit_load
    has_exit_load = "Exit load" in kv
    
    if has_exit_load:
        check("  Exit load is correct (not tooltip)", is_not_tooltip, exit_load[:80])
    else:
        print(f"  {WARN}  Exit load not found (may be Nil or not listed on page)")
    
    # Check that content is not empty
    content = data.get("content", "")
    check("  Content length > 500 chars", len(content) > 500, f"{len(content)} chars")
    
    # Check that content has the improved merged text (no standalone "%" lines)
    lines = content.split("\n")
    standalone_percent = sum(1 for l in lines if l.strip() == "%")
    check("  No standalone '%' lines", standalone_percent == 0, f"Found {standalone_percent}")


print("\n" + "=" * 70)
print("TEST 2: Vectorstore Retrieval Accuracy")
print("=" * 70)

try:
    from src.query.retriever import retrieve_context
    
    # Test 1: Query about exit load for Large Cap Fund
    print("\n  --- Query: 'exit load' filtered to 'ICICI Prudential Large Cap Fund' ---")
    results_lc = retrieve_context("What is the exit load?", fund_name="ICICI Prudential Large Cap Fund")
    
    check("Retriever returns results", len(results_lc) > 0, f"{len(results_lc)} chunks")
    
    if results_lc:
        # Check that ALL returned chunks belong to the correct fund
        all_correct_fund = all(
            c.metadata.get("scheme_name") == "ICICI Prudential Large Cap Fund"
            for c in results_lc
        )
        check("All chunks are from Large Cap Fund", all_correct_fund)
        
        # Check that at least one chunk mentions exit load info
        has_exit_info = any("1%" in c.page_content or "exit" in c.page_content.lower() for c in results_lc)
        check("At least one chunk has exit load data", has_exit_info)
    
    # Test 2: Query about expense ratio for Technology Fund
    print("\n  --- Query: 'expense ratio' filtered to 'ICICI Prudential Technology Fund' ---")
    results_tech = retrieve_context("What is the expense ratio?", fund_name="ICICI Prudential Technology Fund")
    
    check("Retriever returns results", len(results_tech) > 0, f"{len(results_tech)} chunks")
    
    if results_tech:
        all_correct_fund = all(
            c.metadata.get("scheme_name") == "ICICI Prudential Technology Fund"
            for c in results_tech
        )
        check("All chunks are from Technology Fund", all_correct_fund)
        
        has_expense_info = any("1.27" in c.page_content or "expense" in c.page_content.lower() for c in results_tech)
        check("At least one chunk has expense ratio data", has_expense_info)
    
    # Test 3: Cross-fund isolation — querying one fund should NOT return another
    print("\n  --- Query: 'fund details' filtered to 'ICICI Prudential Silver ETF FOF' ---")
    results_silver = retrieve_context("Tell me about this fund", fund_name="ICICI Prudential Silver ETF FOF")
    
    check("Retriever returns results", len(results_silver) > 0, f"{len(results_silver)} chunks")
    
    if results_silver:
        no_wrong_fund = all(
            c.metadata.get("scheme_name") == "ICICI Prudential Silver ETF FOF"
            for c in results_silver
        )
        check("No cross-fund contamination", no_wrong_fund)

except ImportError as e:
    print(f"\n  {WARN}  Could not import retriever (likely missing dependencies): {e}")
    print("         Skipping vectorstore tests. Run with venv to test.")
except Exception as e:
    print(f"\n  {FAIL}  Vectorstore test failed: {e}")


print("\n" + "=" * 70)
print("TEST 3: Index Manifest Verification")
print("=" * 70)

manifest_path = PROJECT_ROOT / "vectorstore" / "index_manifest.json"
if manifest_path.exists():
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    check("Manifest has total_chunks > 50", manifest.get("total_chunks", 0) > 50, 
          f"{manifest.get('total_chunks', 0)} chunks")
    check("Manifest has 8 schemes", len(manifest.get("schemes_indexed", [])) == 8,
          f"{len(manifest.get('schemes_indexed', []))} schemes")
    check("Has golden_facts chunk type", "golden_facts" in manifest.get("chunk_types", []))
    check("Has detailed_text chunk type", "detailed_text" in manifest.get("chunk_types", []))
else:
    check("Manifest file exists", False)


# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
total = len(results)
passed = sum(1 for _, ok in results if ok)
failed = total - passed
print(f"  Total: {total}  |  Passed: {passed}  |  Failed: {failed}")
if failed == 0:
    print(f"\n  🎉 All tests passed!")
else:
    print(f"\n  ⚠️  {failed} test(s) failed. Review the output above.")
print("=" * 70)
