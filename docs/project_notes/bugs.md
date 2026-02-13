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

### 2026-02-13 - ChallengeOperator Bloom's level test: cognitive_load cancels gap adjustment
- **Issue**: `test_diagnostic_gaps_lower_bloom` expected ("apply", "analyze") but got "evaluate"
- **Root Cause**: Expert audience fixture had `cognitive_load=0.8` which pushed Bloom's level back up, canceling the diagnostic gap pull-down effect
- **Solution**: Created test-specific AudienceProfile with `cognitive_load=0.5` to isolate the gap adjustment
- **Prevention**: When testing one adjustment factor, neutralize other factors that could counteract it

### 2026-02-13 - Pre-existing: test_ai_pipeline.py passes strings to get_layer()
- **Issue**: `AttributeError: 'str' object has no attribute 'value'` in test_ai_pipeline.py
- **Root Cause**: Test iterates layer names as strings instead of LayerName enums when calling `artifact.get_layer()`
- **Solution**: Not yet fixed (pre-existing, not introduced by Phase 8)
- **Prevention**: Use LayerName enum values consistently when calling get_layer()/set_layer()
