"""Checklist-item detection: the capability the 147 labels measure.

For one tenancy agreement and one checklist requirement, decide whether
the agreement addresses it: present / deficient / missing, with an
evidence clause id and a one-line reason. This mirrors the human
labeling protocol exactly (eval/LABELING_GUIDE.md), so the machine's
verdict is compared to the expert's on equal terms.

The prompt is deliberately close to the instructions Richard labeled
under: judge against the requirement text only, the preamble counts,
present means substantively met, deficient means the topic is addressed
but a stated element is missing, missing means not addressed at all.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from .llm_client import LLMClient

VERDICTS = ("present", "deficient", "missing")

_PROMPT = """You are auditing a Singapore residential tenancy agreement against one checklist requirement. Decide whether the agreement meets it.

Judge against the REQUIREMENT text only, not your broader opinion of the clause.
- "present": the agreement substantively meets the requirement.
- "deficient": the agreement addresses the topic but fails a stated element of the requirement (wrong figure, missing sub-condition, vague where specificity is required).
- "missing": the agreement does not address the topic at all.
The opening/preamble of the agreement counts as much as numbered clauses (rent, term, and deposit often live there).

REQUIREMENT ({item_title}): {requirement}

TENANCY AGREEMENT:
{agreement}

Respond with ONLY a JSON object, no other text:
{{"verdict": "present|deficient|missing", "evidence": "<clause number or 'preamble' or ''>", "reason": "<one sentence>"}}"""


@dataclass
class Detection:
    verdict: str
    evidence: str
    reason: str
    raw: str


def _parse(raw: str) -> Detection:
    """Extract the JSON object robustly; fall back to keyword scan."""
    m = re.search(r"\{.*\}", raw, re.S)
    if m:
        try:
            d = json.loads(m.group(0))
            v = str(d.get("verdict", "")).strip().lower()
            if v in VERDICTS:
                return Detection(v, str(d.get("evidence", "")).strip(),
                                 str(d.get("reason", "")).strip(), raw)
        except json.JSONDecodeError:
            pass
    # Fallback: first verdict word that appears
    low = raw.lower()
    for v in VERDICTS:
        if v in low:
            return Detection(v, "", "(parsed from freetext)", raw)
    return Detection("missing", "", "(unparseable; defaulted)", raw)


def detect(client: LLMClient, agreement_text: str, item_title: str,
           requirement: str) -> Detection:
    prompt = _PROMPT.format(item_title=item_title, requirement=requirement,
                            agreement=agreement_text)
    return _parse(client.complete(prompt))
