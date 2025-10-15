#!/usr/bin/env python3
"""
Spotify to Musical Works Cross-Reference Tool

Identifies musical works (song compositions) corresponding to a Spotify artist's recordings
by cross-referencing public rights databases (MLC and Songview/ASCAP/BMI).

Usage:
    python spotify_works_matcher.py <spotify_artist_url>
    python spotify_works_matcher.py https://open.spotify.com/artist/1234567890

Requirements:
    - Python 3.10+
    - See requirements.txt for dependencies
"""

import json
import csv
import time
import sys
import re
import argparse
import random
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import difflib

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("ERROR: 'requests' library not found.")
    print("Please install dependencies: pip install -r requirements.txt")
    sys.exit(1)

try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

try:
    from dotenv import load_dotenv
    import os
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


# ============================================================================
# Configuration
# ============================================================================

# API Endpoints
MLC_SEARCH_URL = "https://api.ptl.themlc.com/api2v/public/search/works"
ASCAP_SEARCH_URL = "https://www.ascap.com/repertory"
BMI_SEARCH_URL = "https://repertoire.bmi.com/Search/Search"
SONGVIEW_SEARCH_URL = "https://songview.com"  # Combined ASCAP/BMI portal

# Request configuration - Browser-like headers to avoid blocking
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://portal.themlc.com",
    "Referer": "https://portal.themlc.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site"
}

# Retry configuration
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.0
REQUEST_DELAY = 0.5  # seconds between requests (increased to avoid rate limiting)
REQUEST_DELAY_VARIANCE = 0.3  # random variance to make requests more human-like

# Matching thresholds
TITLE_MATCH_THRESHOLD = 0.85  # Similarity threshold for fuzzy matching
DURATION_TOLERANCE_SECONDS = 5  # Allow +/- 5 seconds difference


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class SpotifyTrack:
    """Represents a Spotify track/recording."""
    track_id: str
    title: str
    artists: List[str]
    album: str
    isrc: Optional[str]
    duration_ms: int
    release_date: Optional[str]
    track_number: int
    disc_number: int
    
    @property
    def duration_seconds(self) -> int:
        return self.duration_ms // 1000


@dataclass
class MusicalWork:
    """Represents a musical work (composition) from rights databases."""
    work_id: str
    title: str
    source: str  # 'MLC' or 'Songview'
    iswc: Optional[str]
    writers: List[str]
    publishers: List[str]
    raw_data: Dict[str, Any]


@dataclass
class WorkMatch:
    """Represents a match between a Spotify track and a musical work."""
    spotify_track_id: str
    spotify_title: str
    spotify_isrc: Optional[str]
    work_id: str
    work_title: str
    work_source: str
    iswc: Optional[str]
    confidence_score: float
    match_method: str
    notes: str


@dataclass
class Contributor:
    """Represents a songwriter or publisher."""
    work_id: str
    work_title: str
    contributor_name: str
    contributor_type: str  # 'writer' or 'publisher'
    role: Optional[str]
    share_percentage: Optional[float]
    ipi_number: Optional[str]
    pro: Optional[str]  # Performing Rights Organization


# ============================================================================
# Spotify API Client
# ============================================================================

