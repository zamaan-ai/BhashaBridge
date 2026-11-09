"""Gnani Prisma (STT), Timbre (TTS), and Evon (Reasoning LLM) client adapters."""
import base64
import json
import httpx
from . import config

class ProviderNotConfigured(RuntimeError):
    pass

class ProviderError(RuntimeError):
    pass


def _headers(extra=None):
    if not config.GNANI_API_KEY:
        raise ProviderNotConfigured("GNANI_API_KEY is missing. Add your private key to the local .env file.")
    headers = {config.GNANI_AUTH_HEADER: config.GNANI_API_KEY, "Accept": "application/json"}
    if extra:
        headers.update(extra)
    return headers


def _prisma_language(language: str) -> tuple[str, str]:
    """Map dashboard language choices to documented BCP-47 locale fields."""
    mapping = {
        "hi-en": ("hi-IN", "en-IN"),
        "bn-en": ("bn-IN", "en-IN"),
        "hi": ("hi-IN", "hi-IN"),
        "bn": ("bn-IN", "bn-IN"),
        "en": ("en-IN", "en-IN"),
        "indic-auto": ("hi-IN", "en-IN"),
    }
    return mapping.get(language, ("hi-IN", "en-IN"))


async def prisma_transcribe(audio_bytes: bytes, filename: str, language: str = None):
    """Transcribe audio using Gnani Prisma v3 REST API with code-mix support."""
    if not config.GNANI_PRISMA_URL:
        raise ProviderNotConfigured("GNANI_PRISMA_URL is not configured.")
    if language is None:
        language = config.DEFAULT_LANGUAGE
    language_code, preferred_language = _prisma_language(language)
    files = {"audio_file": (filename or "audio.wav", audio_bytes, "audio/wav")}
    data = {
        "language_code": language_code,
        "preferred_language": preferred_language,
        "format": config.GNANI_PRISMA_FORMAT,
    }
    async with httpx.AsyncClient(timeout=config.GNANI_HTTP_TIMEOUT) as client:
        try:
            response = await client.post(config.GNANI_PRISMA_URL, headers=_headers(), files=files, data=data)
        except httpx.HTTPError as exc:
            raise ProviderError(f"Prisma network error: {exc}") from exc
    if response.status_code >= 400:
        detail = response.text[:500]
        if response.status_code in (401, 403):
            detail = "Gnani rejected the API key or its permissions. Check the key in your Gnani dashboard."
        elif response.status_code == 429:
            detail = "Gnani rate limit or credit limit reached. Check your account usage."
        raise ProviderError(f"Prisma returned HTTP {response.status_code}: {detail}")
    try:
        result = response.json()
    except ValueError as exc:
        raise ProviderError("Prisma returned a non-JSON response; expected a JSON transcript.") from exc
    transcript = result.get("transcript") or result.get("text")
    if not isinstance(transcript, str) or not transcript.strip():
        raise ProviderError(f"Prisma response did not contain a transcript. Returned keys: {list(result.keys())}")
    return {
        "provider": "gnani_prisma",
        "model": config.GNANI_PRISMA_MODEL,
        "transcript": transcript.strip(),
        "asr_confidence": result.get("confidence"),
        "simulation": False,
        "request_id": result.get("request_id"),
        "detected_language": result.get("detected_language_code") or result.get("language_code"),
    }


def _sse_audio(response_text: str) -> bytes:
    """Collect audio from Gnani Timbre SSE events."""
    chunks = []
    event_name = ""
    data_lines = []

    def process_event(name, data):
        if not data:
            return []

        if name == "error":
            raise ProviderError(
                f"Timbre synthesis failed: {data[:400]}"
            )

        if name not in ("chunk", "audio_chunk"):
            return []

        # Newer Timbre format: JSON containing Base64 audio.
        try:
            body = json.loads(data)
        except (ValueError, TypeError):
            body = None

        if isinstance(body, dict):
            encoded = (
                body.get("audio")
                or body.get("audio_base64")
            )
        else:
            # Older format: raw Base64 in audio_chunk.
            encoded = data

        if not isinstance(encoded, str) or not encoded.strip():
            return []

        try:
            decoded = base64.b64decode(
                encoded.strip(), validate=True
            )
        except Exception as exc:
            raise ProviderError(
                "Timbre returned an invalid Base64 audio chunk."
            ) from exc

        return [decoded] if decoded else []

    for raw_line in response_text.splitlines():
        line = raw_line.strip()

        if not line:
            chunks.extend(process_event(
                event_name, "\n".join(data_lines)
            ))
            event_name = ""
            data_lines = []
            continue

        if line.startswith("event:"):
            event_name = line[6:].strip()
        elif line.startswith("data:"):
            data_lines.append(line[5:].strip())

    # Process a final event even if the response has no trailing blank line.
    chunks.extend(process_event(
        event_name, "\n".join(data_lines)
    ))

    if not chunks:
        raise ProviderError(
            "Timbre SSE response contained no audio chunks. "
            "Check the returned event format."
        )

    return b"".join(chunks)


