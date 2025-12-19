import requests
from typing import Optional, Dict, Any, List

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    

    def chat(self, document_id: int, question: str, chat_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """챗봇 질문하기"""
        payload = {
            "document_id": document_id,
            "question": question,
            "chat_history": chat_history or []
        }
        response = requests.post(f"{self.base_url}/api/chatbot/chat", json=payload)
        response.raise_for_status()
        return response.json()
    
    def recommend_resources(self, document_id: int) -> Dict[str, Any]:
        """자료 추천받기"""
        payload = {
            "document_id": document_id
        }
        response = requests.post(f"{self.base_url}/api/chatbot/recommend", json=payload)
        response.raise_for_status()
        return response.json()
 