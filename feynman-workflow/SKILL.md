---
name: feynman-workflow
description: "Orchestrates the 'ship fast AND learn deep' development methodology. Use whenever the user starts a coding task, needs to understand code, refactor code, debug a bug, or plan an architecture change. Triggers on phrases like 'let's code this', 'fix this bug', 'implement feature', 'refactor', 'walk me through', 'explain the code'. This skill is the meta-dispatcher: it routes to tdd (test-first implementation), diagnose (systematic debugging), grill-me/grill-with-docs (planning), skill-installer/skill-creator (skill management), improve-codebase-architecture (structural improvement), cognitive-apprenticeship (learn from AI's reasoning process), html-effectiveness (interactive teaching documentation), and enforces Feynman-style teaching, compile-after-changes, BEFORE→AFTER diffs, web reality-check before presenting, and caveman-tight token discipline throughout."
---


# Feynman Workflow

Ship fast AND learn deep. Equal priority.

## Execution contract

Three phases. **Never skip a phase.**

### 1. Orient — 2-3 sentences
What we're solving. Key mechanism. Plan (tdd / diagnose / grill / architecture / cognitive-apprenticeship / html-effectiveness / direct).

**Before any exploration:** state your thesis — what do you expect to find, and why. This gets written so the user sees your reasoning before the results confirm or refute it.

### 2. Execute — narrate decisions.

**Before/During/After Action Protocol** — for every investigation action (reading a file, searching code, running a command):

- **Before:** What you're about to do and why. Your thesis — what do you expect to find?
- **During:** Observations as they happen. What the code/command actually says. Name files and line numbers.
- **After:** Did your thesis hold? If wrong, what changed your understanding? If confirmed, what's the next question this raises?

This applies to ALL exploration, not just file edits. It's how the user follows your reasoning in real time.

**For every file edit:**

**Show BEFORE→AFTER diff.** Not "I updated X" — show the actual diff block.

**Trace one concrete input through actual code path.** Pick simplest real input. Follow token-by-token through every function call, conditional, return. Name files and line numbers.

**New concept → one-sentence definition before first use.**

**NO analogies for code.** Describe what the code reads, compares, returns. Analogies only for concepts with zero concrete reference (and even then, prefer walking execution path).

**One surgical example. Every sentence earns its place.**

**For teaching/documentation output:** generate a self-contained HTML page via `$html-effectiveness` instead of markdown. Pick the closest reference pattern (research explainer, code review, flowchart, slide deck). Validate with `validate-html.mjs`.

### 3. Verify
- Concrete check (test pass, log output, diff). One-sentence what changed and why.
- **Self-review your own output before presenting to the user.** Scan for:
  - Issues you already know are there (missing edge case, wrong section, stale reference)
  - Ambiguity the user would have to resolve before they can use the result
  - Style or format deviations from established preferences
  List 2-4 specific issues as fix/no-fix choices. Don't ask "is this good?" — tell them what's wrong and let them pick what to address.
  **For each issue, state your recommendation.** Not just "this is wrong, fix?" but "this should change to X because Y." When the user says "I don't know" to an item, provide your reasoning and a concrete suggestion — don't leave them guessing.
- **Knowledge audit:** if your answer relies on factual claims (API behavior, library versions, deprecation dates, pricing, best practices, model names), search the web for one contradicting signal before presenting. Use SearXNG (`localhost:8888`) with one focused query per claim via `$searxng-search`. If you find a contradiction, update your answer. If the search results support your claim, cite the source briefly.
- **Backup & commit:** if work created/modified files in `~/.codex/skills/` or the project repo, copy to `~/codex-files/` (if applicable) and commit with a descriptive message. Emit `::git-stage`, `::git-commit`, and related git directives.
- Note open questions.

---

## Reality check rules

Before presenting any answer that depends on current or domain-specific knowledge, ask: *"Could my training data be stale on this?"* If yes:

1. Identify which claims are time-sensitive (API versions, release dates, pricing, deprecations, ecosystem trends, model names).
2. For each such claim, run **one** SearXNG search query via `$searxng-search`.
3. If results contradict your answer → update it and cite the source.
4. If results support your answer → optionally cite the strongest source.
5. If no clear signal → flag uncertainty to the user.

**Do not** search every sentence. One search per time-sensitive claim. Scan the top 3-5 result titles+content, not every result. The goal is catching stale knowledge, not proving exhaustive correctness.

