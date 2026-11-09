# Methodology and Proposed Evaluation Design

## 1. Multi-Script Slot Extraction

The prototype applies rule-based patterns to ASR hypotheses across Latin/Romanized, Devanagari, and Bengali scripts. Candidate categories include negation, monetary amounts, dates/times, and selected action terms. Coverage is incomplete and language-dependent; extraction must be treated as a review signal, not a guarantee of meaning preservation.

## 2. Acoustic Feature Extraction

Supported WAV input is decoded for basic signal indicators, including RMS energy, clipping fraction, duration, and a silence heuristic. These are screening features. They are not a calibrated signal-to-noise ratio estimator and do not independently establish speech intelligibility or ASR confidence.

## 3. Verification Policy

The application can recommend `re_record`, `confirm`, or a proceed-style state based on audio heuristics and detected candidate slots. The policy is advisory. This prototype does not execute consequential downstream actions, and its ability to prevent action inversions has not been measured.

## 4. Current Evaluation

`research/evaluate.py` computes corpus WER/CER and micro exact-match slot precision, recall, F1, and MCSP from an annotated CSV. The bundled CSV contains 20 constructed illustrative text examples, not audio recordings or participant observations. The current evaluation is therefore a functional test of the scoring script and examples, not an empirical speech-system study.

## 5. Proposed Empirical Protocol

A future study should use consented, representative recordings; independent transcript and slot annotation; speaker-disjoint held-out splits; documented language and acoustic conditions; and a comparison of direct ASR against the full verification policy. It should measure missed critical slots, false alerts, confirmation outcomes, action-inversion interception, latency, and cost. Report uncertainty intervals and annotation agreement. Do not claim effectiveness until this study is completed.
