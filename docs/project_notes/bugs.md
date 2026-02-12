# Bug Log

Track bugs encountered, their root causes, solutions, and prevention strategies.

---

### 2026-02-12 - pip install fails with PEP 668 externally-managed-environment
- **Issue**: `pip install -e ".[dev]"` failed on system Python
- **Root Cause**: Ubuntu/WSL system Python is marked as externally managed (PEP 668)
- **Solution**: Created venv with `python3 -m venv .venv` and installed there
- **Prevention**: Always use a virtual environment for project installs

### 2026-02-12 - hatchling build fails with "Readme file does not exist: README.md"
- **Issue**: `pip install -e .` failed during build
- **Root Cause**: `pyproject.toml` had `readme = "README.md"` but no README.md file existed
- **Solution**: Changed to inline readme: `readme = {text = "Universal understanding middleware", content-type = "text/plain"}`
- **Prevention**: Use inline readme text in pyproject.toml when no README file is needed, or create the README first
