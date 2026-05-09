---
name: feynman-workflow
description: "Orchestrates the 'ship fast AND learn deep' development methodology. Use whenever the user starts a coding task, needs to understand code, refactor code, debug a bug, or plan an architecture change. Triggers on phrases like 'let's code this', 'fix this bug', 'implement feature', 'refactor', 'walk me through', 'explain the code'. This skill is the meta-dispatcher: it routes to tdd (test-first implementation), diagnose (systematic debugging), grill-me/grill-with-docs (planning), improve-codebase-architecture (structural improvement), cognitive-apprenticeship (learn from AI's reasoning process), and enforces Feynman-style teaching, compile-after-changes, BEFORE→AFTER diffs, and caveman-tight token discipline throughout."
---


# Feynman Workflow

Ship fast AND learn deep. Equal priority.

## Execution contract

Three phases. **Never skip a phase.**

### 1. Orient — 2-3 sentences
What we're solving. Key mechanism. Plan (tdd / diagnose / grill / architecture / cognitive-apprenticeship / direct).

### 2. Execute — narrate decisions. For every file edit:

**Show BEFORE→AFTER diff.** Not "I updated X" — show the actual diff block.

**Trace one concrete input through actual code path.** Pick simplest real input. Follow token-by-token through every function call, conditional, return. Name files and line numbers.

**New concept → one-sentence definition before first use.**

**NO analogies for code.** Describe what the code reads, compares, returns. Analogies only for concepts with zero concrete reference (and even then, prefer walking execution path).

**One surgical example. Every sentence earns its place.**

### 3. Verify
Concrete check (test pass, log output, diff). One-sentence what changed and why. Note open questions.

---

## Compile enforcement — MUST EXECUTE, not inspect

After every file edit: **YOU MUST run the syntax checker command via `exec_command`.** Do NOT visually inspect the code as a substitute for running the actual command. The check must be a real subprocess execution.

| Language | `exec_command` with this command |
|----------|----------------------------------|
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
- **After any solution:** Two-pass extraction — get the answer first, then ask "reflect on your approach."

If user asks "why": stop, trace execution path. Answer is always in code path, never in analogy.

---

## Reference files

- `references/teaching-protocol.md` — Full teaching examples and anti-patterns
- `references/cognitive-apprenticeship.md` — Quick reference for the 6 methods and prompts (full skill lives at `$cognitive-apprenticeship`)
- `scripts/compile_check.py` — Batch syntax checker for all languages; run via `exec_command` after batch edits
