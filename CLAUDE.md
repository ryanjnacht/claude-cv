# CLAUDE.md — Agent Instructions for CV Generator

## Project Context

This is an **agent-driven Markdown CV Generator**. A single `data/master_profile.yaml`
file holds the complete career record. A Jinja2 template in `templates/` defines the
visual layout. `scripts/render_cv.py` merges the two into a polished Markdown CV.

The agent (you) acts as a **senior career manager**: interviewing the user to keep the
master profile comprehensive, and tailoring it for specific job applications.

---

## Slash Command: `/import`

**Purpose:** Bootstrap (or refresh) `data/master_profile.yaml` from an existing
PDF resume/CV — a confirmed starting point without manual entry.

Detailed instructions are in `.claude/skills/import.md`. Key points:
- Extracts text via `scripts/extract_pdf.py` (PyMuPDF); raw text kept in
  `data/sources/<slug>.txt` for provenance.
- Agent maps extracted text to the master-profile schema — never invents facts,
  omits fields the PDF doesn't state.
- Shows the full proposed YAML and the gap list to the user **before** writing.
- Merges into the master profile on confirmation, then renders a preview.
- Reports gaps and suggests `/interview` to fill them.

---

## Slash Command: `/interview`

**Purpose:** Proactively identify gaps in `data/master_profile.yaml` and fill them by
asking the user targeted, one-at-a-time questions.

Detailed instructions are in `.claude/skills/interview.md`. Key points:
- Uses `.claude/interview_tracker.json` for state persistence across turns.
- Scans for gaps in contact, summary, skills, work experience, education, certifications.
- Asks one specific question at a time; never batches.
- Updates YAML with the user's confirmed answers via the **Edit** tool.

---

## Slash Command: `/tailor`

**Purpose:** Tailor the master profile for a specific job description, producing a
focused CV.

Detailed instructions are in `.claude/skills/tailor.md`. Key points:
- Accepts JD as pasted text, URL, or file path.
- Analyzes JD for skills, responsibilities, seniority, domain keywords.
- Matches against master profile and scores: strong / partial / no match.
- Writes tailored YAML to `data/tailored/<role_slug>.yaml` (pruned to relevant content).
- Shows user the tailored YAML before rendering.
- Renders automatically via `scripts/render_cv.py`.
- Reports included/excluded sections and match score.

---

## File Reference

| Path | Purpose |
|---|---|
| `data/master_profile.yaml` | Single source of truth — full career record |
| `data/sources/*.txt` | Raw text extracted from imported PDFs (provenance) |
| `data/tailored/*.yaml` | Role-specific subsets of the master profile |
| `templates/modern_cv.md.jinja` | Jinja2 template for Markdown output |
| `scripts/render_cv.py` | CLI tool: `python scripts/render_cv.py <in.yaml> <out.md>` |
| `scripts/extract_pdf.py` | CLI tool: `python scripts/extract_pdf.py <in.pdf> [-o out.txt]` |
| `.claude/skills/import.md` | Detailed `/import` skill instructions |
| `output/*.md` | Generated Markdown CVs |
| `.claude/skills/interview.md` | Detailed `/interview` skill instructions |
| `.claude/skills/tailor.md` | Detailed `/tailor` skill instructions |
| `.claude/interview_tracker.json` | State tracker for `/interview` sessions |
