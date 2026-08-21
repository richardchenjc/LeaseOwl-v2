# Labeling guide: expert ground truth for LeaseOwl v2 evaluation

**What this produces:** the ground truth that RAG1 (the clause critique
and missing-clause detector) will be scored against. Every row you fill
becomes one test case. The protocol is written down before labeling
starts so the methodology is documented, and so every judgment call is
consistent across all seven TAs.

## The task

Open `eval/labels_template.csv`. Each row is one (tenancy agreement,
checklist item) pair: 7 TAs x 21 checklist items = 147 rows. For each
row, read the TA (use `eval/segmented_reference.md` for clause ids and
opening lines instead of re-reading whole documents) and fill three
columns:

**verdict** — exactly one of:
- `present` — the TA substantively meets the requirement as written in
  the `requirement` column.
- `deficient` — the TA addresses the topic but fails a stated element of
  the requirement (wrong number, missing sub-condition, vague where the
  requirement demands specificity).
- `missing` — the TA does not address the topic at all.

**evidence_clause_id** — the clause id(s) supporting your verdict,
semicolon-separated (e.g. `1;2`). For `missing`, leave blank.

**notes** — optional, but write one whenever the call was close.
Borderline cases are the most valuable rows in the whole exercise,
because they are where the LLM is most likely to disagree with you and
where the disagreement analysis gets interesting.

## Judgment rules

1. **Judge against the requirement text only**, not your broader
   opinions of the clause. If the requirement says "refund period
   typically 14 days" and the TA says 14 working days, that satisfies
   the stated element; note the working-days nuance rather than
   downgrading.
2. **The preamble counts.** Rent amount and lease term often live in the
   opening paragraph rather than a numbered clause. Use evidence id
   `preamble` for those.
3. **Blank template fields still count as present.** The sample TAs are
   templates with blanks (S$________). If the structure for the
   requirement is there, it is `present`; the blank is a signing matter,
   not a drafting omission.
4. **One verdict per row, always.** If torn between deficient and
   missing: `deficient` requires that the topic is at least mentioned.
5. **Don't consult the app.** Label from the documents alone, before
   seeing any model output, so the ground truth is independent of the
   system it will judge.

## Worked examples (from TA4, the room-rental agreement)

- Item 4, Security Deposit (requirement: amount; refund period; deduction
  conditions; cannot offset last month's rent): TA4 clauses 1 and 2 give
  0.5 month deposit, no offset of last month, refund within 14 working
  days after deductions for damage. Verdict `present`, evidence `1;2`,
  note "14 working days vs 14 days; IPA-invalid forfeiture clause is
  unusual".
- Item 5, Problem-Free Period (requirement: defined period, typically 30
  days, for landlord to rectify defects found at start): if nothing in
  TA4 defines such a period, verdict `missing`, evidence blank.
- Item 6, Minor Repairs (requirement: specific cost threshold, tenant
  pays up to it): a TA that assigns repair duties but names no dollar
  threshold is `deficient`, evidence the repair clause id, note "no
  threshold stated".

## Order and effort

Start with TA1 (7 clauses, one page) to calibrate on easy ground, then
TA2, TA3, TA5, then the long ones (TA4, TA6, TA7). Expect two to three
hours total. Fill the CSV in any editor; keep the file as UTF-8.
