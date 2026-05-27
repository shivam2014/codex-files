---
name: filetree
description: >
  Use when the user asks to initialize, update, or lint a FILETREE.md manifest
  — a machine-readable project map with one-line summaries and content hashes per
  file. Also use when the user wants to auto-generate a project overview, track
  file changes across a repo, or maintain a living index that helps agents orient
  in large codebases. Covers /filetree:init, /filetree:update, and /filetree:lint.
license: MIT
---

# Filetree Skill

Maintains `FILETREE.md`: a machine-readable manifest that lists every indexable
file in a git repo with a one-line summary and a content hash. Designed to help
Codex orient quickly in unfamiliar codebases without scanning the full tree.

---

## Commands

### `init` — create FILETREE.md from scratch

1. Run `filetree.py todo` (no existing manifest, so every file is `added`).
2. For each file, write a summary ≤ 25 words describing its **purpose** (not
   implementation). Use the repo's canonical language (see "Summary language"
   below).
3. Collect results into a JSON payload:
   ```json
   {"updates": [{"path": "src/foo.py", "summary": "..."}]}
   ```
4. Pipe into the apply step:
   ```bash
   echo '<json>' | python <scripts/filetree.py> apply
   ```

### `update` — sync after code changes

1. Run `filetree.py todo --split` to diff manifest vs repo state and get batches.
2. Process each batch file: read it, decide each item (new summary or
   `UNCHANGED` — see rules below), write a `part_NN.json`.
3. Apply all parts:
   ```bash
   python <scripts/filetree.py> apply <split_dir>/part_*.json
   ```
4. Run the coverage gate on `apply`'s return — see "Coverage gate" below.

### `lint` — CI-friendly drift check

```bash
python <scripts/filetree.py> lint
```

Exits 1 if any file is added, changed, removed, or renamed relative to the
manifest. No LLM work — pure hash comparison.

---

## Wiring into AGENTS.md

After creating or updating `FILETREE.md`, wire a reference into the project's
agent contract so future Codex sessions discover it automatically.

```bash
python <scripts/filetree.py> wire-target
```

The output lists each candidate file (`AGENTS.md`, `CLAUDE.md`), whether it
exists, whether it is a symlink, and any lines that already mention FILETREE.md.

Pick the first file that exists (prefer `AGENTS.md`). Edit the **real path**
shown in `real_path` (not the symlink name). Add a line like:

```
@FILETREE.md
```

or

```
- FILETREE.md — project file map; read this to orient in the codebase
```

Skip files where `matches` already contains a backticked `FILETREE.md` reference.

---

## Shared rules

### Summary style

One line, max 25 words, describes what the file is **for** (its role/purpose).
Not what it implements internally.

- Good: "JWT auth middleware; parses token from request header and injects user_id"
- Bad: "Defines AuthMiddleware class with `__init__` and `__call__` methods"
- Bad: "Handles auth" (too vague)

Present tense. No marketing words.

### Summary language

One run, ONE language. Every summary uses the same language as determined by:

1. The dominant natural language of `AGENTS.md` / `CLAUDE.md` (the agent contract).
2. Else `README` (any localized variant).
3. Else (update only) the dominant language of existing FILETREE.md entries.
4. Else English.

Resolve the language ONCE, up front. Every sub-agent prompt must state it
explicitly ("Write all summaries in <language>"). Sub-agents never re-detect.

### UNCHANGED bias (update only)

During **update**, the old summary already captures the file's purpose. Most
changes (typos, refactors, comments, small additions) don't change purpose.

Output `"UNCHANGED"` if the old summary still describes the file's purpose.

Output a new summary only when:
- A major new feature meaningfully expands purpose
- A previously central concern has been removed
- The file has been substantially rewritten for a different goal
- **The old summary is in the wrong language** — rewrite in the target language

During **init**, every file gets a real summary (no old summary to keep).

#### Rationalizations that resolve to UNCHANGED

| Excuse | Reality |
|--------|---------|
| "Diff is large, so I should rewrite" | Diff size ≠ purpose change |
| "Let me polish the old summary" | Polishing burns ~100x tokens vs UNCHANGED |
| "It's slightly more accurate now" | "Slightly better wording" ≠ purpose changed |
| "Not sure if purpose changed" | Not sure = it didn't |
| "New function added" | A helper in the same role doesn't expand purpose |

### Symlinks

Some `added`/`changed` items carry a `symlink_target` field. **Do not Read
the file** — a Read follows the link (wasteful, fails on broken links). Write
exactly `symlink → <target>` using the supplied `symlink_target`.

### Processing the work plan (todo --split)

Always run `todo --split` (the script chunks work into files). Output:

```json
{"stats": {...}, "removed": [...], "renamed": [...],
 "split_dir": "/tmp/filetree_XXXX",
 "batches": [{"file": ".../batch_00.json", "count": 25}, ...]}
```

- **0 batches** → no LLM work; apply the empty payload via stdin:
  ```bash
  echo '{"updates": []}' | python <scripts/filetree.py> apply
  ```
- **1 batch** → process inline: read the one batch file, decide each item,
  write `<split_dir>/part_00.json`.
- **Multiple batches** → spawn one sub-agent per batch (e.g. haiku-class).
  Each sub-agent: read SKILL.md, read its batch file, write `part_NN.json`.
  Sub-agents run in parallel and never see each other's batch.

### Part-file shape

Each `part_NN.json` carries ONLY summaries — no hashes, no removals:

```json
{"updates": [{"path": "...", "summary": "..."}]}
```

Apply all parts in one call:

```bash
python <scripts/filetree.py> apply <split_dir>/part_*.json
```

### Coverage gate

After `apply`, check its return for:

1. `missing_from_manifest` — any indexable file still without an entry.
2. Anomaly keys: `applied < received`, `skipped_unchanged_new`,
   `skipped_missing_path`.

If any are non-empty, summarize those files into one more part and re-run
`apply`. Loop until every key is clean. Only then report success.

Never hand-roll a coverage diff — the script's keys are the only evidence.