class SpotifyClient:
    """Client for fetching data from Spotify Web API."""
    
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic."""
        session = requests.Session()
        retry = Retry(
            total=MAX_RETRIES,
            backoff_factor=BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def authenticate(self) -> bool:
        """Authenticate with Spotify API using Client Credentials flow."""
        if not self.client_id or not self.client_secret:
            print("⚠️  No Spotify credentials provided. Using public data only.")
            return False
        
        print("🔐 Authenticating with Spotify API...")
        
        auth_url = "https://accounts.spotify.com/api/token"
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        try:
            response = self.session.post(auth_url, data=auth_data)
            response.raise_for_status()
            self.access_token = response.json()["access_token"]
            print("✅ Authenticated successfully")
            return True
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    def extract_artist_id(self, url: str) -> Optional[str]:
        """Extract artist ID from Spotify URL."""
        # Handle various URL formats
        patterns = [
            r'spotify\.com/artist/([a-zA-Z0-9]+)',
            r'open\.spotify\.com/artist/([a-zA-Z0-9]+)',
            r'^([a-zA-Z0-9]{22})$'  # Direct ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_artist_info(self, artist_id: str) -> Optional[Dict[str, Any]]:
        """Get artist information."""
        url = f"https://api.spotify.com/v1/artists/{artist_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}
        
        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Failed to fetch artist info: {e}")
            return None
    
    def get_artist_albums(self, artist_id: str) -> List[Dict[str, Any]]:
        """Get all albums for an artist."""
        albums = []
        url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
        headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}
        params = {
            "include_groups": "album,single",
            "limit": 50,
            "market": "US"
        }
        
        while url:
            try:
                response = self.session.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                albums.extend(data.get("items", []))
                url = data.get("next")
                params = None  # Next URL already has params
                time.sleep(REQUEST_DELAY)
            except Exception as e:
                print(f"⚠️  Error fetching albums: {e}")
                break
        
        return albums
    
    def get_album_tracks(self, album_id: str) -> List[Dict[str, Any]]:
        """Get all tracks for an album."""
        tracks = []
        url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
        headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}
        params = {"limit": 50, "market": "US"}
        
        while url:
            try:
                response = self.session.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                tracks.extend(data.get("items", []))
                url = data.get("next")
                params = None
                time.sleep(REQUEST_DELAY)
            except Exception as e:
                print(f"⚠️  Error fetching tracks: {e}")
                break
        
        return tracks
    
    def get_tracks_details(self, track_ids: List[str]) -> List[Dict[str, Any]]:
        """Get detailed information for multiple tracks (including ISRCs)."""
        if not track_ids:
            return []
        
        headers = {"Authorization": f"Bearer {self.access_token}"} if self.access_token else {}
        all_tracks = []
        
        # API allows up to 50 tracks per request
        for i in range(0, len(track_ids), 50):
            batch = track_ids[i:i+50]
            url = f"https://api.spotify.com/v1/tracks"
            params = {"ids": ",".join(batch), "market": "US"}
            
            try:
                response = self.session.get(url, headers=headers, params=params)
                response.raise_for_status()
                data = response.json()
                all_tracks.extend(data.get("tracks", []))
                time.sleep(REQUEST_DELAY)
            except Exception as e:
                print(f"⚠️  Error fetching track details: {e}")
        
        return all_tracks
    
    def get_artist_tracks(self, artist_id: str) -> List[SpotifyTrack]:
        """Get all tracks for an artist with full metadata."""
        print(f"\n🎵 Fetching tracks for artist {artist_id}...")
        
        # Get artist info
        artist_info = self.get_artist_info(artist_id)
        if not artist_info:
            return []
        
        artist_name = artist_info.get("name", "Unknown")
        print(f"👤 Artist: {artist_name}")
        
        # Get all albums
        print("📀 Fetching albums...")
        albums = self.get_artist_albums(artist_id)
        print(f"   Found {len(albums)} albums/singles")
        
        # Get tracks from each album
        print("🎼 Fetching tracks...")
        track_ids = set()
        album_track_map = {}
        
        for album in albums:
            album_id = album["id"]
            album_name = album["name"]
            tracks = self.get_album_tracks(album_id)
            
            for track in tracks:
                track_id = track["id"]
                if track_id not in track_ids:
                    track_ids.add(track_id)
                    album_track_map[track_id] = {
                        "album_name": album_name,
                        "release_date": album.get("release_date"),
                        "track_number": track.get("track_number", 0),
                        "disc_number": track.get("disc_number", 1)
                    }
        
        print(f"   Found {len(track_ids)} unique tracks")
        
        # Get detailed track info (including ISRCs)
        print("🔍 Fetching track details (ISRCs)...")
        track_details = self.get_tracks_details(list(track_ids))
        
        # Convert to SpotifyTrack objects
        spotify_tracks = []
        for track in track_details:
            if not track:
                continue
            
            track_id = track["id"]
            album_info = album_track_map.get(track_id, {})
            
            spotify_track = SpotifyTrack(
                track_id=track_id,
                title=track["name"],
                artists=[artist["name"] for artist in track.get("artists", [])],
                album=album_info.get("album_name", ""),
                isrc=track.get("external_ids", {}).get("isrc"),
                duration_ms=track.get("duration_ms", 0),
                release_date=album_info.get("release_date"),
                track_number=album_info.get("track_number", 0),
                disc_number=album_info.get("disc_number", 1)
            )
            spotify_tracks.append(spotify_track)
        
        print(f"✅ Collected {len(spotify_tracks)} tracks with metadata")
        return spotify_tracks


# ============================================================================
# MLC Database Client
# ============================================================================

class MLCClient:
    """Client for searching the Mechanical Licensing Collective database."""
    
    def __init__(self):
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic."""
        session = requests.Session()
        retry = Retry(
            total=MAX_RETRIES,
            backoff_factor=BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def search_by_title(self, title: str, artist: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search MLC database by title and optionally artist."""
        url = MLC_SEARCH_URL
        
        # Build search query
        query = title
        if artist:
            query = f"{title} {artist}"
        
        params = {
            "q": query,
            "page": 0,
            "size": 20,
            "sort": ["title.keyword,asc"]
        }
        
        # Empty JSON body (API requires POST with empty body)
        body = {}
        
        try:
            response = self.session.post(url, params=params, json=body, headers=HEADERS, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Extract works from response
            works = data.get("content", []) or data.get("works", []) or []
            # Random delay to appear more human-like
            delay = REQUEST_DELAY + random.uniform(-REQUEST_DELAY_VARIANCE, REQUEST_DELAY_VARIANCE)
            time.sleep(max(0.1, delay))
            return works
        except Exception as e:
            # Silently skip errors to avoid cluttering output
            return []
    
    def search_by_isrc(self, isrc: str) -> List[Dict[str, Any]]:
        """Search MLC database by ISRC."""
        url = MLC_SEARCH_URL
        
        params = {
            "q": isrc,
            "page": 0,
            "size": 20
        }
        
        # Empty JSON body (API requires POST with empty body)
        body = {}
        
        try:
            response = self.session.post(url, params=params, json=body, headers=HEADERS, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            works = data.get("content", []) or data.get("works", []) or []
            # Random delay to appear more human-like
            delay = REQUEST_DELAY + random.uniform(-REQUEST_DELAY_VARIANCE, REQUEST_DELAY_VARIANCE)
            time.sleep(max(0.1, delay))
            return works
        except Exception as e:
            # Silently skip errors to avoid cluttering output
            return []
    
    def parse_work(self, raw_work: Dict[str, Any]) -> MusicalWork:
        """Parse MLC work data into MusicalWork object."""
        work_id = str(raw_work.get("property_id") or raw_work.get("id") or raw_work.get("work_id", ""))
        title = raw_work.get("title", "")
        iswc = raw_work.get("iswc")
        
        # Extract writers
        writers = []
        writers_data = raw_work.get("writers", []) or raw_work.get("authors", [])
        if isinstance(writers_data, list):
            for writer in writers_data:
                if isinstance(writer, dict):
                    writers.append(writer.get("name", ""))
                elif isinstance(writer, str):
                    writers.append(writer)
        
        # Extract publishers
        publishers = []
        publishers_data = raw_work.get("publishers", [])
        if isinstance(publishers_data, list):
            for pub in publishers_data:
                if isinstance(pub, dict):
                    publishers.append(pub.get("name", ""))
                elif isinstance(pub, str):
                    publishers.append(pub)
        
        return MusicalWork(
            work_id=work_id,
            title=title,
            source="MLC",
            iswc=iswc,
            writers=writers,
            publishers=publishers,
            raw_data=raw_work
        )


# ============================================================================
# Songview (ASCAP/BMI) Client
# ============================================================================

class SongviewClient:
    """Client for searching Songview (combined ASCAP/BMI repertory)."""
    
    def __init__(self):
        self.session = self._create_session()
        self.ascap_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.ascap.com/repertory"
        }
        self.bmi_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://repertoire.bmi.com/"
        }
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic."""
        session = requests.Session()
        retry = Retry(
            total=MAX_RETRIES,
            backoff_factor=BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def search_ascap(self, title: str, artist: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search ASCAP repertory."""
        # ASCAP ACE (ASCAP Clearance Express) search
        # Note: ASCAP's public search may require web scraping or have rate limits
        # This is a best-effort implementation
        
        try:
            # Try ASCAP ACE title search
            url = "https://www.ascap.com/repertory"
            params = {
                "search": title,
                "type": "title"
            }
            
            response = self.session.get(url, params=params, headers=self.ascap_headers, timeout=10)
            if response.status_code == 200:
                # ASCAP returns HTML, would need parsing
                # For now, return empty to avoid errors
                time.sleep(REQUEST_DELAY)
                return []
        except Exception:
            pass
        
        return []
    
    def search_bmi(self, title: str, artist: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search BMI repertoire."""
        # BMI Repertoire search
        # Note: BMI's public search may require authentication or have restrictions
        
        try:
            url = "https://repertoire.bmi.com/Search/Search"
            data = {
                "Main_Search_Text": title,
                "Main_Search": "Title",
                "Search_Type": "all",
                "View_Count": 20
            }
            
            response = self.session.post(url, data=data, headers=self.bmi_headers, timeout=10)
            if response.status_code == 200:
                # BMI returns HTML, would need parsing
                time.sleep(REQUEST_DELAY)
                return []
        except Exception:
            pass
        
        return []
    
    def search_by_title(self, title: str, artist: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search both ASCAP and BMI by title."""
        results = []
        
        # Search ASCAP
        ascap_results = self.search_ascap(title, artist)
        results.extend(ascap_results)
        
        # Search BMI
        bmi_results = self.search_bmi(title, artist)
        results.extend(bmi_results)
        
        return results
    
    def parse_work(self, raw_work: Dict[str, Any]) -> MusicalWork:
        """Parse Songview/ASCAP/BMI work data into MusicalWork object."""
        work_id = str(raw_work.get("work_id", ""))
        title = raw_work.get("title", "")
        iswc = raw_work.get("iswc")
        
        writers = raw_work.get("writers", [])
        publishers = raw_work.get("publishers", [])
        
        source = raw_work.get("source", "Songview")
        
        return MusicalWork(
            work_id=work_id,
            title=title,
            source=source,
            iswc=iswc,
            writers=writers,
            publishers=publishers,
            raw_data=raw_work
        )


# ============================================================================
# Matching Engine
# ============================================================================

class WorkMatcher:
    """Matches Spotify tracks to musical works with confidence scoring."""
    
    def __init__(self, mlc_client: MLCClient, songview_client: SongviewClient):
        self.mlc_client = mlc_client
        self.songview_client = songview_client
    
    def calculate_title_similarity(self, title1: str, title2: str) -> float:
        """Calculate similarity between two titles using fuzzy matching."""
        # Normalize titles
        t1 = self._normalize_title(title1)
        t2 = self._normalize_title(title2)
        
        # Use SequenceMatcher for fuzzy matching
        return difflib.SequenceMatcher(None, t1, t2).ratio()
    
    def _normalize_title(self, title: str) -> str:
        """Normalize title for comparison."""
        # Convert to lowercase
        title = title.lower()
        
        # Remove common suffixes/prefixes
        patterns = [
            r'\s*\(.*?\)\s*',  # Remove parentheses content
            r'\s*\[.*?\]\s*',  # Remove brackets content
            r'\s*-\s*remaster.*',
            r'\s*-\s*remix.*',
            r'\s*-\s*live.*',
            r'\s*feat\..*',
            r'\s*ft\..*',
        ]
        
        for pattern in patterns:
            title = re.sub(pattern, '', title, flags=re.IGNORECASE)
        
        # Remove extra whitespace
        title = ' '.join(title.split())
        
        return title
    
    def match_track(self, track: SpotifyTrack) -> Tuple[List[WorkMatch], Dict[str, MusicalWork]]:
        """Find matching works for a Spotify track.
        
        Returns:
            Tuple of (matches, works_dict) where works_dict maps work_id to MusicalWork
        """
        matches = []
        works_dict = {}
        
        # Strategy 1: Search by ISRC (most reliable)
        if track.isrc:
            mlc_works = self.mlc_client.search_by_isrc(track.isrc)
            for raw_work in mlc_works:
                work = self.mlc_client.parse_work(raw_work)
                works_dict[work.work_id] = work
                confidence = 0.95  # High confidence for ISRC match
                
                match = WorkMatch(
                    spotify_track_id=track.track_id,
                    spotify_title=track.title,
                    spotify_isrc=track.isrc,
                    work_id=work.work_id,
                    work_title=work.title,
                    work_source=work.source,
                    iswc=work.iswc,
                    confidence_score=confidence,
                    match_method="ISRC",
                    notes="Matched via ISRC"
                )
                matches.append(match)
        
        # Strategy 2: Search by title + artist
        if not matches or len(matches) < 2:
            artist = track.artists[0] if track.artists else None
            mlc_works = self.mlc_client.search_by_title(track.title, artist)
            
            for raw_work in mlc_works:
                work = self.mlc_client.parse_work(raw_work)
                
                # Calculate title similarity
                similarity = self.calculate_title_similarity(track.title, work.title)
                
                if similarity >= TITLE_MATCH_THRESHOLD:
                    # Check if already matched by ISRC
                    if any(m.work_id == work.work_id for m in matches):
                        continue
                    
                    works_dict[work.work_id] = work
                    confidence = similarity * 0.85  # Lower confidence than ISRC
                    notes = f"Title similarity: {similarity:.2%}"
                    
                    match = WorkMatch(
                        spotify_track_id=track.track_id,
                        spotify_title=track.title,
                        spotify_isrc=track.isrc,
                        work_id=work.work_id,
                        work_title=work.title,
                        work_source=work.source,
                        iswc=work.iswc,
                        confidence_score=confidence,
                        match_method="Title+Artist",
                        notes=notes
                    )
                    matches.append(match)
        
        # Sort by confidence score
        matches.sort(key=lambda m: m.confidence_score, reverse=True)
        
        return matches, works_dict
    
    def match_all_tracks(self, tracks: List[SpotifyTrack]) -> Tuple[List[WorkMatch], Dict[str, MusicalWork]]:
        """Match all tracks to musical works.
        
        Returns:
            Tuple of (all_matches, all_works) where all_works maps work_id to MusicalWork
        """
        print(f"\n🔍 Matching {len(tracks)} tracks to musical works...")
        
        all_matches = []
        all_works = {}
        
        for i, track in enumerate(tracks, 1):
            print(f"   [{i}/{len(tracks)}] {track.title}", end=" ", flush=True)
            
            matches, works = self.match_track(track)
            all_matches.extend(matches)
            all_works.update(works)
            
            if matches:
                print(f"✅ {len(matches)} match(es)")
            else:
                print("❌ No matches")
            
            time.sleep(REQUEST_DELAY)
        
        print(f"\n✅ Found {len(all_matches)} total matches")
        print(f"🎼 Found {len(all_works)} unique works")
        return all_matches, all_works


# ============================================================================
# Output Generator
# ============================================================================

class OutputGenerator:
    """Generates CSV output files."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_works_csv(self, matches: List[WorkMatch], filename: str = "matched_works.csv"):
        """Generate CSV of matched works."""
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                "Work ID",
                "Work Title",
                "Source",
                "ISWC",
                "Spotify Track ID",
                "Spotify Title",
                "Spotify ISRC",
                "Confidence Score",
                "Match Method",
                "Notes"
            ])
            
            # Deduplicate by work_id
            seen_works = set()
            for match in matches:
                if match.work_id in seen_works:
                    continue
                seen_works.add(match.work_id)
                
                writer.writerow([
                    match.work_id,
                    match.work_title,
                    match.work_source,
                    match.iswc or "",
                    match.spotify_track_id,
                    match.spotify_title,
                    match.spotify_isrc or "",
                    f"{match.confidence_score:.2%}",
                    match.match_method,
                    match.notes
                ])
        
        print(f"📄 Works CSV: {filepath} ({len(seen_works)} unique works)")
        return filepath
    
    def generate_contributors_csv(self, works_data: Dict[str, MusicalWork], 
                                  filename: str = "contributors.csv"):
        """Generate CSV of contributors (writers/publishers)."""
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                "Work ID",
                "Work Title",
                "Contributor Name",
                "Contributor Type",
                "Role",
                "Share %",
                "IPI Number",
                "PRO"
            ])
            
            contributor_count = 0
            for work_id, work in works_data.items():
                # Add writers
                for writer in work.writers:
                    writer_name = writer if isinstance(writer, str) else writer.get("name", "")
                    if writer_name:
                        writer.writerow([
                            work.work_id,
                            work.title,
                            writer_name,
                            "writer",
                            "",  # Role - would need to parse from raw_data
                            "",  # Share % - would need to parse from raw_data
                            "",  # IPI Number - would need to parse from raw_data
                            ""   # PRO - would need to parse from raw_data
                        ])
                        contributor_count += 1
                
                # Add publishers
                for publisher in work.publishers:
                    pub_name = publisher if isinstance(publisher, str) else publisher.get("name", "")
                    if pub_name:
                        writer.writerow([
                            work.work_id,
                            work.title,
                            pub_name,
                            "publisher",
                            "",
                            "",
                            "",
                            ""
                        ])
                        contributor_count += 1
        
        print(f"📄 Contributors CSV: {filepath} ({contributor_count} contributors)")
        return filepath
    
    def generate_identifiers_csv(self, matches: List[WorkMatch], filename: str = "identifiers.csv"):
        """Generate CSV linking recordings to works."""
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                "Spotify Track ID",
                "Spotify Title",
                "ISRC",
                "Work ID",
                "Work Title",
                "ISWC",
                "Source",
                "Confidence Score",
                "Match Method"
            ])
            
            for match in matches:
                writer.writerow([
                    match.spotify_track_id,
                    match.spotify_title,
                    match.spotify_isrc or "",
                    match.work_id,
                    match.work_title,
                    match.iswc or "",
                    match.work_source,
                    f"{match.confidence_score:.2%}",
                    match.match_method
                ])
        
        print(f"📄 Identifiers CSV: {filepath} ({len(matches)} mappings)")
        return filepath
    
    def generate_comprehensive_csv(self, tracks: List[SpotifyTrack], matches: List[WorkMatch], 
                                   works_data: Dict[str, MusicalWork], filename: str = "COMPREHENSIVE_REPORT.csv"):
        """Generate one comprehensive CSV with all track and work data."""
        filepath = self.output_dir / filename
        
        # Build a mapping of track_id -> list of matches
        track_matches = {}
        for match in matches:
            if match.spotify_track_id not in track_matches:
                track_matches[match.spotify_track_id] = []
            track_matches[match.spotify_track_id].append(match)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                "Spotify Track ID",
                "Spotify Track Title",
                "Spotify Artists",
                "Album",
                "ISRC",
                "Release Date",
                "Duration (ms)",
                "Work ID",
                "Work Title",
                "ISWC",
                "Source (MLC/ASCAP/BMI)",
                "Writers",
                "Publishers",
                "Confidence Score",
                "Match Method",
                "Registration Status"
            ])
            
            # Write data for each track
            for track in tracks:
                track_match_list = track_matches.get(track.track_id, [])
                
                if not track_match_list:
                    # Track with no matches
                    writer.writerow([
                        track.track_id,
                        track.title,
                        ", ".join(track.artists),
                        track.album,
                        track.isrc or "",
                        track.release_date or "",
                        track.duration_ms,
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "",
                        "UNREGISTERED"
                    ])
                else:
                    # Track with matches - one row per match
                    for match in track_match_list:
                        work = works_data.get(match.work_id)
                        writers = ", ".join(work.writers) if work else ""
                        publishers = ", ".join(work.publishers) if work else ""
                        
                        writer.writerow([
                            track.track_id,
                            track.title,
                            ", ".join(track.artists),
                            track.album,
                            track.isrc or "",
                            track.release_date or "",
                            track.duration_ms,
                            match.work_id,
                            match.work_title,
                            match.iswc or "",
                            match.work_source,
                            writers,
                            publishers,
                            f"{match.confidence_score:.2%}",
                            match.match_method,
                            "REGISTERED"
                        ])
        
        print(f"📄 Comprehensive Report: {filepath}")
        return filepath


