"""Language-aware extraction of meaning-critical slots and verification policy.

Supports English, code-mixed Indic (Hinglish, Benglish), Devanagari script,
and Bengali script for speech reliability auditing.
"""
import re
from . import config

# 1. Negation patterns (English, Hinglish, Devanagari, Bengali)
NEGATION_PATTERNS = [
    re.compile(r"\b(not|no|never|don't|dont|didn't|didnt|cannot|can't|cant|won't|wont|neither|nor)\b", re.I),
    re.compile(r"\b(nahi|nahin|naa|mat|na|bilkul nahi|kabhi nahi|mana)\b", re.I),
    re.compile(r"(नहीं|नही|मत|ना|कभी नहीं|बिल्कुल नहीं|नाही)", re.U),
    re.compile(r"(না|নয়|নহে|কখনও না|একদম না|মাত)", re.U),
]

# 2. Amount and Currency patterns (Symbols, Romanized, Devanagari, Bengali)
AMOUNT_PATTERNS = [
    re.compile(r"(?:₹|rs\.?|inr|usd|\$|eur|€)\s?\d[\d,]*(?:\.\d{1,2})?", re.I),
    re.compile(r"\b\d[\d,]*(?:\.\d{1,2})?\s?(?:rupees?|rs|inr|bucks|paise?|rupaye?|taka|koti|hazaar|hazar|lakh|crore)\b", re.I),
    re.compile(r"(?:₹|रु\.?|रुपये|रुपया)\s?[\d०-९]+(?:\.[\d०-९]+)?", re.U),
    re.compile(r"[\d०-९]+(?:\.[\d०-९]+)?\s?(?:रुपये|रुपया|पैसे|हज़ार|हजार|लाख|करोड़)", re.U),
    re.compile(r"(?:টাকা|৳)\s?[\d০-৯]+(?:\.[\d০-৯]+)?", re.U),
    re.compile(r"[\d০-৯]+(?:\.[\d০-৯]+)?\s?(?:টাকা|পয়সা|হাজার|লাখ|কোটি)", re.U),
    re.compile(r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten|hundred|thousand|lakh)\s+(?:rupees|rs|taka)\b", re.I),
    re.compile(r"\b(?:ek|do|teen|chaar|paanch|chhah|saat|aath|nau|das|sau|hazaar|lakh)\s+(?:rupaye|rupees|rs|taka)\b", re.I),
]

# 3. Date & Time patterns (English, Romanized Indic, Devanagari, Bengali)
DATE_TIME_PATTERNS = [
    # Standard date formats (e.g., 15/05/2026, 15-May-2026, 15 May)
    re.compile(r"\b(?:\d{1,2}[-/]\d{1,2}(?:[-/]\d{2,4})?|\d{1,2}(?:st|nd|rd|th)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*)(?:\s+\d{2,4})?\b", re.I),
    # Relative day expressions
    re.compile(r"\b(?:tomorrow|today|yesterday|tonight|day after tomorrow|next\s+(?:week|month|year|monday|tuesday|wednesday|thursday|friday|saturday|sunday))\b", re.I),
    re.compile(r"\b(?:aaj|kal|parson|aane wala kal|beeta kal|agle hafte|agle mahine|agle somwar|agle mangalwar)\b", re.I),
    re.compile(r"(आज|कल|परसों|अगले हफ्ते|अगले महीने|अगले सोमवार|अगले मंगलवार|आगामी)", re.U),
    re.compile(r"(আজ|কাল|পরশু|আগামীকাল|আগামী সপ্তাহ|আগামী সোমবার)", re.U),
    # Months in Devanagari & Bengali
    re.compile(r"[\d०-९]{1,2}\s*(?:जनवरी|फरवरी|मार्च|अप्रैल|मई|जून|जुलाई|अगस्त|सितंबर|अक्टूबर|नवंबर|दिसंबर)(?:\s*[\d०-९]{2,4})?", re.U),
    re.compile(r"[\d০-৯]{1,2}\s*(?:জানুয়ারি|ফেব্রুয়ারি|মার্চ|এপ্রিল|মে|জুন|জুলাই|আগস্ট|সেপ্টেম্বর|অক্টোবর|নভেম্বর|ডিসেম্বর)(?:\s*[\d০-৯]{2,4})?", re.U),
    # Clock times (e.g. 5 pm, 10:30 am, 5 baje, ५ बजे, ৫ টা)
    re.compile(r"\b(?:\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.)|\d{1,2}\s*baje|\d{1,2}\s*o'clock)\b", re.I),
    re.compile(r"[\d०-९]{1,2}(?::[\d०-९]{2})?\s*(?:बजे|घंटे)", re.U),
    re.compile(r"[\d०-९]{1,2}(?::[\d०-९]{2})?\s*(?:टा|ঘণ্টা)", re.U),
]

# 4. Critical Action Intents (High-risk commands where ASR error is catastrophic)
ACTION_PATTERNS = [
    re.compile(r"\b(cancel|delete|abort|stop|terminate|radd|rok|hatao|band karo)\b", re.I),
    re.compile(r"(रद्द|हटाओ|रोक|बंद करो|कैंसिल)", re.U),
    re.compile(r"(বাতিল|বন্ধ কর|মুছে ফেল)", re.U),
    re.compile(r"\b(transfer|send|pay|book|schedule|bhejo|bhej do|kar do)\b", re.I),
    re.compile(r"(भेजो|ट्रांसफर|बुक|भुगतान|पे)", re.U),
    re.compile(r"(পাঠাও|বুক|টাকা দাও)", re.U),
]

