"""Deterministic clause segmentation with reconciliation.

v1 sent the whole agreement to an LLM whose structured output re-emitted
every clause's full text: the largest latency and cost item in the app,
and clauses it silently dropped were unrecoverable. v2 segments locally
and deterministically: clause boundaries are found by numbering pattern,
text is sliced from the original string (nothing is ever re-generated),
and a reconciliation report says how trustworthy the segmentation is.
An LLM boundary-finder remains a fallback for unconventional documents,
returning boundaries only, never text.

Conventions handled (observed across the seven sample TAs):
- Top-level numbering "1. …" or "1) …" at line start; separator required,
  which filters addresses like "18 Cross Street".
- Sub-numbering "1.1 …" folds into its parent clause.
- Numbering that restarts at 1 opens a new section (section-scoped ids).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# A clause heading: number + mandatory "." or ")" separator + space +
# content starting with something heading-like.
_HEADING = re.compile(r"^\s*(\d{1,3})[\.\)]\s+\S")
# Sub-clause like "4.2" folds into parent 4; never starts a new clause.
_SUB = re.compile(r"^\s*\d{1,3}\.\d{1,2}\b")


@dataclass
class Clause:
    clause_id: str  # e.g. "1", "2", or "S2.3" (section 2, clause 3)
    title_line: str
    text: str


@dataclass
class SegmentationReport:
    clauses: list[Clause]
    preamble: str
    coverage: float  # share of document characters inside clauses+preamble
    sequence_flags: list[str] = field(default_factory=list)
    n_sections: int = 1

    @property
    def trustworthy(self) -> bool:
        """Segmentation is presentable without warnings only if coverage
        is near-total and the numbering sequence had no gaps."""
        return self.coverage >= 0.90 and not self.sequence_flags


def segment(text: str) -> SegmentationReport:
    lines = text.splitlines()
    starts: list[tuple[int, int]] = []  # (line index, number)
    for i, line in enumerate(lines):
        if _SUB.match(line):
            continue  # sub-clause: belongs to its parent
        m = _HEADING.match(line)
        if m:
            starts.append((i, int(m.group(1))))

    if not starts:
        return SegmentationReport(
            clauses=[], preamble=text, coverage=0.0,
            sequence_flags=["no numbered clauses found; LLM fallback required"],
        )

    # Sections: numbering restarting at 1 opens a new section.
    section = 1
    flags: list[str] = []
    prev_num = None
    ids: list[str] = []
    for _, num in starts:
        if prev_num is not None:
            if num == 1 and prev_num >= 1:
                section += 1
            elif num != prev_num + 1:
                flags.append(
                    f"numbering jumps {prev_num} to {num} in section {section}: "
                    "possible missed clause or extraction artifact"
                )
        ids.append(str(num) if section == 1 else f"S{section}.{num}")
        prev_num = num
    n_sections = section

    preamble = "\n".join(lines[: starts[0][0]]).strip()
    clauses: list[Clause] = []
    for k, (line_i, _) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
        chunk = "\n".join(lines[line_i:end]).strip()
        clauses.append(
            Clause(clause_id=ids[k], title_line=lines[line_i].strip()[:100], text=chunk)
        )

    covered = len(preamble) + sum(len(c.text) for c in clauses)
    coverage = covered / max(len(text.strip()), 1)
    return SegmentationReport(
        clauses=clauses, preamble=preamble, coverage=round(coverage, 3),
        sequence_flags=flags, n_sections=n_sections,
    )
