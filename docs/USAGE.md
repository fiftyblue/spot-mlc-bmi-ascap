# Spotify Works Analyzer - Quick Start

## What It Does
Analyzes a Spotify artist's catalog and checks if their songs are registered with MLC, ASCAP, and BMI. Perfect for A&R to identify publishing opportunities.

## Setup (One Time)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note for macOS users:** If you get an "externally-managed-environment" error, use:
   ```bash
   pip install --break-system-packages -r requirements.txt
   ```
   Or install pyperclip via Homebrew:
   ```bash
   brew install pyperclip
   ```

2. **Add Spotify credentials to `.env` file:**
   ```
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   ```

## How to Use

### Simple Method (Clipboard)
1. Copy a Spotify artist URL (e.g., `https://open.spotify.com/artist/...`)
2. Run:
   ```bash
   python3 spotify_works_matcher.py
   ```

The script will automatically read the URL from your clipboard!

### Alternative Method (Command Line)
```bash
python3 spotify_works_matcher.py "https://open.spotify.com/artist/..."
```

## Output

The script creates a timestamped folder in `results/` with:

1. **COMPREHENSIVE_REPORT.csv** - All tracks with registration status, works, writers, publishers
2. **PUBLISHING_SUMMARY.txt** - A&R intelligence report with:
   - Registration coverage %
   - Unregistered tracks (opportunities!)
   - Publisher analysis
   - Opportunity score (HIGH/MEDIUM/LOW)
   - Strategic recommendations

## Example

```bash
# Copy artist URL, then:
python3 spotify_works_matcher.py

# Output appears in:
# results/Artist_Name_20251015_103424/
#   ├── COMPREHENSIVE_REPORT.csv
#   └── PUBLISHING_SUMMARY.txt
```

## What You Get

- **Registered tracks**: Which songs are already in MLC/ASCAP/BMI
- **Unregistered tracks**: Publishing opportunities
- **Publisher info**: Who currently represents the artist
- **Writers**: Songwriting credits
- **Opportunity score**: Is this artist a good publishing target?

---

**That's it!** One script, one command, comprehensive analysis.
