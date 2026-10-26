import re
from functools import lru_cache

try:
    import spacy
except ImportError:  # keeps a clear fallback for initial setup
    spacy = None


@lru_cache
def get_nlp(language: str = "en"):
    if not spacy: return None
    if language == "en":
        try: return spacy.load("en_core_web_sm")
        except OSError: return spacy.blank("en")
    # `xx` provides language-neutral Unicode tokenization. Add a language-specific
    # spaCy package later if production-grade non-English NER is required.
    return spacy.blank("xx")


def detect_language(text: str) -> str:
    """Return an ISO 639-1 language code, falling back safely to `unknown`."""
    # Statistical language classifiers are unreliable for one or two short Latin
    # words (for example, “Hello” can be classified as Finnish). Keep the
    # English intent flow usable for these common chat openers.
    compact = text.strip()
    if compact.isascii() and len(compact) <= 16:
        return "en"
    try:
        from langdetect import DetectorFactory, detect
        DetectorFactory.seed = 0  # deterministic language detection
        return detect(text) if len(text.strip()) >= 3 else "unknown"
    except Exception:
        return "unknown"


def analyze_text(text: str, language: str | None = None) -> dict:
    language = language or detect_language(text)
    nlp = get_nlp(language)
    if nlp is None:
        tokens = re.findall(r"\b\w+[\w'-]*\b|[^\w\s]", text)
        return {"language": language, "tokens": tokens, "lemmas": [t.lower() for t in tokens], "content_tokens": [t.lower() for t in tokens if t.isalpha()], "entities": []}
    doc = nlp(text)
    tokens = [t.text for t in doc]
    lemmas = [t.lemma_.lower() if t.lemma_ else t.text.lower() for t in doc]
    # Retain negation and question terms: indiscriminate stopword removal changes meaning.
    content = [(t.lemma_ or t.text).lower() for t in doc if t.is_alpha and (not t.is_stop or t.lower_ in {"not", "no", "why", "how", "what"})]
    return {"language": language, "tokens": tokens, "lemmas": lemmas, "content_tokens": content, "entities": [{"text": e.text, "label": e.label_} for e in doc.ents]}
