"""Train the reproducible intent classifier and report held-out metrics."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from app.services.intent_classifier import training_examples, train_and_save
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

texts, labels, _ = training_examples()
train_x, test_x, train_y, test_y = train_test_split(texts, labels, test_size=0.25, random_state=42, stratify=labels)
evaluation = Pipeline([("tfidf", TfidfVectorizer(ngram_range=(1,2))), ("classifier", LogisticRegression(max_iter=1500, random_state=42, C=3.0))])
evaluation.fit(train_x, train_y)
print(classification_report(test_y, evaluation.predict(test_x), zero_division=0))
train_and_save()
print("Saved model to app/models/intent_classifier.joblib")
