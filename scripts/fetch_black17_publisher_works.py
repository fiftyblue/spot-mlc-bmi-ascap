#!/usr/bin/env python3
"""
Single-file script to download all works for BLACK 17 PUBLISHING (ID: 16078262)
from the public LMC API and save to JSONL and CSV files.

Usage:
    python fetch_black17_publisher_works.py

Requirements:
    - Python 3.10+
    - requests library (pip install requests)
"""

import json
import csv
import time
import sys
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library not found.")
    print("Please install it by running:")
    print("    pip install requests")
    sys.exit(1)


# Configuration
PUBLISHER_ID = 16078262
PUBLISHER_NAME = "BLACK 17 PUBLISHING"
BASE_URL = f"https://api.ptl.themlc.com/api2v/public/search/works/publisher/{PUBLISHER_ID}"
PAGE_SIZE = 200
EXPECTED_TOTAL = 7185
OUTPUT_JSONL = "black17_works.jsonl"
OUTPUT_CSV = "black17_works.csv"

# Request configuration
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}
REQUEST_BODY = {}  # Empty JSON body; will adjust if API requires more

# Retry configuration
MAX_RETRIES = 5
INITIAL_BACKOFF = 1.0  # seconds
PAGE_DELAY = 0.15  # 150ms between pages


