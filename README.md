# Spotify Works Matcher

> **Cross-reference Spotify recordings with musical works databases (MLC, ASCAP, BMI) to identify publishing rights and opportunities.**

A Python tool that identifies musical works (song compositions) corresponding to a Spotify artist's recordings by cross-referencing public rights databases including the Mechanical Licensing Collective (MLC) and Songview (ASCAP/BMI combined repertory).

Perfect for A&R professionals, music publishers, rights managers, and anyone analyzing music publishing catalogs.

## Features

- **Spotify Integration**: Fetches complete track metadata including titles, ISRCs, durations, and release dates
- **Multi-Database Search**: Queries both MLC and Songview databases for comprehensive coverage
- **Intelligent Matching**: Uses multiple strategies (ISRC matching, fuzzy title matching) with confidence scoring
- **Comprehensive Output**: Generates multiple CSV files:
  - `COMPREHENSIVE_REPORT.csv` - Complete track-to-work mapping with all metadata
  - `matched_works.csv` - Unique matched musical works with confidence scores
  - `contributors.csv` - Detailed songwriters and publishers for each work
  - `identifiers.csv` - Links between recordings (ISRCs) and works (ISWCs)
  - `unregistered_tracks.csv` - Tracks with no MLC registration found
  - `publisher_analysis.csv` - Publisher distribution analysis
  - `PUBLISHING_SUMMARY.txt` - A&R intelligence report

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/spotify-works-matcher.git
cd spotify-works-matcher

# Install dependencies
pip install -r requirements.txt

# (Optional) Set up Spotify API credentials
cp .env.example .env
# Edit .env with your Spotify Client ID and Secret
```

### Basic Usage

```bash
# Analyze an artist
python spotify_works_matcher.py "https://open.spotify.com/artist/ARTIST_ID"

# Results will be saved to: results/ArtistName_TIMESTAMP/
```

### Prerequisites

- Python 3.10 or higher
- pip package manager
- (Optional) Spotify API credentials for better rate limits
  - Get credentials at https://developer.spotify.com/dashboard

## Project Structure

```
spotify-works-matcher/
├── spotify_works_matcher.py   # Main tool
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── docs/                      # Documentation
│   ├── QUICKSTART.md
│   ├── USAGE.md
│   └── TROUBLESHOOTING_GUIDE.md
├── utils/                     # Utility scripts
│   ├── batch_process.py
│   └── create_master_report.py
├── examples/                  # Example files
│   └── example_usage.sh
└── scripts/                   # Dev/test scripts
    └── test_mlc_api.py
```

## Usage Examples

### Basic Usage

```bash
# Analyze a single artist
python spotify_works_matcher.py "https://open.spotify.com/artist/ARTIST_ID"
```

### With Spotify API Credentials (Recommended)

```bash
# Using command-line arguments
python spotify_works_matcher.py "https://open.spotify.com/artist/ARTIST_ID" \
  --client-id YOUR_CLIENT_ID \
  --client-secret YOUR_CLIENT_SECRET