async def timbre_synthesize(text: str, language: str = None, voice: str | None = None):
    """Synthesize speech using Gnani Timbre v3 SSE API."""
    if not config.GNANI_TTS_URL or not config.GNANI_TTS_MODEL:
        raise ProviderNotConfigured("Configure GNANI_TTS_URL and GNANI_TTS_MODEL in .env.")
    payload = {
        "audio_config": {
            "bitrate": config.GNANI_TTS_BITRATE,
            "container": config.GNANI_TTS_CONTAINER,
            "encoding": "linear_pcm",
            "num_channels": config.GNANI_TTS_NUM_CHANNELS,
            "sample_rate": config.GNANI_TTS_SAMPLE_RATE,
            "sample_width": config.GNANI_TTS_SAMPLE_WIDTH,
        },
        "model": config.GNANI_TTS_MODEL,
        "text": text,
        "voice": voice or config.GNANI_TTS_VOICE,
    }
    async with httpx.AsyncClient(timeout=config.GNANI_TTS_TIMEOUT) as client:
        try:
            response = await client.post(
                config.GNANI_TTS_URL,
                headers=_headers({"Content-Type": "application/json", "Accept": "text/event-stream, audio/*, application/json"}),
                json=payload,
            )
        except httpx.HTTPError as exc:
            raise ProviderError(f"Timbre network error: {exc}") from exc
    if response.status_code >= 400:
        detail = response.text[:500]
        if response.status_code in (401, 403):
            detail = "Gnani rejected the API key or its permissions. Check your dashboard."
        elif response.status_code == 429:
            detail = "Gnani rate limit or credit limit reached. Check your account usage."
        raise ProviderError(f"Timbre returned HTTP {response.status_code}: {detail}")

    content_type = response.headers.get("content-type", "").lower()
    if "text/event-stream" in content_type or "event:" in response.text[:300]:
        audio = _sse_audio(response.text)
    elif content_type.startswith("audio/") or "octet-stream" in content_type:
        audio = response.content
    else:
        # Gateway wrapped base64 audio in JSON
        try:
            body = response.json()
        except ValueError as exc:
            raise ProviderError(f"Unrecognized Timbre response content type: {content_type or 'unknown'}") from exc
        encoded = body.get("audio_base64") or body.get("audio")
        if not isinstance(encoded, str):
            raise ProviderError(f"Timbre JSON did not contain audio_base64. Returned keys: {list(body.keys())}")
        try:
            audio = base64.b64decode(encoded)
        except Exception as exc:
            raise ProviderError("Timbre JSON audio field was not valid base64.") from exc
        content_type = body.get("content_type", "audio/mpeg")

    if not audio:
        raise ProviderError("Timbre returned an empty audio payload.")
    return {
        "provider": "gnani_timbre",
        "model": config.GNANI_TTS_MODEL,
        "voice": voice or config.GNANI_TTS_VOICE,
        "audio_base64": base64.b64encode(audio).decode("ascii"),
        "content_type": "audio/mpeg" if config.GNANI_TTS_CONTAINER == "mp3" else content_type or "audio/wav",
        "simulation": False,
    }


