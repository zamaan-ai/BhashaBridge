from app.semantics import extract_slots, verification_decision, generate_confirmation_prompt

def test_negation_is_critical():
    s = extract_slots("Do not book on 15 May")
    assert any(x["type"] == "negation" for x in s)
    assert any(x["type"] == "date_or_time" for x in s)
    assert any(x["type"] == "critical_action" for x in s)

def test_amount_detected():
    assert any(x["type"] == "amount" for x in extract_slots("Pay ₹500"))
    assert any(x["type"] == "amount" for x in extract_slots("1500 rupees"))
    assert any(x["type"] == "amount" for x in extract_slots("१५०० रुपये"))
    assert any(x["type"] == "amount" for x in extract_slots("১০০০ টাকা"))

def test_devanagari_and_bengali_support():
    hi_slots = extract_slots("आज मेरा ऑर्डर रद्द मत करो और ₹५०० भेजो")
    assert any(x["type"] == "negation" for x in hi_slots)
    assert any(x["type"] == "critical_action" for x in hi_slots)
    assert any(x["type"] == "amount" for x in hi_slots)

    bn_slots = extract_slots("কাল ১০০০ টাকা পাঠাও না")
    assert any(x["type"] == "date_or_time" for x in bn_slots)
    assert any(x["type"] == "amount" for x in bn_slots)
    assert any(x["type"] == "negation" for x in bn_slots)

def test_confirmation_for_critical_slot():
    d = verification_decision({"quality_flags": []}, extract_slots("Book on 15 May"))
    assert d["action"] == "confirm"
    assert "critical_slots_detected" in d["reasons"][0]

def test_bad_audio_requests_rerecord():
    d = verification_decision({"quality_flags": ["near_silent"]}, [])
    assert d["action"] == "re_record"

def test_confirmation_prompt_generation():
    slots = extract_slots("Transfer ₹500 on 15 May")
    prompt = generate_confirmation_prompt(slots, "Transfer ₹500 on 15 May", language="hi-en")
    assert "confirm" in prompt.lower()
    assert "500" in prompt or "15 May" in prompt
