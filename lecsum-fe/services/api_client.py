import requests
from typing import Optional, Dict, Any, List

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 60):
        self.base_url = base_url
        self.timeout = timeout
    

    def chat(self, document_id: int, question: str, chat_history: list):
        url = f"{self.base_url}/api/chatbot/chat"

        payload = {
            "document_id": document_id,
            "question": question,
            "chat_history": chat_history 
        }

        res = requests.post(
            url,
            json=payload,
            timeout=self.timeout
        )

        res.raise_for_status()
        return res.json()
    
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
    
    def generate_quiz(self, document_id: int) -> dict:
        payload = {
            "document_id": document_id
        }

        response = requests.post(
            f"{self.base_url}/api/quizzes/generate",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()
    
    def grade_quiz(self, quiz_set_id: int, quiz_id_list: list[int], user_answer_list: list[str]):
        url = f"{self.base_url}/api/quizzes/grade"
        payload = {
            "quiz_set_id": quiz_set_id,
            "quiz_id_list": quiz_id_list,
            "user_answer_list": user_answer_list
        }

        res = requests.post(url, json=payload, timeout=self.timeout)
        res.raise_for_status()
        return res.json()
    
    def get_quiz_sets(self, document_id: int) -> Dict[str, Any]:
        """퀴즈 목록 불러오기"""
        params = {"document_id": document_id}
        response = requests.get(f"{self.base_url}/api/quizzes/quiz-sets", params=params)
        response.raise_for_status()
        return response.json()

    def get_attempts(self, quiz_set_id: Optional[int] = None, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """응시 기록 목록 조회"""
        params = {
            "quiz_set_id": quiz_set_id,
            "limit": limit,
            "offset": offset
        }
        response = requests.get(f"{self.base_url}/api/quizzes/attempts", params=params)
        response.raise_for_status()
        return response.json()

    def get_attempt_detail(self, attempt_id: int) -> Dict[str, Any]:
        """응시 기록 상세 조회 (문제별 결과 포함)"""
        response = requests.get(f"{self.base_url}/api/quizzes/attempts/{attempt_id}")
        response.raise_for_status()
        return response.json()