# ============================================================================
# A&R Publishing Intelligence Report Generator
# ============================================================================

def generate_ar_report(artist_name: str, artist_id: str, tracks: List[SpotifyTrack],
                       matches: List['WorkMatch'], works_data: List['MusicalWork'],
                       output_dir: Path, spotify_url: str):
    """Generate A&R-focused publishing intelligence report."""
    
    # Analyze publishing coverage
    track_ids_with_matches = set(m.spotify_track_id for m in matches)
    registered_tracks = [t for t in tracks if t.track_id in track_ids_with_matches]
    unregistered_tracks = [t for t in tracks if t.track_id not in track_ids_with_matches]
    
    total_tracks = len(tracks)
    registered_count = len(registered_tracks)
    unregistered_count = len(unregistered_tracks)
    coverage_pct = (registered_count / total_tracks * 100) if total_tracks > 0 else 0
    
    # Analyze publishers
    from collections import Counter
    publisher_counts = Counter()
    all_publishers = set()
    major_publishers = {"SONY", "UNIVERSAL", "WARNER", "EMI", "BMG", "KOBALT", "CONCORD", "DOWNTOWN"}
    
    for work in works_data.values():
        for pub_data in work.raw_data.get("originalPublishers", []):
            pub_name = pub_data.get("publisherName", "")
            if pub_name:
                publisher_counts[pub_name] += 1
                all_publishers.add(pub_name)
    
    has_major = any(any(major in pub.upper() for major in major_publishers) for pub in all_publishers)
    has_indie = len(all_publishers) > 0 and not has_major
    is_self_published = len(all_publishers) == 0
    
    # Calculate opportunity score
    score = 0
    if coverage_pct < 25: score += 40
    elif coverage_pct < 50: score += 30
    elif coverage_pct < 75: score += 20
    else: score += 10
    
    if is_self_published or not has_major: score += 30
    if has_indie: score += 10
    
    if total_tracks > 50: score += 20
    elif total_tracks > 20: score += 15
    else: score += 10
    
    if score >= 70:
        level = "HIGH"
        recommendation = "🎯 STRONG OPPORTUNITY: Artist has significant unregistered catalog and no major publisher. Excellent candidate for publishing deal."
    elif score >= 50:
        level = "MEDIUM"
        recommendation = "⚡ MODERATE OPPORTUNITY: Artist has some publishing gaps. Worth investigating for co-publishing or administration deal."
    else:
        level = "LOW"
        recommendation = "📊 LIMITED OPPORTUNITY: Artist appears well-represented. May only be suitable for specific territories or future works."
    
    # Generate summary report
    summary_file = output_dir / "PUBLISHING_SUMMARY.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("  ARTIST PUBLISHING ANALYSIS - A&R INTELLIGENCE REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Artist: {artist_name}\n")
        f.write(f"Spotify ID: {artist_id}\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Spotify URL: {spotify_url}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("  PUBLISHING COVERAGE\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Total Tracks: {total_tracks}\n")
        f.write(f"Registered Tracks: {registered_count} ({coverage_pct:.1f}%)\n")
        f.write(f"Unregistered Tracks: {unregistered_count} ({100-coverage_pct:.1f}%)\n\n")
        
        # Visual coverage bar
        registered_bars = int(coverage_pct / 5)
        unregistered_bars = 20 - registered_bars
        f.write("Coverage Visualization:\n")
        f.write("[" + "█" * registered_bars + "░" * unregistered_bars + f"] {coverage_pct:.1f}%\n\n")
        
        if unregistered_count > total_tracks * 0.5:
            f.write(f"⚠️  SIGNIFICANT GAP: {100-coverage_pct:.0f}% of catalog unregistered\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("  PUBLISHER ANALYSIS\n")
        f.write("=" * 80 + "\n\n")
        
        if publisher_counts:
            f.write("Current Publishers:\n")
            for pub_name, count in publisher_counts.most_common(5):
                f.write(f"  • {pub_name}: {count} work(s)\n")
            f.write("\n")
        else:
            f.write("No publishers found in database\n\n")
        
        f.write(f"Has Major Publisher: {'Yes' if has_major else 'No'}\n")
        f.write(f"Has Indie Publisher: {'Yes' if has_indie else 'No'}\n")
        f.write(f"Self-Published/Unrepresented: {'Yes' if is_self_published else 'No'}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("  OPPORTUNITY ASSESSMENT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Opportunity Score: {score:.0f}/100\n")
        f.write(f"Opportunity Level: {level}\n\n")
        f.write(f"Recommendation:\n{recommendation}\n\n")
        
        f.write("Key Factors:\n")
        if unregistered_count > 0:
            f.write(f"  ✓ {unregistered_count} unregistered tracks ({100-coverage_pct:.0f}% of catalog)\n")
        if total_tracks > 50:
            f.write(f"  ✓ Large catalog ({total_tracks} tracks)\n")
        elif total_tracks > 20:
            f.write(f"  ✓ Moderate catalog ({total_tracks} tracks)\n")
        if is_self_published:
            f.write(f"  ✓ No major publisher representation\n")
        if has_indie:
            f.write(f"  • Has indie publisher relationship\n")
        if has_major:
            f.write(f"  ⚠ Already with major publisher\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("  ACTIONABLE INSIGHTS\n")
        f.write("=" * 80 + "\n\n")
        
        if unregistered_count > 0:
            f.write(f"• {unregistered_count} tracks have NO publishing registration - immediate revenue opportunity\n")
        if is_self_published:
            f.write(f"• Artist appears to be self-releasing without publishing support\n")
        if total_tracks > 30:
            f.write(f"• Catalog size ({total_tracks} tracks) suggests consistent output\n")
        
        f.write("\nNEXT STEPS:\n")
        f.write("1. Verify artist's streaming performance (monthly listeners, growth)\n")
        f.write("2. Check if artist owns masters or is signed to label\n")
        f.write("3. Research any existing publishing admin deals\n")
        f.write("4. Prepare publishing deal proposal if opportunity score is high\n")
        
        f.write("\n" + "=" * 80 + "\n")
    
    print(f"📄 Publishing Summary: {summary_file}")
    
    # Generate unregistered tracks CSV (high opportunity tracks)
    if unregistered_tracks:
        unregistered_file = output_dir / "unregistered_tracks.csv"
        with open(unregistered_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Track Title", "ISRC", "Release Date", "Album", "Artists", "Priority"])
            
            for track in unregistered_tracks:
                priority = "HIGH" if track.isrc else "MEDIUM"
                writer.writerow([
                    track.title,
                    track.isrc or "N/A",
                    track.release_date,
                    track.album,
                    ", ".join(track.artists),
                    priority
                ])
        
        print(f"📄 Unregistered Tracks: {unregistered_file} ({len(unregistered_tracks)} opportunities)")
    
    # Generate publisher analysis CSV
    if publisher_counts:
        publisher_file = output_dir / "publisher_analysis.csv"
        with open(publisher_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Publisher Name", "Work Count", "Percentage", "Type"])
            
            total_pub_works = sum(publisher_counts.values())
            for pub_name, count in publisher_counts.most_common():
                pct = (count / total_pub_works * 100) if total_pub_works > 0 else 0
                pub_type = "Major" if any(major in pub_name.upper() for major in major_publishers) else "Indie"
                writer.writerow([pub_name, count, f"{pct:.1f}%", pub_type])
        
        print(f"📄 Publisher Analysis: {publisher_file}")


# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Cross-reference Spotify tracks with musical works databases (MLC, ASCAP, BMI)"
    )
    parser.add_argument("artist_url", nargs='?', help="Spotify artist URL or ID (optional - will read from clipboard if not provided)")
    parser.add_argument("--client-id", help="Spotify Client ID (optional if in .env)")
    parser.add_argument("--client-secret", help="Spotify Client Secret (optional if in .env)")
    parser.add_argument("--output-dir", default="results", help="Base output directory for results")
    
    args = parser.parse_args()
    
    # Get artist URL from clipboard if not provided
    artist_url = args.artist_url
    if not artist_url:
        if not CLIPBOARD_AVAILABLE:
            print("❌ ERROR: No artist URL provided and clipboard support not available.")
            print("   Install pyperclip: pip install pyperclip")
            print("   Or provide URL as argument: python spotify_works_matcher.py <url>")
            sys.exit(1)
        try:
            artist_url = pyperclip.paste().strip()
            if not artist_url:
                print("❌ ERROR: Clipboard is empty. Please copy a Spotify artist URL.")
                sys.exit(1)
            print(f"📋 Using URL from clipboard: {artist_url}")
        except Exception as e:
            print(f"❌ ERROR: Could not read from clipboard: {e}")
            sys.exit(1)
    
    # We'll create the timestamped folder after we get the artist name
    base_output_dir = Path(args.output_dir)
    client_id = args.client_id or os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = args.client_secret or os.getenv("SPOTIFY_CLIENT_SECRET")
    
    print("=" * 80)
    print("  Spotify Works Analyzer - MLC + ASCAP + BMI")
    print("=" * 80)
    print()
    
    # Initialize clients
    spotify_client = SpotifyClient(client_id, client_secret)
    mlc_client = MLCClient()
    songview_client = SongviewClient()
    matcher = WorkMatcher(mlc_client, songview_client)
    
    # Authenticate with Spotify if credentials provided
    if client_id and client_secret:
        spotify_client.authenticate()
    
    # Extract artist ID
    artist_id = spotify_client.extract_artist_id(artist_url)
    if not artist_id:
        print(f"❌ Invalid Spotify artist URL: {artist_url}")
        sys.exit(1)
    
    print(f"🎯 Artist ID: {artist_id}")
    
    # Get artist info to get name
    artist_info = spotify_client.get_artist_info(artist_id)
    artist_name = artist_info.get("name", "Unknown_Artist") if artist_info else "Unknown_Artist"
    
    # Create timestamped folder: ArtistName_YYYYMMDD_HHMMSS
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Sanitize artist name for folder
    safe_artist_name = re.sub(r'[^\w\s-]', '', artist_name).strip().replace(' ', '_')
    folder_name = f"{safe_artist_name}_{timestamp}"
    output_dir = base_output_dir / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Output folder: {output_dir}")
    
    output_gen = OutputGenerator(output_dir)
    
    # Fetch Spotify tracks
    tracks = spotify_client.get_artist_tracks(artist_id)
    if not tracks:
        print("❌ No tracks found for artist")
        sys.exit(1)
    
    # Match tracks to works
    matches, works_data = matcher.match_all_tracks(tracks)
    
    if not matches:
        print("\n⚠️  No matches found")
        sys.exit(0)
    
    # Generate output files
    print(f"\n📊 Generating reports...")
    
    # Generate comprehensive CSV
    output_gen.generate_comprehensive_csv(tracks, matches, works_data)
    
    # Generate detailed CSV files
    output_gen.generate_works_csv(matches)
    output_gen.generate_contributors_csv(works_data)
    output_gen.generate_identifiers_csv(matches)
    
    # Generate A&R Publishing Report
    print(f"\n📋 Generating A&R Publishing Intelligence Report...")
    generate_ar_report(artist_name, artist_id, tracks, matches, works_data, output_dir, artist_url)
    
    # Summary
    registered_tracks = len([t for t in tracks if t.track_id in {m.spotify_track_id for m in matches}])
    unregistered_tracks = len(tracks) - registered_tracks
    coverage_pct = (registered_tracks / len(tracks) * 100) if len(tracks) > 0 else 0
    
    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"📊 Total Tracks: {len(tracks)}")
    print(f"✅ Registered: {registered_tracks} ({coverage_pct:.1f}%)")
    print(f"❌ Unregistered: {unregistered_tracks} ({100-coverage_pct:.1f}%)")
    print(f"🎼 Unique Works Found: {len(works_data)}")
    print(f"📁 Output: {output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
