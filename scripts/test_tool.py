#!/usr/bin/env python3
"""
Test script for the Spotify Works Matcher tool.

Tests various components without making actual API calls.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from spotify_works_matcher import (
    SpotifyTrack,
    MusicalWork,
    WorkMatch,
    WorkMatcher,
    MLCClient,
    SongviewClient
)


def test_title_normalization():
    """Test title normalization and similarity."""
    print("=" * 80)
    print("Testing Title Normalization and Similarity")
    print("=" * 80)
    
    mlc_client = MLCClient()
    songview_client = SongviewClient()
    matcher = WorkMatcher(mlc_client, songview_client)
    
    test_cases = [
        ("God's Plan", "God's Plan", True),
        ("God's Plan (feat. Drake)", "God's Plan", True),
        ("God's Plan - Remastered", "God's Plan", True),
        ("In My Feelings", "In My Feelings", True),
        ("Nice For What", "Nice for What", True),
        ("Hotline Bling", "Completely Different Song", False),
    ]
    
    for title1, title2, should_match in test_cases:
        similarity = matcher.calculate_title_similarity(title1, title2)
        normalized1 = matcher._normalize_title(title1)
        normalized2 = matcher._normalize_title(title2)
        
        print(f"\nOriginal: '{title1}' vs '{title2}'")
        print(f"Normalized: '{normalized1}' vs '{normalized2}'")
        print(f"Similarity: {similarity:.2%}")
        print(f"Expected match: {should_match}, Actual: {similarity >= 0.85}")
        
        if should_match:
            assert similarity >= 0.80, f"Expected high similarity for '{title1}' vs '{title2}'"
        else:
            assert similarity < 0.85, f"Expected low similarity for '{title1}' vs '{title2}'"
    
    print("\n✅ All title normalization tests passed!")


def test_spotify_track_creation():
    """Test SpotifyTrack data model."""
    print("\n" + "=" * 80)
    print("Testing SpotifyTrack Data Model")
    print("=" * 80)
    
    track = SpotifyTrack(
        track_id="3klE3LHkgBoonHSXDgfKqG",
        title="God's Plan",
        artists=["Drake"],
        album="Scorpion",
        isrc="USCM51800011",
        duration_ms=198973,
        release_date="2018-06-29",
        track_number=1,
        disc_number=1
    )
    
    print(f"\nTrack ID: {track.track_id}")
    print(f"Title: {track.title}")
    print(f"Artists: {', '.join(track.artists)}")
    print(f"ISRC: {track.isrc}")
    print(f"Duration: {track.duration_ms}ms ({track.duration_seconds}s)")
    
    assert track.duration_seconds == 198, "Duration conversion failed"
    
    print("\n✅ SpotifyTrack tests passed!")


def test_musical_work_creation():
    """Test MusicalWork data model."""
    print("\n" + "=" * 80)
    print("Testing MusicalWork Data Model")
    print("=" * 80)
    
    work = MusicalWork(
        work_id="12345",
        title="God's Plan",
        source="MLC",
        iswc="T-123.456.789-0",
        writers=["Aubrey Graham", "Daveon Jackson", "Matthew Samuels"],
        publishers=["Sony/ATV Music Publishing", "Universal Music Publishing"],
        raw_data={}
    )
    
    print(f"\nWork ID: {work.work_id}")
    print(f"Title: {work.title}")
    print(f"Source: {work.source}")
    print(f"ISWC: {work.iswc}")
    print(f"Writers: {', '.join(work.writers)}")
    print(f"Publishers: {', '.join(work.publishers)}")
    
    print("\n✅ MusicalWork tests passed!")


def test_work_match_creation():
    """Test WorkMatch data model."""
    print("\n" + "=" * 80)
    print("Testing WorkMatch Data Model")
    print("=" * 80)
    
    match = WorkMatch(
        spotify_track_id="3klE3LHkgBoonHSXDgfKqG",
        spotify_title="God's Plan",
        spotify_isrc="USCM51800011",
        work_id="12345",
        work_title="God's Plan",
        work_source="MLC",
        iswc="T-123.456.789-0",
        confidence_score=0.95,
        match_method="ISRC",
        notes="Matched via ISRC"
    )
    
    print(f"\nSpotify Track: {match.spotify_title} ({match.spotify_track_id})")
    print(f"Musical Work: {match.work_title} ({match.work_id})")
    print(f"Confidence: {match.confidence_score:.2%}")
    print(f"Method: {match.match_method}")
    print(f"Notes: {match.notes}")
    
    print("\n✅ WorkMatch tests passed!")


def test_url_extraction():
    """Test Spotify URL parsing."""
    print("\n" + "=" * 80)
    print("Testing Spotify URL Extraction")
    print("=" * 80)
    
    from spotify_works_matcher import SpotifyClient
    
    client = SpotifyClient()
    
    test_urls = [
        ("https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4", "3TVXtAsR1Inumwj472S9r4"),
        ("https://spotify.com/artist/3TVXtAsR1Inumwj472S9r4", "3TVXtAsR1Inumwj472S9r4"),
        ("3TVXtAsR1Inumwj472S9r4", "3TVXtAsR1Inumwj472S9r4"),
        ("https://open.spotify.com/artist/3TVXtAsR1Inumwj472S9r4?si=abc123", "3TVXtAsR1Inumwj472S9r4"),
    ]
    
    for url, expected_id in test_urls:
        extracted_id = client.extract_artist_id(url)
        print(f"\nURL: {url}")
        print(f"Expected: {expected_id}")
        print(f"Extracted: {extracted_id}")
        assert extracted_id == expected_id, f"Failed to extract ID from {url}"
    
    print("\n✅ URL extraction tests passed!")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("  Spotify Works Matcher - Test Suite")
    print("=" * 80)
    
    try:
        test_spotify_track_creation()
        test_musical_work_creation()
        test_work_match_creation()
        test_url_extraction()
        test_title_normalization()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
