---
name: local-latex
description: Compile LaTeX documents to PDF using a local TinyTeX installation. Use when the user needs to compile .tex files, generate PDFs, or troubleshoot LaTeX builds on this machine.
---

# Local LaTeX Compilation (TinyTeX)

A lightweight TeX Live 2026 installation at `/Users/shivam94/Documents/Resume/texlive/`. Installed via TinyTeX — auto-installs missing LaTeX packages on demand.

## Setup

Add TinyTeX to PATH before any LaTeX command:

```bash
export PATH="/Users/shivam94/Documents/Resume/texlive/bin/universal-darwin:$PATH"
```

## Compile a .tex file to PDF

```bash
export PATH="/Users/shivam94/Documents/Resume/texlive/bin/universal-darwin:$PATH"
cd /path/to/tex/file
pdflatex -interaction=nonstopmode -halt-on-error filename.tex
```

Two passes are needed for cross-references and outlines:

```bash
export PATH="/Users/shivam94/Documents/Resume/texlive/bin/universal-darwin:$PATH"
cd /path/to/tex/file
pdflatex -interaction=nonstopmode -halt-on-error filename.tex
pdflatex -interaction=nonstopmode -halt-on-error filename.tex
```

## Show the PDF in Codex

After compiling, use a Markdown file link to render the PDF in the Codex sidebar:

```markdown
[Open PDF](/absolute/path/to/filename.pdf)
```

## Install missing packages

TinyTeX auto-installs missing packages during compilation. If that fails, install manually:

```bash
export PATH="/Users/shivam94/Documents/Resume/texlive/bin/universal-darwin:$PATH"
tlmgr install package-name
```

## Check if a package is available

```bash
export PATH="/Users/shivam94/Documents/Resume/texlive/bin/universal-darwin:$PATH"
kpsewhich filename.sty
```

## Troubleshooting

### "Font ... not loadable: Metric (TFM) file not found"
Install the font package:
```bash
tlmgr install charter   # Charter font
tlmgr install avantgar  # Avant Garde
tlmgr install helvetic  # Helvetica
tlmgr install courier   # Courier
```

### "glyphtounicode.tex not found"
The file is part of the `glyphtounicode` package. If the TeX file uses `\input{glyphtounicode}`, ensure `glyphtounicode.tex` is in the TeX path. It's included in the standard TeX Live distribution.

### "Package microtype Error: Letterspacing currently doesn't work with xetex"
This file uses pdfLaTeX, not XeTeX. Always use `pdflatex` with this template, not `xelatex`.

### "I can't find file" or "No output PDF file produced"
Check the `.log` file for the specific error:
```bash
grep -i "error\|missing\|not found" filename.log
```

## Notes

- The installation is at `/Users/shivam94/Documents/Resume/texlive/` (not the default `~/Library/TinyTeX/`)
- TinyTeX installs missing packages automatically during compilation — typically no manual `tlmgr install` needed
- Use `pdflatex` (pdfTeX engine), not XeTeX or LuaTeX, for resume templates using `\textls` and `microtype`
- All generated files (`.aux`, `.log`, `.pdf`) appear alongside the `.tex` file
