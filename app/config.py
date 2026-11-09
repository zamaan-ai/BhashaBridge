"""Environment-backed configuration for BhashaBridge."""
import os
from dotenv import load_dotenv

load_dotenv()

def env(name: str, default: str = "") -> str:
    return os.getenv(name, default)

APP_NAME = env("APP_NAME", "BhashaBridge")
APP_ENV = env("APP_ENV", "development")
APP_VERSION = env("APP_VERSION", "0.3.1")
APP_DESCRIPTION = env(
    "APP_DESCRIPTION",
    "Reliability-Aware Meaning Preservation for Code-Mixed Indian Voice Interfaces."
)
DATA_DIR = env("DATA_DIR", "./data")
MAX_UPLOAD_MB = int(env("MAX_UPLOAD_MB", "20"))
MAX_OVERRIDE_CHARS = int(env("MAX_OVERRIDE_CHARS", "12000"))
DEFAULT_LANGUAGE = env("DEFAULT_LANGUAGE", "hi-en")

# ASR & Verification thresholds
ASR_CONFIDENCE_THRESHOLD = float(env("ASR_CONFIDENCE_THRESHOLD", "0.75"))
POLICY_VERSION = env("POLICY_VERSION", f"bb-verification-{APP_VERSION}")

# Audio quality gate thresholds
AUDIO_MIN_DURATION = float(env("AUDIO_MIN_DURATION", "0.7"))
AUDIO_MAX_DURATION = float(env("AUDIO_MAX_DURATION", "120.0"))
AUDIO_NEAR_SILENT_RMS = float(env("AUDIO_NEAR_SILENT_RMS", "0.003"))
AUDIO_CLIPPING_FRACTION = float(env("AUDIO_CLIPPING_FRACTION", "0.005"))
AUDIO_SILENCE_RATIO = float(env("AUDIO_SILENCE_RATIO", "0.75"))
AUDIO_MIN_SAMPLE_RATE = int(env("AUDIO_MIN_SAMPLE_RATE", "8000"))
AUDIO_MAX_SAMPLE_RATE = int(env("AUDIO_MAX_SAMPLE_RATE", "96000"))
AUDIO_TARGET_SAMPLE_RATE = int(env("AUDIO_TARGET_SAMPLE_RATE", "16000"))

# Gnani Prisma v3 REST interface (Speech-to-Text)
GNANI_API_KEY = env("GNANI_API_KEY")
GNANI_PRISMA_URL = env("GNANI_PRISMA_URL", "https://api.vachana.ai/stt/v3")
GNANI_PRISMA_MODEL = env("GNANI_PRISMA_MODEL", "prisma-v3.0")
GNANI_PRISMA_FORMAT = env("GNANI_PRISMA_FORMAT", "codemix")
GNANI_AUTH_HEADER = env("GNANI_AUTH_HEADER", "X-API-Key-ID")
GNANI_AUTH_SCHEME = env("GNANI_AUTH_SCHEME", "")
GNANI_HTTP_TIMEOUT = int(env("GNANI_HTTP_TIMEOUT", "90"))

# Gnani Timbre v3 SSE interface (Text-to-Speech)
GNANI_TTS_URL = env("GNANI_TTS_URL", "https://api.vachana.ai/api/v1/tts/sse")
GNANI_TTS_MODEL = env("GNANI_TTS_MODEL", "timbre-v3.0")
GNANI_TTS_VOICE = env("GNANI_TTS_VOICE", "Shubham")
GNANI_TTS_CONTAINER = env("GNANI_TTS_CONTAINER", "mp3")
GNANI_TTS_SAMPLE_RATE = int(env("GNANI_TTS_SAMPLE_RATE", "44100"))
GNANI_TTS_BITRATE = env("GNANI_TTS_BITRATE", "192k")
GNANI_TTS_SAMPLE_WIDTH = int(env("GNANI_TTS_SAMPLE_WIDTH", "2"))
GNANI_TTS_NUM_CHANNELS = int(env("GNANI_TTS_NUM_CHANNELS", "1"))
GNANI_TTS_TIMEOUT = int(env("GNANI_TTS_TIMEOUT", "120"))

# Gnani Evon LLM / Reasoning interface
GNANI_EVON_URL = env("GNANI_EVON_URL", "https://api.vachana.ai/v1/chat/completions")
GNANI_EVON_MODEL = env("GNANI_EVON_MODEL", "evon-v1")
GNANI_EVON_TEMPERATURE = float(env("GNANI_EVON_TEMPERATURE", "0.2"))
GNANI_EVON_MAX_TOKENS = int(env("GNANI_EVON_MAX_TOKENS", "250"))
GNANI_EVON_TIMEOUT = int(env("GNANI_EVON_TIMEOUT", "45"))

# Optional local reasoning provider fallback (Ollama)
OLLAMA_URL = env("OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = env("OLLAMA_MODEL", "llama3.2:latest")
OLLAMA_TIMEOUT = int(env("OLLAMA_TIMEOUT", "60"))
