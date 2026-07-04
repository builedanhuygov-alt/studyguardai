# Contributing to StudyGuard AI

Thanks for your interest in improving StudyGuard AI! This guide explains how to
set up your environment and the standards we hold contributions to.

## Development setup
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

## Quality gates (run before pushing)
```bash
ruff check .
black --check .
mypy studyguard
pytest --cov=studyguard --cov-report=term-missing
```
All of the above run automatically in CI on every pull request.

## Commit messages
We use [Conventional Commits](https://www.conventionalcommits.org/):
`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `ci:`, `perf:`.
Example: `feat(session): add drowsiness detector`.

## Adding a detector (plugin system)
You do **not** need to modify `app.py` or the engine. Implement the `Detector`
protocol (`analyze(frame) -> Analysis`), decorate it with `@register_detector`,
and — for a third-party package — expose it via an entry point:
```toml
[project.entry-points."studyguard.detectors"]
my_detector = "my_package.module:MyDetector"
```
Detectors must be **stateless** (no mutable score state); smoothing lives in the
`Aggregator`. Results must contain derived metrics only — never raw frames.

## Tests
- Unit tests live in `tests/`, integration tests in `tests/integration/`.
- Prefer pure functions and inject the clock/collaborators so logic is
  deterministic. Use `FakeDetector` and mocks instead of a real camera.

## Pull requests
Fill out the PR template, keep changes focused, add tests, and update
`CHANGELOG.md` for user-facing changes.
