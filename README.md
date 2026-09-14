# CV Generator

An agent-driven Markdown CV generator that produces a polished, print-ready PDF from a single YAML master profile. Swappable Jinja2 layout templates (a default `modern` and a `classic` variant) define the visual layout; Python scripts merge the two into a Markdown intermediate, which WeasyPrint then renders to PDF.

```
data/master_profile.yaml  →  templates/modern_cv.md.jinja  →  output/cv.md  →  output/cv.pdf
```

## Project Structure

```
data/
  master_profile.yaml      # Single source of truth — full career record
  sources/                 # Raw text extracted from imported PDFs
  tailored/                # Role-specific YAML subsets (generated)
output/                    # Generated Markdown and PDF CVs
scripts/
  render_cv.py             # YAML + Jinja2 → Markdown
  render_pdf.py            # Markdown → HTML → PDF (via WeasyPrint)
  extract_pdf.py           # PDF → raw text (via PyMuPDF)
styles/
  cv.css                   # Print stylesheet (A4, margins, typography)
templates/
  modern_cv.md.jinja       # Default layout template for the Markdown output
  classic_cv.md.jinja      # Alternative "classic" layout template
requirements.txt           # Python dependencies
gen.sh                     # Convenience script: renders the default (modern) layout
```

## Quick Start

### 1. Set up the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**On Debian/Ubuntu** you can use system packages instead, which pull in the required Pango/HarfBuzz libraries automatically:

```bash
sudo apt install python3-yaml python3-jinja2 python3-pymupdf python3-markdown python3-weasyprint
```

### 2. Render the CV

```bash
# Markdown only
python scripts/render_cv.py data/master_profile.yaml output/cv.md

# Markdown + PDF
python scripts/render_cv.py data/master_profile.yaml output/cv.md && \
python scripts/render_pdf.py output/cv.md output/cv.pdf

# Or use the convenience script
bash gen.sh

# Render with an alternative layout template (e.g. the classic style)
python scripts/render_cv.py data/master_profile.yaml output/cv_classic.md \
    --template templates/classic_cv.md.jinja
python scripts/render_pdf.py output/cv_classic.md output/cv_classic.pdf
```

### 3. Inspect the HTML (optional)

```bash
python scripts/render_pdf.py output/cv.md output/cv.pdf --html-only
```

This stops after HTML conversion and writes `output/cv.html` — useful for debugging layout before the PDF step.

## How It Works

### Pipeline

1. **Master Profile** (`data/master_profile.yaml`) — a YAML file holding your complete career record: contact info, summary, skills, work experience, education, and certifications.

