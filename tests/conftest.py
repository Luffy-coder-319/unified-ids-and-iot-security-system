"""
Test collection configuration for this workspace.

Some files under tests/ are diagnostic scripts (they start with "test_" but are meant
to be run as standalone scripts). Those cause pytest collection errors because they
define functions that accept parameters (e.g. packets, label) which pytest treats as
fixtures. To avoid failing the CI/test-run, list those files in collect_ignore so
pytest will skip them during collection.

If you prefer a different approach (fix the files, add proper fixtures, or remove the
test_ prefix), tell me and I can change it.
"""

# Files to ignore during pytest collection (relative to the tests/ directory)
collect_ignore = [
    "test_detection.py",
    "test_hybrid_detection.py",
]
