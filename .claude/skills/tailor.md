# /tailor — Job Description Tailoring

## Purpose

Tailor the master profile for a specific job description, producing a focused CV that
highlights the most relevant experience and skills.

---

## How It Works

### Step 1 — Get the Job Description

Ask the user for a job description. Accept it as:
- **Pasted text** — the user pastes the JD directly into the chat
- **URL** — use WebFetch to fetch the content
- **File path** — read the file from disk

### Step 2 — Analyze the Job Description

Extract the following from the JD:
- **Required skills** — languages, frameworks, tools explicitly listed as requirements
- **Preferred skills** — nice-to-have technologies or experiences
- **Key responsibilities** — main duties and deliverables
- **Seniority level** — junior, mid, senior, staff, principal, lead
- **Domain/industry keywords** — fintech, healthcare, e-commerce, etc.
- **Specific methodologies** — agile, TDD, CI/CD, etc.

### Step 3 — Match Against `data/master_profile.yaml`

For each JD item, score it:
- **Strong match** — exact skill or very close synonym found in the profile
- **Partial match** — related skill present but not an exact match
- **No match** — skill not found in the profile

Calculate an overall match score (percentage of JD skills found in the profile).

### Step 4 — Draft Tailored YAML

Write to `data/tailored/<role_slug>.yaml`:

**Filename convention:** Derive `<role_slug>` from the JD title (lowercase, hyphens).
Examples: `senior-pm-acme`, `staff-engineer-foo`, `lead-data-scientist`.

**Content rules:**
- Reorder skills to prioritize JD-matched items (skills matching the JD come first).
- Rewrite the `summary` to align with the target role's language and terminology.
- Select the most relevant work experience bullets (those matching JD skills/responsibilities).
- Prune bullets that are not JD-relevant.
- Keep the file minimal but complete enough to render (must have all required sections).
- If fewer than 2 work experience entries remain after pruning, include the most
  relevant older roles even if not a direct match.
- If the profile has no direct matches for a key JD requirement, note this to the user
  and suggest what skills to add.

### Step 5 — Pre-render Review

Show the user the tailored YAML content (or a summary of changes) before rendering.
Allow them to make changes or ask for adjustments.

### Step 6 — Render

Run the render script:
```
python scripts/render_cv.py data/tailored/<role_slug>.yaml output/<role_slug>.md
```

### Step 7 — Report

Output a summary including:
- Which sections were included and why
- Which sections were excluded and why
- Match score (percentage of JD skills found in the profile)
- Output file path
- A brief note on how well the CV aligns with the JD

---

## Edge Cases

- **JD is a URL:** Use WebFetch to fetch the content.
- **JD is a file:** Read the file content.
- **Profile has no matches for JD:** Warn the user and suggest what skills to add.
- **Tailored YAML is too thin:** Include the most relevant older roles even if not a
  direct match.
- **User provides a very broad JD:** Prioritize the most senior/important requirements.

---

## Output Report Format

```
✅ Tailored CV generated: data/tailored/<role_slug>.yaml → output/<role_slug>.md

Sections included:
  - Contact (all fields)
  - Summary (rewritten for <role>)
  - Technical Skills: <N> skills matched, <M> partial matches
  - Work Experience: <N> roles, <M> bullets selected

Sections excluded:
  - <section>: <reason>

Match score: <XX>%

Output: output/<role_slug>.md
```
