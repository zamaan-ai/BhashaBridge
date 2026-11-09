import base64
import pytest
from app import config, providers

class FakeResponse:
    def __init__(self, status_code=200, payload=None, text="", content=b"", headers=None):
        self.status_code = status_code
        self._payload = payload
        self.text = text
        self.content = content
        self.headers = headers or {}
    def json(self):
        if self._payload is None:
            raise ValueError("not json")
        return self._payload

class FakeClient:
    response = None
    last_call = None
    def __init__(self, *args, **kwargs): pass
    async def __aenter__(self): return self
    async def __aexit__(self, *args): return False
    async def post(self, url, **kwargs):
        FakeClient.last_call = (url, kwargs)
        return FakeClient.response

@pytest.mark.anyio
async def test_prisma_uses_current_documented_endpoint_and_multipart(monkeypatch):
    monkeypatch.setattr(config, "GNANI_API_KEY", "test-key")
    monkeypatch.setattr(config, "GNANI_PRISMA_URL", "https://api.vachana.ai/stt/v3")
    monkeypatch.setattr(config, "GNANI_PRISMA_MODEL", "prisma-v3.0")
    monkeypatch.setattr(providers.httpx, "AsyncClient", FakeClient)
    FakeClient.response = FakeResponse(payload={"success": True, "transcript": "hello", "request_id": "r1"})
    result = await providers.prisma_transcribe(b"wav", "sample.wav", "hi-en")
    url, kwargs = FakeClient.last_call
    assert url.endswith("/stt/v3")
    assert kwargs["headers"]["X-API-Key-ID"] == "test-key"
    assert "audio_file" in kwargs["files"]
    assert kwargs["data"]["format"] == "codemix"
    assert kwargs["data"]["language_code"] == "hi-IN"
    assert result["transcript"] == "hello"
    assert result["simulation"] is False

@pytest.mark.anyio
async def test_prisma_auth_failure_is_not_silent_success(monkeypatch):
    monkeypatch.setattr(config, "GNANI_API_KEY", "test-key")
    monkeypatch.setattr(config, "GNANI_PRISMA_URL", "https://api.vachana.ai/stt/v3")
    monkeypatch.setattr(providers.httpx, "AsyncClient", FakeClient)
    FakeClient.response = FakeResponse(status_code=401, text="unauthorized")
    with pytest.raises(providers.ProviderError, match="rejected the API key"):
        await providers.prisma_transcribe(b"wav", "sample.wav", "en")

def test_timbre_sse_audio_chunks_are_decoded():
    audio = b"fake-mp3-data"
    encoded = base64.b64encode(audio).decode()
    result = providers._sse_audio(f"event: audio_chunk\ndata: {encoded}\n\nevent: completed\ndata: {{}}\n")
    assert result == audio

@pytest.mark.anyio
async def test_timbre_posts_sse_request_and_returns_audio(monkeypatch):
    monkeypatch.setattr(config, "GNANI_API_KEY", "test-key")
    monkeypatch.setattr(config, "GNANI_TTS_URL", "https://api.vachana.ai/api/v1/tts/sse")
    monkeypatch.setattr(config, "GNANI_TTS_MODEL", "timbre-v3.0")
    monkeypatch.setattr(config, "GNANI_TTS_VOICE", "Shubham")
    monkeypatch.setattr(config, "GNANI_TTS_CONTAINER", "mp3")
    monkeypatch.setattr(providers.httpx, "AsyncClient", FakeClient)
    audio = b"mock-mp3-audio"
    encoded = base64.b64encode(audio).decode()
    FakeClient.response = FakeResponse(
        text=f"event: audio_chunk\ndata: {encoded}\n\nevent: completed\ndata: {{}}\n",
        headers={"content-type": "text/event-stream"},
    )
    result = await providers.timbre_synthesize("Hello", "en-IN", "Shubham")
    url, kwargs = FakeClient.last_call
    assert url.endswith("/api/v1/tts/sse")
    assert kwargs["headers"]["X-API-Key-ID"] == "test-key"
    assert kwargs["json"]["model"] == "timbre-v3.0"
    assert kwargs["json"]["voice"] == "Shubham"
    assert base64.b64decode(result["audio_base64"]) == audio
    assert result["content_type"] == "audio/mpeg"

@pytest.mark.anyio
async def test_gnani_evon_reasoning(monkeypatch):
    monkeypatch.setattr(config, "GNANI_API_KEY", "test-key")
    monkeypatch.setattr(config, "GNANI_EVON_URL", "https://api.vachana.ai/v1/chat/completions")
    monkeypatch.setattr(config, "GNANI_EVON_MODEL", "evon-v1")
    monkeypatch.setattr(providers.httpx, "AsyncClient", FakeClient)
    FakeClient.response = FakeResponse(
        payload={
            "choices": [{"message": {"content": "User wants to schedule meeting on 15 May. Please confirm date."}}]
        }
    )
    result = await providers.gnani_evon_reason("Schedule meeting on 15 May", [{"type": "date_or_time", "value": "15 May"}])
    url, kwargs = FakeClient.last_call
    assert url.endswith("/v1/chat/completions")
    assert kwargs["json"]["model"] == "evon-v1"
    assert "User wants to schedule" in result["text"]
    assert result["provider"] == "gnani_evon"
