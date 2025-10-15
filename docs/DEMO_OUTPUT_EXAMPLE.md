# Tool Output Example - What You'll Get

## Folder Structure

When you run:
```bash
python3 spotify_works_matcher.py "ARTIST_URL" --output-dir results
```

You'll get:
```
results/
└── Henry_Morris_20251013_212026/          ← Timestamped folder with artist name
    ├── PUBLISHING_SUMMARY.txt             ← A&R Intelligence Report (NEW!)
    ├── unregistered_tracks.csv            ← Publishing opportunities (NEW!)
    ├── publisher_analysis.csv             ← Publisher breakdown (NEW!)
    ├── matched_works.csv                  ← Original: Matched works
    ├── contributors.csv                   ← Original: Writers/publishers
    └── identifiers.csv                    ← Original: ISRC→Work mappings
```

## Example: PUBLISHING_SUMMARY.txt

```
================================================================================
  ARTIST PUBLISHING ANALYSIS - A&R INTELLIGENCE REPORT
================================================================================

Artist: Henry Morris
Spotify ID: 1SgGcKiYCO55coa8sdiamq
Analysis Date: 2025-10-13 21:20:26
Spotify URL: https://open.spotify.com/artist/1SgGcKiYCO55coa8sdiamq

================================================================================
  PUBLISHING COVERAGE
================================================================================

Total Tracks: 28
Registered Tracks: 28 (100.0%)
Unregistered Tracks: 0 (0.0%)

Coverage Visualization:
[████████████████████] 100.0%

================================================================================
  PUBLISHER ANALYSIS
================================================================================

Current Publishers:
  • RIGHTSHOLDERS' COOPERATIVE EDEM: 15 work(s)
  • HYDRUS MUSIC PUBLISHING LTD: 8 work(s)
  • DIGICAST USA: 5 work(s)

Has Major Publisher: No
Has Indie Publisher: Yes
Self-Published/Unrepresented: No

================================================================================
  OPPORTUNITY ASSESSMENT
================================================================================

Opportunity Score: 45/100
Opportunity Level: LOW

Recommendation:
📊 LIMITED OPPORTUNITY: Artist appears well-represented. May only be suitable 
for specific territories or future works.

Key Factors:
  • Has indie publisher relationship
  ⚠ High coverage (100% registered)

================================================================================
  ACTIONABLE INSIGHTS
================================================================================

• Artist has full publishing coverage with indie publishers
• Consider co-publishing or territory-specific deals
• Monitor for catalog growth and new releases

NEXT STEPS:
1. Verify artist's streaming performance (monthly listeners, growth)
2. Check if artist owns masters or is signed to label
3. Research any existing publishing admin deals
4. Prepare publishing deal proposal if opportunity score is high

================================================================================
```

## Example: unregistered_tracks.csv

**For an artist with publishing gaps (e.g., Hensonn with 67% unregistered):**

| Track Title | ISRC | Release Date | Album | Artists | Priority |
|------------|------|--------------|-------|---------|----------|
| Sahara | QM4TW2421568 | 2024-01-15 | Sahara | Hensonn | HIGH |
| Antarctica | QM4TW2421569 | 2024-02-20 | Antarctica | Hensonn | HIGH |
| Jump - Sped Up | QM4TW2421570 | 2024-03-10 | Jump Remixes | Hensonn | HIGH |
| ... | ... | ... | ... | ... | ... |

**This CSV only contains unregistered tracks = publishing opportunities!**

## Example: publisher_analysis.csv

| Publisher Name | Work Count | Percentage | Type |
|---------------|------------|------------|------|
| RIGHTSHOLDERS' COOPERATIVE EDEM | 15 | 53.6% | Indie |
| HYDRUS MUSIC PUBLISHING LTD | 8 | 28.6% | Indie |
| DIGICAST USA | 5 | 17.9% | Indie |

## Folder Naming Format

```
{Artist_Name}_{YYYYMMDD}_{HHMMSS}
```

Examples:
- `Henry_Morris_20251013_212026`
- `Drake_20251013_153045`
- `The_Weeknd_20251014_091530`

## Benefits

### 1. **Organized History**
Keep track of all artist analyses:
```
results/
├── Henry_Morris_20251013_212026/
├── Henry_Morris_20251015_140000/    ← Re-analyzed 2 days later
├── Drake_20251013_160000/
└── The_Weeknd_20251014_090000/
```

### 2. **A&R Decision Making**
Quick assessment from `PUBLISHING_SUMMARY.txt`:
- **HIGH score (70+)**: Schedule meeting, prepare offer
- **MEDIUM score (50-69)**: Monitor, consider specific deals
- **LOW score (<50)**: Pass or wait

### 3. **Opportunity Tracking**
`unregistered_tracks.csv` shows exactly which songs need publishing

### 4. **Competitive Intelligence**
`publisher_analysis.csv` shows who you're competing against

## Real-World A&R Workflow

```bash
# 1. Discover artist on Spotify
# 2. Run analysis
python3 spotify_works_matcher.py "ARTIST_URL" --output-dir results

# 3. Review summary
cat results/Artist_Name_TIMESTAMP/PUBLISHING_SUMMARY.txt

# 4. Check opportunities
open results/Artist_Name_TIMESTAMP/unregistered_tracks.csv

# 5. Make decision based on opportunity score
# HIGH (70+) → Prepare offer
# MEDIUM (50-69) → Research more
# LOW (<50) → Pass
```

## Sample Opportunity Scores

### HIGH Opportunity (85/100)
```
Artist: Emerging Indie Artist
- 110 tracks total
- 74 unregistered (67%)
- No major publisher
- Active release schedule
→ STRONG CANDIDATE for full publishing deal
```

### MEDIUM Opportunity (55/100)
```
Artist: Mid-Level Artist
- 45 tracks total
- 20 unregistered (44%)
- Has indie publisher for some works
→ Consider co-publishing or admin deal
```

### LOW Opportunity (35/100)
```
Artist: Established Artist
- 28 tracks total
- 0 unregistered (100% coverage)
- Multiple indie publishers
→ Limited opportunity, monitor for new releases
```

## Next Time You Run

The tool will automatically:
1. Create a new timestamped folder
2. Generate all reports
3. Keep previous analyses intact

So you can compare:
- `Henry_Morris_20251013_212026/` (today)
- `Henry_Morris_20251020_150000/` (next week)

And see if their publishing situation changed!