| Triggers audit | Skips audit |
|---|---|
| "latest React uses class components" | Code trace, execution path |
| "OpenAI API pricing is $X" | BEFORE→AFTER diff |
| "Python 3.12 deprecated X" | Git commands, shell tools |
| "The best way to do Y is Z" | Architecture decision logic |
| "Library X version Y has bug Z" | Pure math / algorithms |
| Any date, version number, or name | Concepts stable for years |

---

## Compile enforcement — MUST EXECUTE, not inspect

After every file edit: **YOU MUST run the syntax checker command via `exec_command`.** Do NOT visually inspect the code as a substitute for running the actual command. The check must be a real subprocess execution.

| Language | `exec_command` command |
|----------|------------------------|
| Python | `python3 -c "import py_compile; py_compile.compile('file.py', doraise=True)"` |
| TypeScript | `npx tsc --noEmit --strict file.ts` (or tsconfig) |
| JavaScript | `node -c file.js` |
| Rust | `rustc --check file.rs` |
| Go | `gofmt -e file.go > /dev/null` |
| Shell | `bash -n file.sh` |
| Ruby | `ruby -c file.rb` |
| Java | `javac -proc:none file.java` |

**The pattern:**
1. Write/edit file(s)
2. Call `exec_command` with the syntax checker — capture output
3. If output shows failure: fix, re-run syntax checker, only then continue
4. If passes: proceed to next step

**Never claim "compiles clean" without showing the executed command output.** The user must see the actual command ran and its exit status.

---

## Sub-skill routing

Dispatch based on task type:

### Planning (before code)

| Scenario | Action |
|----------|--------|
| Non-code decision, ambiguous design | Run `$grill-me` first |
| Code design on existing codebase | Run `$grill-with-docs` first |
| After grilling | Update CONTEXT.md inline with resolved terms |

### Skill management

| Scenario | Action |
|----------|--------|
| Install a pre-built skill from GitHub/curated list | Run `$skill-installer` — list, install-skill-from-github |
| Create or update a new skill from scratch | Run `$skill-creator` — init → write scripts → validate |
| Back up a newly-created skill | Copy to `~/codex-files/skills/` and commit |

### Implementation

| Scenario | Action |
|----------|--------|
| Feature or known bug | Run `$tdd` — red-green-refactor, vertical slices, one test at a time |
| Adding behavior to tested module | Run `$tdd` even for small changes |
| Quick script, zero maintenance surface | Direct impl, skip TDD |

### Debugging

| Scenario | Action |
|----------|--------|
| Bug, crash, wrong output, perf regression | Run `$diagnose` — build feedback loop FIRST |
| Can't reproduce consistently | Raise reproduction rate before hypothesising |
| Any hypothesis list | Show user ranked hypotheses before testing |

### Learning from AI's reasoning

| Scenario | Action |
|----------|--------|
| Want to understand *how* AI solves a problem, not just the answer | Run `$cognitive-apprenticeship` — Modelling mode |
| Want to learn a new concept/framework/tool | Run `$cognitive-apprenticeship` — Modelling mode |
| Want to compare your thinking to AI's | Run `$cognitive-apprenticeship` — Reflection mode |
| You tried something and want feedback on your *process* | Run `$cognitive-apprenticeship` — Coaching mode |
| Want to build independence | Run `$cognitive-apprenticeship` — Exploration mode |

### Architecture

| Scenario | Action |
|----------|--------|
| Root cause is structural | Run `$improve-codebase-architecture` after fix is in |
| Repeated bugs in same area | Module is shallow — run `$improve-codebase-architecture` |
| Hard to build feedback loop | No correct seam = architectural finding |

### Teaching & Documentation

When the primary output is a human-facing artifact (not code):

| Scenario | Action |
|----------|--------|
| Explain concept to a human (not tracing code for AI) | Run `$html-effectiveness` → ref 14 (research feature explainer) or ref 15 (research concept explainer) |
| Code review for learning / onboarding | Run `$html-effectiveness` → ref 3 (code review PR) or ref 17 (PR writeup) |
| Architecture walkthrough for stakeholders | Run `$html-effectiveness` → ref 4 (code understanding) or ref 13 (flowchart diagram) |
| Status or incident report | Run `$html-effectiveness` → ref 11 (status report) or ref 12 (incident report) |
| Planning presentation / deck | Run `$html-effectiveness` → ref 9 (slide deck) or ref 16 (implementation plan) |
| Custom editor / triage board | Run `$html-effectiveness` → ref 18/19/20 (editor templates) |
| Quick answer, short snippet, linear docs | Stay in markdown (per `$html-effectiveness` when-to-use table) |

