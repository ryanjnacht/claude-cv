# /import — Resume/CV Import from PDF

## Purpose

Bootstrap (or refresh) `data/master_profile.yaml` from an existing PDF resume/CV.
The user gets a confirmed, renderable starting point without retyping their whole
history. The agent does the semantic mapping; `scripts/extract_pdf.py` does the
mechanical text extraction.

---

## Invocation

- The user provides a PDF path (or names a file in the workspace).
- If no file is given, ask for the PDF path.

---

## Workflow

### Step 1 — Extract raw text

```
python scripts/extract_pdf.py <pdf_path> -o data/sources/<slug>.txt
```

`<slug>` = the PDF filename without extension, lowercased, non-alphanumerics
replaced with hyphens (e.g. `jane-doe-resume.pdf` → `jane-doe-resume`).

- **Exit 2 (no text layer):** tell the user the PDF appears to be a scanned
  image. Ask for a text-based re-export, a web version (URL), or an offer to
  accept the resume as pasted text instead.
- **Keep the saved raw text** in `data/sources/` for provenance — it is the audit
  trail for everything the agent then writes.
- If the profile is for multiple roles/people, extract each PDF separately with
  distinct slugs.

### Step 2 — Map to the master-profile schema

Read the extracted text and map it to the `data/master_profile.yaml` schema
(see the schema notes in that file's header):

| PDF content | Target field |
|---|---|
| Name, current title | `contact.full_name`, `contact.title` |
| Email, phone, city | `contact.email`, `contact.phone`, `contact.location` |
| LinkedIn / GitHub / site URLs | `contact.linkedin`, `contact.github`, `contact.portfolio` |
| Profile / objective paragraph | `summary` (use verbatim if present) |
| Leadership, soft, transferable skills | `core_skills` |
| Languages, frameworks, cloud, data, tools | `technical_skills.{languages,frameworks,cloud_infra,data,tools}` |
| Jobs (most recent first) | `work_experience[]` — `company`, `title`, `dates`, `bullets` |
| Degrees | `education[]` — `degree`, `institution`, `graduation_year`, `honors` |
| Certs / licenses | `certifications` |

**Mapping rules:**

- **Never invent facts** — only information present in the PDF.
- **Leave a field out** (or as an empty list) if the PDF doesn't state it.
  `/interview` exists to fill exactly these gaps — do not pad.
- **Dates → ISO-8601** `YYYY-MM` or `Present` (e.g. "Jan 2022" → `2022-01`).
- **Bullets:** 3–5 per role where the source supports it; action-verb first;
  keep quantifiers the PDF provides; 1–2 lines each.
- If the PDF has no summary, draft 2–3 sentences from the strongest evidence
  and **mark it as drafted** when presenting to the user.
- Split technical items into the five schema sub-categories by best fit
  (a framework used for infra goes under `cloud_infra`, a test tool under `tools`, etc.).

### Step 3 — Present the draft

Before writing anything:

1. Show the **complete proposed YAML** in chat.
2. List **gaps** — fields the PDF didn't contain (e.g. "no certifications found;
   phone number missing; summary drafted — please review").
3. Wait for the user's confirmation or edits. **Do not write the master profile
   before confirmation.**

### Step 4 — Write the profile

On confirmation:

- **Master profile is sample/placeholder data** (never personally confirmed by
  the user): replace it wholesale, **preserving the file's header comment block**
  (lines 1–11 of `data/master_profile.yaml`).
- **Master profile already holds the user's real data:** merge — add new roles,
  skills, and fields; show the merged result. Never silently drop existing
  confirmed entries.
- Use the **Edit**/**Write** tools; preserve YAML formatting conventions.
- Render a preview so the user sees the result:

```
python scripts/render_cv.py data/master_profile.yaml output/cv.md
```

### Step 5 — Close the loop

Report:

- Sections imported (with counts: roles, skills, certs)
- Sections missing → suggest running `/interview` to fill them
- Path of the provenance text file in `data/sources/`
- Path of the rendered CV

---

## Edge Cases

- **Scanned PDF (exit 2):** as in Step 1 — offer alternate input, don't guess.
- **Multi-page, multi-column layout:** the extracted text may interleave columns;
  read it top-to-bottom and reassemble sections by heading.
- **Non-English resume:** map into the same English schema field names; keep
  proper nouns as-is; flag any translation the agent performed.
- **PDF with tables (dates, skills grids):** extract_pdf.py's text mode may
  fragment table cells — cross-check against section headings before mapping.
- **Very long resume (10+ pages):** still map everything; the tailoring step
  (`/tailor`) is what prunes for a specific role.

---

## Output Report Format

```
✅ Profile imported: data/sources/<slug>.txt → data/master_profile.yaml

Sections imported:
  - Contact: N of 8 fields
  - Summary: <verbatim | drafted>
  - Core skills: N
  - Technical skills: N across M categories
  - Work experience: N roles, M bullets total
  - Education: N entries
  - Certifications: N

Gaps (candidates for /interview):
  - <field>: <reason>

Rendered: output/cv.md
```
