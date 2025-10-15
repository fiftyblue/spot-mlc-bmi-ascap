# Quick Start Guide

Get started with the Spotify Works Matcher in 5 minutes.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Get Spotify Credentials (Optional but Recommended)

1. Go to https://developer.spotify.com/dashboard
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the app name and description
5. Copy your **Client ID** and **Client Secret**

## Step 3: Configure Credentials

Create a `.env` file in this directory:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```
SPOTIFY_CLIENT_ID=your_actual_client_id
SPOTIFY_CLIENT_SECRET=your_actual_client_secret
```

## Step 4: Run the Tool

### Example 1: Basic Usage

```bash
python spotify_works_matcher.py "https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4"
```

### Example 2: With Inline Credentials

```bash
python spotify_works_matcher.py "https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4" \
  --client-id YOUR_CLIENT_ID \
  --client-secret YOUR_CLIENT_SECRET
```

### Example 3: Custom Output Directory

```bash
python spotify_works_matcher.py "https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4" \
  --output-dir results/drake
```

## Step 5: View Results

The tool creates three CSV files in the output directory (default: `output/`):

1. **matched_works.csv** - All matched musical works
2. **contributors.csv** - Writers and publishers
3. **identifiers.csv** - Recording-to-work mappings

Open them in Excel, Google Sheets, or any CSV viewer.

## Example Output

```
================================================================================
  Spotify to Musical Works Cross-Reference Tool
================================================================================

🎯 Artist ID: 3TVXtAsR1Inumwj472S9r4

🎵 Fetching tracks for artist 3TVXtAsR1Inumwj472S9r4...
👤 Artist: Drake
📀 Fetching albums...
   Found 47 albums/singles
🎼 Fetching tracks...
   Found 278 unique tracks
🔍 Fetching track details (ISRCs)...
✅ Collected 278 tracks with metadata

🔍 Matching 278 tracks to musical works...
   [1/278] God's Plan ✅ 1 match(es)
   [2/278] In My Feelings ✅ 1 match(es)
   [3/278] Nice For What ✅ 1 match(es)
   ...

✅ Found 245 total matches
🎼 Found 198 unique works

📊 Generating output files...
📄 Works CSV: output/matched_works.csv (198 unique works)
📄 Contributors CSV: output/contributors.csv (456 contributors)
📄 Identifiers CSV: output/identifiers.csv (245 mappings)

================================================================================
✅ COMPLETED SUCCESSFULLY
================================================================================
📊 Tracks processed: 278
🎵 Matches found: 245
🎼 Unique works: 198
📁 Output directory: output
================================================================================
```

## Troubleshooting

### "No tracks found for artist"
- Check if the Spotify URL is correct
- Try adding credentials for better API access

### "No matches found"
- The artist's works may not be in the MLC database yet
- Try adjusting the matching threshold in the code

### Rate limit errors
- Add delays between requests
- Use Spotify API credentials
- Process smaller batches

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Adjust matching thresholds in `spotify_works_matcher.py`
- Implement Songview integration for ASCAP/BMI data
- Add custom matching strategies

## Tips

1. **Use credentials**: Much better rate limits and data access
2. **Start small**: Test with artists who have fewer tracks
3. **Verify matches**: Always manually verify high-value matches
4. **Batch processing**: Process multiple artists by creating a wrapper script

## Support

For issues:
1. Check the [README.md](README.md) troubleshooting section
2. Verify all dependencies are installed
3. Test with a well-known artist first
