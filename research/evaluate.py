"""Reproducible transcript and critical-slot evaluation.

CSV columns: reference, hypothesis, reference_slots, hypothesis_slots.
Slot columns contain JSON arrays such as
[{"type":"date_time","value":"15 May"}].

Metrics: corpus WER/CER and micro slot precision/recall/F1/MCSP.
Exact normalized slot matches are used; semantic equivalence requires prior
annotation normalization and is not inferred by this script.
"""
from __future__ import annotations
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

def tokens(text: str) -> list[str]:
    return re.findall(r"\w+", (text or "").casefold(), flags=re.UNICODE)

def edit_distance(a, b) -> int:
    # Memory-efficient Levenshtein distance.
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, left in enumerate(a, 1):
        current = [i]
        for j, right in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (left != right)))
        previous = current
    return previous[-1]

def _slots(raw: str, row_number: int, column: str) -> list[tuple[str, str]]:
    try:
        value = json.loads(raw or "[]")
    except json.JSONDecodeError as exc:
        raise ValueError(f"CSV row {row_number}: invalid JSON in {column}: {exc}") from exc
    if not isinstance(value, list):
        raise ValueError(f"CSV row {row_number}: {column} must be a JSON array")
    result = []
    for item in value:
        if not isinstance(item, dict) or "type" not in item or "value" not in item:
            raise ValueError(f"CSV row {row_number}: each {column} item needs type and value")
        result.append((str(item["type"]).casefold(), str(item["value"]).strip().casefold()))
    return result

def score(path: str | Path) -> dict:
    with open(path, newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"reference", "hypothesis", "reference_slots", "hypothesis_slots"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("CSV must contain columns: " + ", ".join(sorted(required)))
        rows = list(reader)
    if not rows:
        raise ValueError("Evaluation CSV contains no utterances")

    word_errors = word_total = char_errors = char_total = 0
    ref_counter: Counter = Counter()
    hyp_counter: Counter = Counter()
    per_type = defaultdict(lambda: Counter())
    for index, row in enumerate(rows, start=2):
        ref_text, hyp_text = row.get("reference") or "", row.get("hypothesis") or ""
        ref_words, hyp_words = tokens(ref_text), tokens(hyp_text)
        word_errors += edit_distance(ref_words, hyp_words)
        word_total += len(ref_words)
        ref_chars, hyp_chars = list(ref_text.casefold()), list(hyp_text.casefold())
        char_errors += edit_distance(ref_chars, hyp_chars)
        char_total += len(ref_chars)
        refs = _slots(row.get("reference_slots", ""), index, "reference_slots")
        hyps = _slots(row.get("hypothesis_slots", ""), index, "hypothesis_slots")
        ref_counter.update(refs); hyp_counter.update(hyps)
        for kind, value in set(refs) | set(hyps):
            per_type[kind]["reference"] += refs.count((kind, value))
            per_type[kind]["hypothesis"] += hyps.count((kind, value))
            per_type[kind]["correct"] += min(refs.count((kind, value)), hyps.count((kind, value)))

    correct = sum((ref_counter & hyp_counter).values())
    ref_n, hyp_n = sum(ref_counter.values()), sum(hyp_counter.values())
    precision = correct / hyp_n if hyp_n else (1.0 if ref_n == 0 else 0.0)
    recall = correct / ref_n if ref_n else (1.0 if hyp_n == 0 else 0.0)
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    by_type = {}
    for kind, counts in sorted(per_type.items()):
        p = counts["correct"] / counts["hypothesis"] if counts["hypothesis"] else 0.0
        r = counts["correct"] / counts["reference"] if counts["reference"] else 0.0
        by_type[kind] = {"precision": p, "recall": r, "f1": 2*p*r/(p+r) if p+r else 0.0, **dict(counts)}
    return {
        "utterances": len(rows),
        "WER": word_errors / word_total if word_total else None,
        "CER": char_errors / char_total if char_total else None,
        "MCSP": correct / ref_n if ref_n else None,
        "slot_precision_micro": precision,
        "slot_recall_micro": recall,
        "slot_f1_micro": f1,
        "reference_slots": ref_n, "hypothesis_slots": hyp_n, "preserved_slots": correct,
        "slot_metrics_by_type": by_type,
        "metric_note": "Exact normalized slot matching only; no semantic equivalence is inferred."
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", help="Path to annotated evaluation CSV")
    args = parser.parse_args()
    print(json.dumps(score(args.csv), indent=2, ensure_ascii=False))
