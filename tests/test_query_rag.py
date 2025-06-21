import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
def test_query_endpoint(rag_client):
    payload = {"query": "what is the document about?"}
    response = rag_client.post("/query", json=payload)
    assert response.status_code == 200
    assert "reply" in response.json()
    
def test_query_with_empty_payload(rag_client):
    response = rag_client.post("/query", json={})
    assert response.status_code == 400

def test_query_with_empty_query(rag_client):
    response = rag_client.post("/query", json={"query": ""})
    assert response.status_code == 400

