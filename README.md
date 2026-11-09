# BhashaBridge

**Reliability-Aware Meaning Preservation for Code-Mixed Indian Voice Interfaces**

BhashaBridge is an intelligent speech verification lab that combines **Gnani Prisma v3** (STT), **Gnani Timbre v3** (TTS), and **Gnani Evon** (Reasoning LLM) to solve a fundamental challenge in Indian voice AI: **preventing catastrophic intent inversion in code-mixed and noisy environments**.

---

## 💡 The Core Problem

Standard Word Error Rate (WER) is an inadequate safety metric for conversational interfaces. A model can achieve a 95% word accuracy while losing a single small word (`nahi` / `mat` / `না`) or a currency symbol (`₹`), completely reversing the user's intended action (e.g., executing a payment instead of aborting it).

BhashaBridge introduces **Meaning-Critical Slot Preservation (MCSP)**: an acoustic-gated verification layer that intercepts high-stakes ambiguities and closes the loop with natural spoken confirmation before actions execute.

---

## ⚡ Architecture & Gnani.ai Stack

```
   [ User Voice Input ]
 (In-Browser Live Mic or PCM WAV)
            │
            ▼
 ┌──────────────────────┐
 │ Acoustic Health Gate │ ──▶ Detects Clipping, Low Energy, Silence Heuristics
 └──────────────────────┘
            │
            ▼
 ┌──────────────────────┐
 │   Gnani Prisma v3    │ ──▶ Code-Mixed Indic ASR (Hinglish, Benglish, Devanagari)
 └──────────────────────┘
            │
            ▼
 ┌──────────────────────┐
 │ Meaning-Critical     │ ──▶ Multi-Script Slot Extraction (Negations, Amounts,
 │ Slot Extractor       │     Dates/Times, High-Risk Action Intents)
 └──────────────────────┘
            │
            ▼
 ┌──────────────────────┐
 │ Verification Policy  │ ──▶ Re-record | Explicit Confirm | Safe Proceed
 └──────────────────────┘
            │
     ┌──────┴────────────────────────┐
     ▼                               ▼
┌──────────────────┐       ┌──────────────────────┐
│  Gnani Timbre v3 │       │   Gnani Evon LLM     │
│ Spoken Readback  │       │ Intent Safety Audit  │
└──────────────────┘       └──────────────────────┘
```

---

## 🚀 Key Features

1. **Live Browser Microphone Ingest**: Directly records in-browser and converts audio to standard 16kHz 16-bit mono PCM WAV client-side.
2. **Gnani Prisma v3 Integration**: REST adapter supporting `/stt/v3`, multipart audio upload, and `format=codemix` across BCP-47 locale pairs.
3. **Multi-Script Semantic Extraction**: Robust literal slot extraction covering English, Hinglish, Bengali-English, Devanagari Hindi (`नहीं`, `रुपये`, `तारीख`), and Bengali (`টাকা`, `না`).
4. **Gnani Timbre v3 Closed Voice Loop**: Generates natural, expressive spoken confirmation prompts in Hindi and English personas (`Shubham`, `Avinash`, `Riyaa`, `Chetana`).
5. **Gnani Evon Reasoning Adapter**: Optional intent-auditing integration; validate against your account and model documentation before relying on its output.
6. **Reproducible Example Evaluator**: Built-in 20-row illustrative CSV with automated WER, CER, and exact slot scoring.

---

## 📊 Evaluation (illustrative examples only)

The bundled `data/benchmark_samples.csv` contains 20 constructed transcript/slot examples. It is not a collection of real recordings or participant data. Running `python research/evaluate.py data/benchmark_samples.csv` currently reports:

| Metric | Result on supplied examples |
|---|---:|
| WER | 4.62% |
| CER | 4.38% |
| Critical-slot precision (micro) | 95.83% |
| Critical-slot recall / MCSP | 86.79% |
| Critical-slot F1 (micro) | 91.09% |
| Negation recall | 37.50% |

These are exact-match scores on illustrative text, not real-world speech performance. The evaluator does not measure avoided action inversions, policy lift, latency, or provider cost. See [`docs/BENCHMARK_RESULTS.md`](docs/BENCHMARK_RESULTS.md) for scope, limitations, and a reproducible evaluation command.

---

## 🛠️ Quick Start

### 1. Installation
```bash
# After creating your own public/private GitHub repository, clone its URL:
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd <REPOSITORY_FOLDER>
chmod +x run.sh
```

### 2. Configure Environment
```bash
cp .env.example .env  # run.sh also creates this safely if it is absent
nano .env
```
Add your private `GNANI_API_KEY`. (Manual transcript testing works without an API key).

### 3. Launch App
```bash
./run.sh
```
Open **`http://127.0.0.1:8000`** in your browser.

---

## 🧪 Automated Tests

Run the test suite:
```bash
.venv/bin/pytest -v
```
The automated suite covers API endpoints, audio decoding, mocked Prisma/Timbre/Evon adapters, semantic extraction, and benchmark scoring. Provider tests use mocks; they do not prove live API connectivity.

---

## 📄 Submission Documents

- [docs/SUBMISSION_CHECKLIST.md](docs/SUBMISSION_CHECKLIST.md): Complete guide for submitting to `gnani.ai/internship`, including social post copy and hashtags.
- [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md): Word-for-word 90-second demo video recording script.
- [docs/BENCHMARK_RESULTS.md](docs/BENCHMARK_RESULTS.md): Reproducible example-based evaluation and limitations.

---

## 🔒 Security & Privacy

- `.env` is excluded via `.gitignore`; `.env.example` contains placeholders only. Never commit API keys. If a key was ever pasted into chat, logs, or a public repository, revoke it and create a replacement.
- Zero raw audio is persisted to disk; all uploads are processed in-memory.
- This is a research prototype for scheduling and information queries. Not intended for direct medical or financial execution.
