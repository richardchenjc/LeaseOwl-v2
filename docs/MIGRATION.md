# v1 → v2 migration

## How to apply this overlay to your fork

1. Fork `chngzhiquan/DS5105-Project` to your account, clone it, create a
   branch `v2`.
2. Copy this folder's contents over the clone (src/, tests/, eval/, docs/,
   pyproject.toml, requirements.txt, .gitignore). Place `ci.yml` at
   `.github/workflows/ci.yml` manually (from the chat file card).
3. Delete from git tracking (they remain in history, which is fine):
   - `**/__pycache__/` (compiled caches; never belong in git)
   - `faiss_index_general_qa/`, `faiss_index_ideal_clauses/` (binary
     indexes; rebuilt from source documents, so tracking them is stale
     data waiting to happen)
   - `streamlit/` legacy duplicates (`main_ver1.py`, `backend_utils_ver1.py`)
     and `backend_utils.py` (superseded by `backend_utils_v2.py`)
   - old `requirements.txt` (UTF-16 encoded; pip cannot parse it — the
     v2 one is UTF-8 and lean)
4. Commit as "v2: hygiene + deterministic segmentation + eval scaffolding",
   crediting the group in the message.

## What changes functionally in v2 (see docs/V2_REVIEW.md for reasoning)

- `src/leaseowl/segmenter.py` replaces the LLM parse chain in
  `backend_utils_v2.py:get_parser_chain/process_pdf_to_clauses`. Clause
  boundaries are found deterministically and text is sliced locally;
  the LLM is reserved as a boundary-only fallback for unconventional
  documents. Segmentation of all seven sample TAs: 100% coverage, zero
  sequence flags, milliseconds instead of minutes.
- `src/leaseowl/pdf_io.py` replaces bare text extraction: scanned PDFs
  are detected and reported to the user instead of failing generically.
- `eval/labels_template.csv` (147 rows) + `eval/segmented_reference.md`
  are the expert-labeling pack: verdict per (TA, checklist item) as
  present / missing / deficient, with evidence clause ids.
- Coming next (needs an OpenAI key): throttled two-tier critique to
  replace the unthrottled per-clause gpt-4o gather, and the eval runner
  with record/replay so CI and reviewers rerun everything key-free.

## Attribution

v1 was a five-person DS5105 group project. v2 changes are solo work on
top of it; keep both facts visible in the README.
