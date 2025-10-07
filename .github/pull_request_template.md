## Summary
Brief description of changes and motivation.

## Changes
-
-
-

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Refactoring (code improvement without functional changes)
- [ ] Documentation update
- [ ] Configuration change

## Related Issues
Fixes #(issue number)

## Testing Performed

### Python Testing
- [ ] All pytest tests pass: `pytest`
- [ ] No new pytest warnings
- [ ] Added/updated tests for new functionality
- [ ] Tested on Windows [version: ]

### GUI Testing
- [ ] All Jest tests pass: `npm run test:frontend`
- [ ] Manually tested in Electron app
- [ ] Tested UI responsiveness

### Integration Testing
- [ ] Python-Electron communication works correctly
- [ ] Configuration reload works
- [ ] Window operations work as expected
- [ ] Multi-monitor setup tested (if applicable)

## Code Quality

### Python
- [ ] Code formatted with black: `black src/spectratact`
- [ ] Linting passes: `flake8 src/spectratact`
- [ ] No security issues introduced
- [ ] Proper error handling added

### JavaScript
- [ ] Code follows project conventions
- [ ] No console errors in browser DevTools
- [ ] IPC handlers properly registered

## Configuration Changes
- [ ] Updated `settings.yml.example` (if applicable)
- [ ] Updated `loaded_apps.yml.example` (if applicable)
- [ ] Configuration validator updated for new fields

## Documentation
- [ ] Updated README.md (if user-facing changes)
- [ ] Added code comments for complex logic
- [ ] Updated API documentation (if applicable)

## Breaking Changes
If this PR introduces breaking changes, describe:
- What breaks
- Migration path for users
- Updated version number appropriately

## Screenshots
If UI changes, attach before/after screenshots.

## Checklist
- [ ] Code builds successfully: `npm run dist:win`
- [ ] No merge conflicts
- [ ] Branch is up to date with main
- [ ] Commit messages are clear and descriptive
