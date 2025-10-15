#!/usr/bin/env python3
"""
Create ONE master CSV with all the A&R info you need.
"""

import csv
import sys
from pathlib import Path
from collections import Counter

def create_master_report(csv_dir: Path, output_file: str = "MASTER_AR_REPORT.csv"):
    """Create one comprehensive CSV with everything."""
    
    # Read matched works
    matched_works_file = csv_dir / "matched_works.csv"
    identifiers_file = csv_dir / "identifiers.csv"
    
    if not identifiers_file.exists():
        print(f"❌ No identifiers.csv found in {csv_dir}")
        return
    
    # Build track data
    track_data = {}
    
    # Read all identifiers
    with open(identifiers_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            track_id = row['Spotify Track ID']
            track_title = row['Spotify Title']
            isrc = row['ISRC']
            work_title = row.get('Work Title', '')
            work_id = row.get('Work ID', '')
            
            if track_id not in track_data:
                track_data[track_id] = {
                    'title': track_title,
                    'isrc': isrc,
                    'matches': [],
                    'match_count': 0
                }
            
            track_data[track_id]['matches'].append(work_title)
            track_data[track_id]['match_count'] += 1
    
    # Calculate stats
    total_tracks = len(track_data)
    tracks_with_matches = sum(1 for t in track_data.values() if t['match_count'] > 0)
    tracks_without_matches = total_tracks - tracks_with_matches
    
    # Determine if matches are real or garbage
    # If we see Greek songs, generic titles, etc., they're likely garbage
    garbage_indicators = ['GREEK', 'WELCOME HOME', 'WEARY EYES', 'QUICK NAP', 'STIN KARDIA']
    
    # Create master CSV
    output_path = csv_dir / output_file
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Track Title',
            'ISRC',
            'Has Publishing?',
            'Match Count',
            'Publishing Status',
            'Opportunity',
            'Notes'
        ])
        
        for track_id, data in track_data.items():
            title = data['title']
            isrc = data['isrc']
            match_count = data['match_count']
            matches = data['matches']
            
            # Determine if matches are real
            has_real_publishing = False
            is_garbage = False
            
            if match_count > 0:
                # Check if matches look like garbage
                sample_match = matches[0].upper() if matches else ''
                if any(indicator in sample_match for indicator in garbage_indicators):
                    is_garbage = True
                    has_publishing = "NO (Bad Data)"
                    status = "UNREGISTERED"
                    opportunity = "HIGH"
                    notes = f"MLC returned {match_count} unrelated works - needs proper registration"
                else:
                    has_publishing = "YES"
                    status = "REGISTERED"
                    opportunity = "LOW"
                    notes = f"Found {match_count} work(s) in MLC"
            else:
                has_publishing = "NO"
                status = "UNREGISTERED"
                opportunity = "HIGH"
                notes = "No publishing found - clear opportunity"
            
            writer.writerow([
                title,
                isrc,
                has_publishing,
                match_count,
                status,
                opportunity,
                notes
            ])
    
    print(f"✅ Created master report: {output_path}")
    print(f"\n📊 Summary:")
    print(f"   Total Tracks: {total_tracks}")
    print(f"   With Matches: {tracks_with_matches}")
    print(f"   Without Matches: {tracks_without_matches}")
    print(f"\n💡 Open {output_file} to see everything in one place!")
    
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_master_report.py <csv_directory>")
        print("\nExample:")
        print("  python create_master_report.py results/Henry_Morris_20251013_212026")
        sys.exit(1)
    
    csv_dir = Path(sys.argv[1])
    
    if not csv_dir.exists():
        print(f"❌ Directory not found: {csv_dir}")
        sys.exit(1)
    
    create_master_report(csv_dir)
