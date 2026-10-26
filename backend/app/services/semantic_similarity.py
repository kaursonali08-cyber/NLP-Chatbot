"""Sentence-Transformer similarity with a deterministic TF-IDF offline fallback."""
import os
from functools import lru_cache
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .intent_classifier import training_examples


@lru_cache
def _sentence_model():
    """Load a cached embedding model without downloading during a chat request."""
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(os.getenv("SENTENCE_TRANSFORMER_MODEL", "paraphrase-multilingual-MiniLM-L12-v2"), local_files_only=True)
    except Exception:
        return None


def similarity_to_training(text: str) -> float:
    examples, _, _ = training_examples()
    model = _sentence_model()
    if model is not None:
        vectors = model.encode(examples + [text], normalize_embeddings=True)
        return float(max(vectors[-1] @ vector for vector in vectors[:-1]))
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(examples + [text])
    if matrix.shape[0] < 2: return 0.0
    return float(cosine_similarity(matrix[-1], matrix[:-1]).max())
