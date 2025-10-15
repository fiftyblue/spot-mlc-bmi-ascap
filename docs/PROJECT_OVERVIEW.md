# Spotify Works Matcher - Project Overview

## What This Tool Does

This tool bridges the gap between **recorded music** (Spotify tracks) and **musical compositions** (works in rights databases). It helps identify which songs (compositions) correspond to which recordings, along with their writers and publishers.

### The Problem It Solves

When you listen to a song on Spotify, you're hearing a **recording** (sound recording). But behind that recording is a **musical work** (the composition - melody, lyrics, arrangement). These are separate copyrights with different rights holders:

- **Recording**: Owned by record labels, performers
- **Musical Work**: Owned by songwriters, publishers

This tool helps you find the musical work information for any Spotify artist's recordings.

## Architecture

```
┌─────────────────────┐
│   Spotify API       │
│  (Track Metadata)   │
└──────────┬──────────┘
           │
           │ ISRCs, Titles, Artists
           ▼
┌─────────────────────┐
│  Matching Engine    │
│  - ISRC matching    │
│  - Fuzzy title      │
│  - Confidence score │
└──────────┬──────────┘
           │
           ├──────────────┬──────────────┐
           ▼              ▼              ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │   MLC    │   │ Songview │   │  Future  │
    │ Database │   │ (ASCAP/  │   │   APIs   │
    │          │   │   BMI)   │   │          │
    └──────────┘   └──────────┘   └──────────┘
           │              │              │
           └──────────────┴──────────────┘
                      │
                      ▼
           ┌─────────────────────┐
           │   CSV Outputs       │
           │  - Works            │
           │  - Contributors     │
           │  - Identifiers      │
           └─────────────────────┘
```

## File Structure

```
spot-mlc-bmi-ascap/
├── spotify_works_matcher.py    # Main tool (900+ lines)
├── fetch_black17_publisher_works.py  # Original MLC fetcher
├── requirements.txt             # Python dependencies
├── .env.example                 # Configuration template
├── .gitignore                   # Git ignore rules
│
├── README.md                    # Full documentation
├── QUICKSTART.md               # 5-minute getting started
├── PROJECT_OVERVIEW.md         # This file
│
├── batch_process.py            # Process multiple artists
├── artists_example.txt         # Example batch input
├── test_tool.py                # Unit tests
│
└── output/                     # Generated CSV files
    ├── matched_works.csv
    ├── contributors.csv
    └── identifiers.csv
```

## Key Components

### 1. Spotify Integration (`SpotifyClient`)

- Authenticates with Spotify API
- Fetches artist information
- Retrieves all albums and tracks
- Extracts ISRCs and metadata

### 2. Database Clients

**MLCClient**: Searches Mechanical Licensing Collective database
- Search by ISRC (most reliable)
- Search by title + artist
- Parse work metadata

**SongviewClient**: Searches ASCAP/BMI combined repertory
- Placeholder implementation
- Requires additional development

### 3. Matching Engine (`WorkMatcher`)

**Strategy 1: ISRC Matching** (95% confidence)
- Direct lookup using International Standard Recording Code
- Most reliable when available

**Strategy 2: Title + Artist Matching** (up to 85% confidence)
- Fuzzy string matching with normalization
- Removes parentheticals, features, remasters
- Uses difflib.SequenceMatcher

**Strategy 3: Future Enhancements**
- Duration comparison
- Release date validation
- Writer name matching

### 4. Output Generator

Produces three CSV files:

1. **matched_works.csv**: Unique musical works
2. **contributors.csv**: Writers and publishers
3. **identifiers.csv**: Recording-to-work mappings

## Data Models

### SpotifyTrack
```python
- track_id: Spotify's unique identifier
- title: Recording title
- artists: List of performing artists
- album: Album name
- isrc: International Standard Recording Code
- duration_ms: Length in milliseconds
- release_date: Release date
- track_number: Position on album
- disc_number: Disc number
```

### MusicalWork
```python
- work_id: Database identifier
- title: Composition title
- source: "MLC" or "Songview"
- iswc: International Standard Musical Work Code
- writers: List of songwriters
- publishers: List of publishers
- raw_data: Full API response
```

### WorkMatch
```python
- spotify_track_id: Links to recording
- spotify_title: Recording title
- spotify_isrc: Recording ISRC
- work_id: Links to composition
- work_title: Composition title
- work_source: Database source
- iswc: Work ISWC
- confidence_score: 0.0 to 1.0
- match_method: "ISRC" or "Title+Artist"
- notes: Additional details
```