# 5. Generic Numbers (candidate identifiers, quantities, account tails)
NUMBER_PATTERN = re.compile(r"\b[\d०-९০-৯]+(?:\.[\d०-९০-৯]+)?\b")


def extract_slots(text: str) -> list[dict]:
    """Extract meaning-critical slots with type, criticality, and confirmation necessity."""
    if not text or not isinstance(text, str):
        return []

    slots = []
    seen_spans = set()

    def add_match(pattern, slot_type, criticality="high", needs_confirmation=True):
        for m in pattern.finditer(text):
            span = (m.start(), m.end())
            val = m.group(0).strip()
            if not val or span in seen_spans:
                continue
            seen_spans.add(span)
            slots.append({
                "type": slot_type,
                "value": val,
                "criticality": criticality,
                "needs_confirmation": needs_confirmation,
                "start": m.start(),
                "end": m.end()
            })

    # High-impact slots first
    for p in NEGATION_PATTERNS:
        add_match(p, "negation", criticality="high", needs_confirmation=True)

    for p in AMOUNT_PATTERNS:
        add_match(p, "amount", criticality="high", needs_confirmation=True)

    for p in DATE_TIME_PATTERNS:
        add_match(p, "date_or_time", criticality="high", needs_confirmation=True)

    for p in ACTION_PATTERNS:
        add_match(p, "critical_action", criticality="high", needs_confirmation=True)

    # Bare numbers (medium criticality if not already covered by amounts or dates)
    for m in NUMBER_PATTERN.finditer(text):
        m_start, m_end = m.start(), m.end()
        # Check overlap with existing high criticality slots
        overlapped = any(s["start"] <= m_start and m_end <= s["end"] for s in slots)
        if not overlapped:
            slots.append({
                "type": "number",
                "value": m.group(0).strip(),
                "criticality": "medium",
                "needs_confirmation": False,
                "start": m_start,
                "end": m_end
            })

    # Sort slots by appearance in text
    slots.sort(key=lambda s: s.get("start", 0))
    # Clean internal span helpers before returning
    for s in slots:
        s.pop("start", None)
        s.pop("end", None)

    return slots


def verification_decision(
    quality: dict,
    slots: list,
    asr_confidence: float | None = None,
    confidence_threshold: float | None = None
) -> dict:
    """Evaluate audio quality flags and extracted slots against a safety-first verification policy."""
    threshold = confidence_threshold if confidence_threshold is not None else config.ASR_CONFIDENCE_THRESHOLD
    reasons = []
    flags = quality.get("quality_flags", [])
    if flags:
        reasons.extend(flags)

    if asr_confidence is not None and asr_confidence < threshold:
        reasons.append(f"low_asr_confidence_{asr_confidence:.2f}")

    critical = [s for s in slots if s.get("criticality") == "high"]
    if critical:
        slot_types = sorted(list({s["type"] for s in critical}))
        reasons.append(f"critical_slots_detected({','.join(slot_types)})")

    # Policy decision matrix:
    # 1. Severely degraded audio requires re-recording.
    if any(f in flags for f in ("near_silent", "possible_clipping", "very_short_audio")):
        action = "re_record"
        recommendation_text = "Audio quality degraded. Please speak closer to the microphone and record again."
    # 2. Critical slots present or low ASR confidence require explicit confirmation.
    elif critical or (asr_confidence is not None and asr_confidence < threshold):
        action = "confirm"
        recommendation_text = "Critical information detected. Explicit user readback confirmation recommended."
    # 3. Clean audio with no critical risk items.
    else:
        action = "proceed_with_correction_option"
        recommendation_text = "Transcript clear. Safe to proceed with an option for user to correct."

    return {
        "action": action,
        "recommendation_text": recommendation_text,
        "reasons": reasons,
        "critical_slot_count": len(critical),
        "total_slot_count": len(slots),
        "policy_version": config.POLICY_VERSION
    }


def generate_confirmation_prompt(slots: list, transcript: str, language: str = None) -> str:
    """Generate a precise, natural confirmation query for Timbre TTS readback."""
    if language is None:
        language = config.DEFAULT_LANGUAGE

    critical = [s for s in slots if s.get("criticality") == "high"]
    if not critical:
        return f"Did you say: {transcript}?"

    amounts = [s["value"] for s in critical if s["type"] == "amount"]
    dates = [s["value"] for s in critical if s["type"] == "date_or_time"]
    negations = [s["value"] for s in critical if s["type"] == "negation"]
    actions = [s["value"] for s in critical if s["type"] == "critical_action"]

    parts = []
    if actions:
        parts.append(f"action '{actions[0]}'")
    if amounts:
        parts.append(f"amount '{amounts[0]}'")
    if dates:
        parts.append(f"date or time '{dates[0]}'")
    if negations:
        parts.append(f"negation '{negations[0]}'")

    details = " and ".join(parts) if parts else "your request"

    if language.startswith("hi"):
        return f"Kripya confirm karein: Kya aap {details} ke sath aage badhna chahte hain?"
    elif language.startswith("bn"):
        return f"Anugraha kore confirm korun: Apni ki {details} confirm korte chan?"
    else:
        return f"Please confirm: Did you mean to proceed with {details}?"