# Or use environment variables (.env file)
python spotify_works_matcher.py "https://open.spotify.com/artist/ARTIST_ID"
```

### Batch Processing

```bash
# Process multiple artists
python utils/batch_process.py examples/artists_example.txt
```

For more examples, see the [examples/](examples/) directory.

## Output Files

The script generates multiple CSV files in a timestamped folder (e.g., `results/ArtistName_20241015_103424/`):

### 1. COMPREHENSIVE_REPORT.csv

The main output file with complete track-to-work mapping:

| Column | Description |
|--------|-------------|
| Spotify Track ID | Spotify's unique track identifier |
| Spotify Track Title | Recording title on Spotify |
| Spotify Artists | Artist name(s) |
| Album | Album name |
| ISRC | International Standard Recording Code |
| Release Date | Track release date |
| Duration (ms) | Track duration in milliseconds |
| Work ID | Unique identifier from the rights database |
| Work Title | Title of the musical composition |
| ISWC | International Standard Musical Work Code |
| Source (MLC/ASCAP/BMI) | Database source |
| Writers | Comma-separated list of songwriters |
| Publishers | Comma-separated list of publishers |
| Confidence Score | Match confidence (0-100%) |
| Match Method | How the match was found (ISRC, Title+Artist, etc.) |
| Registration Status | REGISTERED or UNREGISTERED |

### 2. matched_works.csv

Contains unique musical works matched to the artist's recordings (deduplicated):

| Column | Description |
|--------|-------------|
| Work ID | Unique identifier from the rights database |
| Work Title | Title of the musical composition |
| Source | Database source (MLC or Songview) |
| ISWC | International Standard Musical Work Code |
| Spotify Track ID | Spotify's unique track identifier |
| Spotify Title | Recording title on Spotify |
| Spotify ISRC | International Standard Recording Code |
| Confidence Score | Match confidence (0-100%) |
| Match Method | How the match was found (ISRC, Title+Artist, etc.) |
| Notes | Additional matching details |

### 3. contributors.csv

Lists all songwriters and publishers for matched works (one row per contributor per work):

| Column | Description |
|--------|-------------|
| Work ID | Links to matched_works.csv |
| Work Title | Composition title |
| Contributor Name | Writer or publisher name |
| Contributor Type | "writer" or "publisher" |
| Role | Specific role (composer, lyricist, etc.) |
| Share % | Ownership percentage |
| IPI Number | Interested Parties Information number |
| PRO | Performing Rights Organization (ASCAP, BMI, etc.) |

### 4. identifiers.csv

Maps recordings to works with all identifiers (one row per track-work match):

| Column | Description |
|--------|-------------|
| Spotify Track ID | Spotify's recording identifier |
| Spotify Title | Recording title |
| ISRC | Recording's ISRC code |
| Work ID | Musical work identifier |
| Work Title | Composition title |
| ISWC | Work's ISWC code |
| Source | Database source |
| Confidence Score | Match confidence |
| Match Method | Matching strategy used |

### 5. unregistered_tracks.csv

Lists tracks that have no MLC registration found (publishing opportunities):

| Column | Description |
|--------|-------------|
| Track Title | Recording title |
| ISRC | Recording's ISRC code |
| Release Date | Track release date |
| Album | Album name |
| Artists | Artist name(s) |
| Priority | HIGH (has ISRC) or MEDIUM (no ISRC) |

### 6. publisher_analysis.csv

Analyzes publisher distribution across matched works:

| Column | Description |
|--------|-------------|
| Publisher Name | Publisher name |
| Work Count | Number of works |
| Percentage | Percentage of total works |
| Type | Major or Indie |

### 7. PUBLISHING_SUMMARY.txt

A&R intelligence report with:
- Publishing coverage statistics
- Publisher analysis
- Opportunity assessment score
- Actionable insights and recommendations

## Matching Strategies

The tool uses multiple strategies to find matches, prioritized by reliability:

1. **ISRC Matching** (95% confidence)
   - Direct lookup using International Standard Recording Code
   - Most reliable method when ISRCs are available

2. **Title + Artist Matching** (up to 85% confidence)
   - Fuzzy string matching on normalized titles
   - Considers artist names for disambiguation
   - Confidence based on similarity score

3. **Duration Validation** (optional enhancement)
   - Compares recording duration with work metadata
   - Used to validate or adjust confidence scores

## API Rate Limits and Best Practices

- **Spotify API**: 
  - Without authentication: Limited requests
  - With authentication: Higher rate limits
  - Automatic retry with exponential backoff

- **MLC API**: 
  - Public API with reasonable rate limits
  - 200ms delay between requests
  - Automatic retry on failures

- **Songview**: 
  - May require additional authentication
  - Check terms of service for usage limits

## Limitations and Notes

1. **Songview Integration**: The Songview client is a placeholder. Full implementation requires:
   - Official API access or web scraping approach
   - Proper authentication mechanism
   - Compliance with terms of service

2. **Match Confidence**: Confidence scores are estimates based on:
   - Data quality and completeness
   - Matching method used
   - Title similarity thresholds

3. **Data Coverage**: 
   - Not all recordings have ISRCs in Spotify
   - Not all works are registered in all databases
   - Some matches may be false positives

4. **Performance**: 
   - Processing time depends on catalog size
   - Rate limiting adds delays
   - Large catalogs may take several minutes

## Advanced Configuration

Edit the configuration constants in `spotify_works_matcher.py`:

```python
# Matching thresholds
TITLE_MATCH_THRESHOLD = 0.85  # Adjust fuzzy matching sensitivity
DURATION_TOLERANCE_SECONDS = 5  # Duration comparison tolerance

# Request configuration
REQUEST_DELAY = 0.2  # Seconds between API requests
MAX_RETRIES = 3  # Number of retry attempts
```

## Troubleshooting

For detailed troubleshooting, see [docs/TROUBLESHOOTING_GUIDE.md](docs/TROUBLESHOOTING_GUIDE.md).

**Common Issues:**
- **"No tracks found"** - Verify Spotify URL and try with API credentials
- **"Authentication failed"** - Check Client ID/Secret formatting
- **"No matches found"** - Works may not be registered yet in MLC
- **Rate limit errors** - Increase REQUEST_DELAY or use Spotify credentials

## Legal and Compliance

This tool is designed for legitimate research and rights management purposes:

- Uses only public APIs and data
- Respects rate limits and terms of service
- Does not circumvent access controls
- Outputs are for informational purposes

**Always verify matches manually for critical applications like royalty distribution.**

## Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get up and running in 5 minutes
- **[Usage Guide](docs/USAGE.md)** - Detailed usage instructions
- **[Troubleshooting](docs/TROUBLESHOOTING_GUIDE.md)** - Common issues and solutions
- **[Project Overview](docs/PROJECT_OVERVIEW.md)** - Technical architecture

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Areas for improvement:

- Full Songview/ASCAP/BMI API integration
- Additional matching strategies and algorithms
- Enhanced confidence scoring models
- Support for additional rights databases
- Performance optimizations

## License

MIT License - See LICENSE file for details.

This tool is provided for educational and research purposes. Users are responsible for compliance with all applicable terms of service and regulations.

**Always verify matches manually for critical applications like royalty distribution.**

## Acknowledgments

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/) for recording metadata
- [The Mechanical Licensing Collective](https://www.themlc.com/) for public works database
- ASCAP and BMI for Songview repertory data

---

**Made with ❤️ for the music publishing community**
