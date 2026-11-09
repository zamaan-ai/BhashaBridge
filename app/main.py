from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json, uuid, os
from . import config
from .audio import decode_wav, quality_features, resample, AudioError
from .semantics import extract_slots, verification_decision, generate_confirmation_prompt
from .providers import (
    prisma_transcribe, timbre_synthesize, gnani_evon_reason, ollama_reason, reason_transcript,
    ProviderNotConfigured, ProviderError
)

app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description=config.APP_DESCRIPTION
)
ROOT = Path(__file__).parent
app.mount("/static", StaticFiles(directory=ROOT/"static"), name="static")
Path(config.DATA_DIR).mkdir(parents=True, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home():
    return (ROOT/"static"/"index.html").read_text(encoding="utf-8")

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": config.APP_VERSION,
        "providers": {
            "prisma_configured": bool(config.GNANI_PRISMA_URL and config.GNANI_API_KEY),
            "timbre_configured": bool(config.GNANI_TTS_URL and config.GNANI_API_KEY),
            "evon_configured": bool(config.GNANI_EVON_URL and config.GNANI_API_KEY),
            "ollama_configured": bool(config.OLLAMA_URL)
        },
        "gnani_ecosystem": {
            "prisma_stt": bool(config.GNANI_PRISMA_URL and config.GNANI_API_KEY),
            "timbre_tts": bool(config.GNANI_TTS_URL and config.GNANI_API_KEY),
            "evon_reasoning": bool(config.GNANI_EVON_URL and config.GNANI_API_KEY),
        },
        "local_fallback": {
            "ollama_configured": bool(config.OLLAMA_URL)
        },
        "simulation_mode": False
    }

@app.post("/api/analyze")
async def analyze(
    file: UploadFile = File(...),
    language: str = Form(config.DEFAULT_LANGUAGE),
    transcript_override: str = Form(""),
    auto_generate_speech: bool = Form(False)
):
    limit = config.MAX_UPLOAD_MB * 1024 * 1024
    raw = await file.read(limit + 1)
    if len(raw) > limit:
        raise HTTPException(413, f"Maximum upload is {config.MAX_UPLOAD_MB} MB.")
    if not raw:
        raise HTTPException(400, "Empty upload.")
    if len(transcript_override) > config.MAX_OVERRIDE_CHARS:
        raise HTTPException(413, f"Transcript override exceeds {config.MAX_OVERRIDE_CHARS} characters.")

    try:
        x, sr, meta = decode_wav(raw)
    except AudioError as e:
        raise HTTPException(415, str(e))

    quality = quality_features(x, sr)

    if transcript_override.strip():
        transcript = transcript_override.strip()
        asr = {
            "provider": "user_supplied",
            "model": "manual_transcript",
            "transcript": transcript,
            "asr_confidence": None,
            "simulation": False
        }
    else:
        try:
            asr = await prisma_transcribe(raw, file.filename or "audio.wav", language)
        except ProviderNotConfigured as e:
            raise HTTPException(503, str(e))
        except ProviderError as e:
            raise HTTPException(502, str(e))
        transcript = asr["transcript"]

    slots = extract_slots(transcript)
    decision = verification_decision(quality, slots, asr.get("asr_confidence"))
    readback = generate_confirmation_prompt(slots, transcript, language)
    decision["readback_prompt"] = readback

    confirmation_audio = None
    if auto_generate_speech and decision["action"] == "confirm":
        try:
            confirmation_audio = await timbre_synthesize(readback, language=language)
        except Exception:
            confirmation_audio = None

    return {
        "request_id": str(uuid.uuid4()),
        "audio_metadata": meta,
        "audio_quality": quality,
        "asr": asr,
        "semantic_slots": slots,
        "verification": decision,
        "confirmation_audio": confirmation_audio,
        "notice": "Reliability-aware speech quality and semantic verification layer."
    }

@app.post("/api/reason")
async def reason(payload: dict):
    transcript = str(payload.get("transcript", "")).strip()
    if not transcript:
        raise HTTPException(400, "transcript is required")
    language = str(payload.get("language", config.DEFAULT_LANGUAGE))
    slots = extract_slots(transcript)
    result = await reason_transcript(transcript, slots, language=language, prefer_provider=payload.get("provider", "auto"))
    return {
        "semantic_slots": slots,
        "reasoning": result,
        "notice": "Sovereign Indic reasoning layer for intent auditing. Always confirm high-stakes actions."
    }

@app.post("/api/synthesize")
async def synthesize(payload: dict):
    text = str(payload.get("text", "")).strip()
    language = str(payload.get("language", config.DEFAULT_LANGUAGE.split("-")[0]))
    if not text:
        raise HTTPException(400, "text is required")
    voice = str(payload.get("voice", "")).strip() or config.GNANI_TTS_VOICE
    try:
        return await timbre_synthesize(text, language, voice)
    except ProviderNotConfigured as e:
        raise HTTPException(503, str(e))
    except ProviderError as e:
        raise HTTPException(502, str(e))

@app.get("/api/benchmark")
async def get_benchmark_results():
    """Return metrics calculated from the supplied annotated CSV only.

    The bundled rows are illustrative examples, not an empirical audio study.
    Outcome metrics such as avoided action inversions are not measured here.
    """
    csv_path = Path(config.DATA_DIR) / "benchmark_samples.csv"
    if not csv_path.exists():
        csv_path = Path(config.DATA_DIR) / "evaluation_template.csv"

    samples = []
    scores = {}
    if csv_path.exists():
        import csv
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as handle:
            samples = list(csv.DictReader(handle))
        try:
            from research.evaluate import score
            scores = score(csv_path)
        except (ValueError, OSError, KeyError) as exc:
            scores = {"error": str(exc)}

    negation = scores.get("slot_metrics_by_type", {}).get("negation", {})
    wer = scores.get("WER")
    mcsp = scores.get("MCSP")
    neg_recall = negation.get("recall")

    return {
        "total_test_samples": len(samples),
        "dataset_status": "illustrative_synthetic_examples",
        "scores": scores,
        "metrics_summary": {
            "wer": round(wer * 100, 2) if wer is not None else None,
            "raw_negation_recall": round(neg_recall * 100, 2) if neg_recall is not None else None,
            "bhashabridge_mcsp": round(mcsp * 100, 2) if mcsp is not None else None,
            "avoided_inversions": None,
        },
        "sample_preview": samples,
    }