def make_request_with_retry(url: str, params: Dict[str, Any], body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Make POST request with exponential backoff retry logic."""
    backoff = INITIAL_BACKOFF
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                url,
                params=params,
                json=body,
                headers=HEADERS,
                timeout=30
            )
            
            # Success
            if response.status_code == 200:
                return response.json()
            
            # Rate limit or server error - retry
            if response.status_code in (429, 500, 502, 503, 504):
                if attempt < MAX_RETRIES - 1:
                    print(f"  ⚠️  HTTP {response.status_code}, retrying in {backoff:.1f}s (attempt {attempt + 1}/{MAX_RETRIES})...")
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                else:
                    print(f"  ❌ HTTP {response.status_code} after {MAX_RETRIES} attempts")
                    return None
            
            # Other error
            print(f"  ❌ HTTP {response.status_code}: {response.text[:200]}")
            return None
            
        except requests.exceptions.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                print(f"  ⚠️  Request error: {e}, retrying in {backoff:.1f}s...")
                time.sleep(backoff)
                backoff *= 2
                continue
            else:
                print(f"  ❌ Request failed after {MAX_RETRIES} attempts: {e}")
                return None
    
    return None


def flatten_value(value: Any, max_depth: int = 2) -> str:
    """Flatten nested values for CSV output."""
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    if isinstance(value, list):
        # Array of primitives - join with semicolon
        if all(isinstance(item, (str, int, float, bool, type(None))) for item in value):
            return "; ".join(str(item) for item in value if item is not None)
        # Array of objects - serialize as compact JSON
        return json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    if isinstance(value, dict):
        # Serialize nested objects as compact JSON
        return json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    return str(value)


def extract_csv_columns(works: List[Dict[str, Any]]) -> List[str]:
    """Auto-detect CSV columns from first batch of works."""
    if not works:
        return []
    
    # Collect all unique keys from first few works
    all_keys = set()
    for work in works[:10]:  # Sample first 10 works
        all_keys.update(work.keys())
    
    # Prioritize common/important fields
    priority_fields = [
        'property_id', 'id', 'work_id',
        'title', 'title.keyword',
        'authors', 'author',
        'isbn', 'isbn13', 'isbn10',
        'format', 'binding',
        'publication_date', 'publish_date',
        'price', 'list_price',
        'imprint', 'publisher',
        'series', 'series_name',
        'categories', 'category',
        'description', 'summary'
    ]
    
    # Build column list: priority fields first, then others alphabetically
    columns = []
    for field in priority_fields:
        if field in all_keys:
            columns.append(field)
            all_keys.remove(field)
    
    # Add remaining fields alphabetically
    columns.extend(sorted(all_keys))
    
    return columns


def fetch_all_works() -> List[Dict[str, Any]]:
    """Fetch all works from the API with pagination."""
    all_works = []
    seen_ids = set()
    page = 0
    total_from_api = None
    
    print(f"🚀 Starting fetch for {PUBLISHER_NAME} (ID: {PUBLISHER_ID})")
    print(f"📊 Expected total: {EXPECTED_TOTAL:,} works")
    print(f"🔗 API: {BASE_URL}")
    print(f"📄 Page size: {PAGE_SIZE}\n")
    
    while True:
        params = {
            "page": page,
            "size": PAGE_SIZE,
            "sort": ["title.keyword,asc", "property_id,asc"]
        }
        
        print(f"📥 Fetching page {page} (offset {page * PAGE_SIZE})...", end=" ", flush=True)
        
        response_data = make_request_with_retry(BASE_URL, params, REQUEST_BODY)
        
        if response_data is None:
            print(f"⚠️  Skipping page {page} after failures")
            page += 1
            continue
        
        # Auto-detect response structure
        works_list = None
        
        # Common patterns for paginated responses
        if isinstance(response_data, list):
            works_list = response_data
        elif "content" in response_data:
            works_list = response_data["content"]
            if total_from_api is None and "totalElements" in response_data:
                total_from_api = response_data["totalElements"]
        elif "data" in response_data:
            works_list = response_data["data"]
            if total_from_api is None and "total" in response_data:
                total_from_api = response_data["total"]
        elif "results" in response_data:
            works_list = response_data["results"]
            if total_from_api is None and "total" in response_data:
                total_from_api = response_data["total"]
        elif "works" in response_data:
            works_list = response_data["works"]
            if total_from_api is None and "total" in response_data:
                total_from_api = response_data["total"]
        else:
            # Try to find any list in the response
            for key, value in response_data.items():
                if isinstance(value, list) and len(value) > 0:
                    works_list = value
                    break
        
        if works_list is None:
            print(f"❌ Could not find works list in response")
            print(f"Response keys: {list(response_data.keys())}")
            break
        
        if len(works_list) == 0:
            print("✅ No more items")
            break
        
        # Deduplicate by property_id or id
        new_count = 0
        for work in works_list:
            work_id = work.get("property_id") or work.get("id") or work.get("work_id")
            if work_id and work_id not in seen_ids:
                all_works.append(work)
                seen_ids.add(work_id)
                new_count += 1
            elif work_id is None:
                # No ID field, just add it
                all_works.append(work)
                new_count += 1
        
        print(f"✅ Got {len(works_list)} items ({new_count} new) | Total: {len(all_works):,}")
        
        # Check if we've fetched everything
        if total_from_api and len(all_works) >= total_from_api:
            print(f"\n✅ Reached total count from API: {total_from_api:,}")
            break
        
        # Stop if page returned fewer items than requested
        if len(works_list) < PAGE_SIZE:
            print(f"\n✅ Last page (returned {len(works_list)} < {PAGE_SIZE})")
            break
        
        page += 1
        time.sleep(PAGE_DELAY)  # Polite delay
    
    print(f"\n📦 Total works fetched: {len(all_works):,}")
    if total_from_api:
        print(f"📊 API reported total: {total_from_api:,}")
        if len(all_works) != total_from_api:
            print(f"⚠️  Mismatch: fetched {len(all_works):,} vs API total {total_from_api:,}")
    
    if len(all_works) != EXPECTED_TOTAL:
        print(f"⚠️  Note: Expected {EXPECTED_TOTAL:,} works, got {len(all_works):,}")
    
    return all_works


def save_jsonl(works: List[Dict[str, Any]], filename: str):
    """Save works to JSONL file (one JSON object per line)."""
    print(f"\n💾 Writing JSONL to {filename}...", end=" ", flush=True)
    with open(filename, 'w', encoding='utf-8') as f:
        for work in works:
            f.write(json.dumps(work, ensure_ascii=False) + '\n')
    print(f"✅ {len(works):,} records written")


def save_csv(works: List[Dict[str, Any]], filename: str):
    """Save works to CSV file with auto-detected columns."""
    if not works:
        print(f"⚠️  No works to save to CSV")
        return
    
    print(f"💾 Writing CSV to {filename}...", end=" ", flush=True)
    
    # Auto-detect columns
    columns = extract_csv_columns(works)
    
    with open(filename, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        
        for work in works:
            # Flatten nested values
            row = {col: flatten_value(work.get(col)) for col in columns}
            writer.writerow(row)
    
    print(f"✅ {len(works):,} records written ({len(columns)} columns)")
    print(f"   Columns: {', '.join(columns[:10])}{', ...' if len(columns) > 10 else ''}")


def print_samples(works: List[Dict[str, Any]], count: int = 3):
    """Print sample records."""
    print(f"\n📋 Sample records (first {min(count, len(works))}):\n")
    for i, work in enumerate(works[:count], 1):
        print(f"--- Record {i} ---")
        print(json.dumps(work, indent=2, ensure_ascii=False)[:500])
        if len(json.dumps(work, indent=2)) > 500:
            print("... (truncated)")
        print()


def main():
    """Main execution function."""
    print("=" * 70)
    print(f"  BLACK 17 PUBLISHING - Works Data Fetcher")
    print("=" * 70)
    
    try:
        # Fetch all works
        works = fetch_all_works()
        
        if not works:
            print("\n❌ No works fetched. Exiting.")
            sys.exit(1)
        
        # Save to files
        save_jsonl(works, OUTPUT_JSONL)
        save_csv(works, OUTPUT_CSV)
        
        # Print samples
        print_samples(works, 3)
        
        # Final summary
        print("=" * 70)
        print("✅ COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"📊 Total records: {len(works):,}")
        print(f"📁 JSONL file: {OUTPUT_JSONL}")
        print(f"📁 CSV file: {OUTPUT_CSV}")
        print(f"\n🔗 API endpoint: {BASE_URL}")
        print(f"📄 Page size used: {PAGE_SIZE}")
        print(f"📦 Publisher: {PUBLISHER_NAME} (ID: {PUBLISHER_ID})")
        
        if len(works) == EXPECTED_TOTAL:
            print(f"✅ Matches expected total: {EXPECTED_TOTAL:,}")
        else:
            print(f"⚠️  Expected {EXPECTED_TOTAL:,}, got {len(works):,} (difference: {len(works) - EXPECTED_TOTAL:+,})")
        
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
