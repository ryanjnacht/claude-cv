# /interview — Profile Gap Interview

## Purpose

Identify and fill gaps in `data/master_profile.yaml` by asking the user targeted,
one-at-a-time questions. The agent acts as a senior career manager, probing for
achievement-oriented details, clarifying ambiguities, and ensuring the profile is
comprehensive enough to support tailored CVs for any role.

---

## How It Works

### State Management

Use `.claude/interview_tracker.json` as persistent state across turns.

**On first invocation (no tracker exists):**
1. Read `data/master_profile.yaml`
2. Scan for all gaps using the rules below
3. Create the tracker with all sections unchecked and the full gap list
4. Ask the first question

**On subsequent invocations (tracker exists with `status: "active"`):**
1. Read the tracker
2. Read `last_question_index` — continue from the next question
3. Do NOT repeat the previous question
4. If `last_question_index` is at the end of the list, ask the user if they want to
   continue or start fresh

**On tracker with `status: "complete"`:**
- Tell the user the interview is complete. Offer to do a deep-dive on any specific
  section if they want.

**On corrupted/missing tracker:**
- Re-initialize from scratch: read the YAML, scan for all gaps, create a fresh tracker.

### Tracker Schema

```json
{
  "status": "active",
  "last_section": "work_experience",
  "last_question_index": 2,
  "questions_asked": [
    {
      "section": "work_experience",
      "role": "Stripe",
      "question": "What was the most technically challenging aspect of the fraud detection pipeline?",
      "answer": "Handling exactly-once semantics with Kafka.",
      "yaml_update": {
        "path": "work_experience[0].bullets",
        "action": "append",
        "value": "Implemented sequence-number-based deduplication layer to handle out-of-order Kafka events, reducing duplicate processing by 99%."
      },
      "asked_at": "2026-08-14T10:15:00Z"
    }
  ],
  "sections_checked": {
    "contact": true,
    "summary": true,
    "core_skills": true,
    "technical_skills": true,
    "work_experience": false,
    "education": false,
    "certifications": false
  }
}
```

---

## Gap Detection Rules

Scan `data/master_profile.yaml` against these criteria. Flag each as a gap if violated.

| Section | Gap Criteria |
|---|---|
| `contact` | Missing phone, location, or any URL field (linkedin, github, portfolio) |
| `summary` | Empty, placeholder text (e.g., "TBD"), or under 2 sentences |
| `core_skills` | Fewer than 4 skills listed |
| `technical_skills` | Any sub-category (languages, frameworks, cloud_infra, data, tools) is empty or has only 1 item |
| `work_experience` | Fewer than 2 roles total; any single role with fewer than 3 bullets; dates with ambiguity (e.g., "2022" without month); roles that list only duties with no quantified achievements |
| `education` | Missing education section entirely; missing graduation year; no honors/activities |
| `certifications` | Empty or missing list |

**Order of scanning:** contact → summary → core_skills → technical_skills → work_experience → education → certifications

---

## Question Formulation Rules

- **Be specific.** Reference the YAML content directly. Never ask a generic question.
  - Good: *"Your Shopify role lists 3 bullets. Can you share one more notable achievement from that time?"*
  - Bad: *"Tell me about your work at Shopify."*
- **Ask ONE question at a time.** Never batch questions.
- **If the user says "I don't remember" or "I don't want to share,"** skip that item and move on. Do not press.
- **Keep follow-up questions narrow.** Only one new topic per turn.
- **If the user provides new information that reveals additional gaps,** detect and add them to the question queue.

---

## Update Workflow (per turn)

1. Read `.claude/interview_tracker.json` (if it exists).
2. If it does not exist, read `data/master_profile.yaml`, scan for all gaps, create the tracker with all sections unchecked.
3. If it exists and `status: "active"`, read `last_question_index` and continue from the next question.
4. Read the YAML, identify the next gap based on `sections_checked`.
5. Ask ONE question.
6. Wait for the user's answer.
7. Use the **Edit** tool to update `data/master_profile.yaml` at the appropriate path.
   - If adding a bullet: append to the `bullets` list under the correct `work_experience` entry.
   - If adding a skill: append to the appropriate list.
   - If filling a missing field: use Edit to add the field.
8. Append the question/answer to `questions_asked` in the tracker.
9. Mark the relevant section as checked in `sections_checked`.
10. Update `last_section` and `last_question_index`.
11. If all sections are checked and no gaps remain, set `status: "complete"` and summarize.

---

## Completion Criteria

- All sections in `sections_checked` are `true`.
- No significant gaps remain in the YAML.
- Set `status: "complete"` and summarize all changes made.

---

## YAML Update Rules

- Use the **Edit** tool to update `data/master_profile.yaml`.
- Preserve existing YAML formatting and comment headers.
- Never invent facts — only write what the user confirms.
- Keep bullet points concise: 1–2 lines, action-verb first, quantified where possible.
- Use ISO-8601 dates (YYYY-MM) or "Present" for ongoing roles.
