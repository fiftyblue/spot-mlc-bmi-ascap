# Getting More Detailed CSV Output

## The Issue

The script currently only generates a `COMPREHENSIVE_REPORT.csv` file. If you need more detailed breakdowns with additional MLC data fields, you need to enable the additional CSV exports.

## The Solution

The script has built-in functions to generate 3 additional detailed CSV files, but they're currently disabled in the main output. Here's what's available:

### Available CSV Outputs:

1. **COMPREHENSIVE_REPORT.csv** (Currently Generated)
   - One row per track-work match
   - Includes: Spotify track info, work info, writers, publishers, confidence scores
   - Good for: Overview and quick analysis

2. **matched_works.csv** (Not Currently Generated)
   - One row per unique work
   - Includes: Work ID, Work Title, ISWC, Source, confidence scores
   - Good for: Work-centric analysis

3. **contributors.csv** (Not Currently Generated)
   - One row per contributor (writer/publisher) per work
   - Includes: Work ID, Contributor Name, Type, Role, Share %, IPI, PRO
   - Good for: Detailed rights holder analysis

4. **identifiers.csv** (Not Currently Generated)
   - One row per track-work mapping
   - Includes: All identifiers (ISRC, ISWC, Track IDs, Work IDs)
   - Good for: Database linking and reconciliation

## How to Enable All CSV Exports

### Option 1: Quick Fix (Modify the Script)

Open `spotify_works_matcher.py` and find the section around line 1272-1279 that says:

```python
# Generate output files
print(f"\n📊 Generating reports...")

# Generate comprehensive CSV
output_gen.generate_comprehensive_csv(tracks, matches, works_data)
```

**Replace it with:**

```python
# Generate output files
print(f"\n📊 Generating reports...")

# Generate ALL CSV files
output_gen.generate_comprehensive_csv(tracks, matches, works_data)
output_gen.generate_works_csv(matches)
output_gen.generate_contributors_csv(works_data)
output_gen.generate_identifiers_csv(matches)
```

Then re-run the script.

### Option 2: What You're Missing

The `COMPREHENSIVE_REPORT.csv` has most of the data, but it's formatted differently than the other CSVs. Here's what each specialized CSV provides that might not be obvious in the comprehensive report:

- **matched_works.csv**: Deduplicates works (one work appears once even if matched to multiple tracks)
- **contributors.csv**: Breaks out each writer/publisher into separate rows with detailed metadata
- **identifiers.csv**: Focuses purely on ID mapping without all the extra metadata

## Comparing to "Full MLC Data Pull Sheet"

If you're comparing to a direct MLC database export, note that:

1. **This script only gets PUBLIC MLC data** via their API
2. **Some fields may not be available** through the public API (like detailed share percentages, full IPI numbers, etc.)
3. **The MLC portal may show more fields** than what's available through their public search API

### Fields You Might Be Missing:

The public MLC API may not provide:
- Detailed ownership shares (%)
- Complete IPI numbers for all contributors
- PRO affiliations for all writers
- Publisher contact information
- Territory-specific data
- Historical registration dates

These fields exist in the code structure but may come back empty from the API if they're not publicly available.

## Next Steps

1. **Enable all CSV exports** using Option 1 above
2. **Re-run the script** on the same artist
3. **Check the `contributors.csv`** - this will have the most detailed breakdown
4. **Compare field-by-field** with your "full MLC Data Pull Sheet" to identify specific missing fields

If specific fields are still missing, they may require:
- Direct MLC portal access (not API)
- MLC member login credentials
- Manual data entry from the MLC portal

## Questions?

If you need help modifying the script or have questions about specific fields, let me know which fields from your "full MLC Data Pull Sheet" are missing and I can help identify if they're available through the API.
