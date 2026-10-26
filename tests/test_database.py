from unittest.mock import AsyncMock, patch

def test_conversation_persistence_and_deletion(client, session_id):
    with patch("app.services.chatbot.generate_ollama", new=AsyncMock(return_value=None)):
        created=client.post("/api/chat",json={"session_id":session_id,"message":"Hello"}).json()["conversation_id"]
    conversations=client.get("/api/conversations",params={"session_id":session_id}).json()
    assert conversations[0]["id"]==created
    detail=client.get(f"/api/conversations/{created}",params={"session_id":session_id})
    assert len(detail.json()["messages"])==2
    assert client.delete(f"/api/conversations/{created}",params={"session_id":session_id}).status_code==204

def test_session_isolation(client, session_id):
    item=client.post("/api/conversations",json={"session_id":session_id,"title":"Private"}).json()
    denied=client.get(f"/api/conversations/{item['id']}",params={"session_id":"another-valid-session-id-99"})
    assert denied.status_code==404
