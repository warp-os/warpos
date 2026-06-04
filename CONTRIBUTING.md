# Contributing to WarpOS

Thanks for your interest in contributing to WarpOS! Every contribution helps, whether it's fixing a typo, reporting a bug, or adding a new feature.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/<your-username>/warpos.git
   cd warpos
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/my-feature
   ```

## Development Setup

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=warpos

# Run a specific test file
pytest tests/test_agent.py
```

## Code Style

- We use **Ruff** for linting and formatting
- Run `ruff check .` to lint
- Run `ruff format .` to format
- All code must pass linting before submitting a PR
- Type hints are required for all public functions

## Submitting a PR

1. Make sure all tests pass: `pytest`
2. Lint your code: `ruff check . && ruff format .`
3. Push your branch and open a PR against `main`
4. Fill out the PR template completely
5. Link any related issues

## Reporting Bugs

Use the [bug report template](https://github.com/warp-os/warpos/issues/new?template=bug_report.md). Include:
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- WarpOS version (`pip show warpos`)

## Feature Requests

Use the [feature request template](https://github.com/warp-os/warpos/issues/new?template=feature_request.md). Explain the use case and why it matters to you.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).
