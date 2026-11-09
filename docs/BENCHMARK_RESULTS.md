# BhashaBridge Evaluation Report

**Evaluation input:** `data/benchmark_samples.csv`  
**Rows:** 20 illustrative, constructed transcript/slot examples  
**Evaluation method:** exact normalized text and slot matching via `research/evaluate.py`

## Important scope limitation

The bundled CSV is a small, manually constructed example set. It does **not** contain recorded audio, participant data, independently collected speech, or a controlled comparison of the BhashaBridge verification policy against a baseline. Its latency and provider-cost columns are illustrative metadata and are not evaluated by the script. Therefore, the numbers below describe only this CSV and must not be presented as real-world model performance, an acoustic robustness result, or evidence that downstream action inversions were prevented.

## Reproducible results

Run from the project root:

```bash
python research/evaluate.py data/benchmark_samples.csv
```

The current bundled file produces:

| Metric | Result on supplied examples |
|---|---:|
| Utterances | 20 |
| WER | 4.62% |
| CER | 4.38% |
| Critical-slot precision (micro) | 95.83% |
| Critical-slot recall / MCSP | 86.79% |
| Critical-slot F1 (micro) | 91.09% |
| Reference slots | 53 |
| Hypothesis slots | 48 |
| Exact matched slots | 46 |
| Negation recall | 37.50% (3 of 8) |

These are computed by exact normalized matching. A semantically equivalent value with different wording is not credited unless the annotation is normalized first. The evaluator does not calculate verification-policy lift, confirmation correctness, latency, provider cost, or avoided inversions.

## Interpretation

The examples illustrate how a transcript can preserve most words while omitting a meaning-critical slot. In this sample, negation recall is 37.50%, and amount recall is 75.00%. Those are useful failure cases for development, not population estimates. The application may recommend confirmation based on extracted slots and audio-quality heuristics, but the current CSV does not prove that this policy prevents any percentage of downstream errors.

## Evidence needed for a valid empirical claim

1. Collect consented, representative audio across target languages, accents, speakers, and recording conditions.
2. Document recruitment, consent, privacy, annotation rules, train/dev/test separation, and exclusions.
3. Have independent annotators label reference transcripts and meaning-critical slots; report agreement and adjudication.
4. Evaluate a named ASR baseline and the complete verification policy on the same held-out recordings.
5. Measure false confirmations, missed critical slots, action-inversion interception, latency, and cost with confidence intervals.
6. Publish anonymized aggregate results and the exact evaluation code/data license where permitted.

Until then, describe this report as a **synthetic/example-based functional evaluation**, not an empirical speech benchmark.
