# tests

The pytest suite. Run it with
`uv run pytest tests/ --cov=src --cov-report=term`; coverage must stay at or
above the 90 configured in `pyproject.toml`. `conftest.py` only puts the repo
root and `src` on `sys.path`. No mocking framework is used or permitted:
`test_no_mocks.py` fails the suite if one appears.
