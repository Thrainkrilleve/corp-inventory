# Contributing to Corp Inventory

Thank you for considering contributing to Corp Inventory! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in your interactions with other contributors.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/allianceauth-corp-inventory/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, Alliance Auth version)
   - Any relevant logs or screenshots

### Suggesting Features

1. Check if the feature has already been suggested
2. Create a new issue describing:
   - The problem you're trying to solve
   - Your proposed solution
   - Any alternatives you've considered
   - Why this would be useful to other users

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature/fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Write or update tests as needed
5. Ensure all tests pass:
   ```bash
   python runtests.py
   ```
6. Format your code:
   ```bash
   black corp_inventory
   isort corp_inventory
   ```
7. Commit your changes with a clear message
8. Push to your fork
9. Create a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/allianceauth-corp-inventory.git
cd allianceauth-corp-inventory

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

## Code Style

- Follow PEP 8
- Use Black for formatting (line length 88)
- Use isort for import sorting
- Add docstrings to all functions and classes
- Write meaningful commit messages

## Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Maintain or improve code coverage

## Documentation

- Update README.md if you change functionality
- Update CHANGELOG.md following Keep a Changelog format
- Add docstrings to new code
- Update inline comments as needed

## Questions?

Feel free to ask questions in:
- GitHub Issues
- Alliance Auth Discord

Thank you for contributing!
