# Evaluation & Benchmarking Protocol

## 1. Dataset Format

Benchmark annotations are maintained in standard CSV format (see `data/benchmark_samples.csv`):

- `reference`: Reference ground-truth transcript.
- `hypothesis`: ASR model output transcript.
- `reference_slots`: JSON array of gold critical slots (`[{"type": "date_or_time", "value": "15 May"}]`).
- `hypothesis_slots`: JSON array of extracted slots from the hypothesis.
- `condition`: Recording environment (`clean`, `noisy`, `clipped`, `reverb`).

Supported slot types:
- `negation` (`not`, `nahi`, `mat`, `नहीं`, `না`)
- `amount` (`₹1500`, `500 rupees`, `१५०० रुपये`, `টাকা`)
- `date_or_time` (`15 May`, `tomorrow`, `kal`, `५ बजे`)
- `critical_action` (`transfer`, `cancel`, `pay`, `रद्द`, `भेजो`, `বাতিল`)

## 2. Running Evaluation

Run the evaluation script from the repository root:

```bash
python research/evaluate.py data/benchmark_samples.csv
```

The evaluator computes:
- **WER / CER**: Standard edit-distance error rates.
- **Meaning-Critical Slot Preservation (MCSP)**: Percentage of reference critical slots correctly recovered.
- **Slot Precision / Recall / F1**: Micro and macro scores across all entity categories.
- **Per-Slot Breakdown**: Specific performance on high-risk negation and amount slots.
