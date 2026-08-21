"""Scoring helpers for the evaluation, factored out so they are unit-
testable independently of the LLM and the eval driver."""

from __future__ import annotations

from collections import Counter

VERDICTS = ("present", "deficient", "missing")
FLAGGED = {"deficient", "missing"}  # "this item has a problem"


def kappa(pairs: list[tuple[str, str]]) -> float:
    """Cohen's kappa between two annotators (e.g. human vs model) over the
    three verdict classes. 1.0 = perfect, 0 = chance-level agreement."""
    n = len(pairs)
    if not n:
        return 0.0
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum((ca[c] / n) * (cb[c] / n) for c in VERDICTS)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def binary_metrics(pairs: list[tuple[str, str]]) -> dict:
    """Precision/recall/false-flag for the 'flagged' (problem) view."""
    tp = sum(h in FLAGGED and m in FLAGGED for h, m in pairs)
    fp = sum(h not in FLAGGED and m in FLAGGED for h, m in pairs)
    fn = sum(h in FLAGGED and m not in FLAGGED for h, m in pairs)
    tn = sum(h not in FLAGGED and m not in FLAGGED for h, m in pairs)
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / (tp + fn) if tp + fn else 0.0,
        "false_flag": fp / (fp + tn) if fp + tn else 0.0,
    }
