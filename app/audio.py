"""Deterministic audio intake and quality features."""
import io, wave
import numpy as np
from scipy.signal import resample_poly
from . import config

class AudioError(ValueError): pass

def decode_wav(raw: bytes):
    try:
        with wave.open(io.BytesIO(raw), "rb") as w:
            channels, width, rate, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
            if channels not in (1, 2): raise AudioError("Only mono/stereo WAV is supported.")
            if width not in (1, 2, 3, 4): raise AudioError("Unsupported PCM bit depth.")
            if rate < config.AUDIO_MIN_SAMPLE_RATE or rate > config.AUDIO_MAX_SAMPLE_RATE:
                raise AudioError(f"Sample rate must be between {config.AUDIO_MIN_SAMPLE_RATE} Hz and {config.AUDIO_MAX_SAMPLE_RATE} Hz.")
            data = w.readframes(n)
    except (wave.Error, EOFError) as e:
        raise AudioError("Invalid or unsupported WAV. Convert to PCM WAV using FFmpeg.") from e
    if len(data) == 0: raise AudioError("Audio file is empty.")
    if width == 1:
        x = (np.frombuffer(data, dtype=np.uint8).astype(np.float32) - 128) / 128
    elif width == 2:
        x = np.frombuffer(data, dtype="<i2").astype(np.float32) / 32768
    elif width == 3:
        b = np.frombuffer(data, dtype=np.uint8).reshape(-1,3)
        v = b[:,0].astype(np.int32) | (b[:,1].astype(np.int32)<<8) | (b[:,2].astype(np.int32)<<16)
        v = np.where(v & 0x800000, v - 0x1000000, v)
        x = v.astype(np.float32) / 8388608
    else:
        x = np.frombuffer(data, dtype="<i4").astype(np.float32) / 2147483648
    x = x.reshape(-1, channels).mean(axis=1)
    return x, rate, {"channels": channels, "sample_width_bytes": width, "frames": n}

def quality_features(x: np.ndarray, sr: int):
    x = np.asarray(x, dtype=np.float32)
    if x.size == 0: raise AudioError("No audio samples.")
    duration = len(x) / sr
    rms = float(np.sqrt(np.mean(x * x)))
    peak = float(np.max(np.abs(x)))
    clipping = float(np.mean(np.abs(x) >= 0.999))
    frame = max(1, int(sr * 0.02))
    usable = x[:len(x) // frame * frame]
    if len(usable):
        frames = usable.reshape(-1, frame)
        frms = np.sqrt(np.mean(frames * frames, axis=1))
        threshold = max(1e-5, float(np.max(frms)) * 0.08)
        silence_ratio = float(np.mean(frms < threshold))
        sub_frames = frms[frms < np.quantile(frms, .2)]
        if len(sub_frames) > 0:
            noise_floor = float(np.median(sub_frames))
        else:
            noise_floor = float(np.min(frms))
        if np.isnan(noise_floor):
            noise_floor = 0.0
    else:
        silence_ratio, noise_floor = 1.0, 0.0

    return {
        "duration_seconds": round(duration, 3),
        "sample_rate_hz": sr,
        "rms": round(rms, 6),
        "peak": round(peak, 6),
        "clipping_fraction": round(clipping, 6),
        "silence_fraction_heuristic": round(silence_ratio, 4),
        "low_energy_floor_estimate": round(noise_floor, 7),
        "quality_flags": (
            (["very_short_audio"] if duration < config.AUDIO_MIN_DURATION else []) +
            (["very_long_audio"] if duration > config.AUDIO_MAX_DURATION else []) +
            (["near_silent"] if rms < config.AUDIO_NEAR_SILENT_RMS else []) +
            (["possible_clipping"] if clipping > config.AUDIO_CLIPPING_FRACTION else []) +
            (["high_silence_fraction"] if silence_ratio > config.AUDIO_SILENCE_RATIO else [])
        ),
        "snr_db": None,
        "snr_note": "A reliable SNR requires a calibrated noise reference."
    }

def resample(x: np.ndarray, source_sr: int, target_sr: int = None):
    if target_sr is None:
        target_sr = config.AUDIO_TARGET_SAMPLE_RATE
    if source_sr == target_sr: return x
    from math import gcd
    g = gcd(source_sr, target_sr)
    return resample_poly(x, target_sr//g, source_sr//g).astype(np.float32)