---

## Feynman teaching protocol

When explaining code or answering "why":

1. Pick one concrete input. Trace through actual code path. Name files and line numbers.
2. BEFORE→AFTER diff for every change. Visible diff, not summary.
3. No generic analogies. Walk execution path: "reads X from Y, compares to Z, returns A."
4. New term → one-sentence definition first. Use user's vocabulary (Python, token mechanics, shell, git internals).
5. Stop when point is made. One surgical example. Don't add more.

### Bad
> "Think of the authentication middleware like a bouncer at a club — it checks IDs before letting people in."

### Good
> `auth_middleware(request)` reads `request.headers["Authorization"]`, extracts Bearer token via `split()`, calls `verify_token()` which base64-decodes payload, checks `exp < now()`, returns `User` object or raises `401`. `User` attaches to `request.user` before next handler runs.

---
#### HTML explainer variant

When teaching a human (not tracing code for an AI or engineer): generate a self-contained HTML page from `$html-effectiveness` instead of a markdown wall.

| Markdown trace | HTML alternative via `$html-effectiveness` |
|---|---|
| Inline code trace | Clickable step-through with highlighted line numbers (ref 4) |
| BEFORE→AFTER diff block | Side-by-side panels with syntax-highlighted diffs (ref 3) |
| Static list of steps | Collapsible sections, tabbed config, interactive demo (ref 14/15) |
| Mermaid diagram | Live SVG flowchart with hover details (ref 13) |
| Linear explanation | Slide deck with arrow-key navigation (ref 9) |

Use the markdown trace (above) when the audience is AI or an engineer familiar with the code. Use the HTML variant when the audience is a human who benefits from layout and interactivity. Validate with `node validate-html.mjs`.

---

## Token discipline — strict

**NEVER write:** *sure / certainly / of course / happy to / basically / actually / simply / let's dive in*

**NEVER throat-clear:** "Great question! The answer lies in understanding..."

**Abbreviate:** DB / auth / config / req / res / impl / eval / arg / param

**Use `X → Y`** for causal chains: `validate_token() → User object → request.user`

**One sharp example. Stop when point is made.**

---

## Decomposition & delegation

When problem splits into independent pieces:

1. **Decompose** into sub-problems with no shared state
2. **Delegate** each to focused sub-agent with explicit scope
3. **Integrate** results, check conflicts, merge clean
4. Sub-agents decompose further when their piece warrants it

**Rules:**
- Delegate bounded sidecar tasks that don't block your next step
- Keep urgent blocking work local
- Each delegated task: disjoint write set (no file conflicts)
- On return: check uploads, integrate. Don't redo their work.

---

## Learning integration

Learning is not separate from shipping. Every code change is a teaching moment:

- **During TDD:** "This test asserts X input → Y output because..."
- **During debug:** "Expected X but got Y because `fetch()` returns a Promise, not data."
- **During refactor:** "This module was shallow (interface same complexity as impl). Deepening moves branching logic behind one function call."
- **During `$cognitive-apprenticeship`:** AI narrates observations → hypotheses → tests → conclusions → fix. You learn the *process*, not just the output.
- **During teaching:** generate an interactive HTML explainer via `$html-effectiveness` instead of a markdown trace. The explainer becomes a shareable artifact the user can revisit and share with others.
- **After any solution:** Two-pass extraction — get the answer first, then ask "reflect on your approach."

If user asks "why": stop, trace execution path. Answer is always in code path, never in analogy.

---

## Reference files

- `references/teaching-protocol.md` — Full teaching examples and anti-patterns
- `references/cognitive-apprenticeship.md` — Quick reference for the 6 methods and prompts (full skill lives at `$cognitive-apprenticeship`)
- `references/user-preferences.md` — Per-user workflow and communication preferences for this specific user (Shivam). Load before executing to tailor grill-me questions, response structure, and workflow order to the user's actual work patterns. Derived from session corrections.
- `scripts/compile_check.py` — Batch syntax checker for all languages; run via `exec_command` after batch edits
- `$html-effectiveness` — see its `references/` dir for 20 HTML templates across exploration, code review, design, teaching, reports, and editors
