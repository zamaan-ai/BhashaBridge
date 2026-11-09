import io
import wave
import numpy as np
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def wav_bytes(seconds=1.0, amplitude=0.08, sr=16000):
    samples = (np.sin(2 * np.pi * 440 * np.arange(int(seconds * sr)) / sr) * amplitude)
    pcm = (samples * 32767).astype('<i2').tobytes()
    out = io.BytesIO()
    with wave.open(out, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm)
    return out.getvalue()

def test_health_is_explicit_about_provider_configuration():
    response = client.get('/api/health')
    assert response.status_code == 200
    body = response.json()
    assert body['status'] == 'ok'
    assert body['simulation_mode'] is False
    assert 'providers' in body
    assert 'gnani_ecosystem' in body

def test_manual_transcript_analysis_returns_verification():
    response = client.post('/api/analyze', files={'file': ('sample.wav', wav_bytes(), 'audio/wav')},
                           data={'language': 'hi-en', 'transcript_override': "Please don't cancel the meeting on 15 May."})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body['asr']['provider'] == 'user_supplied'
    assert body['verification']['action'] == 'confirm'
    assert 'readback_prompt' in body['verification']
    assert any(slot['type'] == 'negation' for slot in body['semantic_slots'])
    assert any(slot['type'] == 'date_or_time' for slot in body['semantic_slots'])

def test_invalid_audio_is_rejected():
    response = client.post('/api/analyze', files={'file': ('bad.wav', b'not wav', 'audio/wav')},
                           data={'transcript_override': 'hello'})
    assert response.status_code == 415

def test_empty_upload_is_rejected():
    response = client.post('/api/analyze', files={'file': ('empty.wav', b'', 'audio/wav')},
                           data={'transcript_override': 'hello'})
    assert response.status_code == 400

def test_benchmark_endpoint_returns_metrics():
    response = client.get('/api/benchmark')
    assert response.status_code == 200
    data = response.json()
    assert 'metrics_summary' in data
    assert 'total_test_samples' in data
    assert data['total_test_samples'] >= 1
    assert data['dataset_status'] == 'illustrative_synthetic_examples'
    assert data['metrics_summary']['bhashabridge_mcsp'] == 86.79
    assert data['metrics_summary']['avoided_inversions'] is None
