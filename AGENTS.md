# AGENTS.md - AI News Project Development Guide

## Project Overview

This is a Python project using Pydantic for data modeling with a virtual environment (venv) and `requirements.txt`.

## Environment Setup

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Project Structure

```
.
├── venv/              # Python virtual environment
├── data/              # Data files (input)
├── output/            # Output/generated files
├── scripts/           # Utility scripts
├── requirements.txt   # Python dependencies
└── opencode.json      # OpenCode configuration
```

## Build, Lint, and Test Commands

```bash
# Install dev dependencies
pip install pytest ruff mypy

# Run all tests
pytest

# Run a single test file
pytest tests/test_file.py

# Run a single test function
pytest tests/test_file.py::test_function_name

# Run tests with verbose output
pytest -v

# Run tests matching a pattern
pytest -k "test_pattern"

# Lint with ruff
ruff check .

# Format with ruff
ruff format .

# Type checking with mypy
mypy .
```

## Code Style Guidelines

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Variables/Functions | snake_case | `user_name`, `get_user()` |
| Classes | PascalCase | `UserModel`, `NewsArticle` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Private variables | `_` prefix | `_private_cache` |
| Modules/Files | snake_case | `data_loader.py` |

### Import Order

1. Standard library (os, sys, typing)
2. Third-party (pydantic, httpx)
3. Local imports (relative)

### Type Hints

Always use type hints:

```python
def get_user(user_id: int) -> Optional[User]:
    ...

def process_items(items: List[Dict[str, Any]]) -> List[User]:
    ...
```

### Pydantic Models (v2)

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class NewsArticle(BaseModel):
    model_config = ConfigDict(str_strip=True, validate_assignment=True)
    
    title: str = Field(..., min_length=1, max_length=200)
    content: str
    author: str
    published_at: datetime
    tags: list[str] = Field(default_factory=list)
    url: Optional[str] = None
    
    def is_recent(self, days: int = 7) -> bool:
        from datetime import timedelta
        return datetime.now() - self.published_at < timedelta(days=days)
```

### Error Handling

```python
import logging
logger = logging.getLogger(__name__)

def fetch_data(url: str) -> Optional[dict]:
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException as e:
        logger.error(f"Request timeout for {url}: {e}")
        return None
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error {e.response.status_code} for {url}")
        return None
    except Exception as e:
        logger.exception(f"Unexpected error fetching {url}")
        raise
```

### Recommended File Structure

```
src/
├── __init__.py
├── models/         # Data models (Pydantic)
├── services/       # Business logic
└── utils/         # Utility functions
tests/             # Test files (test_*.py)
data/              # Input data
output/            # Generated output
requirements.txt
requirements-dev.txt
pyproject.toml
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
```

### Testing Guidelines

- Use pytest
- Write descriptive test names: `test_<function>_<expected_behavior>`
- Use fixtures for common setup
- Follow Arrange-Act-Assert pattern
- Test edge cases and error conditions

## Notes for AI Agents

- New project - implement core functionality first
- All code should include type hints
- Pydantic is available for data validation
- No existing tests - write tests as you implement
- Run lint/typecheck before committing
