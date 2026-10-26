from fastapi import APIRouter, Query
from ..schemas import AnalysisOut
from ..services.intent_classifier import classify
from ..services.nlp_processor import analyze_text
from ..services.semantic_similarity import similarity_to_training

router = APIRouter(prefix="/api/nlp", tags=["nlp"])

@router.get("/analyze", response_model=AnalysisOut)
def analyze(text: str = Query(min_length=1, max_length=2000)):
    data = analyze_text(text)
    intent, confidence = classify(text)
    if data["language"] not in {"en", "unknown"}:
        intent, confidence = "unknown", 0.0
    return {"original_text": text, **data, "intent": intent, "confidence": confidence, "semantic_similarity": similarity_to_training(text)}
