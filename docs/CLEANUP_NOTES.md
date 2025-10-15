# Project Cleanup Notes

## Main Script (Use This!)
**`spotify_works_matcher.py`** - The one script you need. Does everything:
- Fetches Spotify tracks
- Checks MLC, ASCAP, BMI databases
- Generates comprehensive CSV report
- Creates A&R publishing intelligence report
- Supports clipboard input

## Redundant Scripts (Can be archived/deleted)

These scripts were created during development but are now redundant since `spotify_works_matcher.py` does it all:

1. **`generate_ar_report_from_csv.py`** - No longer needed. The main script generates A&R reports automatically.

2. **`artist_publishing_analyzer.py`** - Likely an earlier version or duplicate functionality.

3. **`fetch_black17_publisher_works.py`** - Appears to be a specific one-off script for a particular publisher.

4. **`create_master_report.py`** - Likely for batch processing, but not part of core workflow.

5. **`batch_process.py`** - For processing multiple artists. Keep if you need batch functionality, otherwise archive.

## Test Scripts (Keep for development)
- `test_mlc_api.py` - For testing MLC API
- `test_tool.py` - For testing functionality

## Recommended File Structure

```
spot-mlc-bmi-ascap/
├── spotify_works_matcher.py    ← THE MAIN SCRIPT
├── requirements.txt
├── .env
├── USAGE.md                     ← Quick start guide
├── README.md
├── results/                     ← Output folder
│   └── Artist_Name_TIMESTAMP/
│       ├── COMPREHENSIVE_REPORT.csv
│       └── PUBLISHING_SUMMARY.txt
└── archive/                     ← Move old scripts here
    ├── generate_ar_report_from_csv.py
    ├── artist_publishing_analyzer.py
    └── ...
```

## Summary
You now have **one streamlined workflow**:
1. Copy Spotify artist URL
2. Run: `python3 spotify_works_matcher.py`
3. Get comprehensive analysis in `results/`

That's it!
