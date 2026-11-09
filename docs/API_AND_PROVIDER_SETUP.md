# Gnani API Integration Guide

BhashaBridge connects to Gnani.ai's public APIs: **Prisma v3** for speech recognition, **Timbre v3** for voice synthesis, and **Evon** for reasoning.

## Configuration

1. Create a `.env` file from the provided template:
```bash
cp .env.example .env
nano .env
```

2. Set your private `GNANI_API_KEY`:
```ini
GNANI_API_KEY=your_gnani_api_key_here
```

Default endpoint configurations:

| Parameter | Default Value | Notes |
|---|---|---|
| Prisma REST STT | `https://api.vachana.ai/stt/v3` | Multipart audio field: `audio_file` |
| Prisma Output Format | `codemix` | Supports Hinglish & Benglish |
| Prisma Auth Header | `X-API-Key-ID` | Standard Gnani header |
| Timbre SSE TTS | `https://api.vachana.ai/api/v1/tts/sse` | Event stream audio delivery |
| Timbre Model | `timbre-v3.0` (default; confirm model access with your Gnani account) | Default voice: `Shubham` |
| Evon Reasoning LLM | `https://api.vachana.ai/v1/chat/completions` | Indic reasoning model |

## Prisma Speech-to-Text (`/api/analyze`)

When an audio sample is uploaded or recorded via live mic:
- Encoded as 16kHz PCM WAV.
- Posted to Gnani Prisma with language code mapping (`hi-IN`, `bn-IN`, `en-IN`) and `format=codemix`.
- Returns the transcription and provider response fields available from the configured service; do not assume a confidence score is always returned.

## Timbre Text-to-Speech (`/api/synthesize`)

Used to close the voice loop by speaking readback confirmations:
- Sends text and voice ID to `/api/v1/tts/sse`.
- Reconstructs SSE chunk events into an MP3 buffer for playback.
- Default voice: `Shubham`. Other voice IDs depend on the models and entitlements enabled for your Gnani account.

## Local Development & Testing

Run the server locally:
```bash
./run.sh
```
Open `http://127.0.0.1:8000`. You can test with live mic audio, pre-recorded WAV files, or test the semantic verification engine using the manual transcript override without consuming API credits.


**Credential safety:** Keep the API key only in `.env`. Never paste it into source code, screenshots, issue trackers, or public repositories. If a key has been exposed, revoke it with the provider and issue a replacement.
