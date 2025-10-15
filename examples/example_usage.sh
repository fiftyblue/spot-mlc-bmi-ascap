#!/bin/bash
# Example usage scenarios for Spotify Works Matcher

echo "=========================================="
echo "Spotify Works Matcher - Usage Examples"
echo "=========================================="
echo ""

# Example 1: Basic usage (no authentication)
echo "Example 1: Basic usage (no authentication)"
echo "Command:"
echo '  python spotify_works_matcher.py "https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4"'
echo ""

# Example 2: With credentials from environment
echo "Example 2: With credentials from .env file"
echo "Command:"
echo '  python spotify_works_matcher.py "https://open.spotify.com/artist/06HL4z0CvFAxyc27GXpf02"'
echo ""

# Example 3: With inline credentials
echo "Example 3: With inline credentials"
echo "Command:"
echo '  python spotify_works_matcher.py "https://open.spotify.com/artist/1Xyo4u8uXC1ZmMpatF05PJ" \'
echo '    --client-id YOUR_CLIENT_ID \'
echo '    --client-secret YOUR_CLIENT_SECRET'
echo ""

# Example 4: Custom output directory
echo "Example 4: Custom output directory"
echo "Command:"
echo '  python spotify_works_matcher.py "https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4" \'
echo '    --output-dir results/drake'
echo ""

# Example 5: Batch processing
echo "Example 5: Batch processing multiple artists"
echo "Command:"
echo '  python batch_process.py artists_example.txt'
echo ""

# Example 6: Run tests
echo "Example 6: Run tests"
echo "Command:"
echo '  python test_tool.py'
echo ""

echo "=========================================="
echo "Quick Start:"
echo "=========================================="
echo "1. Install dependencies:"
echo "   pip install -r requirements.txt"
echo ""
echo "2. (Optional) Set up credentials:"
echo "   cp .env.example .env"
echo "   # Edit .env with your Spotify API credentials"
echo ""
echo "3. Run the tool:"
echo '   python spotify_works_matcher.py "SPOTIFY_ARTIST_URL"'
echo ""
echo "4. View results in the output/ directory"
echo ""
echo "For more details, see:"
echo "  - QUICKSTART.md (5-minute guide)"
echo "  - README.md (full documentation)"
echo "  - PROJECT_OVERVIEW.md (architecture)"
echo "=========================================="
