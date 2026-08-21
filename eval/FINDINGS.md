# Evaluation findings: what the numbers mean

The auto-generated scorecard is `eval_report.md`; this is the human
analysis on top of it. Model: `gemini-3.6-flash`, 147 (agreement ×
checklist item) pairs, scored against a single expert's blind labels.

## Headline, and why it undersells the result

Exact 3-way accuracy is 61.2% and Cohen's kappa is 0.44 (moderate
agreement beyond chance). Taken alone these read as mediocre. The
interesting result is not the average; it is what the disagreements
reveal about the evaluation design itself.

## The dominant disagreement is a granularity mismatch, not a model error

Of the 64 items the expert judged **present** (requirement substantively
met), the model reclassified **43 as deficient**, in 41 cases with
"…but fails to specify X" reasoning. The initial temptation is to call
this over-flagging. Manual review of all 43 says otherwise: in the large
majority, the missing element X is **literally a sub-requirement named in
the checklist requirement text** — who pays repair costs above the
threshold, HDB approval for subletting, the deposit refund window, the
minimum 6-month term. A few are debatable (e.g. flagging "no mention of
internet" under a utilities clause), but most are legitimate, finer-
grained, true observations.

So the model is not wrong here, and neither is the expert. They are
answering different questions:
- The **expert** applied a holistic standard: does the clause
  substantively address the requirement? → present.
- The **model** applied a literal standard: are all stated sub-elements
  present? → deficient, because one is missing.

A single per-clause verdict (present / deficient / missing) cannot hold
both. It forces "substantively addresses it" and "satisfies every stated
sub-element" into one label, and the 43 disagreements are exactly the
items where those two readings diverge. This is a limitation of the
label schema, not a defect in the model.

## Sensitivity to the scoring rubric (the finding, quantified)

Because the disagreement is a granularity mismatch, the "accuracy" of the
tool depends on which rubric you score against. Two bounds:

| Scoring rubric | Exact accuracy | Kappa | Precision | False-flag |
|---|---|---|---|---|
| **A. Holistic** (expert "present" = gold) | 61.2% | 0.44 | 64% | 70% |
| **B. Sub-element-strict** (credit every model "deficient" on an expert-"present" clause) | 90.5% | 0.84 | 98% | 10% |

Same model, same responses, same labels; only the rubric changed. The
30-point accuracy swing is the finding: with a whole-clause label schema,
the tool's measured quality is dominated by scoring granularity, not by
model capability.

**Neither endpoint is "the true number", and B in particular must not be
read as "the model is 90% accurate."** Rubric B credits all 43 disputed
items as correct, but a few are debatable (e.g. flagging "no mention of
internet" under a utilities clause), so 90.5% is an optimistic ceiling.
More importantly, B accepts the model's own calls as ground truth; taken
as gold that is circular (scoring the model against itself). The honest
reading: true agreement under a proper sub-element rubric lies within
[61%, 90%], and pinning it exactly requires sub-element ground-truth
labels this project does not yet have. The width of the bracket is the
evidence that sub-element scoring (next section) is necessary.

## The consequence for the reported metrics

The 70% "false-flag rate" is therefore largely an artifact of scoring a
sub-element-aware model against whole-clause labels, not evidence that
the tool cries wolf. Read correctly, the model surfaces real, granular
gaps a user would plausibly want to see. The metric is still reported
honestly above, but this is what it means.

## Where model and expert genuinely converge

Of 52 items the expert judged **missing**, the model agreed on 50 and
**never once** called a missing requirement present. Detecting total
absence is not where the divergence lives; the divergence is entirely at
the present ↔ deficient boundary, which the section above explains.

## The design conclusion: score sub-elements, and rate their priority

The disagreement analysis points directly at the v3 design:

1. **Decompose each checklist item into its sub-elements** and score each
   present / absent, rather than emitting one verdict for the whole
   clause. "Minor repairs" becomes {threshold stated? who-pays-excess
   stated?}, each scored independently. This alone would resolve most of
   the 43 disagreements, because the expert and model already agree at
   the sub-element level; they only diverge when forced to collapse to
   one label.
2. **Attach a priority/severity to each gap.** Users want every potential
   issue surfaced, but ranked — a missing HDB-approval clause is more
   consequential than a missing "proof of payment may be requested"
   line, and some gaps (e.g. a deposit refund window) are real on paper
   but practically enforceable only through a small-claims tribunal.
   Presence × severity is the signal a user actually wants.

This is the natural next iteration; it is not applied here because it
requires re-defining the checklist at sub-element granularity and
re-labelling at that granularity, which is a fresh annotation effort.

## What we deliberately did NOT do

We did not tune the prompt to raise the accuracy number against these
147 labels; that would fit the model to its own test set. The honest
baseline is the deliverable, and the disagreement analysis above is
worth more than a tuned number.

## Threats to validity

- **Single annotator.** Ground truth is one expert's judgment. The
  disagreement review here is itself a form of adjudication: on
  inspection, many model "errors" are legitimate sub-element findings,
  which is what motivated the schema conclusion. A second annotator and
  an inter-annotator agreement figure would strengthen it further.
- **Seven agreements, one adversarial** (TA1 is a deliberately abusive
  contract). Small corpus; the direction of the finding is clearer than
  its exact magnitude.
- **One model, one run.** A second backend (the provider-agnostic client
  already supports OpenAI/Anthropic) would show whether the sub-element
  literalism is model-specific or general.

## Reproduce

`python eval/run_eval.py --replay` regenerates every number above from
the committed response cache, with no API key.
