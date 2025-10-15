# Contributing to Spotify Works Matcher

Thanks for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

### Suggesting Features

Feature requests are welcome! Please open an issue describing:
- The problem you're trying to solve
- Your proposed solution
- Any alternative solutions you've considered

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Test your changes thoroughly
5. Commit with clear messages (`git commit -m "Add feature: description"`)
6. Push to your fork (`git push origin feature/your-feature-name`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and modular
- Comment complex logic

### Testing

- Test your changes with real Spotify artist URLs
- Verify output CSV files are generated correctly
- Check that existing functionality still works

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/spotify-works-matcher.git
cd spotify-works-matcher

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your Spotify credentials to .env

# Run tests
python scripts/test_tool.py
```

## Areas for Contribution

We especially welcome contributions in these areas:

- **ASCAP/BMI Integration**: Full implementation of Songview API
- **Matching Algorithms**: Improved fuzzy matching and confidence scoring
- **Performance**: Optimization for large catalogs
- **Testing**: Unit tests and integration tests
- **Documentation**: Tutorials, examples, and guides
- **UI**: Web interface or CLI improvements

## Questions?

Feel free to open an issue for any questions about contributing!
