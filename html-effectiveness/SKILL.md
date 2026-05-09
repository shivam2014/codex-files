---
name: html-effectiveness
description: |
  Create single-file HTML pages for any purpose — exploration, planning, code review, design,
  prototyping, diagrams, slide decks, research explainers, reports, and custom editors.
  Use when the user asks for an HTML page, interactive document, visual comparison, slide deck,
  design system preview, animated prototype, flowchart, explainer, status/incident report,
  triage board, or any self-contained web UI. Best for pages that benefit from layout,
  interactivity, or spatial organization that plain markdown cannot deliver.
---

# HTML Effectiveness Skill

Produce single-file `.html` pages instead of markdown walls when the content benefits from
layout, interactivity, color, or spatial arrangement. Every page is self-contained — no build
step, no external dependencies.

## Principles

- One self-contained `.html` file — inline CSS and JS only
- Minimal, readable HTML structure; no framework or build step
- Dark/light friendly palette via CSS custom properties
- [Dark mode toggle](#dark-mode-toggle) with 3-state cycling (system → dark → light) included by default on every page
- Content-first: use layout to clarify, not decorate
- Prefer serif headings + sans body for long-form reading
- Include small interactive flourishes (hover states, live preview, sliders) when they aid understanding

## When to use HTML instead of markdown

| Use markdown for… | Use HTML for… |
|---|---|
| Short answers, code snippets, quick lists | Side-by-side comparisons, tabbed content |
| Linear docs, READMEs | Interactive explainers, clickable prototypes |
| Simple status updates | Animated timelines, visual charts |
| Static diagrams (Mermaid) | Live SVG illustrations, interactive flowcharts |

## Categories & When to Use Each

### 01 — Exploration & Planning
When the user is unsure what they want and needs to compare options visually.

- [01-exploration-code-approaches](references/01-exploration-code-approaches.html): Side-by-side tradeoffs for multiple implementations
- [02-exploration-visual-designs](references/02-exploration-visual-designs.html): Live layout and palette options to react to
- [16-implementation-plan](references/16-implementation-plan.html): Milestone timeline, data-flow diagram, mockups, risk table

### 02 — Code Review & Understanding
When reviewing code or explaining architecture.

- [03-code-review-pr](references/03-code-review-pr.html): Annotated diff with margin notes, severity tags, jump links
- [17-pr-writeup](references/17-pr-writeup.html): PR description with motivation, before/after, file-by-file tour
- [04-code-understanding](references/04-code-understanding.html): Module map with boxes, arrows, hot path highlighted

### 03 — Design
When discussing visual design tokens or component states.

- [05-design-system](references/05-design-system.html): Color swatches, type scales, spacing tokens as live spec
- [06-component-variants](references/06-component-variants.html): Every size/state/intent of a component on one sheet

### 04 — Prototyping
When motion or interaction needs to be felt, not described.

- [07-prototype-animation](references/07-prototype-animation.html): Isolated transition with sliders for duration/easing
- [08-prototype-interaction](references/08-prototype-interaction.html): Clickable multi-screen flow

### 05 — Illustrations & Diagrams
When you need vector art or process flows.

- [10-svg-illustrations](references/10-svg-illustrations.html): Inline SVG figures for blog posts or docs
- [13-flowchart-diagram](references/13-flowchart-diagram.html): Annotated clickable flowchart with step details

### 06 — Decks
When you need an arrow-key-navigable presentation, no Keynote/PowerPoint.

- [09-slide-deck](references/09-slide-deck.html): Section-based slide deck with left/right navigation

### 07 — Research & Learning
When explaining a concept or feature with multiple dimensions.

- [14-research-feature-explainer](references/14-research-feature-explainer.html): TL;DR box, collapsible steps, tabbed config, FAQ
- [15-research-concept-explainer](references/15-research-concept-explainer.html): Live interactive demo, comparison table, glossary

### 08 — Reports
For recurring documents people actually need to read.

- [11-status-report](references/11-status-report.html): Weekly status with chart, shipped/slipped sections
- [12-incident-report](references/12-incident-report.html): Post-mortem with timeline, log excerpts, checklist

### 09 — Custom Editors
When the user needs to manipulate structured data through a GUI and export results.

- [18-editor-triage-board](references/18-editor-triage-board.html): Drag-and-drop ticket board with markdown export
- [19-editor-feature-flags](references/19-editor-feature-flags.html): Toggle groups with dependency warnings, copy-diff
- [20-editor-prompt-tuner](references/20-editor-prompt-tuner.html): Live template editor with variable slots and preview

## Dark mode toggle

Every HTML page should include a built-in dark mode toggle. Use the 3-state `data-dm` attribute approach to handle all scenarios:

| State | Behavior |
|---|---|
| No `data-dm` | Follows system preference (`prefers-color-scheme`) |
| `data-dm="dark"` | Forces dark mode (overrides system) |
| `data-dm="light"` | Forces light mode (overrides system) |

### Why `html[data-dm]` instead of a class

The `@media (prefers-color-scheme: dark)` media query uses `:root` (specificity 0,1,0). A plain `.dark-mode` class has the same specificity — when the system is in dark mode the media query's `:root` overrides the toggle, making it appear broken.

Using `html[data-dm="dark"]` (specificity **0,1,1**) always wins over `:root`. The media query uses `:root:not([data-dm])` so it yields when a manual override is active.

### Standard toggle button (bottom-right corner)

Add this HTML at the top of `<body>`:

```html
<button class="dm-toggle" id="dmToggle" onclick="toggleDarkMode()" title="Toggle dark/light mode"></button>
```

### CSS variables for dark/light modes

Extend the `:root` block with three variable sets:

```css
/* ── default (light) ──────────────────── */
:root {
  --ivory:    #FAF9F5;
  --paper:    #FFFFFF;
  --slate:    #141413;
  --clay:     #D97757;
  --clay-d:   #B85C3E;
  --oat:      #E3DACC;
  --olive:    #788C5D;
  --sky:      #6A8CAF;
  --g100:     #F0EEE6;
  --g200:     #E6E3DA;
  --g300:     #D1CFC5;
  --g500:     #87867F;
  --g700:     #3D3D3A;
  --rust:     #B04A3F;
  --green:    #5B8C5A;
  --amber:    #C9953C;
  --serif:    ui-serif, Georgia, "Times New Roman", Times, serif;
  --sans:     system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --mono:     ui-monospace, "SF Mono", Menlo, Monaco, Consolas, monospace;
}

/* ── system dark mode (no manual override) ─ */
@media (prefers-color-scheme: dark) {
  :root:not([data-dm]) {
    --ivory:   #1A1A1A;
    --paper:   #242424;
    --slate:   #E8E6DC;
    --clay:    #E8927A;
    --clay-d:  #F0A088;
    --oat:     #3D3D3A;
    --olive:   #8CA87A;
    --sky:     #8AAED0;
    --g100:    #2E2E2E;
    --g200:    #353535;
    --g300:    #454545;
    --g500:    #999999;
    --g700:    #D4D4D4;
    --rust:    #D97A6A;
    --green:   #7AB87A;
    --amber:   #D4A84E;
  }
}

/* ── manual dark override ─────────────── */
html[data-dm="dark"] {
  /* same values as the media query block above */
}

/* ── manual light override ────────────── */
html[data-dm="light"] {
  /* same values as the default :root block */
}
```

For elements that use hardcoded colors (SVG fills, badge backgrounds, etc.), add overrides:

```css
@media (prefers-color-scheme: dark) {
  :root:not([data-dm]) svg .box { fill: #2A2A2A; stroke: #454545; }
}
html[data-dm="dark"] svg .box { fill: #2A2A2A; stroke: #454545; }
html[data-dm="light"] svg .box { fill: #FFFFFF; stroke: #D1CFC5; }
```

### JS toggle (add before `</script>`)

```js
// ── dark mode toggle ──
function toggleDarkMode() {
  var html = document.documentElement;
  var current = html.getAttribute('data-dm');
  if (current === 'dark') {
    html.setAttribute('data-dm', 'light');     // dark → light
  } else if (current === 'light') {
    html.removeAttribute('data-dm');            // light → system pref
  } else {
    html.setAttribute('data-dm', 'dark');       // system → dark
  }
  updateToggleIcon();
  try { localStorage.setItem('dm-pref', html.getAttribute('data-dm') || ''); } catch(e) {}
}

function updateToggleIcon() {
  var dm = document.documentElement.getAttribute('data-dm');
  var btn = document.getElementById('dmToggle');
  if (dm === 'dark') btn.textContent = '☀️';
  else if (dm === 'light') btn.textContent = '🌙';
  else {
    btn.textContent = window.matchMedia('(prefers-color-scheme: dark)').matches ? '☀️' : '🌙';
  }
}

// Restore preference
(function() {
  try {
    var pref = localStorage.getItem('dm-pref');
    if (pref === 'dark') document.documentElement.setAttribute('data-dm', 'dark');
    else if (pref === 'light') document.documentElement.setAttribute('data-dm', 'light');
    updateToggleIcon();
  } catch(e) {}
})();
```

### Toggle button CSS

```css
.dm-toggle {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 42px; height: 42px;
  border-radius: 50%;
  border: 1.5px solid var(--g300);
  background: var(--paper);
  color: var(--slate);
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  transition: background 0.2s, transform 0.15s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.dm-toggle:hover { transform: scale(1.08); }
```

### Code blocks: keep background dark in all modes

Code blocks should **not** use `var(--slate)` for their background — in dark mode `--slate` flips to a light color, making text invisible. Use a hardcoded dark background instead:

```css
.code-block {
  background: #1A1A1A;          /* hardcoded dark — never changes */
  color: #E8E6DC;               /* light text on dark background */
  font-family: var(--mono);
  font-size: 12px;
  line-height: 1.7;
  border-radius: 8px;
  padding: 12px 14px;
  overflow-x: auto;
}
.code-block .dim { color: #8A8A8A; }   /* hardcoded gray */
.code-block .err { color: #E8837C; }   /* red for errors/deletions */
.code-block .fix { color: #7EC87E; }   /* green for additions/fixes */
.code-block .del { color: #E8837C; }   /* red for deletions */
```

Also add overrides for inline `<code>` in paragraphs/lists so they stay readable in dark mode:

```css
@media (prefers-color-scheme: dark) {
  :root:not([data-dm]) p code,
  :root:not([data-dm]) li code {
    background: #2A2A2A;
    color: #E8E6DC;
  }
}
html[data-dm="dark"] p code,
html[data-dm="dark"] li code {
  background: #2A2A2A;
  color: #E8E6DC;
}
html[data-dm="light"] p code,
html[data-dm="light"] li code {
  background: #F0EEE6;
  color: #3D3D3A;
}
```

This applies to the validation script's checks: rendered-but-unreadable code blocks in dark mode are a user-facing bug.

---

### Add `transition` to body for smooth switching

```css
body { transition: background 0.2s, color 0.2s; }
```

---

## How to use the references

Each reference is a complete, working `.html` file. Open it in a browser to see the pattern,
or read the source to understand the structure. When a user request maps to one of the
categories above:

1. Pick the closest reference example
2. Load it as a starting pattern (open the file and read its source)
3. Adapt the structure, styling, and interactivity to the specific task
4. Keep it single-file, self-contained, and dependency-free

## Default styling palette

Use these CSS custom properties for consistent look:

```css
:root {
  --ivory:    #FAF9F5;
  --paper:    #FFFFFF;
  --slate:    #141413;
  --clay:     #D97757;
  --clay-d:   #B85C3E;
  --oat:      #E3DACC;
  --olive:    #788C5D;
  --g100:     #F0EEE6;
  --g200:     #E6E3DA;
  --g300:     #D1CFC5;
  --g500:     #87867F;
  --g700:     #3D3D3A;
  --serif:    ui-serif, Georgia, "Times New Roman", Times, serif;
  --sans:     system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --mono:     ui-monospace, "SF Mono", Menlo, Monaco, Consolas, monospace;
}
```

## Guidelines for writing good HTML pages

- **Structure**: `<header>`, `<section>`, `<footer>` semantic elements
- **Typography**: serif for headings, sans for body, mono for code
- **Responsive**: `clamp()` for font sizes, `auto-fill`/`auto-fit` for grids
- **Interactivity**: Keep JS under 50 lines; use `click`, `input`, `drag` events
- **Export**: For editors, always include a copy/export button that serializes state
- **Universal reset gotcha**: `* { margin: 0; padding: 0; }` strips default list indentation. Always add `ul { padding-left: 20px; }` when using bullet points.
- **SVG**: Inline SVG for diagrams — color with currentColor or CSS variables
- **No frameworks**: No React, no libraries, no CDN scripts — vanilla HTML/CSS/JS
- **File size**: Target under 30 KB; if it's bigger, inline only what's needed

## Validation

Always validate generated HTML before presenting it. Run these checks — manually or via the provided script.

### Checklist of common rendering bugs

| # | Check | Catches |
|---|---|---|
| 1 | SVG `<text>` elements contain **no HTML tags** (`<code>`, `<strong>`, `<br>`) | Raw angle brackets showing in diagram labels |
| 2 | Annotation text is **offset from arrows** (not on same y coord) | Labels sitting on top of connector lines |
| 3 | Dark mode toggle **actually switches colors** (test in both system modes) | `@media` query overriding manual class due to specificity |
| 4 | All `</svg>` and `</details>` have matching open tags | Broken layout when a section doesn't render |
| 5 | Hover/click interactions work without console errors | `onclick`, `addEventListener`, `getElementById` typos |
| 6 | SVG text overflows viewBox or container rect | Text clipped or overflowing decorative boxes |
| 7 | Universal reset `padding:0` with `<ol>` but no restore rule | Numbered lists without visible indentation |

### Automated validation script

Run this Node.js script against any generated HTML file to catch the most common issues automatically:

```bash
node /path/to/validate-html.mjs page.html
```

Save this as `validate-html.mjs` alongside your HTML files:

```js
#!/usr/bin/env node
import { readFileSync } from 'node:fs';

const path = process.argv[2];
if (!path) { console.error('Usage: node validate-html.mjs <file.html>'); process.exit(1); }

const html = readFileSync(path, 'utf-8');
let errors = 0;
let warnings = 0;

function fail(type, msg) {
  console.log(`  ${type === 'ERR' ? '✖' : '⚠'}  [${type}] ${msg}`);
  type === 'ERR' ? errors++ : warnings++;
}

function parseNum(s) { const v = parseFloat(s); return isNaN(v) ? null : v; }

function textWidth(text, fontSize, fontFamily) {
  const CW = { mono: 0.62, sans: 0.55, serif: 0.52, def: 0.55 };
  let cw = CW.def;
  if (/mono/i.test(fontFamily)) cw = CW.mono;
  else if (/serif/i.test(fontFamily)) cw = CW.serif;
  else if (/sans|system-ui/i.test(fontFamily)) cw = CW.sans;
  return text.length * cw * fontSize;
}

// ── 1. SVG text with HTML tags ──
for (const t of html.match(/<text[^>]*>.*?<\/text>/gs) || []) {
  const raw = t.match(/<text[^>]*>([\s\S]*?)<\/text>/)[1];
  if (/<[a-z]+[ >]/.test(raw) && !/<tspan/.test(raw))
    fail('ERR', `SVG <text> contains HTML tag: "${raw.slice(0, 60)}..."`);
  const inside = t.replace(/<[^>]+>/g, '').trim();
  if (!inside) fail('WARN', 'SVG <text> appears empty');
}

// ── 2. Annotation overlapping arrows ──
const labelY = [...html.matchAll(/class="sub"[^>]*y="(\d+)"/g)].map(m => +m[1]);
const arrowY = [...html.matchAll(/class="arrow"[^>]*y1="(\d+)"/g)].map(m => +m[1]);
for (const ly of labelY) for (const ay of arrowY)
  if (Math.abs(ly - ay) < 6)
    fail('WARN', `Annotation at y=${ly} overlaps arrow at y=${ay}`);

// ── 3. Dark mode specificity ──
if (html.includes('prefers-color-scheme: dark') &&
    html.includes('class="dark-mode"') &&
    !html.includes('html[data-dm=') && !html.includes('html.dark-mode'))
  fail('WARN', 'Uses .dark-mode class without html[data-dm] — may be overridden by @media');

// ── 4. Matching SVG/Details tags ──
const svgO = (html.match(/<svg[\s>]/g) || []).length;
const svgC = (html.match(/<\/svg>/g) || []).length;
if (svgO !== svgC) fail('ERR', `SVG: ${svgO} opens, ${svgC} closes`);

const detO = (html.match(/<details[\s>]/g) || []).length;
const detC = (html.match(/<\/details>/g) || []).length;
if (detO !== detC) fail('ERR', `<details>: ${detO} opens, ${detC} closes`);

// ── 5. JS onclick references exist ──
const onClickFns = [...new Set([...html.matchAll(/onclick="(\w+)\(/g)].map(m => m[1]))];
for (const fn of onClickFns)
  if (!html.includes(`function ${fn}(`))
    fail('ERR', `onclick="${fn}()" but no function ${fn} defined`);

// ── 6. SVG text overflow ──
// Uses nearest-rect matching: for each text, find the rect with the MOST
// horizontal overlap (the visual container), then check overflow against only that rect.
for (const [fullSvg, vbStr, content] of html.matchAll(/<svg[^>]*viewBox="([^"]*)"[^>]*>([\s\S]*?)<\/svg>/g)) {
  const vbParts = vbStr.trim().split(/\s+/);
  if (vbParts.length < 4) continue;
  const vbW = parseInt(vbParts[2], 10);
  const vbH = parseInt(vbParts[3], 10);
  if (!vbW || !vbH) continue;

  // Collect rects
  const rects = [];
  for (const rm of content.matchAll(/<rect[^>]*>/g)) {
    const r = { x: 0, y: 0, w: 0, h: 0 };
    const rx = rm[0].match(/x="([^"]*)"/);  if (rx) r.x = parseNum(rx[1]) || 0;
    const ry = rm[0].match(/y="([^"]*)"/);  if (ry) r.y = parseNum(ry[1]) || 0;
    const rw = rm[0].match(/width="([^"]*)"/); if (rw) r.w = parseNum(rw[1]) || 0;
    const rh = rm[0].match(/height="([^"]*)"/); if (rh) r.h = parseNum(rh[1]) || 0;
    if (r.w > 0 && r.h > 0) rects.push(r);
  }

  // Process text blocks
  for (const tb of content.matchAll(/<text[^>]*>[\s\S]*?<\/text>/g)) {
    const h = tb[0];
    const xa = h.match(/x="([^"]*)"/); if (!xa) continue;
    const xVal = parseNum(xa[1]); if (xVal === null) continue;
    const ya = h.match(/y="([^"]*)"/);
    const yVal = ya ? parseNum(ya[1]) || 0 : 0;
    const anchor = (h.match(/text-anchor="([^"]*)"/) || [, 'start'])[1];
    const fs = parseInt((h.match(/font-size="(\d+)"/) || [, '12'])[1], 10) || 12;
    const ff = (h.match(/font-family="([^"]*)"/) || [, 'sans'])[1];

    // Extract lines (handle tspans)
    const lines = [];
    const tspans = [...h.matchAll(/<tspan[^>]*>([\s\S]*?)<\/tspan>/g)];
    if (tspans.length) {
      for (const ts of tspans) {
        const t = ts[1].replace(/<[^>]+>/g, '').trim();
        if (t) lines.push(t);
      }
    } else {
      const d = h.replace(/<[^>]+>/g, '').trim();
      if (d) lines.push(d);
    }

    for (const line of lines) {
      const tw = textWidth(line, fs, ff);
      let left, right;
      if (anchor === 'middle') { left = xVal - tw/2; right = xVal + tw/2; }
      else if (anchor === 'end') { left = xVal - tw; right = xVal; }
      else { left = xVal; right = xVal + tw; }

      // ── Check viewBox clipping ──
      const vL = Math.max(0, Math.round(-left));
      const vR = Math.max(0, Math.round(right - vbW));
      if (vL > 2 || vR > 2) {
        const s = [];
        if (vL > 2) s.push(`left ${vL}px`);
        if (vR > 2) s.push(`right ${vR}px`);
        fail('ERR', `SVG text clipped by viewBox (${s.join(', ')}): "${line.slice(0, 50)}..."`);
      }

      // ── Check rect overflow (nearest-rect matching) ──
      // Find the rect with the most horizontal overlap
      let bestOverlap = 0;
      let bestRect = null;
      for (const r of rects) {
        if (yVal < r.y - 10 || yVal > r.y + r.h + 10) continue;
        const overlap = Math.min(right, r.x + r.w) - Math.max(left, r.x);
        if (overlap > bestOverlap) {
          bestOverlap = overlap;
          bestRect = r;
        }
      }

      if (bestRect) {
        const rL = bestRect.x;
        const rR = bestRect.x + bestRect.w;
        const oL = Math.max(0, Math.round(rL - left));
        const oR = Math.max(0, Math.round(right - rR));

        if (oL > 2 || oR > 2) {
          const s = [];
          if (oL > 2) s.push(`left ${oL}px`);
          if (oR > 2) s.push(`right ${oR}px`);
          // Only flag if text primarily belongs to this rect (>50% overlap)
          const textArea = right - left;
          const overlapRatio = bestOverlap / textArea;
          if (overlapRatio > 0.3) {
            fail('WARN', `SVG text overflows container rect (${s.join(', ')}): "${line.slice(0, 50)}..."`);
          }
        }
      }
    }
  }
}

// ── 7. Universal reset list gotcha ──
if (/\*\{[^}]*padding:\s*0/.test(html)) {
  if (/<ol[\s>]/.test(html) && !/ol\s*\{[^}]*padding-left/.test(html))
    fail('WARN', 'Universal reset `padding:0` but <ol> used without `ol { padding-left: ... }`');
}

console.log(`\n${errors + warnings} issues found (${errors} errors, ${warnings} warnings).`);
process.exit(errors > 0 ? 1 : 0);

```

### Using the script

```bash
# Validate the debugging chronicle (catches SVG <code> tags, arrow overlaps, etc.)
node validate-html.mjs debugging-chronicle.html
```

The script checks for:
- HTML tags inside SVG `<text>` elements
- Annotation labels overlapping arrows (within 6px)
- Dark mode class specificity issues
- Mismatched `<svg>`/`<details>` open/close tags
- `onclick` functions that are never defined (caught before runtime)
- SVG text overflow beyond viewBox bounds (error) or container rect bounds (warning)
- Universal reset `padding:0` with `<ol>` and no restore rule

The SVG overflow check uses **nearest-rect matching**: for each `<text>`, it finds the `<rect>` with the most horizontal overlap that vertically contains the text's y-position, then checks if the text's estimated pixel width extends beyond that rect. It handles `<tspan>` multi-line text, different font families (mono 0.62×, sans 0.55×, serif 0.52×), and text anchors (start/middle/end). Known limitations: column-header text not inside rects, and text inside SVG `<path>` shapes, may produce false-positive warnings.
