# Gnani.ai Great Indian AI Internship Challenge — Official Submission Guide

**Challenge Portal:** [https://www.gnani.ai/internship](https://www.gnani.ai/internship)  
**Submission Deadline:** November 10, 2026, 11:59 PM IST (Strict; No extensions)  
**Project Name:** BhashaBridge  
**Subtitle:** Reliability-Aware Meaning Preservation for Code-Mixed Indian Voice Interfaces  
**Core Technologies Used:** Gnani Prisma v3 (STT), Gnani Timbre v3 (TTS), Gnani Evon (Reasoning LLM)

---

## 📌 Submission Checklist

- [x] **1. Working Prototype Built**:
  - Full-stack voice intelligence lab (FastAPI + Modern Web Dashboard).
  - In-browser live microphone recording (16kHz PCM WAV encoding).
  - Gnani Prisma v3 REST adapter for multilingual and Hinglish/Benglish code-mix ASR.
  - Gnani Timbre v3 SSE adapter for Indian voice synthesis and spoken readback.
  - Gnani Evon adapter for sovereign Indic intent reasoning and ambiguity resolution.
  - Heuristic audio quality gating (clipping, RMS, silence detection).
  - Language-aware Meaning-Critical Slot Preservation (MCSP) extraction across Roman, Devanagari, and Bengali scripts.
- [ ] **2. Real-world Evaluation & Evidence (not yet complete)**:
  - The bundled 20-row CSV is illustrative constructed text, not real recorded speech.
  - Its computed example metrics are documented in `docs/BENCHMARK_RESULTS.md`; they are not empirical user or model-performance claims.
  - A consented audio dataset and held-out end-to-end evaluation are still required for real-world claims.
- [ ] **3. Record 90-Second Demo Video**:
  - Follow the word-for-word script in `docs/DEMO_SCRIPT.md`.
  - Capture screen + clear microphone audio.
- [ ] **4. Publish Public Social Post (Mandatory Requirement)**:
  - Post the video on **LinkedIn** (and/or **X / Twitter**).
  - Tag **@Gnani.ai** and include required hashtags: `#GreatIndianAIInternshipChallenge` and `#GnaniAI`.
- [ ] **5. Submit Official Form**:
  - Open [gnani.ai/internship](https://www.gnani.ai/internship).
  - Fill candidate/team details.
  - Provide GitHub repository URL and public LinkedIn/X video URL.

---

## 📱 Ready-to-Use LinkedIn / X Post Copy

Copy and paste this text when uploading your demo video:

```text
🚀 Excited to unveil BhashaBridge for the @Gnani.ai Great Indian AI Internship Challenge!

In Indian voice AI, a 95% accurate transcription can still be catastrophic. If a noisy or code-mixed audio drops a single word like "nahi", "mat", or a currency qualifier, intent is completely inverted (e.g. paying instead of cancelling).

Introducing BhashaBridge:
A reliability-aware verification layer built on Gnani.ai’s sovereign AI stack:
🎙️ Gnani Prisma v3 — Code-mixed Indic speech-to-text
🔊 Gnani Timbre v3 — Real-time expressive voice readback
🧠 Gnani Evon — Sovereign Indic intent reasoning & safety auditing

Key Innovations:
✅ Acoustic-Gated Verification: Flags clipping, reverb, and low-energy audio before dispatching commands.
✅ Meaning-Critical Slot Preservation (MCSP): Tracks high-impact entities (negations, amounts, dates, critical actions) across English, Hinglish, Devanagari, and Bengali.
✅ Selective Readback Loop: Offers confirmation prompts for selected meaning-critical details; prevention effectiveness has not yet been measured.

Evaluated with a small illustrative transcript/slot CSV; real-world speech performance remains unmeasured.

Check out the demo video below and our open-source codebase!

#GreatIndianAIInternshipChallenge #GnaniAI #VoiceAI #SovereignAI #IndicAI #BuildForIndia #GenerativeAI
```

---

## 🏗️ Repository Submission Preparation

Before pushing your repository to GitHub:
1. Ensure `.env` is **NOT committed** (it is already included in `.gitignore`).
2. Include `.env.example` so reviewers can test with their own Gnani API keys.
3. Reviewers can run the application with one command:
   ```bash
   ./run.sh
   ```
   and access the dashboard at `http://127.0.0.1:8000`.
