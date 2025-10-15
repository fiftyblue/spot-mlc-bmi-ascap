# Project Structure

```
spotify-works-matcher/
│
├── 📄 spotify_works_matcher.py    # Main application
├── 📄 requirements.txt             # Python dependencies
├── 📄 README.md                    # Project documentation
├── 📄 LICENSE                      # MIT License
├── 📄 CONTRIBUTING.md              # Contribution guidelines
├── 📄 .env.example                 # Environment variables template
├── 📄 .gitignore                   # Git ignore rules
│
├── 📁 docs/                        # Documentation
│   ├── QUICKSTART.md               # Quick start guide
│   ├── USAGE.md                    # Detailed usage instructions
│   ├── TROUBLESHOOTING_GUIDE.md    # Common issues and solutions
│   ├── PROJECT_OVERVIEW.md         # Technical architecture
│   ├── AR_PUBLISHING_TOOL_SPEC.md  # A&R features specification
│   └── DEMO_OUTPUT_EXAMPLE.md      # Example output files
│
├── 📁 utils/                       # Utility scripts
│   ├── README.md                   # Utils documentation
│   ├── batch_process.py            # Batch process multiple artists
│   ├── create_master_report.py     # Combine multiple reports
│   └── generate_ar_report_from_csv.py  # Generate A&R reports
│
├── 📁 examples/                    # Example files
│   ├── README.md                   # Examples documentation
│   ├── artists_example.txt         # Example artist list
│   └── example_usage.sh            # Example shell scripts
│
├── 📁 scripts/                     # Development/testing scripts
│   ├── README.md                   # Scripts documentation
│   ├── test_mlc_api.py             # Test MLC API connectivity
│   ├── test_tool.py                # Integration tests
│   └── fetch_black17_publisher_works.py  # Example publisher script
│
└── 📁 results/                     # Output directory (gitignored)
    └── ArtistName_TIMESTAMP/       # Timestamped results folder
        ├── COMPREHENSIVE_REPORT.csv
        ├── matched_works.csv
        ├── contributors.csv
        ├── identifiers.csv
        ├── unregistered_tracks.csv
        ├── publisher_analysis.csv
        └── PUBLISHING_SUMMARY.txt
```

## Key Files

### Core Application
- **spotify_works_matcher.py** - Main tool that fetches Spotify data and matches with MLC/ASCAP/BMI

### Configuration
- **requirements.txt** - Python package dependencies
- **.env.example** - Template for environment variables (Spotify credentials)
- **.gitignore** - Prevents committing sensitive data and output files

### Documentation
- **README.md** - Main project documentation
- **docs/** - Detailed guides and specifications
- **CONTRIBUTING.md** - How to contribute to the project
- **LICENSE** - MIT License

### Utilities
- **utils/** - Helper scripts for batch processing and report generation
- **examples/** - Example usage patterns and sample data
- **scripts/** - Development and testing tools

## Output Structure

Each run creates a timestamped folder in `results/` containing:
- CSV files with matched works and contributor data
- A&R intelligence report (PUBLISHING_SUMMARY.txt)
- Analysis of unregistered tracks and publisher distribution
