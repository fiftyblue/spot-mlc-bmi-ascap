# A&R Publishing Intelligence Tool - Specification

## Purpose
Transform the tool from general matching to **A&R-focused publishing opportunity analysis**.

## Key Questions to Answer

### 1. Publishing Coverage
- **What percentage of their catalog is registered?**
- Which tracks are registered vs. unregistered?
- Are they leaving money on the table?

### 2. Publisher Intelligence  
- **Who represents them currently?**
  - Major publisher (Sony, Universal, Warner, etc.)?
  - Indie publisher?
  - Self-published/no publisher?
- How many different publishers do they work with?
- Is there a primary publisher relationship?

### 3. A&R Opportunity Assessment
- **Should we approach this artist for a publishing deal?**
- Opportunity score (0-100)
- Recommendation: High/Medium/Low priority

## New Output Format

### Executive Summary Report (`PUBLISHING_SUMMARY.txt`)

```
================================================================================
  ARTIST PUBLISHING ANALYSIS - A&R INTELLIGENCE REPORT
================================================================================

Artist: Hensonn
Spotify ID: 0snouHYzOWSgxRBYMQsa3H
Analysis Date: 2025-10-13
Catalog Size: 110 tracks

================================================================================
  PUBLISHING COVERAGE
================================================================================

Registered Tracks: 36 / 110 (32.7%)
Unregistered Tracks: 74 / 110 (67.3%)

Coverage Visualization:
[██████░░░░░░░░░░░░░░] 32.7%

⚠️  SIGNIFICANT GAP: 67% of catalog unregistered

================================================================================
  PUBLISHER ANALYSIS
================================================================================

Current Publishers:
  • No major publisher found
  • No indie publisher found
  • Self-published or unrepresented

Publisher Status: INDEPENDENT / UNREPRESENTED

================================================================================
  OPPORTUNITY ASSESSMENT
================================================================================

Opportunity Score: 85/100
Opportunity Level: HIGH

🎯 RECOMMENDATION:
STRONG PUBLISHING OPPORTUNITY - Artist has 74 unregistered tracks (67% of catalog)
with no major publisher representation. Excellent candidate for:
  - Full publishing deal
  - Co-publishing agreement  
  - Administration deal

Key Factors:
  ✓ Large catalog (110 tracks)
  ✓ Significant unregistered works (67%)
  ✓ No major publisher competition
  ✓ Active release schedule

================================================================================
  ACTIONABLE INSIGHTS
================================================================================

• 74 tracks have NO publishing registration - immediate revenue opportunity
• Artist appears to be self-releasing without publishing support
• Catalog size (110 tracks) suggests consistent output
• Recent releases show active career - good timing for approach
• No existing major publisher relationships to navigate

NEXT STEPS:
1. Verify artist's streaming performance (monthly listeners, growth)
2. Check if artist owns masters or is signed to label
3. Research any existing publishing admin deals
4. Prepare publishing deal proposal

================================================================================
```

### Track Details CSV (`track_publishing_details.csv`)

| Track Title | ISRC | Registered | Publishers | Writers | Opportunity | Notes |
|------------|------|------------|------------|---------|-------------|-------|
| Jump | QM4TW2421567 | ✅ Yes | None found | Unknown | Low | Already registered |
| Sahara | QM4TW2421568 | ❌ No | None | Unknown | **HIGH** | Unregistered - publishing opportunity |
| Antarctica | QM4TW2421569 | ❌ No | None | Unknown | **HIGH** | Unregistered - publishing opportunity |

### Publisher Analysis CSV (`publisher_analysis.csv`)

| Publisher Name | Track Count | Share % | Type | Notes |
|---------------|-------------|---------|------|-------|
| None Found | 74 | 67.3% | N/A | Unrepresented tracks |
| [If any found] | X | X% | Major/Indie | Current relationship |

### Opportunity Tracks CSV (`high_opportunity_tracks.csv`)

**Only unregistered tracks** - these are the publishing opportunities:

| Track Title | ISRC | Release Date | Streams (if available) | Priority |
|------------|------|--------------|------------------------|----------|
| Sahara | ... | 2024-01-15 | Unknown | HIGH |
| Antarctica | ... | 2024-02-20 | Unknown | HIGH |

## Scoring Algorithm

### Opportunity Score (0-100)

```python
score = 0

# Coverage scoring (inverse - less coverage = more opportunity)
if coverage < 25%: score += 40
elif coverage < 50%: score += 30
elif coverage < 75%: score += 20
else: score += 10

# Publisher status
if no_major_publisher: score += 30
if no_indie_publisher: score += 10
if self_published: score += 10

# Catalog size
if tracks > 50: score += 20
elif tracks > 20: score += 15
else: score += 10

# Opportunity Level
if score >= 70: "HIGH"
elif score >= 50: "MEDIUM"
else: "LOW"
```

## Key Changes to Tool

### 1. Focus on Unregistered Tracks
- Highlight tracks WITHOUT publishing as opportunities
- Separate registered vs. unregistered in all reports

### 2. Publisher Intelligence
- Identify publisher names from MLC data
- Classify as Major/Indie/Self-Published
- Flag competitive situations

### 3. A&R Recommendations
- Clear opportunity scoring
- Actionable next steps
- Deal type suggestions (full publishing, co-pub, admin)

### 4. Executive Summary First
- Lead with opportunity assessment
- Business-focused language
- Quick decision-making format

## Usage for A&R Team

```bash
# Analyze an artist
python artist_publishing_analyzer.py "SPOTIFY_URL" --output-dir results

# Review the summary
cat results/PUBLISHING_SUMMARY.txt

# Check unregistered tracks
open results/high_opportunity_tracks.csv

# Make decision
# - High score (70+): Schedule meeting, prepare offer
# - Medium score (50-69): Monitor, consider for specific deals
# - Low score (< 50): Pass or wait for future catalog
```

## Additional Features to Add

### 1. Streaming Data Integration (Future)
- Pull monthly listeners from Spotify
- Estimate revenue potential
- Calculate publishing value

### 2. Competitive Intelligence
- Flag if artist recently left publisher
- Identify publishing deal expiration patterns
- Track catalog growth rate

### 3. Territory Analysis
- Which territories are covered
- International opportunities
- Sub-publishing needs

### 4. Writer Analysis
- Is artist the sole writer?
- Co-writing patterns
- Split analysis

## Sample Use Cases

### Use Case 1: Emerging Artist Scout
"I found this artist with 100K monthly listeners. Should we approach them?"
→ Tool shows 80% unregistered, no major publisher → **HIGH OPPORTUNITY**

### Use Case 2: Competitive Analysis
"Artist is with Indie Publisher X. Should we try to sign them?"
→ Tool shows only 30% coverage, indie deal → **MEDIUM OPPORTUNITY** (co-pub possible)

### Use Case 3: Catalog Acquisition
"Should we acquire this artist's back catalog?"
→ Tool shows 90% already with Major Publisher → **LOW OPPORTUNITY**

## Implementation Priority

1. **Phase 1** (Now): Update output format to A&R focus
2. **Phase 2**: Add opportunity scoring algorithm
3. **Phase 3**: Enhance publisher intelligence
4. **Phase 4**: Add streaming data integration
5. **Phase 5**: Build web dashboard for A&R team

---

This transforms the tool from a technical matching system into an **A&R decision-making tool** focused on publishing opportunities.
