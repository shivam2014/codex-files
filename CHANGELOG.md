# Changelog

All notable changes to the codex-files skill library are tracked here.

## [2026-05-09] — Dark mode toggle + validation

### Added
- **Dark mode toggle**: 3-state `data-dm` attribute system added to SKILL.md
  - System preference → force dark → force light → system preference
  - `html[data-dm="dark"]` selector with higher specificity than `:root` to win over media queries
  - Fixed bottom-right toggle button with local-storage persistence
- **Validation section**: Automated `validate-html.mjs` script that catches:
  - HTML tags inside SVG `<text>` elements
  - Annotation labels overlapping arrows
  - Dark mode class specificity issues
  - Mismatched open/close tags for `<svg>` and `<details>`
  - `onclick` functions without definitions
  - Content overflowing SVG `viewBox`
- **Principles** now mention dark mode toggle as a default feature

### Fixed
- SVG `<text>` elements should not contain HTML markup — SVG doesn't render it
- Annotation labels must be offset from arrow lines (at least 6px)

## [2026-05-03] — Initial skill scaffold

### Added
- 20 reference HTML templates across 9 categories
- Default styling palette with CSS custom properties
- Guidelines for writing good HTML pages
