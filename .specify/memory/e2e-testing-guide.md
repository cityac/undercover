# E2E Testing Guide

Project-specific knowledge base for generating and running Playwright E2E tests.

> App structure filled for UnderCover. Extend DOM patterns, page objects and pitfalls as features land.

## App Structure

| Component | Detail |
|-----------|--------|
| **Frontend** | Vite dashboard on `http://localhost:5173` (`baseURL` in `playwright.config.ts`) |
| **API** | FastAPI on `http://127.0.0.1:8000`, health at `/api/health` |
| **Auth** | None until the IMPROVE build day (sign-in arrives then; `e2e/.auth/` is gitignored for it) |
| **Config** | No `.env.e2e`; Playwright starts both servers itself (`webServer`, `reuseExistingServer: true`) |
| **Test runner** | `npx playwright test e2e/{file}.spec.ts` (all: `npm run e2e`, also part of `npm run check`) |
| **Config file** | `playwright.config.ts` (testDir `e2e`, output `e2e/test-results`) |

Rules: e2e tests never call a real model (stub model, constitution III); the dashboard follows `docs/BRAND.md`.

### Environment Variables

```
E2E_PAUSE                    — Set to "1" for page.pause() in tests
```

## DOM Patterns

Document selectors for common UI elements in your app:

### Framework-Specific Selectors
<!-- Example for MUI:
- **Autocomplete root:** `.MuiAutocomplete-root:has-text("Label") input`
- **Popover menus:** `.MuiPopover-paper`
- **Backdrop (loading):** `.MuiBackdrop-root`
-->

### App-Specific Selectors
<!-- Document custom component selectors here -->

## Highlight / Focus CSS Values

Document any CSS values used for focus/highlight states:

<!-- Example:
### Active Item (blue theme)
- `backgroundColor`: `rgb(227, 242, 253)` (`#e3f2fd`)
- `boxShadow`: contains `25, 118, 210`
-->

## Page Object Inventory

List all page objects with their methods:

<!-- Example:
### LoginPage (`login.page.js`)
| Method | Description |
|--------|-------------|
| `login(user, pass)` | Fill credentials and submit |
| `expectLoggedIn()` | Assert redirect to dashboard |
-->

## Assertion Helpers

List custom assertion functions:

<!-- Example:
| Function | Checks |
|----------|--------|
| `assertHighlighted(locator)` | backgroundColor + boxShadow |
-->

## Pitfalls & Lessons Learned

Document timing issues, flaky patterns, and workarounds:

### Timing
<!-- Example:
- Always add `waitForTimeout(300)` after dropdown interactions
- Wait for loading spinners to disappear before assertions
-->

### Known Issues
<!-- Example:
- Save button triggers backend call that may timeout without backend running
- Auth state expires after 30 minutes — re-run auth setup if tests fail with 401
-->

### Test Conventions
<!-- Example:
- Test files: `client/e2e/tests/{feature}.spec.js`
- Grouping: `test.describe('TICKET-ID: Feature Name', () => { ... })`
- Naming: `test('US1-AC1: description', ...)`
- Skip: `test.skip(condition, 'reason')` for unmet preconditions
- Debug: `if (process.env.E2E_PAUSE) await page.pause();`
-->
