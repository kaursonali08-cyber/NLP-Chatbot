import json
from functools import lru_cache
from pathlib import Path
from joblib import dump, load
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "intent_classifier.joblib"
DATA_PATH = ROOT / "data" / "intents.json"


def training_examples():
    intents = json.loads(DATA_PATH.read_text())
    texts, labels = [], []
    for item in intents:
        texts.extend(item["patterns"]); labels.extend([item["tag"]] * len(item["patterns"]))
    return texts, labels, intents


def train_and_save():
    texts, labels, _ = training_examples()
    pipeline = Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)), ("classifier", LogisticRegression(max_iter=1500, random_state=42, C=3.0))])
    pipeline.fit(texts, labels)
    MODEL_PATH.parent.mkdir(exist_ok=True)
    dump(pipeline, MODEL_PATH)
    return pipeline


@lru_cache
def get_classifier():
    return load(MODEL_PATH) if MODEL_PATH.exists() else train_and_save()


def classify(text: str) -> tuple[str, float]:
    model = get_classifier()
    probabilities = model.predict_proba([text])[0]
    best = probabilities.argmax()
    return str(model.classes_[best]), float(probabilities[best])


@lru_cache
def response_map():
    _, _, intents = training_examples()
    return {item["tag"]: item["responses"] for item in intents}
