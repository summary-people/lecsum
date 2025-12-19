import requests
from typing import Optional, Dict, Any, List

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 15):
        self.base_url = base_url
        self.timeout = timeout
    

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
    
    def upload_document(self, file, summary_style: str):
        files = {
            "file": (file.name, file, file.type)
        }
        data = {
            "summary_style": summary_style
        }

        response = requests.post(
            f"{self.base_url}/api/uploads/documents",
            files=files,
            data=data,
            timeout=300
        )

        return response.json()
    
    def get_documents(self, limit: int = 10, offset: int = 0) -> dict:
        """
        요약 문서 목록 조회
        GET /api/uploads/documents
        """
        url = f"{self.base_url}/api/uploads/documents"
        params = {
            "limit": limit,
            "offset": offset,
        }

        try:
            res = requests.get(url, params=params, timeout=self.timeout)
            res.raise_for_status()
            return res.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": False,
                "message": f"백엔드 요청 실패: {e}",
                "data": None,
            }
