# LeaseOwl v2: Code Review, Latency Diagnosis, and User-Risk Inventory
**Reviewed 18 Aug 2026 against commit of 15 Nov 2025 (chngzhiquan/DS5105-Project). This document is the v2 roadmap; findings below are traceable to specific code.**

## 1. The latency mystery, solved (and it wasn't the semantic search)

The remembered problem: full analysis took minutes. The remembered suspect: semantic comparison. The code says otherwise. FAISS similarity search over a few hundred template chunks runs in milliseconds; retrieval is nowhere near the bottleneck. The minutes come from three LLM-architecture choices:

**1a. The parser re-emits the entire document.** `get_parser_chain()` sends the whole agreement to gpt-4o-mini with structured output that returns every clause's full text as JSON. The model therefore generates the entire tenancy agreement token by token as output. A 15-page TA means tens of thousands of output tokens in a single call: likely one to three minutes on its own, the largest single latency item, plus proportional cost, plus truncation risk on long documents.

**1b. One gpt-4o call per clause, unthrottled.** `parallel_rag_node` fires `asyncio.gather` over every clause with no concurrency limit, each calling gpt-4o (the large model) even for boilerplate clauses. Twenty to forty simultaneous gpt-4o calls trigger provider rate limits; the client then retries with backoff, which users experience as unexplained minutes.

**1c. Heavy cold start.** The embedding model (sentence-transformers over torch) loads at import time, and each uploaded document gets embedded on CPU to build its Q&A index before anything else happens.

**v2 fixes, in order of payoff:**
- Parser returns clause boundaries and titles only; clause text is sliced locally from the raw string. Output tokens drop by an order of magnitude. Add a deterministic regex-first segmenter for conventionally numbered TAs, with the LLM as fallback for unstructured documents. Parser fidelity becomes measurable (see §3).
- Two-tier critique: gpt-4o-mini triages every clause; only flagged or uncertain clauses escalate to the large model. Batch small clauses several per call.
- `asyncio.Semaphore` (5 to 8 concurrent), shared client instance, per-clause progress reported to the UI so waiting is visible instead of mysterious.
- Cache analyses keyed on (clause text hash, template version, model): re-uploading the same document becomes instant and free.
- Whether the semantic search itself needs improvement is currently unknowable, because nothing measures it. The §3 evaluation adds retrieval hit rate against labeled clause-to-template mappings; optimize retrieval only if those numbers say so. Measuring before tuning is the discipline.

## 2. The false-flag testing that was planned but never landed

Confirmed absent from the repo. The `Validation/` folder covers RAG2 (the chatbot) only, and its 265-row golden set is largely paraphrases of the source content scoring perfect 1.0 ROUGE, so it grades the system on questions it nearly memorised while measuring chunk retrieval rather than answer quality. RAG1, the product's headline feature (risk ratings, unfair-clause flags, missing-clause detection), has no evaluation of any kind. Its false-flag rate, miss rate, and retrieval accuracy are all unmeasured.

**v2 builds it:** the repo already contains seven sample TAs and a CEA-grounded checklist of 20+ requirements with importance levels. Expert labels (Richard) mark, per TA, each checklist item as present / missing / deficient. The pipeline is then scored on: missing-clause detection precision and recall, flag agreement, false-flag rate (overall and by importance level), and retrieval hit rate. Refusal and out-of-scope cases get added to the RAG2 golden set along with near-miss traps. Every eval run records LLM responses to JSON for replay, so CI and reviewers rerun the full evaluation without keys or cost.

## 3. User's-eye problem inventory (ranked by harm)

1. **Silent clause loss.** If the parser skips clause 14, every downstream report is confidently incomplete and the user cannot tell. Worst failure in the system because it converts trust into risk. Mitigation: local slicing (§1), a reconciliation check (extracted clauses vs numbering sequence vs document length), and parser fidelity measured on the seven labeled TAs.
2. **Unmeasured judgment.** Flags and risk ratings with unknown false-flag and miss rates, delivered in authoritative language. Mitigation: §2 evaluation, plus reporting confidence honestly in the UI.
3. **Silent truncation.** `compress_ta_text` cuts at 120k characters (80k in fast mode); tail clauses of long agreements are never analyzed and the user is not told. Mitigation: explicit warning listing unanalyzed sections, or chunked multi-pass analysis.
4. **Privacy.** Users upload personal tenancy agreements (names, addresses, rent, sometimes ID numbers) which are sent verbatim to a third-party API. For a Singapore product this is a PDPA-relevant design fact. Mitigation: prominent disclosure at minimum; a redaction pass (names/IDs masked before API calls) as the real fix.
5. **Scanned PDFs fail unhelpfully.** Image-based PDFs extract as empty text and the pipeline returns None. Mitigation: detect and tell the user "this PDF is scanned; OCR is not supported" rather than a generic failure.
6. **Opaque waiting.** Minutes of processing behind a spinner with no progress. Mitigation: per-clause progress (§1 fixes make the wait shorter and visible).
7. **Repeat cost.** No caching, so every re-upload re-pays the full API cost. Mitigation: §1 cache.
8. **Session fragility.** Streamlit state dies on refresh mid-analysis. Mitigation: modest (persist last report to disk); acknowledged limitation otherwise.
9. **Overtrust framing.** Output reads as legal advice. Mitigation: standing disclaimer plus the §2 accuracy numbers published in the README, which is more honest than any disclaimer.
10. **Unvalidated translation.** Nine output languages, none evaluated. Mitigation: scope translation out of v2 claims; mark experimental.
11. **Developer experience.** requirements.txt is UTF-16 (pip cannot parse it), compiled caches and binary FAISS indexes are committed, duplicate module generations confuse newcomers, no tests, no CI. Mitigation: hygiene pass, pytest on pure functions, GitHub Actions, .env-based key handling.

## 4. v2 scope, phased

**Phase 1 (this week, before AIAP submission):** repo hygiene; parser boundary-slicing rework with reconciliation check; concurrency throttle and progress; the §2 evaluation harness with expert labels on all seven TAs; record-replay; honest README with measured numbers; group work credited, v2 contributions stated.
**Phase 2 (before October interview):** two-tier critique and caching; truncation warning; redaction pass; RAG2 golden-set hardening; retrieval tuning if the measurements justify it.
**Out of scope, stated:** translation validation, OCR, mobile.
