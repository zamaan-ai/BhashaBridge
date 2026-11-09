# BhashaBridge Demo Walkthrough
**Target duration:** 90–120 seconds  
**Format:** Screen recording with clear narration

### 0:00–0:15 — Problem
Show the dashboard. Explain that a transcript can sound fluent while missing a negation, amount, or date, so consequential actions should not be triggered from transcription alone.

### 0:15–0:35 — Input and transcription
Use a consented sample recording or manual transcript mode. State clearly whether the displayed transcript came from a live Gnani Prisma request or a manual test. Show the audio-quality indicators.

### 0:35–0:55 — Meaning-critical slots
Show extracted candidate slots for negation, amount, date/time, and action. Explain that extraction is heuristic and should be reviewed; it is not a guarantee of correct interpretation.

### 0:55–1:15 — Verification and readback
Show the confirmation recommendation and, if live credentials are configured, demonstrate Timbre readback. Explain that the prototype recommends confirmation and does not execute financial or other consequential actions.

### 1:15–1:30 — Evaluation and limitations
Show the benchmark panel. Explain that the bundled 20 rows are illustrative constructed examples, not real speech recordings. Report the computed example metrics only: WER 4.62%, CER 4.38%, slot precision 95.83%, slot recall/MCSP 86.79%, slot F1 91.09%, and negation recall 37.50%. Explicitly state that avoided inversions and real-world effectiveness have not yet been measured.

### Closing
Describe BhashaBridge as a prototype exploring reliability-aware verification for code-mixed Indian voice interfaces.