## Matching Algorithm

```python
for each track:
    # Step 1: Try ISRC match
    if track.isrc exists:
        search MLC by ISRC
        if found:
            create match with 95% confidence
    
    # Step 2: Try title match
    if no ISRC match or want more results:
        search MLC by title + artist
        for each result:
            calculate title similarity
            if similarity >= 85%:
                create match with (similarity * 0.85) confidence
    
    # Step 3: Sort by confidence
    return matches sorted by confidence score
```

## API Endpoints Used

### Spotify Web API
- `GET /v1/artists/{id}` - Artist info
- `GET /v1/artists/{id}/albums` - Artist albums
- `GET /v1/albums/{id}/tracks` - Album tracks
- `GET /v1/tracks` - Track details (batch)

### MLC Public API
- `GET /api2v/public/search/works/title` - Search by title
- `GET /api2v/public/search/works/isrc` - Search by ISRC

### Songview (Future)
- Endpoint TBD - requires research

## Configuration Options

### Environment Variables
```bash
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
OUTPUT_DIR=output
TITLE_MATCH_THRESHOLD=0.85
DURATION_TOLERANCE_SECONDS=5
REQUEST_DELAY=0.2
MAX_RETRIES=3
```

### Command Line Arguments
```bash
--client-id         Spotify Client ID
--client-secret     Spotify Client Secret
--output-dir        Output directory for CSVs
```

## Performance Characteristics

### Speed
- ~1-2 seconds per track (with delays)
- 100 tracks: ~2-3 minutes
- 500 tracks: ~10-15 minutes

### Rate Limits
- Spotify: 30 requests/second (with auth)
- MLC: ~5 requests/second (recommended)
- Delays built in to respect limits

### Accuracy
- ISRC matches: 95%+ confidence
- Title matches: 70-85% confidence
- Overall match rate: 60-80% (depends on catalog)

## Future Enhancements

### High Priority
1. **Full Songview Integration**
   - Implement actual API calls
   - Add authentication
   - Parse ASCAP/BMI data

2. **Enhanced Matching**
   - Duration comparison
   - Writer name validation
   - Multiple database consensus

3. **Better Contributor Data**
   - Parse share percentages
   - Extract IPI numbers
   - Identify PRO affiliations

### Medium Priority
4. **Caching Layer**
   - Cache API responses
   - Avoid duplicate searches
   - Speed up re-runs

5. **Web Interface**
   - Simple web UI
   - Real-time progress
   - Interactive results

6. **Export Formats**
   - JSON output
   - Excel with formatting
   - Database import scripts

### Low Priority
7. **Additional Sources**
   - YouTube Content ID
   - Apple Music
   - SoundExchange

8. **Analytics**
   - Match quality reports
   - Coverage statistics
   - Writer/publisher insights

## Known Limitations

1. **Songview Not Implemented**: Placeholder only
2. **No Share Percentages**: Not parsed from MLC data
3. **No IPI Numbers**: Not extracted yet
4. **Single Database**: Only MLC fully implemented
5. **No Caching**: Repeated searches hit API
6. **Basic Error Handling**: Could be more robust
7. **No Resume**: Can't resume interrupted runs

## Testing

Run the test suite:
```bash
python test_tool.py
```

Tests cover:
- Data model creation
- URL parsing
- Title normalization
- Similarity calculation

## Deployment Considerations

### For Personal Use
- Run locally
- Use .env for credentials
- Process one artist at a time

### For Production
- Add database caching
- Implement rate limiting
- Add monitoring/logging
- Use task queue (Celery)
- Add authentication
- Deploy as web service

## Legal & Compliance

- Uses only public APIs
- Respects rate limits
- No circumvention of access controls
- Outputs for informational purposes only
- Manual verification required for critical uses

## Contributing

Areas needing development:
1. Songview API integration
2. Enhanced contributor parsing
3. Additional matching strategies
4. Performance optimization
5. Web interface
6. Documentation improvements

## Support & Resources

- **Spotify API Docs**: https://developer.spotify.com/documentation/web-api
- **MLC API**: https://api.ptl.themlc.com/
- **Songview**: https://songview.com/
- **ISRC**: https://isrc.ifpi.org/
- **ISWC**: https://www.iswc.org/

## Version History

- **v1.0** (Current): Initial release
  - Spotify integration
  - MLC search
  - Basic matching
  - CSV output

## License

Educational and research purposes. Users responsible for compliance with all applicable terms of service.
