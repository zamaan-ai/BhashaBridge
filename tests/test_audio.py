import io,wave,numpy as np
from app.audio import decode_wav,quality_features

def wav_bytes():
    x=(np.sin(np.arange(16000)*2*np.pi*220/16000)*10000).astype("<i2")
    b=io.BytesIO()
    with wave.open(b,"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000);w.writeframes(x.tobytes())
    return b.getvalue()

def test_decode_and_quality():
    x,sr,m=decode_wav(wav_bytes())
    q=quality_features(x,sr)
    assert sr==16000 and m["channels"]==1
    assert .9<q["duration_seconds"]<1.1
    assert q["snr_db"] is None
