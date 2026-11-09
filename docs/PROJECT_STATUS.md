# Project Status

**Version:** 0.3.1  
**Status:** Functional prototype with mocked automated tests; live provider operation and real-world effectiveness require separate verification.

## Implemented

1. FastAPI backend and browser dashboard for WAV upload and in-browser recording.
2. Audio inspection utilities for supported PCM WAV formats and heuristic quality indicators.
3. Gnani Prisma STT, Timbre TTS, and Evon adapters. Automated provider tests are mocked and do not establish live service availability.
4. Multi-script rule-based extraction of selected negations, amounts, dates/times, and action terms. This is heuristic extraction, not a validated language-understanding model.
5. A proceed/confirm/re-record recommendation flow and optional spoken readback. This prototype does not execute financial, medical, or other consequential actions.
6. An evaluator for WER, CER, and exact normalized critical-slot precision/recall/F1.

## Evaluation status

The bundled 20-row CSV is illustrative and text-based, not real audio or participant data. The reproducible current metrics are WER 4.62%, CER 4.38%, slot precision 95.83%, slot recall/MCSP 86.79%, slot F1 91.09%, and negation recall 37.50%. The evaluator does not measure policy lift, action interception, latency, or provider cost. No empirical claim of 96.5% MCSP or 100% avoided inversions is supported by the bundled data.

## Verification status

- Automated test suite: run locally with `pytest -q`; test count is whatever the current checkout reports.
- Python and JavaScript syntax checks: run before release.
- Live Prisma/Timbre/Evon credentials and endpoint compatibility: not verified by mocked tests.
- Real-world audio robustness and downstream safety: not yet evaluated.

## Before public submission

- Configure private credentials in `.env`; never commit it.
- Run a live provider smoke test with a replaceable test key.
- Record a demo that accurately labels mocked/manual and live API steps.
- Collect lawful, consented audio and perform a held-out evaluation before making empirical performance claims.
- Publish the repository and demo links, then complete the official submission form.
