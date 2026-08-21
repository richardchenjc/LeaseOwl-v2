"""Score the detector against the expert labels. The headline evaluation.

For each of the 147 (TA, checklist item) pairs, the detector produces a
verdict; we compare it to Richard's label and report:
- exact-match accuracy (3-way: present/deficient/missing)
- a binary "flagged" view (deficient or missing = the agreement has a
  problem on this item) with precision, recall, and false-flag rate,
  because in use the actionable signal is "this needs attention"
- accuracy by importance level (a miss on a CRITICAL item matters more)
- the full confusion matrix
- inter-annotator style agreement (Cohen's kappa) between model and human

Usage:
    python eval/run_eval.py            # live (needs GOOGLE_API_KEY); caches to eval/replays
    python eval/run_eval.py --replay   # offline from cache only (no key)
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "src")

from leaseowl.detector import detect
from leaseowl.llm_client import GeminiClient, ReplayClient
from leaseowl.pdf_io import extract_text
from leaseowl.scoring import FLAGGED, VERDICTS, binary_metrics, kappa

LABELS = Path("eval/labels_template.csv")
TA_DIR = Path("TA_sample")
def load_labels() -> list[dict]:
    with open(LABELS, encoding="utf-8-sig", newline="") as f:
        return [r for r in csv.DictReader(f) if (r["verdict"] or "").strip()]


def ta_texts() -> dict[str, str]:
    return {p.name: extract_text(p).text for p in sorted(TA_DIR.glob("*.pdf"))}



def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replay", action="store_true",
                    help="serve from cache only, no API key needed")
    args = ap.parse_args()

    from dotenv import load_dotenv
    load_dotenv()
    MODEL = "gemini-3.6-flash"
    inner = None if args.replay else GeminiClient(model=MODEL)
    client = ReplayClient(inner, model=MODEL)  # same key namespace live & replay
    labels = load_labels()
    texts = ta_texts()

    rows = []
    for i, lab in enumerate(labels, 1):
        before = client.misses
        det = detect(client, texts[lab["ta_file"]], lab["item_title"],
                     lab["requirement"])
        source = "LIVE" if client.misses > before else "cached"
        rows.append({
            "ta": lab["ta_file"], "item": lab["item_id"],
            "importance": (lab.get("importance") or "").strip() or "UNSET",
            "human": lab["verdict"].strip().lower(),
            "model": det.verdict, "model_reason": det.reason,
        })
        if not args.replay:
            print(f"[{i}/{len(labels)}] ({source:6}) {lab['ta_file']} item {lab['item_id']}: "
                  f"human={rows[-1]['human']} model={det.verdict}")

    # --- metrics
    n = len(rows)
    exact = sum(r["human"] == r["model"] for r in rows)
    pairs = [(r["human"], r["model"]) for r in rows]
    bm = binary_metrics(pairs)
    tp, fp, fn, tn = bm["tp"], bm["fp"], bm["fn"], bm["tn"]
    precision, recall, false_flag = bm["precision"], bm["recall"], bm["false_flag"]
    k = kappa(pairs)

    by_imp = defaultdict(lambda: [0, 0])
    for r in rows:
        by_imp[r["importance"]][1] += 1
        by_imp[r["importance"]][0] += r["human"] == r["model"]

    conf = Counter((r["human"], r["model"]) for r in rows)

    # --- write report
    out = ["# LeaseOwl v2 evaluation: detector vs expert labels", "",
           f"Model: `{client.model}`  ·  Items scored: {n}", "",
           "## Headline", "",
           f"- Exact 3-way accuracy: **{exact}/{n} = {exact/n:.1%}**",
           f"- Cohen's kappa (model vs human): **{k:.2f}** "
           "(agreement beyond chance; >0.6 substantial, >0.8 near-perfect)",
           "",
           "## Problem detection (deficient or missing = flagged)", "",
           f"- Precision: {precision:.1%}  (of items the model flags, how many the expert also flagged)",
           f"- Recall: {recall:.1%}  (of items the expert flagged, how many the model caught)",
           f"- False-flag rate: {false_flag:.1%}  (of items the expert judged fine, how many the model wrongly flagged)",
           f"- TP {tp} · FP {fp} · FN {fn} · TN {tn}", "",
           "## Accuracy by importance", "",
           "| Importance | Accuracy |", "|---|---|"]
    for imp, (ok, tot) in sorted(by_imp.items()):
        out.append(f"| {imp} | {ok}/{tot} = {ok/tot:.0%} |")
    out += ["", "## Confusion matrix (rows = expert, cols = model)", "",
            "| expert \\ model | present | deficient | missing |", "|---|---|---|---|"]
    for h in VERDICTS:
        cells = " | ".join(str(conf.get((h, m), 0)) for m in VERDICTS)
        out.append(f"| {h} | {cells} |")
    out += ["", "## Disagreements (for error analysis)", "",
            "| TA | item | expert | model | model reason |", "|---|---|---|---|---|"]
    for r in rows:
        if r["human"] != r["model"]:
            out.append(f"| {r['ta']} | {r['item']} | {r['human']} | {r['model']} | "
                       f"{r['model_reason'][:80]} |")

    report = "\n".join(out)
    Path("eval").mkdir(exist_ok=True)
    Path("eval/eval_report.md").write_text(report, encoding="utf-8")
    # machine-readable too
    with open("eval/eval_results.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    print(f"\ncache: {client.hits} hits, {client.misses} live calls")
    print(f"wrote eval/eval_report.md and eval/eval_results.csv")
    print("\n" + "\n".join(out[:18]))


if __name__ == "__main__":
    main()