async def gnani_evon_reason(transcript: str, slots: list, language: str = None):
    """Reason about intent and verification using Gnani Evon sovereign LLM."""
    if not config.GNANI_API_KEY:
        raise ProviderNotConfigured("GNANI_API_KEY is not configured.")
    if language is None:
        language = config.DEFAULT_LANGUAGE
    url = config.GNANI_EVON_URL
    prompt = (
        "You are Gnani Evon, a sovereign Indic language reasoning model. "
        "Analyze the user's voice transcript and extracted semantic slots. "
        "1. Identify the core user intent. "
        "2. Detect any critical ambiguity, negation conflicts, date/amount mismatches. "
        "3. Provide a clear, polite 1-sentence confirmation prompt in natural Hinglish/English for the user.\n\n"
        f"Transcript: {transcript}\n"
        f"Detected Slots: {json.dumps(slots, ensure_ascii=False)}"
    )
    headers = {
        config.GNANI_AUTH_HEADER: config.GNANI_API_KEY,
        "Authorization": f"Bearer {config.GNANI_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "model": config.GNANI_EVON_MODEL,
        "messages": [
            {"role": "system", "content": "You are Gnani Evon, an Indic voice interaction verification assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": config.GNANI_EVON_TEMPERATURE,
        "max_tokens": config.GNANI_EVON_MAX_TOKENS
    }
    async with httpx.AsyncClient(timeout=config.GNANI_EVON_TIMEOUT) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
        except httpx.HTTPError as exc:
            raise ProviderError(f"Gnani Evon network error: {exc}") from exc

    if response.status_code >= 400:
        detail = response.text[:400]
        raise ProviderError(f"Gnani Evon returned HTTP {response.status_code}: {detail}")

    try:
        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as exc:
        raise ProviderError(f"Failed to parse Gnani Evon response: {exc}") from exc

    if not content:
        raise ProviderError("Gnani Evon returned an empty completion.")

    return {
        "provider": "gnani_evon",
        "model": config.GNANI_EVON_MODEL,
        "text": content.strip(),
        "simulation": False
    }


async def ollama_reason(transcript: str, slots: list):
    """Optional local Ollama reasoning fallback."""
    url = config.OLLAMA_URL.rstrip("/") + "/api/chat"
    prompt = (
        "You are a language-understanding component for an Indian voice interface. "
        "Summarize the user's intent without inventing missing facts. Preserve negation, dates, amounts and names. "
        "If a critical detail is ambiguous, formulate a concise readback confirmation. Return concise plain text.\n"
        f"Transcript: {transcript}\nCandidate slots: {json.dumps(slots, ensure_ascii=False)}"
    )
    async with httpx.AsyncClient(timeout=config.OLLAMA_TIMEOUT) as client:
        try:
            response = await client.post(url, json={"model": config.OLLAMA_MODEL, "stream": False,
                "messages": [{"role": "user", "content": prompt}]})
        except httpx.HTTPError as exc:
            raise ProviderError(f"Ollama unavailable: {exc}") from exc
    if response.status_code >= 400:
        raise ProviderError(f"Ollama returned HTTP {response.status_code}: {response.text[:300]}")
    data = response.json()
    return {"provider": "ollama", "model": config.OLLAMA_MODEL,
            "text": data.get("message", {}).get("content", ""), "simulation": False}


async def reason_transcript(transcript: str, slots: list, language: str = None, prefer_provider: str = "auto"):
    """Route reasoning through Gnani Evon first, with fallback to Ollama or rule-based verification."""
    if language is None:
        language = config.DEFAULT_LANGUAGE
    errors = []
    # 1. Try Gnani Evon if auto or explicitly requested
    if prefer_provider in ("auto", "evon", "gnani"):
        try:
            return await gnani_evon_reason(transcript, slots, language)
        except Exception as e:
            errors.append(f"Evon: {e}")

    # 2. Try Ollama fallback
    if prefer_provider in ("auto", "ollama"):
        try:
            return await ollama_reason(transcript, slots)
        except Exception as e:
            errors.append(f"Ollama: {e}")

    # 3. Rule-based fallback summary when no remote reasoning provider is reachable
    from .semantics import generate_confirmation_prompt
    readback = generate_confirmation_prompt(slots, transcript, language)
    return {
        "provider": "rule_based_fallback",
        "model": f"{config.APP_NAME.lower()}-intent-eval-{config.APP_VERSION}",
        "text": f"Intent Analysis: Identified {len(slots)} semantic slots. Recommended Readback: \"{readback}\"",
        "readback_prompt": readback,
        "diagnostics": errors,
        "simulation": False
    }
