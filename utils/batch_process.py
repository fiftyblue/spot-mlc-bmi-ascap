#!/usr/bin/env python3
"""
Batch processor for multiple Spotify artists.

Usage:
    python batch_process.py artists.txt
    
Where artists.txt contains one Spotify artist URL per line.
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime


def process_artists_batch(artists_file: str):
    """Process multiple artists from a file."""
    
    # Read artist URLs
    artists_path = Path(artists_file)
    if not artists_path.exists():
        print(f"❌ File not found: {artists_file}")
        sys.exit(1)
    
    with open(artists_path, 'r') as f:
        artist_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not artist_urls:
        print("❌ No artist URLs found in file")
        sys.exit(1)
    
    print("=" * 80)
    print(f"  Batch Processing {len(artist_urls)} Artists")
    print("=" * 80)
    print()
    
    # Create batch output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_dir = Path(f"batch_output_{timestamp}")
    batch_dir.mkdir(exist_ok=True)
    
    results = []
    
    for i, url in enumerate(artist_urls, 1):
        print(f"\n{'='*80}")
        print(f"Processing Artist {i}/{len(artist_urls)}: {url}")
        print(f"{'='*80}\n")
        
        # Extract artist ID for output directory name
        artist_id = url.split('/')[-1].split('?')[0]
        output_dir = batch_dir / artist_id
        
        # Run the main script
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "spotify_works_matcher.py",
                    url,
                    "--output-dir", str(output_dir)
                ],
                capture_output=False,
                text=True,
                check=True
            )
            
            results.append({
                "url": url,
                "artist_id": artist_id,
                "status": "success",
                "output_dir": str(output_dir)
            })
            
            print(f"\n✅ Successfully processed {artist_id}")
            
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Failed to process {artist_id}")
            results.append({
                "url": url,
                "artist_id": artist_id,
                "status": "failed",
                "output_dir": str(output_dir)
            })
        except Exception as e:
            print(f"\n❌ Error processing {artist_id}: {e}")
            results.append({
                "url": url,
                "artist_id": artist_id,
                "status": "error",
                "error": str(e)
            })
    
    # Print summary
    print("\n" + "=" * 80)
    print("  BATCH PROCESSING COMPLETE")
    print("=" * 80)
    print(f"\nTotal artists: {len(artist_urls)}")
    print(f"Successful: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"Failed: {sum(1 for r in results if r['status'] != 'success')}")
    print(f"\nOutput directory: {batch_dir}")
    
    # Write summary file
    summary_file = batch_dir / "batch_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("Batch Processing Summary\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Total artists: {len(artist_urls)}\n")
        f.write(f"Successful: {sum(1 for r in results if r['status'] == 'success')}\n")
        f.write(f"Failed: {sum(1 for r in results if r['status'] != 'success')}\n\n")
        
        f.write("Results:\n")
        f.write("-" * 80 + "\n")
        for result in results:
            f.write(f"\nArtist ID: {result['artist_id']}\n")
            f.write(f"URL: {result['url']}\n")
            f.write(f"Status: {result['status']}\n")
            if 'output_dir' in result:
                f.write(f"Output: {result['output_dir']}\n")
            if 'error' in result:
                f.write(f"Error: {result['error']}\n")
    
    print(f"Summary written to: {summary_file}")
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python batch_process.py <artists_file>")
        print("\nExample:")
        print("  python batch_process.py artists.txt")
        print("\nThe artists file should contain one Spotify artist URL per line.")
        sys.exit(1)
    
    process_artists_batch(sys.argv[1])
