# Contributing to SpectraTact

Guidelines for contributing to SpectraTact.

## Code of Conduct

Be respectful and professional. Focus on constructive feedback and collaborative problem-solving.

## Contribution Types

Accepted contributions include:

- Bug Reports: Report issues
- Feature Requests: Suggest improvements
- Code Contributions: Fix bugs, add features, improve performance
- Documentation: Update guides, API docs, examples
- Testing: Add tests, improve coverage

## Setup

```bash
pip install -e .[dev]
npm install
pre-commit install
```

See [Developer Guide](docs/developer-guide.md) for details.

## Development

**Run:**
```bash
python -m spectratact              # Python component
npm run dev:win                    # GUI (Windows)
npm run dev:unix                   # GUI (macOS/Linux)
```

**Test:**
```bash
npm run test                       # All tests
pytest                              # Python only
npm run test:frontend              # JavaScript only
```

**Style:**
```bash
black src/spectratact              # Format Python
flake8 src/spectratact             # Lint Python
mypy src/spectratact               # Type check
npx eslint src/desktop             # Lint JavaScript
pre-commit run --all-files         # Run all checks
```

## Workflow

1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes following code style
3. Add/update tests
4. Run tests and linters
5. Commit with clear messages
6. Push and create pull request

**Commit format:**
```
Add feature: brief description

Details if needed.
```

Examples: `Fix: Window detection Unicode bug`, `Add: Custom layout support`

## Pull Requests

**Checklist:**
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Tests added for new functionality
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

Use PR template in `.github/pull_request_template.md`.

## Adding Features

**Python:**
1. Add module under `src/spectratact/`
2. Write tests in `test/backend/`
3. Update docs

**GUI:**
1. Add module in `src/desktop/modules/` or `src/desktop/main/`
2. Register IPC handlers if needed
3. Write tests in `test/frontend/`

**Configuration:**
1. Add to `docs/examples/*.example.yml`
2. Update `src/spectratact/config/validator.py`
3. Document in `docs/configuration.md`

## Reporting Issues

**Bug reports (.github/ISSUE_TEMPLATE/bug_report.md):**
- OS and versions (Python, Node.js, SpectraTact)
- Steps to reproduce
- Expected vs actual behavior
- Logs from `logs/app.log`

**Feature requests (.github/ISSUE_TEMPLATE/feature_request.md):**
- Problem solved
- Proposed solution
- Use cases

## License

Contributions licensed under GPL-3.0-or-later.

---

Version 0.1.0 | Beta | Python 3.8-3.13 | Node.js 18.0+ | Windows 10/11

Copyright 2025 dhaneshbb. Licensed under GPL-3.0-or-later.
