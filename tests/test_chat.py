from unittest.mock import AsyncMock, patch

def test_chat_and_validation(client, session_id):
    with patch("app.services.chatbot.generate_ollama", new=AsyncMock(return_value=None)):
        response = client.post("/api/chat", json={"session_id":session_id,"message":"Hello"})
    assert response.status_code == 200
    body=response.json(); assert body["intent"] == "greeting"; assert body["response_source"] == "intent_fallback"
    invalid=client.post("/api/chat", json={"session_id":session_id,"message":" "})
    assert invalid.status_code == 422

def test_unavailable_model_is_transparent(client, session_id):
    with patch("app.services.chatbot.generate_ollama", new=AsyncMock(return_value=None)):
        response=client.post("/api/chat",json={"session_id":session_id,"message":"What is quantum entanglement?"})
    assert response.status_code==200
    assert response.json()["response_source"] in {"intent_fallback","model_unavailable"}