2. **Template** (`templates/modern_cv.md.jinja` by default) — a Jinja2 template that maps YAML fields to Markdown structure. It uses inline HTML for layout-critical sections (job headers, bullet points, section dividers) so the PDF renderer handles them reliably. Other layouts in `templates/` (e.g. the `classic` variant) are selected with the `--template` flag — see [Choosing a layout](#choosing-a-layout).

3. **Render** (`scripts/render_cv.py`) — loads the YAML, renders the template, and writes a Markdown file to `output/cv.md`.

4. **PDF** (`scripts/render_pdf.py`) — converts the Markdown to HTML (via python-markdown), applies the print stylesheet (`styles/cv.css`), and renders the final PDF with WeasyPrint. Style-agnostic: it consumes whatever Markdown the chosen template produced, so no flags change here when switching layouts.

### Master Profile Schema

```yaml
contact:
  full_name: "Your Name"
  title: "Job Title"
  email: "you@example.com"
  phone: "+1234567890"
  location: "City, Country"
  linkedin: "linkedin.com/in/username"    # omit or empty to skip
  github: "github.com/username"            # omit or empty to skip
  website: ""                              # omit or empty to skip

summary: |
  A brief professional summary...

core_skills:
  - "Skill 1"
  - "Skill 2"

technical_skills:
  architecture_cloud:
    - "AWS"
    - "Azure"
  data_platforms:
    - "PostgreSQL"
    - "Kafka"
  engineering_ecosystems:
    - "Python"
    - "Java"

work_experience:
  - company: "Company Inc."
    title: "Job Title"
    dates: "2020-01 – Present"
    bullets:
      - "Achievement-oriented bullet point."
      - "Another achievement."

education:
  - degree: "Degree Name"
    institution: "University"
    graduation_year: "2018"
    honors: "Cum Laude"

certifications:
  - "Certification Name — Issuing Body, Year"
```

**Date format:** ISO-8601 (`YYYY-MM`) or `"Present"` for current roles. Year-only is fine for older roles.

**Omitting fields:** Empty or null `linkedin`, `github`, and `website` values are automatically excluded from the output.

## Slash Commands

This project includes Claude Code slash commands for managing your career profile.
Both `/import` and `/interview` require `data/master_profile.yaml` to exist — they
do not create it from scratch.

- **`/import`** — Bootstrap the master profile from an existing PDF resume. Extracts
  text via PyMuPDF, maps it to the YAML schema, and overwrites the file after you
  confirm. Start with an empty skeleton (committed to the repo) and let `/import`
  populate it.

- **`/interview`** — Proactively identifies gaps in the master profile and fills them
  by asking targeted, one-at-a-time questions. State is persisted in
  `.claude/interview_tracker.json`.

- **`/tailor`** — Tailors the master profile for a specific job description. Analyzes
  the JD for skills and keywords, then writes a focused CV to
  `data/tailored/<role_slug>.yaml`.

## Customization

### Choosing a layout

Two built-in layouts ship with the project. Both render from the same
`data/master_profile.yaml`; only the template differs.

| Layout | Template | Look & feel |
|---|---|---|
| Modern (default) | `templates/modern_cv.md.jinja` | Single-column masthead with a horizontal contact rule, grouped technical-skills section, optional Certifications section |
| Classic | `templates/classic_cv.md.jinja` | Google Docs–style 2-column masthead (name/title left, contact right), merged 2-column skills grid, all-caps section headings |

To render with an alternative layout, pass `--template` to `render_cv.py`:

```bash
python scripts/render_cv.py data/master_profile.yaml output/cv_classic.md \
    --template templates/classic_cv.md.jinja
python scripts/render_pdf.py output/cv_classic.md output/cv_classic.pdf
```

The PDF step needs no changes: `render_pdf.py` applies the print stylesheet
(`styles/cv.css`) to whatever Markdown it is given, and both templates carry
their layout-critical styling inline. Use distinct output file names (e.g.
`cv_classic.md` / `cv_classic.pdf`) so the layouts don't overwrite each other.

> **Note:** the templates expect slightly different profile fields — for example,
> the classic template reads `edu.dates` for education entries while the modern
> template reads `edu.graduation_year`. Fields missing from the profile simply
> render as blank in that layout.

### Changing the layout

Edit the template in use (e.g. `templates/modern_cv.md.jinja` or `templates/classic_cv.md.jinja`). Templates use Jinja2 syntax with inline HTML for layout-critical sections. Variables map 1:1 to fields in `master_profile.yaml`.

### Changing the print styles

Edit `styles/cv.css`. This is a standard CSS print stylesheet targeting A4 paper. It controls margins, typography, section headings, and spacing. The template's inline styles take precedence where both are present.

### Adding a new template

Copy `templates/modern_cv.md.jinja` to a new file and pass it via the `--template` flag:

```bash
python scripts/render_cv.py data/master_profile.yaml output/cv.md \
    --template templates/my_template.md.jinja
```

## Dependencies

| Package | Purpose |
|---|---|
| PyYAML | Parse the master profile YAML |
| Jinja2 | Template rendering |
| PyMuPDF | PDF text extraction (for `/import`) |
| Markdown | Markdown-to-HTML conversion |
| WeasyPrint | HTML-to-PDF rendering |

## License

Private — for personal use only.
