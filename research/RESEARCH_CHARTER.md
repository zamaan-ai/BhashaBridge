# Research Charter: Reliability-Aware Meaning Preservation for Code-Mixed Indian Voice Interfaces

## Abstract & Problem Definition

Automatic Speech Recognition (ASR) systems deployed in conversational interfaces are traditionally evaluated using Word Error Rate (WER). However, in code-mixed Indian linguistic contexts (e.g., Hindi-English and Bengali-English), WER fails to capture catastrophic semantic inversions. An utterance can achieve 95% word accuracy while dropping a single crucial particle—such as a negation word (`nahi`, `mat`, `না`) or a monetary amount—completely reversing the user's intent.

BhashaBridge investigates whether an adaptive verification layer combining acoustic quality gating, multi-script slot extraction, and selective confirmation can maximize intent preservation while minimizing user friction.

---

## Core Hypotheses

- **H1 (Intent Preservation)**: Selective verification on critical entity slots achieves significantly higher Meaning-Critical Slot Preservation (MCSP) than unverified baseline ASR.
- **H2 (Acoustic Gating)**: Early detection of clipping, reverb, and low-energy audio prevents avoidable downstream hallucinations and misinterpretations.
- **H3 (Selective Readback)**: Targeted confirmation of high-impact slots (negation, amount, date) protects users against catastrophic actions while avoiding the latency and friction of full confirmation dialogues.

---

## Experimental Baselines

1. **Baseline A**: Direct ASR hypothesis passed to reasoning/downstream execution without verification.
2. **Baseline B**: Acoustic quality filter applied to reject degraded recordings, followed by standard ASR.
3. **Proposed (BhashaBridge)**: Acoustic quality gating + multi-script Meaning-Critical Slot extraction + dynamic confirmation readback loop.

---

## Primary Metric: Meaning-Critical Slot Preservation (MCSP)

$$\text{MCSP} = \frac{\sum \text{Correctly Preserved Critical Slots}}{\sum \text{Total Reference Critical Slots}}$$

Evaluated alongside:
- Word Error Rate (WER) and Character Error Rate (CER)
- Micro/Macro Precision, Recall, and F1 per slot type
- Catastrophic Inversion Prevention Rate (percentage of dropped negations intercepted before action execution)
