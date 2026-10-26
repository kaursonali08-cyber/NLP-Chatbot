from app.services.intent_classifier import classify
from app.services.nlp_processor import analyze_text

def test_greeting_intent():
    intent, confidence = classify("hello there")
    assert intent == "greeting" and 0 <= confidence <= 1

def test_preprocessing_preserves_negation():
    result = analyze_text("I do not understand Python")
    assert "not" in result["content_tokens"]

def test_language_is_reported_when_detector_is_available():
    result = analyze_text("¿Qué es la inteligencia artificial?")
    assert result["language"] != "en"
