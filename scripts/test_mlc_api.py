#!/usr/bin/env python3
"""Quick test of MLC API with improved headers."""

import requests
import json

# Browser-like headers
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://portal.themlc.com",
    "Referer": "https://portal.themlc.com/"
}

def test_search(query):
    """Test MLC search with a query."""
    url = "https://api.ptl.themlc.com/api2v/public/search/works"
    params = {
        "q": query,
        "page": 0,
        "size": 5
    }
    body = {}
    
    print(f"\n🔍 Searching for: '{query}'")
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    try:
        response = requests.post(url, params=params, json=body, headers=HEADERS, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            works = data.get("content", [])
            print(f"✅ Found {len(works)} works")
            
            if works:
                print(f"\nFirst result:")
                work = works[0]
                print(f"  Title: {work.get('title')}")
                print(f"  ID: {work.get('propertyId') or work.get('id')}")
                print(f"  ISWC: {work.get('iswc')}")
                
                writers = work.get('writers', [])
                if writers:
                    print(f"  Writers: {', '.join([w.get('firstName', '') + ' ' + w.get('lastName', '') for w in writers[:3]])}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("  MLC API Test")
    print("=" * 70)
    
    # Test various queries
    test_search("Blinding Lights")
    test_search("Starboy")
    test_search("The Hills")
    
    print("\n" + "=" * 70)
    print("Test complete!")
    print("=" * 70)
