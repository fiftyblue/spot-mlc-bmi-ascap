# Utility Scripts

Helper scripts for advanced workflows and batch processing.

## Available Utilities

### batch_process.py
Process multiple artists from a list file.

```bash
python utils/batch_process.py artists.txt
```

### create_master_report.py
Combine multiple artist reports into a single master report.

```bash
python utils/create_master_report.py results/
```

### generate_ar_report_from_csv.py
Generate A&R publishing intelligence report from existing CSV data.

```bash
python utils/generate_ar_report_from_csv.py results/Artist_Name/COMPREHENSIVE_REPORT.csv
```

## Usage

All utilities are designed to work with the output from `spotify_works_matcher.py`. Run the main script first, then use these utilities for additional analysis.
